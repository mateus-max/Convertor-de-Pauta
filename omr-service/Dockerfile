FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl python3 python3-pip python3-venv && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /tmp/audiveris /opt/audiveris \
 && curl -fL "https://github.com/Audiveris/audiveris/releases/download/5.11.0/Audiveris-5.11.0-ubuntu24.04-x86_64.deb" -o /tmp/audiveris/audiveris.deb \
 && apt-get update && apt-get install -y /tmp/audiveris/audiveris.deb \
 && launcher=$(find /opt /usr -type f \( -name 'Audiveris' -o -name 'audiveris' \) -perm -111 -print -quit) && test -n "$launcher" && ln -sf "$launcher" /usr/local/bin/audiveris && rm -rf /var/lib/apt/lists/* /tmp/audiveris

WORKDIR /app
COPY requirements.txt .
RUN python3 -m venv /opt/venv && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt
COPY app.py .
ENV PATH="/opt/venv/bin:$PATH"
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
