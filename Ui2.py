import streamlit as st
from PIL import Image
import base64

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Set page config
st.set_page_config(page_title="Nomura Holdings Chatbot", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background-color: #FFFFFF;
    }
    .css-1d391kg {
        background-color: #ED1C24;
    }
    .css-1d391kg p {
        font-size: 1.2rem;
        font-weight: 600;
        color: white !important;
    }
    .stButton>button {
        color: #FFFFFF;
        background-color: #ED1C24;
        border: none;
    }
    .stTextInput>div>div>input {
        border-color: #ED1C24;
    }
    [data-testid="stSidebar"] {
        background-color: #ED1C24;
    }
    [data-testid="stSidebar"] .css-pkbazv {
        color: white;
    }
    .sidebar-logo {
        font-size: 2.5rem;
        font-weight: bold;
        color: #ED1C24;
        text-shadow: 2px 2px 3px rgba(255,255,255,0.1);
        -webkit-background-clip: text;
        -moz-background-clip: text;
        background-clip: text;
        background-color: rgba(255,255,255,0.3);
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<p class="sidebar-logo">NOMURA</p>', unsafe_allow_html=True)
    st.markdown("---")
    st.header("Nomura Holdings Info")
    st.info("Nomura Holdings, Inc. is a Japanese financial holding company and a principal member of the Nomura Group. It is a major participant in the global financial markets.")
    
    # Add any additional widgets or information here
    if st.button("Learn More About Nomura"):
        st.markdown("[Visit Nomura's Website](https://www.nomura.com/)")

# Main content
st.title("Nomura Holdings Chatbot")

# Main chat interface
st.header("How can I assist you today?")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Enter your question here"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate response from Nomura chatbot (placeholder response)
    response = f"Thank you for your question about Nomura Holdings. Here's what I found: {prompt}"
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.markdown("---")
st.markdown("© 2023 Nomura Holdings, Inc. All rights reserved.")
