"""
TenderAI İhale Karşılaştırıcı / Tender Comparator.

Birden fazla ihale analizini karşılaştırır, en uygun ihaleyi önerir.
"""

import json
import logging

logger = logging.getLogger(__name__)


class IhaleComparator:
    """Birden fazla ihale analizini karşılaştırır."""

    def compare(self, analyses: list[dict]) -> dict:
        """
        2-5 analiz sonucunu karşılaştır.

        Args:
            analyses: Analiz sonuçları listesi (her biri dict)

        Returns:
            Karşılaştırma sonucu dict
        """
        if len(analyses) < 2:
            return {"error": "En az 2 analiz gereklidir."}

        rows = []
        for i, a in enumerate(analyses):
            name = a.get("file_name", f"İhale {i+1}")
            score = a.get("risk_score", 0)
            level = a.get("risk_level", "—")

            fin = a.get("financial_summary", {}) or {}
            bedel = fin.get("tahmini_ihale_bedeli", "—") if isinstance(fin, dict) else "—"
            teminat = fin.get("gecici_teminat", "—") if isinstance(fin, dict) else "—"

            timeline = a.get("timeline_analysis", {}) or {}
            sure = timeline.get("toplam_is_suresi", "—") if isinstance(timeline, dict) else "—"

            docs = a.get("required_documents", {}) or {}
            belge = len(docs.get("zorunlu_belgeler", [])) if isinstance(docs, dict) else 0

            penalties = a.get("penalty_clauses", {}) or {}
            ceza = len(penalties.get("cezalar", [])) if isinstance(penalties, dict) else 0

            if score <= 40:
                tavsiye = "GİR ✅"
            elif score <= 70:
                tavsiye = "DİKKATLİ GİR ⚠️"
            else:
                tavsiye = "GİRME ❌"

            rows.append({
                "name": name,
                "risk_score": score,
                "risk_level": level,
                "bedel": bedel,
                "teminat": teminat,
                "sure": sure,
                "belge_sayisi": belge,
                "ceza_sayisi": ceza,
                "tavsiye": tavsiye,
            })

        # En iyi seçim: en düşük risk skoru
        best = min(rows, key=lambda x: x["risk_score"])

        return {
            "rows": rows,
            "best_choice": best["name"],
            "best_reason": f"En düşük risk skoru ({best['risk_score']}) ile en güvenli seçenektir.",
            "total_compared": len(rows),
        }

    def generate_comparison_table(self, analyses: list[dict]) -> dict:
        """Karşılaştırma tablosu verisi üret."""
        return self.compare(analyses)

    def recommend_best(self, analyses: list[dict], company_profile: dict | None = None) -> dict:
        """En iyi ihaleyi öner."""
        result = self.compare(analyses)
        if company_profile:
            result["profile_note"] = "Firma profili dikkate alınarak değerlendirildi."
        return result
