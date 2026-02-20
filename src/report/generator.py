"""
TenderAI PDF Rapor Üretici / PDF Report Generator.

fpdf2 kütüphanesi ile analiz sonuçlarından profesyonel
PDF rapor üretir. DejaVuSans fontu ile Türkçe karakter desteği.

Generates professional PDF reports from analysis results
using fpdf2 library. Turkish character support via DejaVuSans font.
"""

import io
import logging
from datetime import datetime, timezone
from pathlib import Path

from fpdf import FPDF

logger = logging.getLogger(__name__)

# Font dizini / Font directory
_FONTS_DIR = Path(__file__).resolve().parent.parent.parent / "assets" / "fonts"

# ============================================================
# Renkler / Colors
# ============================================================

_COLORS = {
    "primary": (55, 71, 133),       # Koyu mavi / Dark blue
    "primary_light": (102, 126, 234),  # Açık mavi / Light blue
    "success": (39, 174, 96),       # Yeşil / Green
    "warning": (243, 156, 18),      # Turuncu / Orange
    "danger": (231, 76, 60),        # Kırmızı / Red
    "dark": (44, 62, 80),           # Koyu gri / Dark gray
    "gray": (149, 165, 166),        # Gri / Gray
    "light": (236, 240, 241),       # Açık gri / Light gray
    "white": (255, 255, 255),       # Beyaz / White
    "black": (30, 30, 30),          # Siyah / Black
    "row_even": (245, 247, 250),    # Çift satır / Even row
    "row_odd": (255, 255, 255),     # Tek satır / Odd row
}


# ============================================================
# TenderPDF — Custom FPDF alt sınıfı
# ============================================================


class TenderPDF(FPDF):
    """Header ve footer ile özelleştirilmiş FPDF / Custom FPDF with header/footer."""

    def __init__(self, file_name: str = "Analiz Raporu") -> None:
        super().__init__(orientation="P", unit="mm", format="A4")
        self._file_name = file_name
        self._is_cover = True  # Kapak sayfasında header/footer gösterme

    def header(self) -> None:
        """Her sayfanın üst kısmı / Top of every page."""
        if self._is_cover:
            return
        self.set_font("DejaVu", "B", 8)
        self.set_text_color(*_COLORS["gray"])
        self.cell(0, 6, "TenderAI - İhale Analiz Raporu", align="L")
        self.cell(0, 6, self._file_name, align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*_COLORS["primary"])
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self) -> None:
        """Her sayfanın alt kısmı / Bottom of every page."""
        if self._is_cover:
            return
        self.set_y(-15)
        self.set_font("DejaVu", "", 7)
        self.set_text_color(*_COLORS["gray"])
        self.cell(0, 8, f"Sayfa {self.page_no()}/{{nb}}", align="C")


# ============================================================
# ReportGenerator Sınıfı / ReportGenerator Class
# ============================================================


class ReportGenerator:
    """
    Profesyonel PDF rapor üretici / Professional PDF report generator.

    Analiz sonuçlarından A4 boyutunda, Türkçe destekli,
    tablolu ve renkli PDF rapor üretir.
    """

    def __init__(self) -> None:
        """ReportGenerator başlat / Initialize."""
        self._font_regular = str(_FONTS_DIR / "DejaVuSans.ttf")
        self._font_bold = str(_FONTS_DIR / "DejaVuSans-Bold.ttf")

        # Font dosyalarının varlığını kontrol et
        if not Path(self._font_regular).exists():
            raise FileNotFoundError(
                f"DejaVuSans.ttf bulunamadı: {self._font_regular}\n"
                "assets/fonts/ dizinine DejaVuSans.ttf koyun."
            )

    def generate(
        self,
        analysis_result: dict,
        file_name: str = "İhale Şartnamesi",
    ) -> bytes:
        """
        Tam PDF rapor üret ve bytes olarak döndür.
        Generate full PDF report and return as bytes.

        Args:
            analysis_result: Analiz sonucu dict'i / Analysis result dict
            file_name: İhale dosya adı / Tender file name

        Returns:
            PDF içeriği bytes / PDF content as bytes
        """
        pdf = TenderPDF(file_name=file_name)

        # Font kayıt / Register fonts
        pdf.add_font("DejaVu", "", self._font_regular)
        pdf.add_font("DejaVu", "B", self._font_bold)
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.alias_nb_pages()

        # Sayfaları oluştur / Build pages
        self._add_cover_page(pdf, analysis_result, file_name)
        pdf._is_cover = False  # Artık header/footer göster

        self._add_executive_summary(pdf, analysis_result)
        self._add_risk_analysis(pdf, analysis_result.get("risk_analysis", {}))
        self._add_required_documents(pdf, analysis_result.get("required_documents", {}))
        self._add_penalty_clauses(pdf, analysis_result.get("penalty_clauses", {}))
        self._add_financial_summary(pdf, analysis_result.get("financial_summary", {}))
        self._add_timeline(pdf, analysis_result.get("timeline_analysis", {}))
        self._add_disclaimer(pdf)

        # bytes olarak döndür / Return as bytes
        buf = io.BytesIO()
        pdf.output(buf)
        buf.seek(0)
        logger.info(f"PDF rapor üretildi / Report generated: {file_name}")
        return buf.getvalue()

    # ----------------------------------------------------------
    # Kapak Sayfası / Cover Page
    # ----------------------------------------------------------

    def _add_cover_page(self, pdf: TenderPDF, result: dict, file_name: str) -> None:
        """Kapak sayfası / Cover page."""
        pdf.add_page()

        # Üst boşluk
        pdf.ln(35)

        # Logo ve başlık
        pdf.set_font("DejaVu", "B", 28)
        pdf.set_text_color(*_COLORS["primary"])
        pdf.cell(0, 15, "TenderAI", align="C", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("DejaVu", "", 12)
        pdf.set_text_color(*_COLORS["gray"])
        pdf.cell(0, 8, "Yapay Zeka Destekli İhale Analiz Platformu", align="C", new_x="LMARGIN", new_y="NEXT")

        pdf.ln(15)

        # Çizgi
        pdf.set_draw_color(*_COLORS["primary"])
        pdf.set_line_width(1)
        pdf.line(40, pdf.get_y(), 170, pdf.get_y())
        pdf.ln(15)

        # Rapor başlığı
        pdf.set_font("DejaVu", "B", 22)
        pdf.set_text_color(*_COLORS["dark"])
        pdf.cell(0, 12, "İHALE ANALİZ RAPORU", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(8)

        # Dosya adı
        pdf.set_font("DejaVu", "", 14)
        pdf.set_text_color(*_COLORS["primary_light"])
        display_name = file_name if len(file_name) <= 60 else file_name[:57] + "..."
        pdf.cell(0, 10, display_name, align="C", new_x="LMARGIN", new_y="NEXT")

        pdf.ln(20)

        # Risk skoru büyük
        risk_score = result.get("risk_score", 0)
        risk_level = result.get("risk_level", "—")
        color = self._risk_color_rgb(risk_score)

        pdf.set_font("DejaVu", "B", 48)
        pdf.set_text_color(*color)
        pdf.cell(0, 25, str(risk_score), align="C", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("DejaVu", "B", 14)
        pdf.cell(0, 8, f"Risk Seviyesi: {risk_level}", align="C", new_x="LMARGIN", new_y="NEXT")

        pdf.ln(25)

        # Alt bilgiler
        pdf.set_font("DejaVu", "", 10)
        pdf.set_text_color(*_COLORS["dark"])
        now = datetime.now(timezone.utc).strftime("%d.%m.%Y %H:%M UTC")
        pdf.cell(0, 7, f"Analiz Tarihi: {now}", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 7, "Hazırlayan: TenderAI Yapay Zeka Analiz Sistemi", align="C", new_x="LMARGIN", new_y="NEXT")

    # ----------------------------------------------------------
    # Yönetici Özeti / Executive Summary
    # ----------------------------------------------------------

    def _add_executive_summary(self, pdf: TenderPDF, result: dict) -> None:
        """Yönetici özeti sayfası / Executive summary page."""
        pdf.add_page()
        self._section_title(pdf, "Yönetici Özeti")

        risk_score = result.get("risk_score", 0)
        risk_level = result.get("risk_level", "—")
        exec_data = result.get("executive_summary", {})

        # Risk ve tavsiye kutusu
        if risk_score <= 35:
            advice = "GİR — Bu ihaleye katılım önerilir."
            advice_color = _COLORS["success"]
        elif risk_score <= 65:
            advice = "DİKKATLİ GİR — Risklere karşı önlem alınmalıdır."
            advice_color = _COLORS["warning"]
        else:
            advice = "GİRME — Yüksek risk, katılım önerilmez."
            advice_color = _COLORS["danger"]

        # Risk kutusu
        pdf.set_fill_color(*advice_color)
        pdf.set_text_color(*_COLORS["white"])
        pdf.set_font("DejaVu", "B", 14)
        pdf.cell(0, 12, f"  TAVSİYE: {advice}", fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

        # Metrikler
        pdf.set_text_color(*_COLORS["dark"])
        pdf.set_font("DejaVu", "B", 11)
        pdf.cell(95, 8, f"Risk Skoru: {risk_score}/100", new_x="RIGHT")
        pdf.cell(95, 8, f"Risk Seviyesi: {risk_level}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

        # Genel değerlendirme
        ozet = ""
        if isinstance(exec_data, dict):
            ozet = exec_data.get("ozet", exec_data.get("genel_degerlendirme", ""))
        elif isinstance(exec_data, str):
            ozet = exec_data

        if ozet:
            self._sub_heading(pdf, "Genel Değerlendirme")
            self._body_text(pdf, str(ozet))

        # Güçlü yanlar
        guclu = exec_data.get("guclu_yanlar", []) if isinstance(exec_data, dict) else []
        if guclu:
            self._sub_heading(pdf, "Güçlü Yanlar")
            for item in guclu:
                self._bullet(pdf, str(item), color=_COLORS["success"])

        # Riskli alanlar
        zayif = []
        if isinstance(exec_data, dict):
            zayif = exec_data.get("zayif_yanlar", exec_data.get("riskli_alanlar", []))
        if zayif:
            self._sub_heading(pdf, "Riskli Alanlar")
            for item in zayif:
                self._bullet(pdf, str(item), color=_COLORS["danger"])

    # ----------------------------------------------------------
    # Risk Analizi / Risk Analysis
    # ----------------------------------------------------------

    def _add_risk_analysis(self, pdf: TenderPDF, data: dict) -> None:
        """Risk analizi sayfası / Risk analysis page."""
        pdf.add_page()
        self._section_title(pdf, "Risk Analizi")

        if not data or data.get("error"):
            self._body_text(pdf, "Risk analizi verisi bulunamadı.")
            return

        ozet = data.get("ozet", "")
        if ozet:
            self._body_text(pdf, str(ozet))
            pdf.ln(4)

        riskler = data.get("riskler", [])
        if not riskler:
            self._body_text(pdf, "Belirgin risk tespit edilmedi.")
            return

        headers = ["Kategori", "Başlık", "Seviye", "Öneri"]
        col_widths = [28, 52, 22, 88]

        rows = []
        for risk in riskler:
            if not isinstance(risk, dict):
                continue
            rows.append([
                risk.get("kategori", "—"),
                risk.get("baslik", "—"),
                risk.get("seviye", "—"),
                risk.get("oneri", "—"),
            ])

        self._add_table(pdf, headers, rows, col_widths, severity_col=2)

    # ----------------------------------------------------------
    # Gerekli Belgeler / Required Documents
    # ----------------------------------------------------------

    def _add_required_documents(self, pdf: TenderPDF, data: dict) -> None:
        """Gerekli belgeler sayfası / Required documents page."""
        pdf.add_page()
        self._section_title(pdf, "Gerekli Belgeler")

        if not data or data.get("error"):
            self._body_text(pdf, "Belge analizi verisi bulunamadı.")
            return

        # Zorunlu belgeler
        zorunlu = data.get("zorunlu_belgeler", [])
        if zorunlu:
            self._sub_heading(pdf, "Zorunlu Belgeler")
            headers = ["#", "Belge Adı", "Detay"]
            col_widths = [12, 88, 90]
            rows = []
            for i, item in enumerate(zorunlu, 1):
                if isinstance(item, dict):
                    name = item.get("belge_adi", item.get("ad", str(item)))
                    detail = item.get("aciklama", item.get("not", ""))
                else:
                    name = str(item)
                    detail = ""
                rows.append([str(i), name, detail])
            self._add_table(pdf, headers, rows, col_widths)

        # İsteğe bağlı
        istege = data.get("istege_bagli_belgeler", [])
        if istege:
            pdf.ln(4)
            self._sub_heading(pdf, "İsteğe Bağlı Belgeler")
            for item in istege:
                name = item.get("belge_adi", str(item)) if isinstance(item, dict) else str(item)
                self._bullet(pdf, name)

        # Uyarılar
        uyarilar = data.get("onemli_uyarilar", [])
        if uyarilar:
            pdf.ln(4)
            self._sub_heading(pdf, "Önemli Uyarılar")
            for u in uyarilar:
                self._bullet(pdf, str(u), color=_COLORS["danger"])

    # ----------------------------------------------------------
    # Ceza Maddeleri / Penalty Clauses
    # ----------------------------------------------------------

    def _add_penalty_clauses(self, pdf: TenderPDF, data: dict) -> None:
        """Ceza maddeleri sayfası / Penalty clauses page."""
        pdf.add_page()
        self._section_title(pdf, "Ceza Maddeleri")

        if not data or data.get("error"):
            self._body_text(pdf, "Ceza analizi verisi bulunamadı.")
            return

        cezalar = data.get("cezalar", [])
        if not cezalar:
            self._body_text(pdf, "Belirgin ceza maddesi tespit edilmedi.")
            return

        self._body_text(pdf, f"Toplam {len(cezalar)} ceza maddesi tespit edildi.")
        pdf.ln(4)

        headers = ["Ceza Türü", "Miktar/Oran", "Risk", "Referans"]
        col_widths = [50, 45, 25, 70]

        rows = []
        for ceza in cezalar:
            if not isinstance(ceza, dict):
                continue
            rows.append([
                ceza.get("ceza_turu", "—"),
                ceza.get("miktar_oran", "—"),
                ceza.get("risk_seviyesi", "—"),
                ceza.get("madde_referans", "—"),
            ])

        self._add_table(pdf, headers, rows, col_widths, severity_col=2)

    # ----------------------------------------------------------
    # Mali Özet / Financial Summary
    # ----------------------------------------------------------

    def _add_financial_summary(self, pdf: TenderPDF, data: dict) -> None:
        """Mali özet sayfası / Financial summary page."""
        pdf.add_page()
        self._section_title(pdf, "Mali Özet")

        if not data or data.get("error"):
            self._body_text(pdf, "Mali analiz verisi bulunamadı.")
            return

        # Ana bilgiler tablo olarak
        info_rows = [
            ["Tahmini İhale Bedeli", str(data.get("tahmini_ihale_bedeli", "Belirtilmemiş"))],
            ["Geçici Teminat", str(data.get("gecici_teminat", "Belirtilmemiş"))],
            ["Kesin Teminat", str(data.get("kesin_teminat", "Belirtilmemiş"))],
        ]

        odeme = data.get("odeme_kosullari", "")
        if odeme:
            info_rows.append(["Ödeme Koşulları", str(odeme)])

        fiyat = data.get("fiyat_farki", "")
        if fiyat:
            info_rows.append(["Fiyat Farkı", str(fiyat)])

        headers = ["Kalem", "Bilgi"]
        col_widths = [55, 135]
        self._add_table(pdf, headers, info_rows, col_widths)

        # Mali riskler
        mali_riskler = data.get("mali_riskler", [])
        if mali_riskler:
            pdf.ln(4)
            self._sub_heading(pdf, "Mali Riskler")
            for risk in mali_riskler:
                self._bullet(pdf, str(risk), color=_COLORS["warning"])

    # ----------------------------------------------------------
    # Süre Analizi / Timeline Analysis
    # ----------------------------------------------------------

    def _add_timeline(self, pdf: TenderPDF, data: dict) -> None:
        """Süre analizi sayfası / Timeline analysis page."""
        pdf.add_page()
        self._section_title(pdf, "Süre Analizi")

        if not data or data.get("error"):
            self._body_text(pdf, "Süre analizi verisi bulunamadı.")
            return

        # Temel bilgiler
        sure = data.get("toplam_is_suresi", "")
        baslama = data.get("ise_baslama_suresi", "")

        if sure or baslama:
            rows = []
            if sure:
                rows.append(["Toplam İş Süresi", str(sure)])
            if baslama:
                rows.append(["İşe Başlama", str(baslama)])
            self._add_table(pdf, ["Bilgi", "Değer"], rows, [55, 135])
            pdf.ln(4)

        # Milestones
        milestones = data.get("milestones", [])
        if milestones:
            self._sub_heading(pdf, "Önemli Tarihler / Milestones")
            headers = ["Aşama", "Süre"]
            col_widths = [95, 95]
            rows = []
            for ms in milestones:
                if isinstance(ms, dict):
                    rows.append([
                        ms.get("asama", ms.get("asamme", "—")),
                        ms.get("sure", "—"),
                    ])
                else:
                    rows.append([str(ms), "—"])
            self._add_table(pdf, headers, rows, col_widths)

        # Gecikme riski
        gecikme = data.get("gecikme_riski_degerlendirmesi", "")
        if gecikme:
            pdf.ln(4)
            self._sub_heading(pdf, "Gecikme Riski Değerlendirmesi")
            self._body_text(pdf, str(gecikme))

    # ----------------------------------------------------------
    # Yasal Uyarı / Disclaimer
    # ----------------------------------------------------------

    def _add_disclaimer(self, pdf: TenderPDF) -> None:
        """Yasal uyarı sayfası / Disclaimer page."""
        pdf.add_page()
        self._section_title(pdf, "Yasal Uyarı ve İletişim")

        pdf.ln(8)

        disclaimer = (
            "Bu rapor TenderAI yapay zeka sistemi tarafından otomatik olarak üretilmiştir. "
            "Raporda yer alan değerlendirmeler, yapay zeka modellerinin ihale şartname "
            "metnini analiz etmesi sonucunda oluşturulmuş olup, kesin hukuki veya mali "
            "tavsiye niteliği taşımamaktadır.\n\n"
            "İhale katılım kararlarınızda bu raporu yalnızca yardımcı bir araç olarak "
            "kullanınız. Kesin kararlar için mutlaka alanında uzman hukukçu, mali müşavir "
            "ve teknik danışmanlardan profesyonel destek alınız.\n\n"
            "4734 sayılı Kamu İhale Kanunu ve 4735 sayılı Kamu İhale Sözleşmeleri Kanunu "
            "kapsamındaki değerlendirmeler, şartnamenin analiz edilebilen bölümlerine "
            "dayanmaktadır. Şartnamede yer almayan veya okunamayan bölümler analiz "
            "kapsamı dışındadır.\n\n"
            "TenderAI, bu raporda yer alan bilgilerin doğruluğu, eksiksizliği veya "
            "güncelliği konusunda herhangi bir garanti vermemektedir."
        )

        self._body_text(pdf, disclaimer)

        pdf.ln(10)

        # İletişim
        self._sub_heading(pdf, "İletişim")
        pdf.set_font("DejaVu", "", 10)
        pdf.set_text_color(*_COLORS["dark"])
        pdf.cell(0, 7, "Web: www.tenderai.com.tr", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 7, "E-posta: destek@tenderai.com.tr", new_x="LMARGIN", new_y="NEXT")

        pdf.ln(15)

        # Alt bilgi
        now = datetime.now(timezone.utc).strftime("%d.%m.%Y %H:%M UTC")
        pdf.set_font("DejaVu", "", 8)
        pdf.set_text_color(*_COLORS["gray"])
        pdf.cell(0, 6, f"Rapor üretim tarihi: {now}", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, "TenderAI v1.0.0 — Yapay Zeka Destekli İhale Analiz Platformu", align="C")

    # ============================================================
    # Yardımcı Metodlar / Helper Methods
    # ============================================================

    def _section_title(self, pdf: FPDF, title: str) -> None:
        """Bölüm başlığı / Section title."""
        pdf.set_font("DejaVu", "B", 16)
        pdf.set_text_color(*_COLORS["primary"])
        pdf.cell(0, 12, title, new_x="LMARGIN", new_y="NEXT")
        pdf.set_draw_color(*_COLORS["primary"])
        pdf.set_line_width(0.6)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(6)

    def _sub_heading(self, pdf: FPDF, text: str) -> None:
        """Alt başlık / Sub heading."""
        pdf.set_font("DejaVu", "B", 11)
        pdf.set_text_color(*_COLORS["dark"])
        pdf.cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)

    def _body_text(self, pdf: FPDF, text: str) -> None:
        """Gövde metni / Body text."""
        pdf.set_font("DejaVu", "", 10)
        pdf.set_text_color(*_COLORS["black"])
        pdf.multi_cell(0, 6, text)
        pdf.ln(2)

    def _bullet(
        self, pdf: FPDF, text: str, color: tuple = None
    ) -> None:
        """Madde işareti / Bullet point."""
        pdf.set_font("DejaVu", "", 9)
        pdf.set_text_color(*(color or _COLORS["dark"]))
        pdf.cell(6, 6, "•")
        pdf.multi_cell(0, 6, text)
        pdf.ln(1)

    def _add_table(
        self,
        pdf: FPDF,
        headers: list[str],
        rows: list[list[str]],
        col_widths: list[int],
        severity_col: int | None = None,
    ) -> None:
        """
        Tablo çiz / Draw table.

        Args:
            pdf: FPDF nesnesi
            headers: Başlık metinleri
            rows: Satır verileri
            col_widths: Sütun genişlikleri (mm)
            severity_col: Risk seviyesi sütun indeksi (renkli yazmak için)
        """
        # Başlık satırı / Header row
        pdf.set_font("DejaVu", "B", 8)
        pdf.set_fill_color(*_COLORS["primary"])
        pdf.set_text_color(*_COLORS["white"])

        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 8, header, border=1, fill=True, align="C")
        pdf.ln()

        # Veri satırları / Data rows
        pdf.set_font("DejaVu", "", 8)
        for row_idx, row in enumerate(rows):
            fill_color = _COLORS["row_even"] if row_idx % 2 == 0 else _COLORS["row_odd"]
            pdf.set_fill_color(*fill_color)

            # Satır yüksekliğini hesapla / Calculate row height
            row_height = 7

            for col_idx, cell_text in enumerate(row):
                cell_text = str(cell_text)[:80]  # Uzun metinleri kes

                if severity_col is not None and col_idx == severity_col:
                    color = self._risk_color_text(cell_text)
                    pdf.set_text_color(*color)
                    pdf.set_font("DejaVu", "B", 8)
                else:
                    pdf.set_text_color(*_COLORS["black"])
                    pdf.set_font("DejaVu", "", 8)

                pdf.cell(
                    col_widths[col_idx], row_height,
                    cell_text, border=1, fill=True, align="L",
                )

            pdf.ln()

    @staticmethod
    def _risk_color_rgb(score: int) -> tuple:
        """Skor bazlı RGB renk / Score-based RGB color."""
        if score <= 40:
            return _COLORS["success"]
        elif score <= 70:
            return _COLORS["warning"]
        else:
            return _COLORS["danger"]

    @staticmethod
    def _risk_color_text(level: str) -> tuple:
        """Seviye metin bazlı RGB renk / Level text-based RGB color."""
        level_upper = level.upper().strip()
        if level_upper in ("KRİTİK",):
            return (180, 0, 0)
        elif level_upper in ("YÜKSEK",):
            return _COLORS["danger"]
        elif level_upper in ("ORTA",):
            return _COLORS["warning"]
        elif level_upper in ("DÜŞÜK",):
            return _COLORS["success"]
        return _COLORS["dark"]
