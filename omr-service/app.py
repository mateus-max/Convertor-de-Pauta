import os
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(title="Convertor de Pauta OMR", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://convertor-de-pauta.web.app", "https://convertor-de-pauta.firebaseapp.com"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

AUDIVERIS = os.environ.get("AUDIVERIS_BIN", "/opt/audiveris/bin/Audiveris")
MAX_BYTES = 20 * 1024 * 1024
ALLOWED = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".pdf"}


@app.get("/health")
def health():
    return {"ok": True, "engine": "Audiveris", "version": "5.11.0"}


@app.post("/api/recognize")
async def recognize(file: UploadFile = File(...)):
    suffix = Path(file.filename or "score.png").suffix.lower()
    if suffix not in ALLOWED:
        raise HTTPException(415, "Formato não suportado. Envie JPG, PNG, TIFF, BMP ou PDF.")
    data = await file.read()
    if not data or len(data) > MAX_BYTES:
        raise HTTPException(413, "O ficheiro está vazio ou ultrapassa 20 MB.")

    with tempfile.TemporaryDirectory(prefix="score-omr-") as temp:
        root = Path(temp)
        source = root / ("input" + suffix)
        output = root / "out"
        output.mkdir()
        source.write_bytes(data)
        command = [AUDIVERIS, "-batch", "-export", "-output", str(output), "--", str(source)]
        try:
            run = subprocess.run(command, capture_output=True, text=True, timeout=240, check=False)
        except subprocess.TimeoutExpired:
            raise HTTPException(504, "A análise demorou demasiado tempo. Tente uma imagem mais pequena ou nítida.")
        if run.returncode != 0:
            detail = (run.stderr or run.stdout or "Audiveris não conseguiu processar a imagem.")[-3500:]
            raise HTTPException(422, detail)
        candidates = list(output.rglob("*.mxl")) + list(output.rglob("*.musicxml")) + list(output.rglob("*.xml"))
        if not candidates:
            raise HTTPException(422, "O motor não conseguiu gerar MusicXML para esta partitura.")
        result_path = candidates[0]
        try:
            if result_path.suffix.lower() == ".mxl":
                with zipfile.ZipFile(result_path) as archive:
                    container = ET.fromstring(archive.read("META-INF/container.xml"))
                    ns = {"c": "urn:oasis:names:tc:opendocument:xmlns:container"}
                    rootfile = container.find(".//c:rootfile", ns)
                    if rootfile is None:
                        raise ValueError("MusicXML container sem rootfile")
                    xml = archive.read(rootfile.attrib["full-path"]).decode("utf-8")
            else:
                xml = result_path.read_text(encoding="utf-8")
            ET.fromstring(xml)
        except Exception as exc:
            raise HTTPException(500, f"Não foi possível ler o MusicXML exportado: {exc}")
        return JSONResponse({"ok": True, "engine": "Audiveris 5.11.0", "filename": result_path.name, "musicxml": xml})
