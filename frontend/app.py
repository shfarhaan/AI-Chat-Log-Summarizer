import streamlit as st
import requests
import os

# CONFIGURATION
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Chat Summarizer", layout="centered")
st.title("AI Chat with Summarizer")

# SESSION STATE INITIALIZATION
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

# Layout columns for actions
col1, col2 = st.columns([3, 1])

with col1:
    # USER INPUT FIELD
    user_input = st.text_input("You:", key="chat_input")
    if st.button("Send") and user_input.strip():
        try:
            res = requests.post(
                f"{API_URL}/chat", json={"user_input": user_input}
            )
            res.raise_for_status()
            ai_response = res.json()["ai_response"]

            # Save to session log
            st.session_state.chat_log.append(("You", user_input))
            st.session_state.chat_log.append(("AI", ai_response))
            # Clear input field after send
            st.session_state.user_input = ""
        except Exception as e:
            st.error(f"Failed to connect to API: {str(e)}")

with col2:
    # CLEAR IN-PAGE CHAT HISTORY
    if st.button("Clear Chat"):
        st.session_state.chat_log = []
        st.success("In-page chat history cleared.")

    # RESET BACKEND LOG FILE
    if st.button("Reset Log File"):
        try:
            res = requests.post(f"{API_URL}/chat/clear")
            res.raise_for_status()
            st.success("Backend chat log file reset.")
        except Exception as e:
            st.error(f"Failed to reset backend log: {str(e)}")

st.divider()

# DISPLAY CHAT HISTORY
if st.session_state.chat_log:
    st.subheader("Conversation:")
    for speaker, message in st.session_state.chat_log:
        st.markdown(f"**{speaker}:** {message}")

st.divider()

# SUMMARY GENERATION
if st.button("Summarize Conversation"):
    try:
        res = requests.get(f"{API_URL}/summarize")
        res.raise_for_status()
        summary = res.json()

        st.subheader("Summary")
        st.markdown(f"- **Total Exchanges:** {summary['total_exchanges']}")
        st.markdown(f"- **User Messages:** {summary['user_count']}")
        st.markdown(f"- **AI Messages:** {summary['ai_count']}")
        st.markdown(
            f"- **Common Keywords:** `{', '.join(summary['keywords'])}`"
        )
        st.markdown(f"- **Inferred Topic:** {summary['topic']}")
        # Optional: display 100-word summary if available
        if 'summary_100_words' in summary:
            st.markdown(f"- **100-Word Summary:** {summary['summary_100_words']}")
    except Exception as e:
        st.error(f"Summary failed: {str(e)}")

st.divider()
# (Optional) Summarize All Logs
if st.button("Summarize All Logs"):
    try:
        res = requests.get(f"{API_URL}/summarize-all")
        res.raise_for_status()
        summaries = res.json()

        if not summaries:
            st.warning("No chat logs found in the backend/data/ folder.")
        else:
            for fname, summary in summaries.items():
                st.markdown(f"### {fname}")
                st.markdown(f"- **Total Exchanges:** {summary['total_exchanges']}")
                st.markdown(f"- **User Messages:** {summary['user_count']}")
                st.markdown(
                    f"- **AI Messages:** {summary['ai_count']}"
                )
                st.markdown(
                    f"- **Keywords:** `{', '.join(summary['keywords'])}`"
                )
                st.markdown(f"- **Topic:** {summary['topic']}")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            st.warning("No summaries available. The backend log file may be empty.")
        else:
            st.error(f"Failed to summarize all logs: {str(e)}")
    except Exception as e:
        st.error(f"Failed to summarize all logs: {str(e)}")
