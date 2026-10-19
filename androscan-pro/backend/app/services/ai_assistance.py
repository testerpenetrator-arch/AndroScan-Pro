"""Privacy-preserving local assistance draft. No external model/provider is called in F9.11."""
from collections import Counter

DISCLAIMER = (
    "Sugerencia asistida, no dictamen definitivo. Debe revisarla un analista humano. "
    "Esta versión utiliza reglas locales; no envía APK, evidencias ni hallazgos a servicios externos."
)

CATEGORY_GUIDANCE = {
    "STORAGE": "Verifique si datos sensibles se almacenan sin protección adecuada y revise el contexto de uso.",
    "CRYPTO": "Revise el algoritmo, el tamaño de clave, la generación/gestión de claves y el uso criptográfico real.",
    "AUTH": "Valide los controles de autenticación, autorización, sesión y los escenarios de abuso pertinentes.",
    "NETWORK": "Compruebe TLS, validación de certificados y exposición de datos durante las comunicaciones.",
    "PLATFORM": "Revise permisos, componentes exportados, intents y la interacción con otros componentes Android.",
    "CODE": "Examine el fragmento y el flujo de datos relacionado; confirme si la condición reportada es explotable.",
    "RESILIENCE": "Determine si el control de resiliencia es necesario para el modelo de amenazas de la aplicación.",
    "PRIVACY": "Determine qué datos personales se procesan, su finalidad, minimización y exposición.",
    "OTHER": "Valide manualmente el contexto técnico, el impacto y la reproducibilidad del hallazgo.",
}


def draft_assistance(findings: list) -> dict:
    counts = Counter(f.severity for f in findings)
    guidance = []
    for f in findings:
        guidance.append({
            "finding_id": f.id,
            "title": f.title,
            "observed_severity": f.severity,
            "observed_priority": f.priority,
            "review_state": f.review_state,
            "explanation": (f.description or "El detector no aportó una descripción detallada.")[:1200],
            "validation_steps": CATEGORY_GUIDANCE.get(f.category, CATEGORY_GUIDANCE["OTHER"]),
            "human_review_required": True,
        })
    return {
        "summary": f"Se preparó una guía preliminar para {len(findings)} hallazgo(s). Requiere validación humana.",
        "finding_count": len(findings),
        "by_severity": {k: counts.get(k, 0) for k in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]},
        "suggestions": guidance,
        "limitations": [
            "La guía se genera mediante reglas locales y no constituye una conclusión de un modelo generativo.",
            "No confirma explotabilidad ni ausencia de vulnerabilidades.",
            "No modifica severidad, prioridad, estado de revisión ni decisión del analista.",
        ],
    }
