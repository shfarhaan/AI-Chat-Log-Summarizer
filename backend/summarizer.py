# backend/summarizer.py

import os
import numpy as np
import networkx as nx
import nltk

from typing import Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from parser import parse_chat_log
from nltk.tokenize import sent_tokenize
from nltk.cluster.util import cosine_distance



nltk.download('stopwords')
nltk.download('punkt')

def generate_summary(file_path: str = "backend/data/chat.txt", num_sentences: int = 3):
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

    # Generate keywords using TF-IDF
    stop_words = stopwords.words('english')
    vectorizer = TfidfVectorizer(stop_words=stop_words, max_features=10)
    tfidf_matrix = vectorizer.fit_transform([all_text])
    keywords = vectorizer.get_feature_names_out()

    # Try TF-IDF based summary first
    summary_text = tfidf_based_summary(all_text, tfidf_matrix, vectorizer, num_sentences)
    
    # If TF-IDF summary fails, try TextRank algorithm
    if not summary_text or len(summary_text.strip()) < 20:
        summary_text = extractive_summary(all_text, num_sentences)
    
    # If both fail, create a simple frequency-based summary
    if not summary_text or len(summary_text.strip()) < 20:
        summary_text = frequency_based_summary(all_text, user_msgs, ai_msgs, keywords)

    summary = {
        "summary_text": summary_text,
        "total_exchanges": total_exchanges,
        "user_count": len(user_msgs),
        "ai_count": len(ai_msgs),
        "keywords": list(keywords),
        "topic": f"The conversation mainly focused on: {', '.join(keywords)}."
    }
    return summary

def tfidf_based_summary(text: str, tfidf_matrix, vectorizer, num_sentences: int = 3):
    """Generate summary using TF-IDF scores to rank sentences"""
    try:
        sentences = sent_tokenize(text)
        
        if len(sentences) <= num_sentences:
            return text
        
        # Get feature names (keywords) and their TF-IDF scores
        feature_names = vectorizer.get_feature_names_out()
        tfidf_scores = tfidf_matrix.toarray()[0]  # Get scores for the single document
        
        # Create word-score mapping
        word_scores = dict(zip(feature_names, tfidf_scores))
        
        # Score each sentence based on TF-IDF scores of words it contains
        sentence_scores = []
        for i, sentence in enumerate(sentences):
            sentence_score = 0
            words = sentence.lower().split()
            word_count = 0
            
            for word in words:
                # Clean word (remove punctuation)
                clean_word = ''.join(char for char in word if char.isalnum())
                if clean_word in word_scores:
                    sentence_score += word_scores[clean_word]
                    word_count += 1
            
            # Average score per word (avoid bias toward longer sentences)
            if word_count > 0:
                avg_score = sentence_score / word_count
                # Boost score slightly for sentences with more important words
                final_score = avg_score * (1 + (word_count / len(words)))
                sentence_scores.append((final_score, i, sentence))
        
        # Sort sentences by score and select top ones
        sentence_scores.sort(reverse=True, key=lambda x: x[0])
        
        # Get top sentences but maintain original order
        selected_indices = sorted([score_tuple[1] for score_tuple in sentence_scores[:num_sentences]])
        summary_sentences = [sentences[i] for i in selected_indices]
        
        return ' '.join(summary_sentences)
    
    except Exception as e:
        return ""

def extractive_summary(text: str, num_sentences: int = 3):
    """Generate extractive summary using TextRank algorithm"""
    try:
        # Tokenize into sentences
        sentences = sent_tokenize(text)
        
        if len(sentences) <= num_sentences:
            return text
        
        # Remove stopwords and create word frequency matrix
        stop_words = stopwords.words('english')
        
        # Create similarity matrix
        sentence_similarity_matrix = build_similarity_matrix(sentences, stop_words)
        
        # Apply PageRank algorithm
        sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_matrix)
        scores = nx.pagerank(sentence_similarity_graph)
        
        # Rank sentences based on scores
        ranked_sentence = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)
        
        # Select top sentences
        selected_sentences = []
        for i in range(min(num_sentences, len(ranked_sentence))):
            selected_sentences.append(ranked_sentence[i][1])
        
        # Order sentences as they appear in original text
        summary_sentences = []
        for sentence in sentences:
            if sentence in selected_sentences:
                summary_sentences.append(sentence)
        
        return ' '.join(summary_sentences)
    
    except Exception as e:
        return ""

def build_similarity_matrix(sentences, stop_words):
    """Build similarity matrix for sentences"""
    similarity_matrix = np.zeros((len(sentences), len(sentences)))
    
    for idx1 in range(len(sentences)):
        for idx2 in range(len(sentences)):
            if idx1 == idx2:
                continue
            similarity_matrix[idx1][idx2] = sentence_similarity(sentences[idx1], sentences[idx2], stop_words)
    
    return similarity_matrix

def sentence_similarity(sent1, sent2, stopwords=None):
    """Calculate similarity between two sentences"""
    if stopwords is None:
        stopwords = []
    
    sent1 = [w.lower() for w in sent1.split()]
    sent2 = [w.lower() for w in sent2.split()]
    
    all_words = list(set(sent1 + sent2))
    
    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)
    
    # Build vectors
    for w in sent1:
        if w in stopwords:
            continue
        vector1[all_words.index(w)] += 1
    
    for w in sent2:
        if w in stopwords:
            continue
        vector2[all_words.index(w)] += 1
    
    return 1 - cosine_distance(vector1, vector2)

def frequency_based_summary(text: str, user_msgs: list, ai_msgs: list, keywords: list):
    """Generate a simple frequency-based summary as fallback"""
    try:
        # Create a basic summary based on conversation structure and keywords
        summary_parts = []
        
        # Conversation overview
        if len(user_msgs) > 0 and len(ai_msgs) > 0:
            summary_parts.append(f"This conversation involved {len(user_msgs)} user messages and {len(ai_msgs)} AI responses.")
        
        # Topic identification
        if keywords and len(keywords) > 0:
            main_topics = ', '.join(keywords[:5])  # Top 5 keywords
            summary_parts.append(f"The discussion primarily covered topics related to {main_topics}.")
        
        # Find most informative sentences
        sentences = sent_tokenize(text)
        if len(sentences) > 3:
            # Score sentences based on keyword presence
            sentence_scores = []
            for sentence in sentences:
                score = 0
                sentence_lower = sentence.lower()
                for keyword in keywords:
                    if keyword.lower() in sentence_lower:
                        score += 1
                if len(sentence.split()) > 5:  # Prefer longer sentences
                    sentence_scores.append((score, sentence))
            
            # Sort by score and take top sentences
            sentence_scores.sort(reverse=True)
            if sentence_scores:
                top_sentence = sentence_scores[0][1]
                summary_parts.append(f"Key point: {top_sentence}")
        
        return ' '.join(summary_parts) if summary_parts else "The conversation covered various topics but no clear summary could be generated."
    
    except Exception as e:
        return "Summary generation failed, but the conversation contained meaningful exchanges."
    
    
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