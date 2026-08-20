import streamlit as st
import requests
from bs4 import BeautifulSoup
from google import genai
from google.genai import errors

st.set_page_config(
    page_title="Text Intelligence",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #0a0a0c;
    }
    
    .stTextArea textarea {
        background-color: #121214 !important;
        border: 1px solid #27272a !important;
        color: #ededed !important;
        border-radius: 8px;
        padding: 12px;
    }
    
    .stSelectbox div[data-baseweb="select"] {
        background-color: #121214 !important;
        border: 1px solid #27272a !important;
        border-radius: 8px;
    }
    
    div[data-baseweb="select"] input {
        caret-color: transparent !important;
        cursor: pointer !important;
    }
    
    .stButton button {
        background-color: #ededed !important;
        border: none !important;
        border-radius: 8px;
        transition: all 0.2s ease;
        width: 100%;
        padding: 0.5rem 1rem;
    }
    
    .stButton button p, .stButton button div, .stButton button span {
        color: #0a0a0c !important;
        font-weight: 600 !important;
    }
    
    .stButton button:hover {
        background-color: #ffffff !important;
        transform: translateY(-1px);
    }
    
    div[data-testid="stContainer"] {
        background-color: #121214;
        border: 1px solid #27272a;
        border-radius: 12px;
        padding: 1.5rem;
    }
    
    h1, h2, h3, p, span, div {
        color: #ededed;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

if "output_data" not in st.session_state:
    st.session_state.output_data = None

st.title("Automated Text Intelligence")
st.markdown(
    "Transform articles, notes, or web pages into structured insights, summaries, or social content instantly."
)

col_mode, col_input = st.columns([1, 3])

with col_mode:
    utility_mode = st.selectbox(
        "Select Mode",
        [
            "Summarize Text",
            "List The Actionable Steps",
            "Turn into a Social Media message",
        ],
        label_visibility="collapsed",
    )

with col_input:
    user_input = st.text_area(
        "Input",
        placeholder="Enter raw text or a target URL (https://...)",
        height=200,
        label_visibility="collapsed",
    )

execute_btn = st.button("Generate", type="primary")

if execute_btn:
    target_content = ""

    if user_input:
        if user_input.startswith("http://") or user_input.startswith("https://"):
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                resp = requests.get(user_input, headers=headers, timeout=10)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    for script in soup(["script", "style", "nav", "footer"]):
                        script.decompose()
                    target_content = soup.get_text(separator=" ", strip=True)
                else:
                    st.error("Failed to fetch URL.")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            target_content = user_input

        if target_content:
            with st.spinner("Processing content..."):
                try:
                    api_key = st.secrets["GEMINI_API_KEY"]
                    client = genai.Client(api_key=api_key)

                    if utility_mode == "Summarize Text":
                        prompt = f"Provide a clean summary and 3 key points for the following content:\n\n{target_content}"
                    elif utility_mode == "List The Actionable Steps":
                        prompt = f"Create a clear, prioritized list of actionable steps or deliverables from the following content:\n\n{target_content}"
                    else:
                        prompt = f"Convert the following content into an engaging social media message. Keep the tone and language simple, minimal and mature. Don't make it either overly rigid, or too pretentious, showy, or overly excited. Keep the use of emojis - minimal and what's actually important:\n\n{target_content}"

                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=prompt,
                    )

                    st.session_state.output_data = response.text
                except KeyError:
                    st.error(
                        "Configuration Error: GEMINI_API_KEY is missing from Streamlit secrets."
                    )
                except errors.APIError as e:
                    st.error(f"API communication error: {e}")
                except Exception as e:
                    st.error(f"System exception: {e}")
    else:
        st.warning("Input content is empty. Provide text or a valid URL.")

st.divider()

if st.session_state.output_data:
    st.subheader("Output")
    st.markdown(st.session_state.output_data)
else:
    st.subheader("Features")
    c1, c2, c3 = st.columns(3)
    with c1:
        with st.container(border=True):
            st.markdown("### Multi-Format Input")
            st.markdown(
                "Seamlessly input raw text blocks or direct web URLs via automated scraping to get the desired outputs."
            )
    with c2:
        with st.container(border=True):
            st.markdown("### Intelligent Processing")
            st.markdown(
                "Uses advanced language models like (`gemini-3.6-flash`) to analyze, scan, and reformat content."
            )
    with c3:
        with st.container(border=True):
            st.markdown("### Tailored Outputs")
            st.markdown(
                "Receive clean summaries, actionable steps, or well-curated social media messages instantly."
            )
