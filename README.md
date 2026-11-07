# TenderAI

A Streamlit prototype for analysing Turkish tender specifications: PDF text
extraction, AI-assisted risk analysis, retrieval-assisted questions, comparisons
and PDF/Excel/DOCX report components. Its outputs require human review and are
not procurement or legal advice.

## Components

`app.py` and `ui/` provide the interface. `src/pdf_parser/` extracts PDF text;
`src/ai_engine/` contains OpenAI/Gemini adapters, FAISS retrieval, chat, matching
and comparison logic. SQLAlchemy stores users and analysis records under
`src/database/`; `src/auth/`, `payment/` and `report/` are separate modules.
The code is a broad prototype: the presence of payment or authentication modules
does not establish a production deployment or payment-provider integration.

There is **no implemented standalone REST API server** in this checkout.
[Programmatic components](docs/API.md) describe the actual Python modules.

## Local setup

Use Python 3.12 in an isolated environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
cp .env.example .env
# Edit .env before starting; use DEMO_MODE=true for a synthetic demonstration.
streamlit run app.py
```

Set a strong unique `SECRET_KEY`. Live analysis requires a configured provider
key (`OPENAI_API_KEY` and/or `GEMINI_API_KEY`, according to the chosen flow).
`config/settings.py` defines the supported settings, including `DATABASE_URL`
and `DEMO_MODE`. Example/default keys are not deployment credentials. Demo data
is illustrative and does not evaluate model quality.

## Docker

```bash
cp .env.example .env
# Configure .env, then:
docker compose up --build -d tenderai
```

The app is available on port 8501. The image uses a non-root user and persists
data/logs with volumes. `.dockerignore` excludes local secrets and runtime data
from the build context. The optional `production` profile also starts nginx
(requiring local certificates) and Watchtower with Docker-socket access; inspect
that profile before use. It is not a verified production deployment recipe.
Container build/runtime was not validated in the audit environment.

## Tests

```bash
python -m pip install pytest pytest-cov pytest-socket
# First download public tokenizer tables into a local cache, not an AI API:
python -c "import tiktoken; tiktoken.get_encoding('o200k_base'); tiktoken.get_encoding('cl100k_base')"
DEMO_MODE=true python -m pytest tests -q --disable-socket --allow-unix-socket
```

The audit passed all 234 tests with both tokenizer tables cached and external
sockets blocked. An uncached offline run passed 219 and failed 15
because tiktoken attempted an initial table download. Tokenizer assets must be
cached before a fully offline run. Test counts are not a permanent passing badge;
inspect the current CI run. Lint/security failures are no longer intentionally
converted into successful workflow exits.

## Limitations and data handling

PDF layouts and text extraction vary; image-only scans are not guaranteed to work.
Retrieval and generated findings can miss or invent important details. Review
source citations and calculations yourself. Live provider calls can transmit
document text outside the machine; use only documents you may process and send.
Keep uploads, extracted text, databases, logs, reports and keys out of commits.
Dependency ranges are broad; the audited local resolved environment does not
prove every future resolution or container image is safe.


## License and contact

No license file is currently included; no new license or redistribution grant is asserted here. Author: [Muhammet Fatih Çetintaş](https://github.com/M-Fatih-C).
