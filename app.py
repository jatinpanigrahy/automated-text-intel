import streamlit as st
import requests
from bs4 import BeautifulSoup
from google import genai
from google.genai import errors

st.set_page_config(page_title="TextSift", layout="centered")

st.title("TextSift")
st.markdown(
    "Transform articles, notes, or web pages into structured intelligence instantly."
)

st.divider()

with st.sidebar:
    st.header("Configuration")
    utility_mode = st.selectbox(
        "Operation Mode",
        [
            "Summarize Text",
            "List The Actionable Steps",
            "Turn into a Social Media message",
        ],
    )
    st.divider()
    st.markdown("System: `gemini-3.6-flash`")
    st.markdown("Status: Ready")

input_tab1, input_tab2 = st.tabs(["Raw Text Input", "Web URL Input"])

source_text = ""

with input_tab1:
    raw_input = st.text_area(
        "Paste content here:",
        placeholder="Enter articles, meeting notes, or documentation...",
        height=200,
    )
    if raw_input:
        source_text = raw_input

with input_tab2:
    url_input = st.text_input(
        "Enter target URL:", placeholder="https://example.com/article"
    )
    if url_input:
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url_input, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                for script in soup(["script", "style"]):
                    script.decompose()
                source_text = soup.get_text(separator=" ", strip=True)
                st.success("Web page successfully parsed.")
            else:
                st.error(f"Failed to fetch URL. Status code: {response.status_code}")
        except Exception as e:
            st.error(f"Error fetching URL: {e}")

st.divider()

if st.button("Execute Processing", type="primary"):
    if not source_text.strip():
        st.warning("Input content is empty. Provide text or a valid URL.")
    else:
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

                st.subheader("Output Intelligence")
                st.markdown(response.text)

            except KeyError:
                st.error(
                    "Configuration Error: GEMINI_API_KEY is missing from Streamlit secrets."
                )
            except errors.APIError as e:
                st.error(f"API communication error: {e}")
            except Exception as e:
                st.error(f"System exception: {e}")
