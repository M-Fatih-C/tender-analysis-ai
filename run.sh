#!/bin/bash
# ============================================================
# TenderAI Başlatma Scripti / Startup Script v2.0.0
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
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "  ╔═══════════════════════════════════════╗"
echo "  ║       📋 TenderAI v2.0.0              ║"
echo "  ║   İhale Şartname Analiz Platformu     ║"
echo "  ╚═══════════════════════════════════════╝"
echo -e "${NC}"

# 1. Virtual env kontrol / Check virtual env
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚙️  Virtual environment oluşturuluyor...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment aktif${NC}"

# 2. Bağımlılıklar / Dependencies
echo -e "${YELLOW}📦 Bağımlılıklar kontrol ediliyor...${NC}"
pip install -q -r requirements.txt 2>/dev/null
echo -e "${GREEN}✅ Bağımlılıklar yüklendi${NC}"

# 3. .env kontrol / Check .env
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env dosyası bulunamadı, .env.example'dan kopyalanıyor...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}📝 Lütfen .env dosyasını düzenleyip API key'leri girin.${NC}"
    else
        echo "OPENAI_API_KEY=sk-your-key-here" > .env
        echo "GEMINI_API_KEY=" >> .env
        echo "DEMO_MODE=true" >> .env
        echo "SECRET_KEY=change-me-$(date +%s)" >> .env
        echo -e "${YELLOW}📝 Temel .env oluşturuldu. API key ekleyin veya --demo kullanın.${NC}"
    fi
fi

# 4. Demo modu / Demo mode
if [ "$1" = "--demo" ]; then
    export DEMO_MODE=true
    echo -e "${GREEN}🎮 Demo modu aktif${NC}"
fi

# 5. Dizinler / Directories
mkdir -p logs data/uploads data/reports

# 6. DB initialize
echo -e "${YELLOW}🗄️  Veritabanı başlatılıyor...${NC}"
python3 -c "from src.database.db import DatabaseManager; DatabaseManager().init_db(); print('✅ Database hazır')" 2>/dev/null || {
    echo -e "${RED}❌ Veritabanı hatası${NC}"
    exit 1
}

# 7. Mevcut port kontrol / Check port
if lsof -ti:8501 >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Port 8501 kullanılıyor, kapatılıyor...${NC}"
    lsof -ti:8501 | xargs kill -9 2>/dev/null
    sleep 1
fi

# 8. Streamlit başlat / Start Streamlit
echo ""
echo -e "${GREEN}🚀 TenderAI başlatılıyor...${NC}"
echo -e "   ${CYAN}Local:    http://localhost:8501${NC}"
echo -e "   ${CYAN}Demo:     ./run.sh --demo${NC}"
echo ""

streamlit run app.py \
    --server.port=8501 \
    --browser.gatherUsageStats=false
