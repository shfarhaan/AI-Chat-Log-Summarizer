# AI CHAT LOG SUMMARIZER

### Phase 1: ` Brainstorming project structure  `


## 🔧 Technologies Used

| Layer               | Technology                              |
| ------------------- | --------------------------------------- |
| Frontend            | Streamlit                               |
| Backend             | FastAPI                                 |
| AI Model            | Gemini (via google-generativeai)        |
| NLP / Summarization | nltk, scikit-learn                      |
| HTTP Client         | requests (for frontend → backend calls) |

---

## 🏗️ Project Structure

```text
ai-chat-summarizer/
├── backend/
│   ├── chatbot.py          # Gemini integration
│   ├── parser.py           # Chat log parser
│   ├── summarizer.py       # TF-IDF + topic and summary 
│   ├── main.py             # FastAPI app with /chat and /summarize endpoints
│   ├── data/               # Stores chat.txt and other logs
│   └── requirements.txt
├── frontend/
│   ├── app.py              # Streamlit chat UI
│   └── requirements.txt
├── .env                    # Contains GEMINI_API_KEY (not tracked by Git)
├── README.md               # You're here!
```


