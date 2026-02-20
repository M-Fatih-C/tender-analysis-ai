# 📋 TenderAI v2.0.0

**Yapay Zeka ile İhale Şartname Analiz Platformu**

AI-powered tender specification analysis platform for Turkish public procurement.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-red)
![Tests](https://img.shields.io/badge/Tests-234%20passed-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🎯 Özellikler

| Özellik | Açıklama |
|---------|----------|
| 🔍 **AI Analiz** | OpenAI + Gemini destekli 6 adımlı risk analizi |
| 📚 **Batch Analiz** | 10 dosyaya kadar toplu PDF analizi |
| 💬 **Chatbot** | Şartnameye RAG tabanlı soru-cevap |
| ⚖️ **Karşılaştırma** | Birden fazla ihaleyi yan yana inceleme |
| 🏢 **Firma Profili** | Uygunluk skoru hesaplama |
| 📊 **Dashboard** | Gauge, trend, donut, aktivite grafikleri |
| 📥 **Rapor** | PDF ve Excel çıktı |
| 🔔 **Bildirimler** | In-app bildirim sistemi |

---

## 🚀 Hızlı Başlangıç

### Seçenek 1: Docker (Önerilen)
```bash
# Klonla
git clone https://github.com/M-Fatih-C/tender-analysis-ai.git
cd tender-analysis-ai

# .env oluştur
cp .env.example .env
# API key'leri düzenle

# Başlat
docker compose up -d

# Aç: http://localhost:8501
```

### Seçenek 2: Manuel
```bash
# Klonla
git clone https://github.com/M-Fatih-C/tender-analysis-ai.git
cd tender-analysis-ai

# Script ile başlat
chmod +x run.sh
./run.sh

# Veya demo modda
./run.sh --demo
```

### Seçenek 3: Adım Adım
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# .env'i düzenle
streamlit run app.py
```

---

## ⚙️ Ortam Değişkenleri

| Değişken | Zorunlu | Açıklama |
|----------|:-------:|----------|
| `OPENAI_API_KEY` | ⚠️ | OpenAI API key (GPT-4o-mini) |
| `GEMINI_API_KEY` | ⚠️ | Google Gemini API key (fallback) |
| `SECRET_KEY` | ✅ | JWT/Session güvenlik anahtarı |
| `DEMO_MODE` | ❌ | `true` = API key'siz demo mod |
| `DATABASE_URL` | ❌ | SQLite/PostgreSQL URL |

> En az bir API key gerekli. İkisi de yoksa `--demo` modunu kullanın.

---

## 📐 Proje Yapısı

```
tender-analysis-ai/
├── app.py                    # Ana giriş noktası
├── config/                   # Ayarlar, demo data
├── src/
│   ├── ai_engine/            # OpenAI, Gemini, chatbot, matcher, comparator
│   ├── auth/                 # Kimlik doğrulama
│   ├── database/             # SQLAlchemy modeller + CRUD
│   ├── pdf_parser/           # PDF metin çıkarma
│   ├── report/               # PDF + Excel rapor üretimi
│   └── utils/                # Yardımcı fonksiyonlar
├── ui/
│   ├── components/           # Header, sidebar, styles, onboarding
│   └── views/                # 8 sayfa (login, dashboard, analiz, vb.)
├── tests/                    # 234 test
├── Dockerfile                # Multi-stage production build
├── docker-compose.yml        # Production stack + nginx
└── .github/workflows/ci.yml  # GitHub Actions CI/CD
```

---

## 🧪 Test

```bash
# Tüm testleri çalıştır
python -m pytest tests/ -v

# Coverage ile
python -m pytest tests/ --cov=src --cov-report=html
```

---

## 🐳 Production Deployment

```bash
# Sadece web app
docker compose up -d

# Nginx reverse proxy ile
docker compose --profile production up -d

# Logları izle
docker compose logs -f tenderai
```

---

## 📄 Lisans

MIT License — © 2025 TenderAI
