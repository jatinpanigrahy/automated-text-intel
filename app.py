import streamlit as st
import requests
from bs4 import BeautifulSoup
from google import genai
from google.genai import errors

st.set_page_config(page_title="TextSift", layout="wide")

st.title("TextSift")
st.markdown("Professional text processing and extraction utility.")
st.divider()

col_meta1, col_meta2, col_meta3 = st.columns(3)
with col_meta1:
    st.metric(label="Engine", value="Gemini 3.6-flash")
with col_meta2:
    st.metric(label="Status", value="Operational")
with col_meta3:
    st.metric(label="Interface", value="Dual-Pane Workspace")

st.divider()

col_input, col_output = st.columns(2, gap="large")

source_text = ""

with col_input:
    st.subheader("Source Input")

    utility_mode = st.selectbox(
        "Operation Mode",
        [
            "Summarize Text",
            "List The Actionable Steps",
            "Turn into a Social Media message",
        ],
    )

    input_type = st.radio("Input Source Type", ["Raw Text", "Web URL"], horizontal=True)

    if input_type == "Raw Text":
        raw_input = st.text_area(
            "Paste content:",
            placeholder="Enter articles, notes, or documentation here...",
            height=280,
        )
        if raw_input:
            source_text = raw_input
    else:
        url_input = st.text_input(
            "Target URL:", placeholder="https://example.com/article"
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
                    st.error(
                        f"Failed to fetch URL. Status code: {response.status_code}"
                    )
            except Exception as e:
                st.error(f"Error fetching URL: {e}")

    execute_btn = st.button(
        "Execute Processing", type="primary", use_container_width=True
    )

with col_output:
    st.subheader("Output Intelligence")

    output_container = st.container(border=True)

    with output_container:
        if not execute_btn:
            st.info(
                "Configure settings on the left, provide content, and click execute to generate output."
            )
        else:
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

                        st.markdown(response.text)

                    except KeyError:
                        st.error(
                            "Configuration Error: GEMINI_API_KEY is missing from Streamlit secrets."
                        )
                    except errors.APIError as e:
                        st.error(f"API communication error: {e}")
                    except Exception as e:
                        st.error(f"System exception: {e}")
