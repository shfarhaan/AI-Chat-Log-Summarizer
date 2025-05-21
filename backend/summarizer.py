# backend/summarizer.py

from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from parser import parse_chat_log
import nltk

nltk.download('stopwords')

def generate_summary(file_path: str = "backend/data/chat.txt"):
    user_msgs, ai_msgs = parse_chat_log(file_path)
    total_exchanges = len(user_msgs) + len(ai_msgs)

    all_text = " ".join(user_msgs + ai_msgs)
    if not all_text.strip():
        return {
            "total_exchanges": 0,
            "user_count": 0,
            "ai_count": 0,
            "keywords": [],
            "topic": "No conversation detected."
        }

    stop_words = stopwords.words('english')
    vectorizer = TfidfVectorizer(stop_words=stop_words, max_features=5)
    tfidf_matrix = vectorizer.fit_transform([all_text])
    keywords = vectorizer.get_feature_names_out()

    summary = {
        "total_exchanges": total_exchanges,
        "user_count": len(user_msgs),
        "ai_count": len(ai_msgs),
        "keywords": list(keywords),
        "topic": f"The conversation mainly focused on: {', '.join(keywords)}."
    }
    return summary
