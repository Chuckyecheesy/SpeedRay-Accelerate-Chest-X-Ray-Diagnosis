"""Deterministic diagnostic summary from chest X-ray top finding. No LLM."""

from typing import Any, Dict

# Medically accurate, simple explanations and next steps per condition (NIH 14 / CXR).
# Keys match model pathology names; normalize spaces to underscores for lookup.
CONDITION_SUMMARIES: Dict[str, Dict[str, str]] = {
    "Atelectasis": {
        "explanation": "Atelectasis is collapse or incomplete expansion of lung tissue. On X-ray it may show volume loss, shifted fissures, opacity, or crowded vessels. Common causes include mucus plug, foreign body, or compression.",
        "recommended_next_steps": "Clinical correlation; consider chest physiotherapy or bronchoscopy if persistent. Follow-up X-ray to confirm resolution.",
    },
    "Consolidation": {
        "explanation": "Consolidation is airspace opacification, often with air bronchograms, indicating filling of alveoli. It can represent pneumonia, edema, or hemorrhage.",
        "recommended_next_steps": "Correlate with symptoms and labs. Consider sputum culture and antibiotics if infection suspected. Follow-up imaging in 6–8 weeks if no improvement.",
    },
    "Infiltration": {
        "explanation": "Infiltration is a non-specific parenchymal opacity on X-ray. It may represent pneumonia, atelectasis, or other parenchymal process.",
        "recommended_next_steps": "Clinical correlation and repeat imaging. Further workup (e.g., CT) if persistent or worsening.",
    },
    "Pneumothorax": {
        "explanation": "Pneumothorax is air in the pleural space. X-ray may show absent lung markings and a visible visceral pleural edge; tension pneumothorax can cause mediastinal shift.",
        "recommended_next_steps": "Assess stability and oxygen saturation. Large or symptomatic pneumothorax may require chest tube; small stable cases may be observed with follow-up X-ray.",
    },
    "Edema": {
        "explanation": "Pulmonary edema appears as interstitial or alveolar opacities, Kerley lines, peribronchial cuffing, and often cardiomegaly or pleural effusions, typically bilateral.",
        "recommended_next_steps": "Assess volume status and cardiac function. Consider diuretics, oxygen, and treatment of underlying cause (e.g., heart failure). BNP and echocardiography if indicated.",
    },
    "Emphysema": {
        "explanation": "Emphysema on X-ray shows hyperlucency, flattened hemidiaphragms, increased retrosternal space, and possibly bullae with attenuated vessels—a chronic obstructive pattern.",
        "recommended_next_steps": "Spirometry to confirm COPD. Optimize inhaler therapy; smoking cessation; vaccination. Consider pulmonary rehab.",
    },
    "Fibrosis": {
        "explanation": "Fibrosis appears as reticular or honeycomb opacities with volume loss and traction. It may be basilar or diffuse and suggests chronic parenchymal scarring.",
        "recommended_next_steps": "HRCT for pattern characterization. Consider rheumatology or pulmonology referral; exclude drug-induced or occupational causes.",
    },
    "Effusion": {
        "explanation": "Pleural effusion on X-ray shows blunted costophrenic angle and meniscus sign. It can be transudate (e.g., heart failure) or exudate (infection, malignancy).",
        "recommended_next_steps": "Assess size and symptoms. Consider thoracentesis for diagnostic or therapeutic purposes. Treat underlying cause.",
    },
    "Pneumonia": {
        "explanation": "Pneumonia on X-ray shows focal or multifocal consolidation, air bronchograms, and possibly parapneumonic effusion in lobar or bronchopneumonic pattern.",
        "recommended_next_steps": "Correlate with clinical picture; cultures and antibiotics per guidelines. Follow-up X-ray in 6–8 weeks to confirm resolution.",
    },
    "Pleural_Thickening": {
        "explanation": "Pleural thickening is smooth or nodular pleural opacity, often apical or along the chest wall. It can be benign (prior infection) or related to asbestos or malignancy.",
        "recommended_next_steps": "Compare with prior imaging. If new or changing, consider CT and clinical workup for malignancy or asbestos exposure.",
    },
    "Cardiomegaly": {
        "explanation": "Cardiomegaly is an enlarged cardiac silhouette on X-ray (e.g., cardiothoracic ratio > 0.5), which may reflect chamber enlargement, pericardial effusion, or mediastinal mass.",
        "recommended_next_steps": "Echocardiography to assess function and chamber size. Evaluate for heart failure, valvular disease, or pericardial effusion.",
    },
    "Nodule": {
        "explanation": "A nodule is a rounded opacity generally under 3 cm. Characterization depends on size, margins, and calcification; many are benign but require follow-up.",
        "recommended_next_steps": "Compare with prior imaging. Follow Fleischner or similar guidelines; consider CT for characterization and interval follow-up.",
    },
    "Mass": {
        "explanation": "A mass is an opacity greater than 3 cm on X-ray. It requires further characterization; differential includes malignancy, granuloma, and round pneumonia.",
        "recommended_next_steps": "CT chest for characterization. Consider biopsy or PET if malignancy suspected. Multidisciplinary review as appropriate.",
    },
    "Hernia": {
        "explanation": "Diaphragmatic hernia may show bowel or stomach in the thorax and abnormal diaphragmatic contour; hiatal hernia may show retrocardiac air-fluid level.",
        "recommended_next_steps": "Correlate with symptoms. Consider upper GI series or CT for anatomy. Surgical referral if symptomatic or complicated.",
    },
}


def _normalize_condition_name(name: str) -> str:
    """Match model output to our keys (e.g. 'Pleural Thickening' -> 'Pleural_Thickening')."""
    if not name or not name.strip():
        return "Finding"
    normalized = name.strip().replace(" ", "_")
    if normalized in CONDITION_SUMMARIES:
        return normalized
    with_spaces = name.strip()
    if with_spaces in CONDITION_SUMMARIES:
        return with_spaces
    for key in CONDITION_SUMMARIES:
        if key.replace("_", " ") == with_spaces or key == normalized:
            return key
    return "Finding"


def get_diagnostic_summary(
    filename: str,
    top_critical: Dict[str, Any],
) -> Dict[str, str]:
    """
    Generate a short, deterministic diagnostic report for the top finding.

    Input:
        filename: image name (unused in output but accepted for API consistency).
        top_critical: {"name": "<disease>", "score": <float>, "risk": "<Low|Moderate|High>"}

    Output JSON:
        top_finding, risk, explanation, recommended_next_steps
    """
    name = (top_critical.get("name") or "Finding").strip()
    score = top_critical.get("score")
    risk = (top_critical.get("risk") or "Low").strip()
    if risk not in ("Low", "Moderate", "High"):
        risk = "Low"

    key = _normalize_condition_name(name)
    entry = CONDITION_SUMMARIES.get(key)
    if entry:
        explanation = entry["explanation"]
        recommended_next_steps = entry["recommended_next_steps"]
    else:
        explanation = (
            f"{name} was identified on the chest X-ray. Findings should be interpreted in clinical context."
        )
        recommended_next_steps = "Clinical correlation and follow-up imaging or specialist referral as indicated."

    return {
        "top_finding": name,
        "risk": risk,
        "explanation": explanation,
        "recommended_next_steps": recommended_next_steps,
    }
