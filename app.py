import streamlit as st
import requests
from bs4 import BeautifulSoup
from google import genai
from google.genai import errors

st.set_page_config(page_title="TextSift", layout="wide")

st.title("TextSift")
st.markdown(
    "Transform articles, notes, or web pages into structured intelligence instantly."
)

col_input_box, col_btn1, col_btn2, col_btn3 = st.columns([4, 1, 1, 1])

if "source_text" not in st.session_state:
    st.session_state.source_text = ""

with col_input_box:
    user_input = st.text_input(
        "Input Source",
        placeholder="Enter raw text or paste a target URL...",
        label_visibility="collapsed",
    )

with col_btn1:
    if st.button("Sample Article", use_container_width=True):
        st.session_state.source_text = "Artificial intelligence is rapidly transforming software development. Engineers are shifting from writing boilerplate code to orchestrating intelligent systems. However, this transition requires a deep understanding of API design, asynchronous execution, and rigorous error handling. Teams must prioritize clean architecture over temporary hacks to maintain long-term velocity."
        st.rerun()

with col_btn2:
    if st.button("Meeting Notes", use_container_width=True):
        st.session_state.source_text = "Project sync on Q3 roadmap. Action item: Rahul to finalize the database schema by Tuesday. Action item: Priya to set up CI/CD pipeline on GitHub Actions. Deadline for MVP release is August 30. All team members must review security compliance docs before next sprint."
        st.rerun()

with col_btn3:
    if st.button("Clear", use_container_width=True):
        st.session_state.source_text = ""
        st.rerun()

source_text = user_input if user_input else st.session_state.source_text

st.divider()

col_mode, col_empty = st.columns([2, 4])
with col_mode:
    utility_mode = st.selectbox(
        "Operation Mode",
        [
            "Summarize Text",
            "List The Actionable Steps",
            "Turn into a Social Media message",
        ],
    )

st.divider()

if not source_text.strip():
    st.markdown("### How this tool works")
    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        with st.container(border=True):
            st.markdown("#### Summarization")
            st.markdown(
                "Condenses lengthy articles and documentation into core executive takeaways."
            )

    with c2:
        with st.container(border=True):
            st.markdown("#### Action Extraction")
            st.markdown(
                "Isolates clear, prioritized execution steps and deliverables from raw notes."
            )

    with c3:
        with st.container(border=True):
            st.markdown("#### Format Conversion")
            st.markdown(
                "Transforms raw notes and text blocks into professional distribution copy."
            )
else:
    st.subheader("Processing Result")
    with st.spinner("Processing content..."):
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
            client = genai.Client(api_key=api_key)

            if utility_mode == "Summarize Text":
                prompt = f"Provide a clean executive summary and 3 key takeaways for the following content:\n\n{source_text}"
            elif utility_mode == "List The Actionable Steps":
                prompt = f"Extract a clear, prioritized list of actionable steps or deliverables from the following content:\n\n{source_text}"
            else:
                prompt = f"Convert the following content into a professional, engaging social media message suitable for LinkedIn or X:\n\n{source_text}"

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
            )

            with st.container(border=True):
                st.markdown(response.text)

        except KeyError:
            st.error(
                "Configuration Error: GEMINI_API_KEY is missing from Streamlit secrets."
            )
        except errors.APIError as e:
            st.error(f"API communication error: {e}")
        except Exception as e:
            st.error(f"System exception: {e}")

st.markdown(
    "<br><hr><p style='text-align: center; color: gray; font-size: 0.8rem;'>Powered by Google Gemini (gemini-3.6-flash)</p>",
    unsafe_allow_html=True,
)
