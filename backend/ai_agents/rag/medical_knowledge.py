"""Static medical knowledge for chest X-ray pathologies (NIH 14). Used for RAG when no NoSQL."""

# Short CXR-relevant descriptions and differentials for each NIH pathology.
# Keys must match model pathology names (e.g. Pleural_Thickening with underscore).
CHEST_XRAY_KNOWLEDGE = {
    "Atelectasis": (
        "Atelectasis on chest X-ray: collapse or incomplete expansion of lung tissue. "
        "Findings may include volume loss, shift of fissures, opacity, and crowding of vessels. "
        "Differentials: mucus plug, foreign body, mass, pleural effusion."
    ),
    "Consolidation": (
        "Consolidation on CXR: airspace opacification with possible air bronchograms. "
        "Suggests filling of alveoli (e.g. pneumonia, edema, hemorrhage). "
        "Differentials: bacterial pneumonia, viral pneumonia, aspiration, infarction."
    ),
    "Infiltration": (
        "Infiltration on chest X-ray: non-specific parenchymal opacity. "
        "May represent pneumonia, atelectasis, or other parenchymal process. "
        "Clinical correlation and follow-up imaging often needed."
    ),
    "Pneumothorax": (
        "Pneumothorax on CXR: air in pleural space, often with absent lung markings and visible visceral pleural edge. "
        "May show mediastinal shift in tension. Differentials: primary spontaneous, trauma, iatrogenic, bulla rupture."
    ),
    "Edema": (
        "Pulmonary edema on CXR: interstitial or alveolar opacities, Kerley lines, peribronchial cuffing, "
        "cardiomegaly, pleural effusions. Often bilateral. Differentials: cardiogenic, fluid overload, ARDS."
    ),
    "Emphysema": (
        "Emphysema on chest X-ray: hyperlucency, flattened hemidiaphragms, increased retrosternal space, "
        "bullae, attenuated vessels. Chronic obstructive pattern."
    ),
    "Fibrosis": (
        "Fibrosis on CXR: reticular or honeycomb opacities, volume loss, traction. "
        "May be basilar or diffuse. Differentials: UIP, NSIP, chronic hypersensitivity pneumonitis."
    ),
    "Effusion": (
        "Pleural effusion on CXR: blunted costophrenic angle, meniscus, layering on lateral decubitus. "
        "Differentials: transudate (CHF, cirrhosis), exudate (infection, malignancy)."
    ),
    "Pneumonia": (
        "Pneumonia on chest X-ray: focal or multifocal consolidation, air bronchograms, "
        "possible parapneumonic effusion. Lobar, bronchopneumonic, or interstitial patterns."
    ),
    "Pleural_Thickening": (
        "Pleural thickening on CXR: smooth or nodular pleural opacity, often apical or along chest wall. "
        "Differentials: benign (prior infection, hemothorax), asbestos-related, malignancy."
    ),
    "Cardiomegaly": (
        "Cardiomegaly on CXR: enlarged cardiac silhouette (e.g. cardiothoracic ratio > 0.5). "
        "May be associated with chamber enlargement, pericardial effusion, or mediastinal mass."
    ),
    "Nodule": (
        "Nodule on chest X-ray: rounded opacity generally under 3 cm. "
        "Characterization by size, margins, calcification. Follow-up or further imaging (CT) often indicated."
    ),
    "Mass": (
        "Mass on CXR: opacity greater than 3 cm. Requires further characterization. "
        "Differentials: malignancy, granuloma, round pneumonia. CT recommended."
    ),
    "Hernia": (
        "Hernia on chest X-ray: diaphragmatic hernia may show bowel or stomach in thorax, "
        "abnormal diaphragmatic contour. Hiatal hernia may show retrocardiac air-fluid level."
    ),
}


def get_chunks_for_diseases(disease_names: list) -> list:
    """Return RAG text chunks for the given disease names (from model output)."""
    chunks = []
    for name in disease_names:
        text = CHEST_XRAY_KNOWLEDGE.get(name) or CHEST_XRAY_KNOWLEDGE.get(
            name.replace(" ", "_")
        )
        if text:
            chunks.append(text)
    return chunks
