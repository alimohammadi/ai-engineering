import streamlit as st
import requests
from chatbot_ui.core.config import config


# -----------------------------
# API CALL FUNCTION
# -----------------------------
def api_call(method, url, **kwargs):
    def _show_error_popup(message):
        st.session_state["error_popup"] = {
            "visible": True,
            "message": message
        }

    try:
        response = getattr(requests, method.lower())(url, **kwargs)

        try:
            response_data = response.json()
        except ValueError:
            response_data = {"message": "Invalid response format from server"}

        if response.ok:
            return True, response_data

        return False, response_data

    except requests.exceptions.ConnectionError:
        _show_error_popup("Connection error. Please check your network connection.")
        return False, {"message": "Connection error"}

    except requests.exceptions.Timeout:
        _show_error_popup("The request timed out. Please try again later.")
        return False, {"message": "Request timeout"}

    except Exception as e:
        _show_error_popup("An unexpected error occurred.")
        return False, {"message": str(e)}


# -----------------------------
# INITIALIZE SESSION STATE
# -----------------------------
if "provider" not in st.session_state:
    st.session_state.provider = "OpenAI"

if "model_name" not in st.session_state:
    st.session_state.model_name = "gpt-5-nano"

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! How can I assist you today?"}
    ]


# -----------------------------
# SIDEBAR
# -----------------------------
with st.sidebar:
    st.title("Side Bar")

    provider = st.selectbox(
        "Provider",
        ["OpenAI", "Groq", "Google"],
        index=["OpenAI", "Groq", "Google"].index(st.session_state.provider)
    )

    if provider == "OpenAI":
        model_name = st.selectbox(
            "Model",
            ["gpt-5-nano", "gpt-5-mini"],
        )

    elif provider == "Groq":
        model_name = st.selectbox(
            "Model",
            ["llama-3.3-70b-versatile"],
        )

    elif provider == "Google":
        model_name = st.selectbox(
            "Model",
            ["gemini-2.5-flash"],
        )

    # Save to session state
    st.session_state.provider = provider
    st.session_state.model_name = model_name


# -----------------------------
# DISPLAY CHAT HISTORY
# -----------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------
# HANDLE USER INPUT
# -----------------------------
if prompt := st.chat_input("Type your message..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Call API and display assistant response
    with st.chat_message("assistant"):
        success, response_data = api_call(
            "POST",
            f"{config.API_URL}/chat",
            json={
                "provider": st.session_state.provider,
                "models_name": st.session_state.model_name,
                "messages": st.session_state.messages,
            },
        )

        if success:
            answer = response_data.get("message", "No response from server.")
        else:
            answer = response_data.get("message", "Something went wrong.")

        st.write(answer)

    # Save assistant message
    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )