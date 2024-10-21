import streamlit as st
from PIL import Image
import base64

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
        padding-top: 2rem;
    }
    [data-testid="stSidebar"] .css-pkbazv {
        color: white;
    }
    .sidebar-logo {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 1rem 0;
    }
    .sidebar-logo img {
        width: 80%;
        height: auto;
        object-fit: contain;
        filter: brightness(0) invert(1);
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-logo"><img src="https://upload.wikimedia.org/wikipedia/commons/5/55/Nomura_logo.svg" alt="Nomura Logo"></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.header("Nomura Holdings Info")
    st.info("Nomura Holdings, Inc. is a Japanese financial holding company and a principal member of the Nomura Group. It is a major participant in the global financial markets.")
    
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
