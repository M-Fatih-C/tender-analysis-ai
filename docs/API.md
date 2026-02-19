# TenderAI API Dokümantasyonu / API Documentation

## Genel Bakış / Overview

TenderAI REST API, ihale teknik şartname analiz hizmetlerine programatik erişim sağlar.

> **Not:** API henüz geliştirme aşamasındadır. Modül 8'de implement edilecektir.

---

## Base URL

```
http://localhost:8000/api/v1
```

---

## Kimlik Doğrulama / Authentication

API, JWT (JSON Web Token) tabanlı kimlik doğrulama kullanır.

### Token Alma / Get Token

```http
POST /auth/login
Content-Type: application/json

{
  "username": "kullanici",
  "password": "sifre123"
}
```

**Yanıt / Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### Token Kullanımı / Using Token

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

---

## Endpoint'ler / Endpoints

### 1. Analiz / Analysis

#### PDF Yükleme ve Analiz / Upload and Analyze PDF

```http
POST /analysis/upload
Content-Type: multipart/form-data
Authorization: Bearer {token}

file: <PDF dosyası>
```

**Yanıt / Response:**

```json
{
  "analysis_id": 1,
  "status": "processing",
  "message": "Analiz başlatıldı"
}
```

#### Analiz Sonucu Alma / Get Analysis Result

```http
GET /analysis/{analysis_id}
Authorization: Bearer {token}
```

**Yanıt / Response:**

```json
{
  "analysis_id": 1,
  "status": "completed",
  "risk_score": 72.5,
  "risk_analysis": [...],
  "required_documents": [...],
  "penalty_clauses": [...],
  "financial_summary": {...},
  "timeline_analysis": {...}
}
```

#### Analiz Geçmişi / Analysis History

```http
GET /analysis/history?page=1&limit=20
Authorization: Bearer {token}
```

---

### 2. Kullanıcı / User

#### Kayıt / Register

```http
POST /auth/register
Content-Type: application/json

{
  "email": "kullanici@email.com",
  "username": "kullanici",
  "password": "sifre123",
  "full_name": "Ad Soyad"
}
```

#### Profil / Profile

```http
GET /user/profile
Authorization: Bearer {token}
```

---

### 3. Abonelik / Subscription

#### Plan Listesi / Plan List

```http
GET /subscription/plans
```

#### Abonelik Durumu / Subscription Status

```http
GET /subscription/status
Authorization: Bearer {token}
```

---

## Hata Kodları / Error Codes

| Kod | Açıklama |
|-----|----------|
| 400 | Geçersiz istek / Bad Request |
| 401 | Kimlik doğrulama hatası / Unauthorized |
| 403 | Yetkisiz erişim / Forbidden |
| 404 | Kaynak bulunamadı / Not Found |
| 413 | Dosya boyutu çok büyük / File Too Large |
| 422 | İşlenemeyen veri / Unprocessable Entity |
| 429 | Çok fazla istek / Rate Limit Exceeded |
| 500 | Sunucu hatası / Internal Server Error |

---

## Rate Limiting

| Plan | Limit |
|------|-------|
| Ücretsiz | 10 istek/dakika |
| Temel | 30 istek/dakika |
| Profesyonel | 100 istek/dakika |
| Kurumsal | Sınırsız |

---

> 📌 Bu dokümantasyon Modül 8'de güncellenecektir.
