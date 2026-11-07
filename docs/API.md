# Programmatic components

This checkout is a Streamlit application, not an implemented REST API service.
Earlier `/api/v1` login/analysis examples described a proposed API and are not
working HTTP endpoints. No API authentication or deployment guarantee is made.

The current entry point is `streamlit run app.py`. Python modules include:

| Area | Source |
|---|---|
| PDF extraction | `src/pdf_parser/parser.py` |
| AI analysis and retrieval | `src/ai_engine/analyzer.py`, `chatbot.py` |
| Gemini adapter / comparison | `gemini_analyzer.py`, `comparator.py` |
| Persistence | `src/database/models.py`, `db.py` |
| Authentication and plans | `src/auth/auth.py`, `src/payment/payment.py` |
| Exports | `src/report/` |

Read method signatures and the corresponding `tests/test_*.py` examples before
using a component. APIs may change during prototype development. Live provider
calls require your own credentials and authorization to transmit document text.
A standalone HTTP API, its threat model and endpoint tests remain future work.
