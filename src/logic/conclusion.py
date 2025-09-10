def build_conclusion_prompt(
    title: str | None,
    content: str | None,
    tone: str,
    audience: str | None,
    language: str,
    num_variants: int,
    length_choice: str,
    competitor_snippets: list[str] | None = None,
) -> str:
    competitor_section = "\n".join(competitor_snippets or [])
    return f"""
Generate {num_variants} different conclusion variants for the article below.

Rules:
- Keep each conclusion cohesive and self-contained.
- Match tone: {tone}.
- Write in: {language}.
- If target audience is provided, mention or imply it: {audience or 'N/A'}.
- Encourage reader action when appropriate (subscribe, share, comment, explore next steps).
- Be SEO-aware but natural; avoid keyword stuffing.
- Avoid repeating the same phrasing across variants.
- Do not copy from competitor snippets.

Length guidance: {length_choice}.

Article title (optional): {title or ''}
Article content (if provided):\n{content or ''}

Competitor snippets (for context, do not copy):\n{competitor_section}

Only list the {num_variants} conclusions, one per line or numbered list. Do not add anything else.
"""


