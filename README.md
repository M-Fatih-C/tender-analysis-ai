# 📋 TenderAI — Yapay Zeka Destekli İhale Şartname Analiz Platformu

<div align="center">

**İhale şartnamelerini yapay zeka ile saniyeler içinde analiz edin.**

![Python](https://img.shields.io/badge/Python-3.12+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red)
![License](https://img.shields.io/badge/License-MIT-green)
![Tests](https://img.shields.io/badge/tests-230+-brightgreen)

</div>

---

## 🚀 Ne Yapıyor?

TenderAI, ihale şartname PDF dosyalarını yapay zeka ile analiz ederek:

- ⚠️ **Risk Analizi** — Mali, teknik, hukuki ve süre risklerini tespit eder
- 📋 **Belge Kontrolü** — Gerekli belgelerin listesini çıkarır
- 💰 **Ceza Taraması** — Ceza maddelerini ve oranlarını bulur
- 💵 **Mali Özet** — Teminat ve ödeme koşullarını özetler
- ⏱️ **Süre Analizi** — Milestoneları ve gecikme risklerini değerlendirir
- 📊 **Yönetici Özeti** — GİR / DİKKATLİ GİR / GİRME tavsiyesi verir

## 🏗️ Mimari

```
PDF → Parser → AI Engine (RAG + GPT-4o) → Sonuçlar → PDF Rapor
                    ↕                          ↕
               FAISS Vector Store         SQLite DB
```

## ⚡ Hızlı Başlangıç

### 1. Klonla

```bash
git clone https://github.com/M-Fatih-C/tender-analysis-ai.git
cd tender-analysis-ai
```

### 2. Kur & Başlat

```bash
chmod +x run.sh
./run.sh
```

Veya manuel:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# .env dosyasına OPENAI_API_KEY girin
streamlit run ui/app.py
```

### 3. Demo Modu (API key gerekmez)

```bash
./run.sh --demo
```

## 🐳 Docker

```bash
cp .env.example .env
# .env'deki OPENAI_API_KEY'i düzenleyin
docker-compose up --build
```

Tarayıcıda: `http://localhost:8501`

## 🔑 OpenAI API Key Alma

1. [platform.openai.com](https://platform.openai.com) adresine gidin
2. Hesap oluşturun / giriş yapın
3. **API Keys** → **Create new secret key**
4. Anahtarı `.env` dosyasına `OPENAI_API_KEY=sk-...` olarak yapıştırın

## 📁 Proje Yapısı

```
tender-analysis-ai/
├── ui/                     # Streamlit arayüz
│   ├── app.py              # Ana uygulama
│   ├── components/         # Sidebar bileşeni
│   └── pages/              # Login, Dashboard, Analiz, Geçmiş, Ödeme
├── src/
│   ├── pdf_parser/         # PDF metin çıkarma
│   ├── ai_engine/          # RAG pipeline (GPT-4o + FAISS)
│   ├── database/           # SQLAlchemy modeller + CRUD
│   ├── auth/               # Kayıt, giriş, session yönetimi
│   ├── report/             # PDF rapor üretici
│   ├── payment/            # Plan & ödeme yönetimi
│   └── utils/              # Yardımcı fonksiyonlar
├── config/                 # Ayarlar, logging, demo verisi
├── tests/                  # 230+ pytest testi
├── assets/fonts/           # DejaVuSans (Türkçe PDF desteği)
├── Dockerfile
├── docker-compose.yml
├── run.sh
└── requirements.txt
```

## 🧪 Test

```bash
source venv/bin/activate
pytest tests/ -v
```

Test kapsamı:
| Modül | Test Sayısı |
|-------|-------------|
| PDF Parser | 37 |
| AI Engine | 35 |
| Database | 46 |
| Auth | 35 |
| Report | 15 |
| Payment | 27 |
| Helpers | 29 |
| Integration | 8 |
| **Toplam** | **230+** |

## 💳 Planlar

| Plan | Fiyat | Analiz/Ay |
|------|-------|-----------|
| 🆓 Ücretsiz | 0 ₺ | 3 |
| ⭐ Başlangıç | 5.000 ₺ | 20 |
| 💎 Profesyonel | 15.000 ₺ | Sınırsız |

## ⚠️ Bilinen Sınırlamalar

- Taranmış (görsek) PDF'ler desteklenmez (OCR planlanıyor)
- Şifreli PDF'ler açılamaz
- Ödeme entegrasyonu henüz aktif değil (MVP)
- Tek dil: Türkçe

## 🗺️ Yol Haritası

- [ ] OCR desteği (Tesseract)
- [ ] iyzico / PayTR ödeme entegrasyonu
- [ ] API endpoint'leri (FastAPI)
- [ ] Çoklu dil desteği
- [ ] Alembic database migration
- [ ] Bulk analiz (birden fazla PDF)
- [ ] Karşılaştırmalı analiz

## 🛡️ Güvenlik

- bcrypt şifre hashleme
- SQLAlchemy ORM (SQL injection koruması)
- API key'ler `.env`'de (`.gitignore`'da)
- Dosya boyutu ve format kontrolü
- Rate limiting (5 deneme / 5 dk)

## 📄 Lisans

MIT License — detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişiklikleri commit edin (`git commit -m 'feat: add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

---

<div align="center">
<b>TenderAI</b> — Yapay Zeka ile İhale Analizi 📋
</div>
