import io
import pandas as pd
import streamlit as st

from src.logic.conclusion import build_conclusion_prompt
from src.services.gemini_client import gemini_text_response
from src.services.serp_client import get_serp_competitor_snippets


def main():
    st.set_page_config(page_title="Alwrity", layout="wide")

    st.markdown(
        """
        <style>
        ::-webkit-scrollbar-track { background: #e1ebf9; }
        ::-webkit-scrollbar-thumb {
            background-color: #90CAF9; border-radius: 10px; border: 3px solid #e1ebf9;
        }
        ::-webkit-scrollbar-thumb:hover { background: #64B5F6; }
        ::-webkit-scrollbar { width: 16px; }
        div.stButton > button:first-child {
            background: #1565C0; color: white; border: none; padding: 12px 24px; border-radius: 8px;
            text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 10px 2px;
            cursor: pointer; transition: background-color 0.3s ease; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
            font-weight: bold;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<style>header {visibility: hidden;}</style>', unsafe_allow_html=True)
    st.markdown('<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>', unsafe_allow_html=True)

    st.title("✍️ Alwrity - AI Conclusion Generator")

    with st.expander("API Configuration 🔑", expanded=False):
        st.markdown(
            '''If the default Gemini API key is unavailable or exceeds its limits, you can provide your own key below.<br>
            <a href="https://aistudio.google.com/app/apikey" target="_blank">Get Gemini API Key</a><br>
            <a href="https://serper.dev" target="_blank">Get SERPER API Key</a>''',
            unsafe_allow_html=True,
        )
        user_gemini_api_key = st.text_input("Gemini API Key", type="password")
        user_serper_api_key = st.text_input("Serper API Key (for SERP research)", type="password")

    with st.expander("PRO-TIP - Follow the steps below for best results.", expanded=True):
        col1, col2 = st.columns([5, 5])
        with col1:
            input_title = st.text_input(
                "🔑 Blog post title (optional)",
                placeholder="e.g., 10 AI Tools That Transform Digital Marketing",
            )
            input_content = st.text_area(
                "📄 Paste your blog/article content (recommended)",
                placeholder="Paste the full article body for best conclusions...",
                height=240,
            )
        with col2:
            input_tone = st.selectbox(
                "🎛️ Tone",
                ("Neutral", "Confident", "Friendly", "Professional", "Persuasive", "Educational"),
                index=0,
            )
            input_language = st.selectbox(
                "🌐 Language",
                ("English", "Spanish", "French", "German", "Chinese", "Japanese", "Other"),
                index=0,
            )
            if input_language == "Other":
                input_language = st.text_input("Specify Language", placeholder="e.g., Italian, Dutch")
            input_audience = st.text_input(
                "🎯 Target Audience (optional)",
                placeholder="e.g., for Marketers, for Developers",
            )
            length_choice = st.selectbox(
                "🧩 Conclusion length",
                ("Short (1-2 sentences)", "Medium (3-5 sentences)", "Long (1-2 paragraphs)"),
                index=1,
            )

    serp_snippets = []
    serp_cache_key = f"serp_{(input_title or '')[:64]}_{user_serper_api_key}"
    if input_title:
        if serp_cache_key in st.session_state:
            serp_snippets = st.session_state[serp_cache_key]
        else:
            serp_snippets = get_serp_competitor_snippets(input_title, user_serper_api_key)
            st.session_state[serp_cache_key] = serp_snippets
        if serp_snippets == 'RATE_LIMIT':
            st.warning('⚠️ Serper API rate limit or quota exceeded. Try later or use a different key.')
            serp_snippets = []
        elif serp_snippets:
            st.markdown('<h4 style="margin-top:1.5rem; color:#1976D2;">🔎 Competitor snippets from Google SERP</h4>', unsafe_allow_html=True)
            _ = st.selectbox('View a competitor snippet:', serp_snippets)

    st.markdown('<h3 style="margin-top:2rem;">How many conclusions do you want?</h3>', unsafe_allow_html=True)
    num_variants = st.slider('Number of conclusion variants', min_value=1, max_value=10, value=3)

    if st.button('Generate Conclusions'):
        with st.spinner("Generating conclusions..."):
            if not input_content and not input_title:
                st.error('Provide either content or a title to generate conclusions.')
            else:
                prompt = build_conclusion_prompt(
                    title=input_title,
                    content=input_content,
                    tone=input_tone,
                    audience=input_audience,
                    language=input_language,
                    num_variants=num_variants,
                    length_choice=length_choice,
                    competitor_snippets=serp_snippets,
                )
                conclusions = gemini_text_response(prompt, user_gemini_api_key)
                if conclusions == 'RATE_LIMIT':
                    st.warning('⚠️ Gemini API rate limit or quota exceeded. Try later or use a different key.')
                    return
                if not conclusions:
                    st.error('Failed to generate conclusions. Please try again.')
                    return

                st.session_state['conclusions_raw'] = conclusions
                st.markdown(conclusions)

                # Export to Excel for A/B testing
                lines = [t.strip().lstrip('0123456789. ') for t in conclusions.split('\n') if t.strip()]
                df = pd.DataFrame({'Conclusion': lines})
                excel_buffer = io.BytesIO()
                try:
                    df.to_excel(excel_buffer, index=False, engine='openpyxl')
                    excel_buffer.seek(0)
                    st.download_button(
                        label="Download Conclusions as Excel",
                        data=excel_buffer,
                        file_name="conclusions.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                except Exception:
                    pass


if __name__ == "__main__":
    main()


