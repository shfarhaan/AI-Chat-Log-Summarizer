import streamlit as st
import requests
import time
import html
import re

# CONFIGURATION
# API_URL = "http://127.0.0.1:8000"
API_URL = "https://ai-chat-log-summarizer-uj8f.onrender.com"

# Page configuration
st.set_page_config(
    page_title="Khejurey Alaap with AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for ChatGPT-like styling
st.markdown("""
<style>
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container styling */
    .main-container {
        max-width: 900px;
        margin: 0 auto;
        padding: 0;
    }
    
    /* Header styling */
    .chat-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .chat-header h1 {
        margin: 0;
        font-size: 2.2em;
        font-weight: 600;
    }
    
    .chat-header p {
        margin: 5px 0 0 0;
        opacity: 0.9;
        font-size: 1.1em;
    }
    
    /* Chat messages styling */
    .chat-message {
        padding: 15px 20px;
        margin: 10px 0;
        border-radius: 18px;
        max-width: 80%;
        word-wrap: break-word;
        line-height: 1.5;
        font-size: 15px;
    }
    
    .user-message {
        background: #007AFF;
        color: white;
        margin-left: auto;
        margin-right: 0;
        border-bottom-right-radius: 5px;
    }
    
    .ai-message {
        background: #F1F3F4;
        color: #333;
        margin-left: 0;
        margin-right: auto;
        border-bottom-left-radius: 5px;
        border: 1px solid #E1E3E4;
    }
    
    /* Input area styling */
    .input-container {
        position: sticky;
        bottom: 0;
        background: white;
        padding: 2px 0;
        border-top: 1px solid #326c8a;
        margin-top: 3px;
    }
    
    /* Button styling */
    .action-buttons {
        display: flex;
        gap: 10px;
        margin: 20px 0;
        justify-content: center;
        flex-wrap: wrap;
    }
    
    .summary-card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border: 1px solid #E1E3E4;
    }
    
    .summary-header {
        color: #000000;
        font-size: 1.3em;
        font-weight: 600;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .metric-container {
        display: flex;
        gap: 20px;
        margin: 15px 0;
        flex-wrap: wrap;
    }
    
    .metric-box {
        background: #F8F9FA;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        min-width: 100px;
        border: 1px solid #E9ECEF;
    }
    
    .metric-value {
        font-size: 1.8em;
        font-weight: 700;
        color: #007AFF;
        display: block;
    }
    
    .metric-label {
        font-size: 0.9em;
        color: #666;
        margin-top: 5px;
    }
    
    .keywords-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 15px 0;
    }
    
    .keyword-tag {
        background: #E3F2FD;
        color: #1976D2;
        padding: 6px 12px;
        border-radius: 15px;
        font-size: 0.9em;
        font-weight: 500;
    }
    
    .summary-text {
        background: #F8F9FA;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #007AFF;
        margin: 15px 0;
        font-size: 15px;
        line-height: 1.6;
        color: #1976D2;

    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .chat-message {
            max-width: 95%;
        }
        
        .metric-container {
            justify-content: center;
        }
        
        .chat-header h1 {
            font-size: 1.8em;
        }
    }
</style>
""", unsafe_allow_html=True)

# SESSION STATE INITIALIZATION
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []
if "show_summary" not in st.session_state:
    st.session_state.show_summary = False
# Add a key for input clearing
if "input_key" not in st.session_state:
    st.session_state.input_key = 0

# Sidebar with randomness controls
with st.sidebar:
    st.markdown("### 🎛️ AI Response Settings")
    
    # Preset buttons
    st.markdown("**Quick Presets:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎯 Focused", help="Conservative, predictable responses"):
            st.session_state.temperature = 0.2
            st.session_state.top_p = 0.5
            st.session_state.top_k = 10
    
    with col2:
        if st.button("⚖️ Balanced", help="Good mix of accuracy and creativity"):
            st.session_state.temperature = 0.7
            st.session_state.top_p = 0.9
            st.session_state.top_k = 40
    
    with col3:
        if st.button("🎨 Creative", help="More varied, creative responses"):
            st.session_state.temperature = 1.0
            st.session_state.top_p = 0.95
            st.session_state.top_k = 100
    
    st.markdown("---")
    st.markdown("**Manual Controls:**")
    
    # Initialize default values if not set
    if 'temperature' not in st.session_state:
        st.session_state.temperature = 0.7
    if 'top_p' not in st.session_state:
        st.session_state.top_p = 0.9
    if 'top_k' not in st.session_state:
        st.session_state.top_k = 40
    
    # Sliders for fine control
    temperature = st.slider(
        "🌡️ Temperature (Randomness)", 
        min_value=0.0, max_value=1.0, 
        value=st.session_state.temperature, 
        step=0.1,
        help="Higher = more random/creative responses"
    )
    
    top_p = st.slider(
        "🎯 Top-p (Nucleus Sampling)", 
        min_value=0.1, max_value=1.0, 
        value=st.session_state.top_p, 
        step=0.05,
        help="Focus on top % of probable words"
    )
    
    top_k = st.slider(
        "🔢 Top-k (Token Pool)", 
        min_value=1, max_value=100, 
        value=st.session_state.top_k, 
        step=5,
        help="Number of top tokens to consider"
    )
    
    # Update session state
    st.session_state.temperature = temperature
    st.session_state.top_p = top_p
    st.session_state.top_k = top_k
    
    # Display current settings
    st.markdown("---")
    st.markdown("**Current Settings:**")
    st.info(f"""
    🌡️ Temperature: {temperature}
    🎯 Top-p: {top_p}
    🔢 Top-k: {top_k}
    """)
    
    st.markdown("---")
    st.markdown("### 🛠️ Tools")
    
    if st.button("📚 View All Summaries", use_container_width=True):
        try:
            with st.spinner("Loading all summaries..."):
                res = requests.get(f"{API_URL}/summarize-all", timeout=30)
                res.raise_for_status()
                summaries = res.json()
                
                if summaries:
                    st.markdown("### 📊 All Chat Summaries")
                    for fname, summary in summaries.items():
                        with st.expander(f"📄 {fname}"):
                            if summary.get('summary_text'):
                                st.info(summary['summary_text'])
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total", summary.get('total_exchanges', 0))
                            with col2:
                                st.metric("User", summary.get('user_count', 0))
                            with col3:
                                st.metric("AI", summary.get('ai_count', 0))
                            
                            if summary.get('keywords'):
                                st.markdown("**Keywords:** " + " • ".join([f"`{k}`" for k in summary['keywords']]))
                else:
                    st.info("No summaries found.")
        except Exception as e:
            st.error(f"Failed to load summaries: {str(e)}")
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
    This app uses advanced NLP techniques:
    - **TF-IDF** for keyword extraction
    - **TextRank** for sentence ranking
    - **Smart summarization** algorithms
    - **Configurable AI randomness**
    
    💡 **Tips:**
    - Adjust randomness for different conversation styles
    - Use presets for quick configuration
    - Lower temperature = more focused responses
    - Higher temperature = more creative responses
    """)
    
    # Connection status
    try:
        res = requests.get(f"{API_URL}/", timeout=5)
        if res.status_code == 200:
            st.success("🟢 Backend Connected")
        else:
            st.error("🔴 Backend Issues")
    except:
        st.error("🔴 Backend Offline")

# Header
st.markdown("""
<div class="chat-header">
    <h1>🤖 AI Chat Summarizer</h1>
    <p>Intelligent conversations with smart summarization & configurable randomness</p>
</div>
""", unsafe_allow_html=True)

# Main chat interface
col1, col2, col3 = st.columns([1, 6, 1])



with col2:
    # Chat display area
    chat_container = st.container()
    
    def clean_message_display(message: str) -> str:
        """Clean message for safe HTML display"""
        # Escape HTML to prevent rendering issues
        message = html.escape(message)
        # Convert newlines to <br> tags for proper display
        message = message.replace('\n', '<br>')
        return message

    with chat_container:
        if st.session_state.chat_log:
            st.markdown("### 💬 Conversation")
            for speaker, message in st.session_state.chat_log:
                
                # Clean the message before displaying
                clean_message = clean_message_display(message)
                
                if speaker == "You":
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        {message}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message ai-message">
                        {message}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 50px; color: #666;">
                <h3>👋 Welcome to AI Chat Summarizer</h3>
                <p>Start a conversation below and I'll help you summarize it intelligently!</p>
                <p>🎛️ Adjust AI randomness settings in the sidebar for different conversation styles.</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Input area
    user_input = st.text_input(
        "Message", 
        placeholder="Type your message here...",
        key=f"chat_input_{st.session_state.input_key}",
        label_visibility="collapsed"
    )
    
    # Action buttons
    col_send, col_clear, col_reset, col_summary = st.columns(4)
    
    with col_send:
        if st.button("📤 Send", use_container_width=True, type="primary"):
            if user_input.strip():
                with st.spinner("🤔 Thinking..."):
                    try:
                        # Include randomness parameters in the request
                        payload = {
                            "user_input": user_input,
                            "temperature": st.session_state.temperature,
                            "top_p": st.session_state.top_p,
                            "top_k": st.session_state.top_k
                        }
                        
                        res = requests.post(
                            f"{API_URL}/chat", 
                            json=payload,
                            timeout=30
                        )
                        res.raise_for_status()
                        ai_response = res.json()["ai_response"]

                        # Save to session log
                        st.session_state.chat_log.append(("You", user_input))
                        st.session_state.chat_log.append(("AI", ai_response))
                        
                        # Clear input by incrementing the key
                        st.session_state.input_key += 1
                        
                        # Rerun to show new messages and cleared input
                        st.rerun()
                        
                    except requests.exceptions.Timeout:
                        st.error("⏰ Request timed out. Please try again.")
                    except requests.exceptions.ConnectionError:
                        st.error("🔌 Cannot connect to AI service. Please check if the backend is running.")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Please enter a message first!")
    
    with col_clear:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_log = []
            st.session_state.show_summary = False
            st.session_state.input_key += 1
            st.success("✅ Chat cleared!")
            st.rerun()
    
    with col_reset:
        if st.button("🔄 Reset Backend", use_container_width=True):
            try:
                res = requests.post(f"{API_URL}/chat/clear", timeout=10)
                res.raise_for_status()
                st.success("✅ Backend reset!")
            except Exception as e:
                st.error(f"❌ Reset failed: {str(e)}")
    
    with col_summary:
        if st.button("📊 Summarize", use_container_width=True, type="secondary"):
            if st.session_state.chat_log:
                st.session_state.show_summary = True
                st.rerun()
            else:
                st.warning("⚠️ No conversation to summarize!")
    
    # Summary section (keep your existing summary code)
    if st.session_state.show_summary:
        with st.spinner("🧠 Generating intelligent summary..."):
            try:
                res = requests.get(f"{API_URL}/summarize", timeout=30)
                res.raise_for_status()
                summary = res.json()
                
                st.markdown("""
                <div class="summary-card">
                    <div class="summary-header">
                        📝 Conversation Summary
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Main summary text
                if summary.get('summary_text') and summary['summary_text'] != "No conversation found in this file.":
                    st.markdown(f"""
                    <div class="summary-text">
                        <strong>📋 Summary:</strong><br>
                        {summary['summary_text']}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Statistics
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-box">
                        <span class="metric-value">{summary.get('total_exchanges', 0)}</span>
                        <div class="metric-label">Total Messages</div>
                    </div>
                    <div class="metric-box">
                        <span class="metric-value">{summary.get('user_count', 0)}</span>
                        <div class="metric-label">Your Messages</div>
                    </div>
                    <div class="metric-box">
                        <span class="metric-value">{summary.get('ai_count', 0)}</span>
                        <div class="metric-label">AI Responses</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Keywords
                if summary.get('keywords'):
                    keywords_html = "".join([f'<span class="keyword-tag">{keyword}</span>' for keyword in summary['keywords']])
                    st.markdown(f"""
                    <div>
                        <strong>🏷️ Key Topics:</strong><br>
                        <div class="keywords-container">
                            {keywords_html}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Topic focus
                if summary.get('topic'):
                    st.markdown(f"""
                    <div style="margin-top: 15px; color: #000000; padding: 15px; background: #E8F5E8; border-radius: 10px; border-left: 4px solid #4CAF50;">
                        <strong>🎯 Main Focus:</strong> {summary['topic']}
                    </div>
                    """, unsafe_allow_html=True)
                
            except requests.exceptions.Timeout:
                st.error("⏰ Summary generation timed out. Please try again.")
            except Exception as e:
                st.error(f"❌ Summary failed: {str(e)}")