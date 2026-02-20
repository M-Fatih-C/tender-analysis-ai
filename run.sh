#!/bin/bash
# ============================================================
# TenderAI Başlatma Scripti / Startup Script
# ============================================================
# Kullanım / Usage:
#   chmod +x run.sh
#   ./run.sh
#   ./run.sh --demo   # Demo modunda başlat
# ============================================================

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}📋 TenderAI v1.0.0${NC}"
echo "================================"

# 1. Virtual env kontrol / Check virtual env
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚙️  Virtual environment oluşturuluyor...${NC}"
    python3 -m venv venv
fi

echo -e "${GREEN}✅ Virtual environment aktif${NC}"
source venv/bin/activate

# 2. Bağımlılıklar / Dependencies
echo -e "${YELLOW}📦 Bağımlılıklar kontrol ediliyor...${NC}"
pip install -q -r requirements.txt

# 3. .env kontrol / Check .env
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env dosyası bulunamadı, .env.example'dan kopyalanıyor...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}📝 Lütfen .env dosyasını düzenleyip OPENAI_API_KEY'i girin.${NC}"
    else
        echo -e "${RED}❌ .env.example bulunamadı!${NC}"
    fi
fi

# 4. Demo modu / Demo mode
if [ "$1" = "--demo" ]; then
    export DEMO_MODE=true
    echo -e "${GREEN}🎭 Demo modu aktif${NC}"
fi

# 5. Dizinler / Directories
mkdir -p logs data/uploads data/reports

# 6. DB initialize
echo -e "${GREEN}🗄️  Veritabanı başlatılıyor...${NC}"
python3 -c "from src.database.db import DatabaseManager; DatabaseManager().init_db(); print('✅ Database hazır')"

# 7. Streamlit başlat / Start Streamlit
echo ""
echo -e "${GREEN}🚀 TenderAI başlatılıyor...${NC}"
echo -e "   URL: ${YELLOW}http://localhost:8501${NC}"
echo ""

streamlit run app.py \
    --server.port=8501 \
    --browser.gatherUsageStats=false
