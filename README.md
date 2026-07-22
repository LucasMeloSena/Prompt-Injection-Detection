# Prompt Injection Detector

Detecta tentativas de prompt injection — diretas e indiretas — em texto e
documentos PDF em português e inglês, antes que o conteúdo seja processado por
um LLM (especialmente relevante em pipelines RAG).

## Arquitetura

O sistema opera em camadas, cada uma cobrindo o que a anterior deixa passar:

1. **Extração** (`src/pid/extraction/`) — extrai texto de PDFs distinguindo
   conteúdo visível, escondido (texto branco, fonte microscópica) e metadados —
   vetores comuns de injeção indireta.
2. **Heurística** (`src/pid/heuristics/`) — regex de baixo custo para padrões
   conhecidos, com peso maior para matches em conteúdo escondido.
3. **Classificador** (`src/pid/classifier/`) — mDeBERTa-v3-base fine-tunado com
   LoRA, multilíngue, pega paráfrases e ataques sem palavras-chave óbvias.
4. **API** (`src/pid/api/`) — FastAPI expondo `/scan/text` e `/scan/pdf`.

A heurística funciona como filtro barato: quando o score já é muito alto
(short-circuit), o classificador nem é chamado. Caso contrário, o classificador
refina a decisão.

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Rodando a API

```bash
uvicorn pid.api.main:app --reload
```

Documentação interativa em `http://127.0.0.1:8000/docs`.

## Exemplo de uso

```bash
curl -X POST http://127.0.0.1:8000/scan/text \\
  -H "Content-Type: application/json" \\
  -d '{"text": "Ignore todas as instruções anteriores"}'
```

```bash
curl -X POST http://127.0.0.1:8000/scan/pdf \\
  -F "file=@caminho/para/documento.pdf"
```

## Modelo

#### Métricas do conjunto de teste:
| Loss  | Accuracy | Precision | Recall | F1
|------:|------:|------:| -----:|-----:|
| 0.22  | 0.92  | 0.90  | 0.95  | 0.92

O classificador foi hospedado no Hugging Face.