import streamlit as st
import requests
from bs4 import BeautifulSoup
from google import genai
from google.genai import errors

st.set_page_config(
    page_title="TextSift", layout="wide", initial_sidebar_state="collapsed"
)

st.markdown(
    """
    <style>
    .main {
        padding: 2rem;
    }
    .stButton button {
        border-radius: 6px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("TextSift")
st.markdown(
    "Transform articles, notes, or web pages into structured intelligence instantly."
)

col_mode, col_input = st.columns([1, 3])
with col_mode:
    utility_mode = st.selectbox(
        "Operation Mode",
        [
            "Summarize Text",
            "List The Actionable Steps",
            "Turn into a Social Media message",
        ],
        label_visibility="collapsed",
    )

with col_input:
    user_input = st.text_input(
        "Input",
        placeholder="Enter raw text or a target URL (https://...)",
        label_visibility="collapsed",
    )

sample_col1, sample_col2, sample_col3, sample_col4 = st.columns([1, 1, 1, 6])
with sample_col1:
    sample_1 = st.button("Sample Article", use_container_width=True)
with sample_col2:
    sample_2 = st.button("Sample Notes", use_container_width=True)

target_content = ""

if sample_1:
    target_content = "Artificial intelligence is rapidly transforming software development by automating boilerplate code, assisting in debugging, and optimizing system architectures. Developers who leverage these tools effectively can significantly increase their output and focus on higher-order system design."
elif sample_2:
    target_content = "1. Review Q3 financial reports by Tuesday. 2. Schedule alignment meeting with engineering leads. 3. Update repository documentation before deployment."
elif user_input:
    if user_input.startswith("http://") or user_input.startswith("https://"):
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(user_input, headers=headers, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                for script in soup(["script", "style"]):
                    script.decompose()
                target_content = soup.get_text(separator=" ", strip=True)
            else:
                st.error("Failed to fetch URL.")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        target_content = user_input

st.divider()

if target_content:
    st.subheader("Output Intelligence")
    with st.spinner("Processing content..."):
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
            client = genai.Client(api_key=api_key)

            if utility_mode == "Summarize Text":
                prompt = f"Provide a clean executive summary and 3 key takeaways for the following content:\n\n{target_content}"
            elif utility_mode == "List The Actionable Steps":
                prompt = f"Extract a clear, prioritized list of actionable steps or deliverables from the following content:\n\n{target_content}"
            else:
                prompt = f"Convert the following content into a professional, engaging social media message suitable for LinkedIn or X:\n\n{target_content}"

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
            )

            st.markdown(response.text)

        except KeyError:
            st.error(
                "Configuration Error: GEMINI_API_KEY is missing from Streamlit secrets."
            )
        except errors.APIError as e:
            st.error(f"API communication error: {e}")
        except Exception as e:
            st.error(f"System exception: {e}")
else:
    st.subheader("How this tool works")
    c1, c2, c3 = st.columns(3)
    with c1:
        with st.container(border=True):
            st.markdown("### Summarize Text")
            st.markdown("Condenses lengthy content into core takeaways.")
    with c2:
        with st.container(border=True):
            st.markdown("### List The Actionable Steps")
            st.markdown("Extracts clear, prioritized execution tasks.")
    with c3:
        with st.container(border=True):
            st.markdown("### Turn into a Social Media message")
            st.markdown("Reformats content for professional distribution.")

    st.sidebar.markdown("### System Specs")
    st.sidebar.markdown("Model: `gemini-3.6-flash`")
