import streamlit as st
import requests
from bs4 import BeautifulSoup
from google import genai
from google.genai import errors

st.set_page_config(page_title="TextSift", layout="wide")

st.markdown(
    """
    <style>
    .block-container { padding-top: 2rem; }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("TextSift")
st.markdown(
    "Transform articles, notes, or web pages into structured intelligence instantly."
)
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

    input_type = st.radio(
        "Input Type",
        ["Raw Text", "Web URL"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if input_type == "Raw Text":
        raw_input = st.text_area(
            "Content:",
            placeholder="Paste articles, meeting notes, or documentation...",
            height=300,
            label_visibility="collapsed",
        )
        if raw_input:
            source_text = raw_input
    else:
        url_input = st.text_input(
            "URL:",
            placeholder="https://example.com/article",
            label_visibility="collapsed",
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
            st.markdown("### System Overview")
            st.markdown(
                "TextSift processes unstructured content into structured, high-value outputs."
            )
            st.markdown("---")
            st.markdown("**Capabilities:**")
            st.markdown(
                "- **Summarize Text:** Condenses long texts into concise executive summaries and core takeaways."
            )
            st.markdown(
                "- **List Actionable Steps:** Extracts clear, prioritized deliverables from documentation or notes."
            )
            st.markdown(
                "- **Social Media Format:** Converts technical or long-form content into professional posts for platforms like LinkedIn or X."
            )
            st.markdown("---")
            st.caption("Provide an input on the left and click execute to begin.")
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

with st.sidebar:
    st.header("System Specs")
    st.markdown("Powered by Google Gemini (`gemini-3.6-flash`)")
    st.markdown("Environment: Secure Cloud")
