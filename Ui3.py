import streamlit as st
import base64

# Function to get base64 encoded image
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Function to set background image with fade effect
def set_background_with_fade(image_file):
    bin_str = get_base64_of_bin_file(image_file)
    page_bg_img = f'''
    <style>
    [data-testid="stSidebar"] {{
        background-image: linear-gradient(to bottom, rgba(237, 28, 36, 0), rgba(237, 28, 36, 1) 30%),
                          url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-position: top center;
        background-repeat: no-repeat;
        background-attachment: local;
    }}
    [data-testid="stSidebar"]::before {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(to bottom, rgba(237, 28, 36, 0), rgba(237, 28, 36, 1));
    }}
    [data-testid="stSidebar"] .css-pkbazv {{
        color: white;
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

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
    .sidebar-content {
        position: relative;
        z-index: 1;
    }
</style>
""", unsafe_allow_html=True)

# Set background with fade effect
set_background_with_fade('path_to_nomura_logo.png')  # Replace with actual path to Nomura logo

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    st.markdown("## NOMURA")
    st.markdown("---")
    st.header("Nomura Holdings Info")
    st.info("Nomura Holdings, Inc. is a Japanese financial holding company and a principal member of the Nomura Group. It is a major participant in the global financial markets.")
    
    if st.button("Learn More About Nomura"):
        st.markdown("[Visit Nomura's Website](https://www.nomura.com/)")
    st.markdown('</div>', unsafe_allow_html=True)

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
