import streamlit as st
import requests
import time
from streamlit import session_state

def type_writer_effect(container, text, speed=0.01):
    full_text = ""
    for char in text:
        full_text += char
        container.markdown(full_text + "▌")  # Cursor effect
        time.sleep(speed)
    container.markdown(full_text)  # Remove cursor after typing


def main():
    st.set_page_config(page_title="AI Assistant", page_icon=":red_circle:", layout="wide")

    st.header("CRYPTO ASSISTANT")

    st.markdown("""<style> header {visibility: hidden;},
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@100&display=swap'); 
    body * {
        font-family: 'Roboto', sans-serif !important;
    }
    .st-emotion-cache-b499ls{
        padding: 4rem;
    }
    </style>""", unsafe_allow_html=True)

    with st.sidebar:
        username = st.text_input(label="User Name", placeholder="username")
        st.write("Helpful AI assistant to know the crypto currency prices and and topics related to crypto currencies."
                 "\n- Supports: :blue[Multilingual] queries"
                 "\n- Model: :blue[Llama-3.3-70B-Instruct-Turbo-Free]"
                 "\n- Source: :blue[CoinGecko.com], for crypto-currency price"
                 "\n- Advantage: :blue[Memory capability] for conversational"
                 "\n- Prompt Design: :blue[Chain-Of-Thoughts] Technique")
        st.divider()
        st.subheader(":green[Note]")
        st.write("If prompt fails, please add username, eg: James34, John23, API having some issues, it will fix mostly.")

    # Initialize chat history
    if "messages" not in session_state:
        st.session_state.messages = [{"role": "assistant", "content": "I'm your AI assistant, How may I help you today?"}]

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    prompt = st.chat_input("Enter your message here")
    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)  # Show user input

        st.session_state.messages.append({"role": "user", "content": prompt})  # Save user input
        with st.spinner("Please wait...", show_time=True):
            payload = {"user_id": username, "message": prompt}
            try:
                response = requests.post(
                    url="http://127.0.0.1:8080/conversation",
                    json=payload,
                    verify=False
                ).json()["message"]

                if response == "error":
                    st.info('Please change the username, for continue the chat.')

                # Display assistant response with typing effect
                with st.chat_message("assistant"):
                    msg_container = st.empty()
                    type_writer_effect(msg_container, response)

                st.session_state.messages.append({"role": "assistant", "content": response})  # Save assistant response

            except Exception:
                st.warning('Something went wrong!! Unable to fetch data from API, Please try again later.', icon="⚠️")

    # Clear Chat Button (Above Input Field)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear conversation"):
            st.session_state.messages = [{"role": "assistant", "content": "I'm your AI assistant, How may I help you today?"}]

if __name__ == "__main__":
    main()
