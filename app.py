import streamlit as st
from google import genai
from google.genai import errors

st.set_page_config(page_title="TextSift", layout="centered")

st.title("TextSift")
st.markdown("Automated text processing and extraction utility.")

with st.sidebar:
    st.header("Configuration")
    utility_mode = st.selectbox(
        "Operation Mode", ["Summarize Text", "Extract Action Items", "Analyze Tone"]
    )
    st.divider()
    st.markdown("Model: `gemini-2.5-flash`")

user_text = st.text_area(
    "Input Text Source:",
    placeholder="Paste raw text or documentation here...",
    height=250,
)

if st.button("Execute Processing", type="primary"):
    if not user_text.strip():
        st.warning("Execution halted: Input field is empty.")
    else:
        with st.spinner("Processing request..."):
            try:
                # Automatically fetch the API key from Streamlit Cloud secrets
                api_key = st.secrets["GEMINI_API_KEY"]

                client = genai.Client(api_key=api_key)

                if utility_mode == "Summarize Text":
                    prompt = f"Provide a concise executive summary and 3 key takeaways for the following text:\n\n{user_text}"
                elif utility_mode == "Extract Action Items":
                    prompt = f"Extract all explicit action items and deliverables from the following text:\n\n{user_text}"
                else:
                    prompt = f"Perform a clinical tone and sentiment analysis on the following text:\n\n{user_text}"

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )

                st.success("Processing complete.")
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
