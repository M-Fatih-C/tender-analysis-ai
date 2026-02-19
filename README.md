# 🏗️ TenderAI — İhale Şartname Analiz Platformu

<p align="center">
  <strong>Yapay zeka destekli ihale teknik şartname analizi</strong><br>
  RAG + GPT-4 ile risk analizi, belge kontrolü ve mali özet — tek tıkla.
</p>

---

## 📋 Proje Açıklaması

**TenderAI**, Türkiye'deki kamu ve özel sektör ihalelerine giren firmaların teknik şartname PDF'lerini yapay zeka ile analiz eden bir SaaS platformudur.

Firmalar ihale şartname PDF'lerini sisteme yükler; TenderAI, **RAG (Retrieval Augmented Generation)** ve **GPT-4** kullanarak aşağıdaki analizleri otomatik olarak gerçekleştirir:

- 🔍 **Risk Analizi** — Şartnamedeki riskli maddelerin tespiti ve derecelendirmesi
- 📄 **Gerekli Belge Listesi** — Teklif için sunulması gereken belgelerin çıkarılması
- ⚖️ **Ceza Maddeleri** — Gecikme, eksiklik ve uyumsuzluk cezalarının özetlenmesi
- 💰 **Mali Özet** — Teminat, ödeme koşulları ve mali yükümlülüklerin analizi
- ⏱️ **Süre Analizi** — Proje takvimi, teslim süreleri ve kritik tarihlerin belirlenmesi

---

## ✨ Özellikler

| Özellik | Açıklama |
|---------|----------|
| PDF Analizi | Teknik şartname PDF'lerini otomatik ayrıştırma |
| Yapay Zeka Motoru | GPT-4 + RAG tabanlı akıllı analiz |
| Risk Skorlama | Madde bazlı risk puanlama sistemi |
| Belge Kontrol | Eksik belge uyarı sistemi |
| PDF Rapor | Analiz sonuçlarını PDF olarak dışa aktarma |
| Dashboard | Interaktif analiz paneli (Streamlit) |
| Kullanıcı Yönetimi | JWT tabanlı kimlik doğrulama |
| Ödeme Sistemi | Abonelik bazlı ödeme altyapısı |
| Analiz Geçmişi | Tüm geçmiş analizlere erişim |
| API Desteği | FastAPI ile RESTful API (gelecek sürüm) |

---

## 🛠️ Teknolojiler

| Katman | Teknoloji |
|--------|-----------|
| **Dil** | Python 3.14 |
| **Frontend** | Streamlit |
| **Backend** | FastAPI + Uvicorn |
| **Veritabanı** | SQLite + SQLAlchemy |
| **AI/ML** | OpenAI GPT-4, LangChain, Sentence Transformers |
| **Vektör DB** | Qdrant |
| **PDF İşleme** | pdfplumber, Camelot |
| **Raporlama** | FPDF2, Plotly |
| **Auth** | bcrypt, PyJWT |

---

## 🚀 Kurulum

### 1. Depoyu klonlayın

```bash
git clone https://github.com/<kullanici>/tender-analysis-ai.git
cd tender-analysis-ai
```

### 2. Sanal ortam oluşturun

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
```

### 3. Bağımlılıkları yükleyin

```bash
pip install -r requirements.txt
```

### 4. Ortam değişkenlerini ayarlayın

```bash
cp .env.example .env
# .env dosyasını düzenleyin ve API anahtarlarınızı girin
```

### 5. Uygulamayı başlatın

```bash
streamlit run ui/app.py
```

---

## 📖 Kullanım

1. **Giriş Yapın** — Kullanıcı adı ve şifrenizle sisteme giriş yapın
2. **PDF Yükleyin** — İhale teknik şartname PDF'ini sürükle-bırak ile yükleyin
3. **Analiz Başlatın** — "Analiz Et" butonuyla AI analiz sürecini başlatın
4. **Sonuçları İnceleyin** — Risk analizi, belge listesi, ceza maddeleri ve mali özeti görüntüleyin
5. **Rapor İndirin** — Sonuçları PDF rapor olarak indirin

---

## 📸 Ekran Görüntüleri

> 📷 Ekran görüntüleri yakında eklenecektir.

---

## 📁 Proje Yapısı

```
tender-analysis-ai/
├── config/          # Konfigürasyon ayarları
├── src/             # Ana kaynak kodu
│   ├── pdf_parser/  # PDF ayrıştırma motoru
│   ├── ai_engine/   # AI analiz motoru
│   ├── database/    # Veritabanı modelleri
│   ├── auth/        # Kimlik doğrulama
│   ├── report/      # Rapor üretici
│   ├── payment/     # Ödeme sistemi
│   └── utils/       # Yardımcı araçlar
├── ui/              # Streamlit arayüzü
├── tests/           # Test dosyaları
├── data/            # Veri dizini
└── docs/            # Dokümantasyon
```

---

## 🧪 Testler

```bash
pytest tests/ -v
```

---

## 🗺️ Yol Haritası

- [x] Modül 1: Proje yapısı kurulumu
- [ ] Modül 2: PDF ayrıştırma motoru
- [ ] Modül 3: AI analiz motoru
- [ ] Modül 4: Veritabanı ve kullanıcı yönetimi
- [ ] Modül 5: Streamlit arayüzü
- [ ] Modül 6: Raporlama sistemi
- [ ] Modül 7: Ödeme entegrasyonu
- [ ] Modül 8: FastAPI backend
- [ ] Modül 9: Test ve deployment

---

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) kapsamında lisanslanmıştır.

---

## 📬 İletişim

Sorularınız veya önerileriniz için:

- 📧 Email: info@tenderai.com.tr
- 🐛 Issue: [GitHub Issues](https://github.com/<kullanici>/tender-analysis-ai/issues)

---

<p align="center">
  <sub>TenderAI ile ihalelerde bir adım önde olun. 🚀</sub>
</p>
