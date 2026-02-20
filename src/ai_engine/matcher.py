"""
TenderAI İhale Uygunluk Matcher / Tender Match Scorer.

Firma profilini ihale gereksinimleriyle karşılaştırarak uygunluk skoru hesaplar.
"""

import json
import logging

logger = logging.getLogger(__name__)


class IhaleUygunlukMatcher:
    """Firma profili + ihale uygunluk skoru hesaplar."""

    def calculate_match_score(self, company_profile: dict, analysis_result: dict) -> dict:
        """
        Uygunluk skoru hesapla.

        Değerlendirme (ağırlıklı):
        - Mali yeterlilik (%30)
        - Teknik yeterlilik (%25)
        - Referans uyumu (%20)
        - Ekipman (%15)
        - Genel (%10)

        Returns:
            MatchResult dict
        """
        try:
            fin_score = self._evaluate_financial(company_profile, analysis_result)
            tech_score = self._evaluate_technical(company_profile, analysis_result)
            ref_score = self._evaluate_references(company_profile, analysis_result)
            equip_score = self._evaluate_equipment(company_profile, analysis_result)
            general_score = self._evaluate_general(company_profile, analysis_result)

            overall = int(
                fin_score["score"] * 0.30
                + tech_score["score"] * 0.25
                + ref_score["score"] * 0.20
                + equip_score["score"] * 0.15
                + general_score["score"] * 0.10
            )

            if overall >= 75:
                verdict = "UYGUN"
            elif overall >= 50:
                verdict = "KOŞULLU UYGUN"
            else:
                verdict = "UYGUN DEĞİL"

            # Eksikler, güçlü/zayıf yanlar topla
            missing = fin_score.get("missing", []) + tech_score.get("missing", []) + ref_score.get("missing", [])
            strengths = fin_score.get("strengths", []) + tech_score.get("strengths", [])
            weaknesses = fin_score.get("weaknesses", []) + tech_score.get("weaknesses", [])

            return {
                "overall_score": overall,
                "category_scores": {
                    "mali_yeterlilik": fin_score["score"],
                    "teknik_yeterlilik": tech_score["score"],
                    "referans_uyumu": ref_score["score"],
                    "ekipman": equip_score["score"],
                    "genel": general_score["score"],
                },
                "missing_requirements": missing[:10],
                "strengths": strengths[:5],
                "weaknesses": weaknesses[:5],
                "verdict": verdict,
                "recommendations": self._build_recommendations(overall, missing),
            }
        except Exception as e:
            logger.error(f"Uygunluk hesaplama hatası: {e}")
            return {"overall_score": 0, "verdict": "HESAPLANAMADI", "error": str(e)}

    def _evaluate_financial(self, profile: dict, result: dict) -> dict:
        """Mali yeterlilik değerlendirmesi."""
        score = 50  # Başlangıç
        missing, strengths, weaknesses = [], [], []

        revenue = profile.get("annual_revenue_try", 0) or 0
        credit = profile.get("bank_credit_limit_try", 0) or 0

        if revenue > 50_000_000:
            score += 30
            strengths.append("Yıllık ciro 50M TL üzerinde")
        elif revenue > 20_000_000:
            score += 15
        elif revenue > 0:
            weaknesses.append("Yıllık ciro düşük, iş hacmi yetersiz olabilir")
        else:
            score -= 20
            missing.append("Yıllık ciro bilgisi eksik")

        if credit > 10_000_000:
            score += 20
            strengths.append("Banka kredi limiti yeterli")
        elif credit > 0:
            score += 10
        else:
            missing.append("Banka kredi limiti bilgisi eksik")

        return {"score": max(0, min(100, score)), "missing": missing, "strengths": strengths, "weaknesses": weaknesses}

    def _evaluate_technical(self, profile: dict, result: dict) -> dict:
        """Teknik yeterlilik değerlendirmesi."""
        score = 50
        missing, strengths, weaknesses = [], [], []

        certs = self._parse_json_field(profile.get("certifications", "[]"))
        required_docs = result.get("required_documents", {})
        if isinstance(required_docs, dict):
            zorunlu = required_docs.get("zorunlu_belgeler", [])
            # ISO kontrolleri
            cert_names = [c.lower() for c in certs]
            for doc in zorunlu:
                if isinstance(doc, dict) and "iso" in doc.get("belge_adi", "").lower():
                    iso_name = doc["belge_adi"].lower()
                    if any(iso_name.split()[0] in c for c in cert_names):
                        score += 10
                        strengths.append(f"{doc['belge_adi']} mevcut")
                    else:
                        score -= 10
                        missing.append(f"{doc['belge_adi']} eksik")

        employees = profile.get("employee_count", 0) or 0
        if employees >= 50:
            score += 15
        elif employees >= 10:
            score += 5
        else:
            weaknesses.append("Personel sayısı yeterli olmayabilir")

        return {"score": max(0, min(100, score)), "missing": missing, "strengths": strengths, "weaknesses": weaknesses}

    def _evaluate_references(self, profile: dict, result: dict) -> dict:
        """Referans uyumu."""
        score = 50
        missing, strengths, weaknesses = [], [], []

        refs = self._parse_json_field(profile.get("reference_projects", "[]"))
        areas = self._parse_json_field(profile.get("experience_areas", "[]"))

        if len(refs) >= 5:
            score += 30
            strengths.append(f"{len(refs)} referans proje mevcut")
        elif len(refs) >= 2:
            score += 15
        else:
            weaknesses.append("Referans proje sayısı az")

        if len(areas) >= 3:
            score += 20
        elif len(areas) > 0:
            score += 10

        return {"score": max(0, min(100, score)), "missing": missing, "strengths": strengths, "weaknesses": weaknesses}

    def _evaluate_equipment(self, profile: dict, result: dict) -> dict:
        """Ekipman uyumu."""
        score = 60  # Varsayılan orta
        equip = self._parse_json_field(profile.get("equipment_list", "[]"))
        if len(equip) >= 5:
            score = 85
        elif len(equip) >= 2:
            score = 70
        return {"score": score, "missing": [], "strengths": [], "weaknesses": []}

    def _evaluate_general(self, profile: dict, result: dict) -> dict:
        """Genel uyum."""
        score = 60
        year = profile.get("established_year", 0)
        if year and year <= 2010:
            score += 20  # 15+ yıllık firma
        elif year and year <= 2018:
            score += 10
        return {"score": min(100, score), "missing": [], "strengths": [], "weaknesses": []}

    def _build_recommendations(self, score: int, missing: list) -> list[str]:
        """Öneriler oluştur."""
        recs = []
        if missing:
            recs.append(f"Eksik belgelerinizi tamamlayın: {', '.join(missing[:3])}")
        if score < 50:
            recs.append("Bu ihale için yeterlilik düşük, kapsamlı hazırlık gereklidir.")
        elif score < 75:
            recs.append("Eksikleri tamamlayarak uygunluk skorunuzu artırabilirsiniz.")
        else:
            recs.append("Firma profiliniz bu ihale için büyük ölçüde uygundur.")
        return recs

    @staticmethod
    def _parse_json_field(val) -> list:
        """JSON string veya list parse et."""
        if isinstance(val, list):
            return val
        if isinstance(val, str):
            try:
                parsed = json.loads(val)
                return parsed if isinstance(parsed, list) else []
            except Exception:
                return [v.strip() for v in val.split(",") if v.strip()] if val else []
        return []
