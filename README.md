# AI Chat Summarizer 🤖📊

A chat application that combines conversational AI with advanced text summarization capabilities. Built with FastAPI backend and Streamlit frontend, featuring configurable AI randomness and multiple summarization algorithms.

## ✨ Features

### 🤖 AI Chat Interface
- **Smart Conversations**: Powered by Google's Gemini 2.0 Flash model
- **Configurable Randomness**: Adjust temperature, top-p, and top-k parameters
- **Clean Response Handling**: Automatic HTML tag removal and text cleaning
- **Real-time Chat**: Instant responses with typing indicators

### 📊 Advanced Summarization
- **Multi-Algorithm Approach**: TF-IDF, TextRank, and frequency-based summarization
- **Intelligent Fallbacks**: Automatically switches between methods for optimal results
- **Key Metrics**: Message counts, topic identification, and conversation statistics
- **Keyword Extraction**: Automatic identification of important topics

### 🎛️ Customizable AI Behavior
- **Preset Configurations**: Focused, Balanced, and Creative response modes
- **Manual Fine-tuning**: Granular control over AI parameters
- **Real-time Adjustments**: Change settings during conversations

### 🌐 Production Ready
- **Cloud Deployment**: Configured for Render.com hosting
- **Health Monitoring**: Built-in health check endpoints
- **CORS Support**: Frontend-backend communication handling
- **Error Handling**: Comprehensive exception management

## 🏗️ Architecture

```
ai-chat-summarizer/
├── main.py             # FastAPI backend server
├── chatbot.py          # Google Gemini AI integration
├── parser.py           # Chat log parsing utilities
├── summarizer.py       # Multi-algorithm text summarization
├── requirements.txt    # Python dependencies
├── render.yaml         # Cloud deployment configuration
├── data/               # Chat logs storage
├── frontend/
│   └── app.py         # Streamlit web interface
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Google AI API key (Gemini)
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd ai-chat-summarizer
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file
   echo "GOOGLE_API_KEY=your_gemini_api_key_here" > .env
   ```

4. **Start the backend server**
   ```bash
   uvicorn main:app --host=0.0.0.0 --port=8000 --reload
   ```

5. **Launch the frontend** (in a new terminal)
   ```bash
   cd frontend
   streamlit run app.py
   ```

6. **Access the application**
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 🔧 Configuration

### AI Response Parameters

| Parameter | Range | Description |
|-----------|--------|-------------|
| Temperature | 0.0-1.0 | Controls randomness (0.0 = deterministic, 1.0 = very random) |
| Top-p | 0.1-1.0 | Nucleus sampling threshold |
| Top-k | 1-100+ | Number of top tokens to consider |

### Preset Configurations

- **🎯 Focused** (temp: 0.2, top-p: 0.5, top-k: 10): Conservative, predictable responses
- **⚖️ Balanced** (temp: 0.7, top-p: 0.9, top-k: 40): Good mix of accuracy and creativity
- **🎨 Creative** (temp: 1.0, top-p: 0.95, top-k: 100): More varied, creative responses

## 📡 API Endpoints

### Chat Endpoints
- `POST /chat` - Send message and get AI response
- `POST /chat/clear` - Clear chat history
- `GET /health` - Health check

### Summarization Endpoints
- `GET /summarize` - Summarize current conversation
- `GET /summarize-all` - Summarize all stored conversations

### Example API Usage

```python
import requests

# Send a chat message
response = requests.post("http://localhost:8000/chat", json={
    "user_input": "Hello, how are you?",
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40
})

# Get summary
summary = requests.get("http://localhost:8000/summarize")
```

## 🔧 Technologies Used

| Layer               | Technology                              |
| ------------------- | --------------------------------------- |
| Frontend            | Streamlit                               |
| Backend             | FastAPI                                 |
| AI Model            | Gemini (via google-generativeai)        |
| NLP / Summarization | nltk, scikit-learn                      |
| HTTP Client         | requests (for frontend → backend calls) |

## 🧠 Summarization Algorithms

### 1. TF-IDF Based Summarization
- Uses Term Frequency-Inverse Document Frequency scoring
- Ranks sentences by keyword importance
- Best for technical or topic-focused conversations

### 2. TextRank Algorithm
- Graph-based ranking using PageRank principles
- Identifies most connected/important sentences
- Effective for longer, complex discussions

### 3. Frequency-Based Fallback
- Simple keyword frequency analysis
- Ensures reliable summary generation
- Used when other methods fail

## 🚀 Deployment

### Render.com Deployment

The application is configured for easy deployment on Render.com:

1. **Fork this repository**

2. **Create a new Web Service on Render**
   - Connect your GitHub repository
   - Use the following settings:
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `uvicorn main:app --host=0.0.0.0 --port=$PORT`

3. **Set environment variables:**
   - `GEMINI_API_KEY`: Your Google AI API key
   - `PYTHON_VERSION`: 3.11.0

4. **Deploy and access your application**

### Other Platforms

For the backend deployment, you can also use other platforms supporting Python:
- Heroku
- Railway
- Google Cloud Platform
- AWS
- Azure

*Note: The frontend (Streamlit) would need separate deployment or can be run locally while connecting to your deployed backend.*

## 🛠️ Development

### Customizing AI Responses

Modify `chatbot.py` to:
- Change the AI model
- Add custom prompts
- Implement response filtering

### Frontend Customization

The Streamlit frontend (`frontend/app.py`) uses custom CSS for ChatGPT-like styling. Modify the CSS section to change the appearance.

## 📦 Dependencies

### Core Libraries
- `fastapi` - Web framework for the API
- `streamlit` - Frontend web application
- `google-generativeai` - Google Gemini AI integration
- `nltk` - Natural language processing
- `scikit-learn` - Machine learning algorithms
- `networkx` - Graph algorithms for TextRank
- `numpy` - Numerical computations

### Complete dependency list in `requirements.txt`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Commit your changes: `git commit -am 'Add new feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License. See the LICENSE file for details.

## 🐛 Troubleshooting

### Common Issues

**Backend not connecting:**
- Check if the API URL in `frontend/app.py` matches your backend URL
- Verify environment variables are set correctly
- Ensure all dependencies are installed

**Summarization failing:**
- Check if NLTK data is downloaded (punkt, stopwords)
- Verify chat log files exist in the data directory
- Check backend logs for detailed error messages

**CORS errors:**
- Ensure CORS middleware is properly configured in `main.py`
- Check that frontend URL is in allowed origins

### Getting Help

1. Check the [Issues](https://github.com/shfarhaan/AI-Chat-Log-Summarizer/issues) page
2. Create a new issue with:
   - Clear description of the problem
   - Steps to reproduce
   - Error messages (if any)
   - Environment details

## 🙏 Acknowledgments

- Google AI for the Gemini API
- The open-source communities behind FastAPI, Streamlit, and NLTK
- Contributors to the scientific papers on TextRank and TF-IDF algorithms

---

**Built with ❤️ using Python, FastAPI, and Streamlit**