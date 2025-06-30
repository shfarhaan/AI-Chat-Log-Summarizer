# backend/summarizer.py

from typing import Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from parser import parse_chat_log
import nltk
import os



nltk.download('stopwords')

def generate_summary(file_path: str = "backend/data/chat.txt"):
    user_msgs, ai_msgs = parse_chat_log(file_path)
    total_exchanges = len(user_msgs) + len(ai_msgs)

    all_text = " ".join(user_msgs + ai_msgs)
    if not all_text.strip():
        return {
            "summary_text": "No conversation found in this file.",
            "total_exchanges": 0,
            "user_count": 0,
            "ai_count": 0,
            "keywords": [],
            "topic": "No conversation detected."
        }

    stop_words = stopwords.words('english')
    vectorizer = TfidfVectorizer(stop_words=stop_words, max_features=10)
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



def summarize_folder(folder_path: str = "backend/data/") -> Dict[str, dict]:
    summaries = {}
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            try:
                summary = generate_summary(file_path)
                summaries[filename] = summary
            except Exception as e:
                summaries[filename] = {"error": str(e)}
    return summaries