# Convertor de Pauta

Aplicação web mobile-first para editar uma representação musical, reproduzir notas e exportar MIDI, WAV e PDF.

## Firebase
- Projeto: `convertor-de-pauta`
- Persistência: Firebase Realtime Database.
- Não utiliza Firestore, Firebase Storage nem Cloud Functions.
- O Hosting publica a raiz do repositório.

## Publicação automática
O workflow `.github/workflows/firebase-hosting.yml` publica no Firebase Hosting após cada push para `main`. Configure no GitHub Actions Secrets a chave JSON da conta de serviço com o nome:

`FIREBASE_SERVICE_ACCOUNT_CONVERTOR_DE_PAUTA`

## Limitação importante da versão inicial
O carregamento de imagem e a pré-visualização funcionam, mas a identificação automática fiável de notas, ritmos, claves e letras exige um motor OMR (Optical Music Recognition) treinado. O botão de análise nesta versão informa essa limitação; não finge que reconheceu a partitura. O editor permite inserir, arrastar e apagar notas e escrever letras. MIDI/WAV são gerados a partir das notas editáveis.

As regras do Realtime Database devem permitir acesso de leitura e escrita para o fluxo de gravação. Não publique regras abertas em produção; adicione autenticação antes de disponibilizar dados privados.
