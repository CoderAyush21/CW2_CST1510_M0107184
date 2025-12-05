import streamlit as st
from google import genai
from google.genai import types

client= genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.subheader("🤖  AI Chatbot")


if st.session_state.get("logged_in") != True:
    st.error("Please Log in to access the AI Chatbot ! ")

    if st.button("Return to Home Page"):
     st.switch_page("Home.py")
    st.stop()


# Initialise session state
if 'messages' not in st.session_state:
    st.session_state.messages = []


# Display existing messages
for message in st.session_state.messages:
    if message["role"] == "model":
        role = "assistant"
    else:
        role = message["role"]
    with st.chat_message(role):
        st.markdown(message["parts"][0]["text"])

# Show message count
with st.sidebar:
    st.subheader("💬 Chat Controls")

    # Show message count
    message_count = len(st.session_state.get("messages", []))
    st.metric("Messages", message_count)

    # Clear chat button
    if st.button("Clear Chat", use_container_width=True):
        # Reset messages to initial state
        st.session_state.messages = []
        # Rerun to refresh the interface
        st.rerun()

# User input
prompt = st.chat_input("Say Something")

if prompt:

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "parts": [{"text": prompt}]
    })

    # Send to Gemini
    response = client.models.generate_content_stream(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction="You are an obedient dog. Your name is Neko."),
        contents=st.session_state.messages,
    )

    # Display streaming assistant output
    with st.chat_message("assistant"):
        container = st.empty()
        full_reply = ""
        for chunk in response:
            full_reply += chunk.text
            container.markdown(full_reply)

    # Save assistant message
    st.session_state.messages.append({"role": "model", "parts": [{"text": full_reply}]})
    st.rerun()
