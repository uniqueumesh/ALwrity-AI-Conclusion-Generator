from __future__ import annotations

import os
import streamlit as st

from tenacity import retry, stop_after_attempt, wait_random_exponential


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def gemini_text_response(prompt: str, user_gemini_api_key: str | None = None) -> str | None:
    import google.generativeai as genai

    api_key = user_gemini_api_key or os.getenv('GEMINI_API_KEY')
    if not api_key:
        st.error("GEMINI_API_KEY is missing. Provide it in the API Configuration section or set it in the environment.")
        return None

    try:
        genai.configure(api_key=api_key)
    except Exception as err:
        st.error(f"Failed to configure Gemini: {err}")
        return None

    generation_config = {
        "temperature": 0.6,
        "top_p": 0.3,
        "top_k": 1,
        "max_output_tokens": 1024,
    }

    model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)
    try:
        response = model.generate_content(prompt)
        if hasattr(response, 'code') and response.code == 429:
            return 'RATE_LIMIT'
        if hasattr(response, 'text') and ('rate limit' in response.text.lower() or 'quota' in response.text.lower()):
            return 'RATE_LIMIT'
        return response.text
    except Exception as err:
        if 'quota' in str(err).lower() or 'rate limit' in str(err).lower():
            return 'RATE_LIMIT'
        st.error(f"Failed to get response from Gemini: {err}. Retrying.")
        return None


