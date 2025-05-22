import streamlit as st
import requests

# CONFIGURATION
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Chat S    1 ummarizer", layout="centered")
st.title("AI Chat with Summarizer")

# SESSION STATE INITIALIZATION
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

# INPUT
user_input = st.text_input("You:", key="user_input")

# HANDLE CHAT SUBMISSION
if st.button("Send") and user_input.strip():
    try:
        res = requests.post(f"{API_URL}/chat", json={"user_input": user_input})
        res.raise_for_status()
        ai_response = res.json()["ai_response"]

        # Save to session log
        st.session_state.chat_log.append(("You", user_input))
        st.session_state.chat_log.append(("AI", ai_response))
    except Exception as e:
        st.error(f"Failed to connect to API: {str(e)}")

# DISPLAY CHAT HISTORY
if st.session_state.chat_log:
    st.subheader("Conversation:")
    for speaker, message in st.session_state.chat_log:
        st.markdown(f"**{speaker}:** {message}")

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
        st.markdown(f"- **Common Keywords:** `{', '.join(summary['keywords'])}`")
        st.markdown(f"- **Inferred Topic:** {summary['topic']}")
    except Exception as e:
        st.error(f"Summary failed: {str(e)}")
        
        st.divider()
        st.subheader("Summarize All Chat Logs")

if st.button("Summarize All Files"):
    try:
        res = requests.get(f"{API_URL}/summarize_all")
        res.raise_for_status()
        summaries = res.json()

        if not summaries:
            st.warning("No chat logs found in the backend/data/ folder.")
        else:
            for fname, summary in summaries.items():
                st.markdown(f"### {fname}")
                st.markdown(f"text\n{summary['summary_text']}\n")
    except Exception as e:
        st.error(f"Failed to summarize all logs: {str(e)}")


