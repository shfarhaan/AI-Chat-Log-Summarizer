# Enhanced version with debugging to show which methods are being used

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
nltk.download('punkt_tab')


def generate_summary(file_path: str = "backend/data/chat.txt", num_sentences: int = 6):
    print(f"🔍 Starting summary generation for: {file_path}")
    
    user_msgs, ai_msgs = parse_chat_log(file_path)
    total_exchanges = len(user_msgs) + len(ai_msgs)
    
    print(f"📊 Parsed {len(user_msgs)} user messages and {len(ai_msgs)} AI messages")

    all_text = " ".join(user_msgs + ai_msgs)
    if not all_text.strip():
        print("❌ No text found in conversation")
        return {
            "summary_text": "No conversation found in this file.",
            "total_exchanges": 0,
            "user_count": 0,
            "ai_count": 0,
            "keywords": [],
            "topic": "No conversation detected.",
            "method_used": "none"
        }

    print(f"📝 Total text length: {len(all_text)} characters")
    
    # Generate keywords using TF-IDF
    stop_words = stopwords.words('english')
    vectorizer = TfidfVectorizer(stop_words=stop_words, max_features=10)
    tfidf_matrix = vectorizer.fit_transform([all_text])
    keywords = vectorizer.get_feature_names_out()
    
    print(f"🏷️ Extracted keywords: {list(keywords)}")

    # Try TF-IDF based summary first
    print("🎯 Attempting TF-IDF based summary...")
    summary_text = tfidf_based_summary(all_text, tfidf_matrix, vectorizer, num_sentences)
    method_used = "tfidf"
    
    if summary_text and len(summary_text.strip()) >= 20:
        print(f"✅ TF-IDF summary successful (length: {len(summary_text)})")
    else:
        print(f"⚠️ TF-IDF summary failed or too short (length: {len(summary_text) if summary_text else 0})")
        
        # Try TextRank algorithm
        print("🎯 Attempting TextRank (extractive) summary...")
        summary_text = extractive_summary(all_text, num_sentences)
        method_used = "textrank"
        
        if summary_text and len(summary_text.strip()) >= 20:
            print(f"✅ TextRank summary successful (length: {len(summary_text)})")
        else:
            print(f"⚠️ TextRank summary failed or too short (length: {len(summary_text) if summary_text else 0})")
            
            # Try frequency-based summary as final fallback
            print("🎯 Attempting frequency-based summary...")
            summary_text = frequency_based_summary(all_text, user_msgs, ai_msgs, keywords)
            method_used = "frequency"
            print(f"✅ Frequency-based summary completed (length: {len(summary_text)})")

    summary = {
        "summary_text": summary_text,
        "total_exchanges": total_exchanges,
        "user_count": len(user_msgs),
        "ai_count": len(ai_msgs),
        "keywords": list(keywords),
        "topic": f"The conversation mainly focused on: {', '.join(keywords)}.",
        "method_used": method_used,  # Added to show which method was used
        "debug_info": {
            "text_length": len(all_text),
            "sentences_count": len(sent_tokenize(all_text)),
            "keywords_found": len(keywords)
        }
    }
    
    print(f"🎉 Summary generation complete using {method_used} method")
    return summary

def tfidf_based_summary(text: str, tfidf_matrix, vectorizer, num_sentences: int = 6):
    """Generate summary using TF-IDF scores to rank sentences"""
    print("  🔧 Running TF-IDF analysis...")
    try:
        sentences = sent_tokenize(text)
        print(f"  📄 Found {len(sentences)} sentences")
        
        if len(sentences) <= num_sentences:
            print("  ℹ️ Text is short enough, returning full text")
            return text
        
        # Get feature names (keywords) and their TF-IDF scores
        feature_names = vectorizer.get_feature_names_out()
        tfidf_scores = tfidf_matrix.toarray()[0]
        
        # Create word-score mapping
        word_scores = dict(zip(feature_names, tfidf_scores))
        print(f"  🎯 Top TF-IDF words: {dict(sorted(word_scores.items(), key=lambda x: x[1], reverse=True)[:5])}")
        
        # Score each sentence
        sentence_scores = []
        for i, sentence in enumerate(sentences):
            sentence_score = 0
            words = sentence.lower().split()
            word_count = 0
            
            for word in words:
                clean_word = ''.join(char for char in word if char.isalnum())
                if clean_word in word_scores:
                    sentence_score += word_scores[clean_word]
                    word_count += 1
            
            if word_count > 0:
                avg_score = sentence_score / word_count
                final_score = avg_score * (1 + (word_count / len(words)))
                sentence_scores.append((final_score, i, sentence))
        
        if not sentence_scores:
            print("  ❌ No sentences could be scored")
            return ""
        
        # Sort and select top sentences
        sentence_scores.sort(reverse=True, key=lambda x: x[0])
        selected_indices = sorted([score_tuple[1] for score_tuple in sentence_scores[:num_sentences]])
        summary_sentences = [sentences[i] for i in selected_indices]
        
        result = ' '.join(summary_sentences)
        print(f"  ✅ TF-IDF summary created: {len(result)} characters")
        return result
    
    except Exception as e:
        print(f"  ❌ TF-IDF summary failed: {str(e)}")
        return ""

def extractive_summary(text: str, num_sentences: int = 3):
    """Generate extractive summary using TextRank algorithm"""
    print("  🔧 Running TextRank analysis...")
    try:
        sentences = sent_tokenize(text)
        print(f"  📄 Processing {len(sentences)} sentences")
        
        if len(sentences) <= num_sentences:
            print("  ℹ️ Text is short enough, returning full text")
            return text
        
        stop_words = stopwords.words('english')
        
        # Create similarity matrix
        print("  🔗 Building sentence similarity matrix...")
        sentence_similarity_matrix = build_similarity_matrix(sentences, stop_words)
        
        # Apply PageRank algorithm
        print("  📊 Applying PageRank algorithm...")
        sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_matrix)
        scores = nx.pagerank(sentence_similarity_graph)
        
        # Rank sentences
        ranked_sentence = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)
        
        # Select top sentences
        selected_sentences = []
        for i in range(min(num_sentences, len(ranked_sentence))):
            selected_sentences.append(ranked_sentence[i][1])
        
        # Maintain original order
        summary_sentences = []
        for sentence in sentences:
            if sentence in selected_sentences:
                summary_sentences.append(sentence)
        
        result = ' '.join(summary_sentences)
        print(f"  ✅ TextRank summary created: {len(result)} characters")
        return result
    
    except Exception as e:
        print(f"  ❌ TextRank summary failed: {str(e)}")
        return ""

def build_similarity_matrix(sentences, stop_words):
    """Build similarity matrix for sentences"""
    print(f"    🏗️ Building {len(sentences)}x{len(sentences)} similarity matrix...")
    similarity_matrix = np.zeros((len(sentences), len(sentences)))
    
    for idx1 in range(len(sentences)):
        for idx2 in range(len(sentences)):
            if idx1 == idx2:
                continue
            similarity_matrix[idx1][idx2] = sentence_similarity(sentences[idx1], sentences[idx2], stop_words)
    
    print(f"    ✅ Similarity matrix completed")
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
    print("  🔧 Creating frequency-based summary...")
    try:
        summary_parts = []
        
        # Conversation overview
        if len(user_msgs) > 0 and len(ai_msgs) > 0:
            summary_parts.append(f"This conversation involved {len(user_msgs)} user messages and {len(ai_msgs)} AI responses.")
        
        # Topic identification
        if keywords and len(keywords) > 0:
            main_topics = ', '.join(keywords[:5])
            summary_parts.append(f"The discussion primarily covered topics related to {main_topics}.")
        
        # Find most informative sentences
        sentences = sent_tokenize(text)
        if len(sentences) > 3:
            sentence_scores = []
            for sentence in sentences:
                score = 0
                sentence_lower = sentence.lower()
                for keyword in keywords:
                    if keyword.lower() in sentence_lower:
                        score += 1
                if len(sentence.split()) > 5:
                    sentence_scores.append((score, sentence))
            sentence_scores.sort(reverse=True)
            if sentence_scores:
                top_sentence = sentence_scores[0][1]
                summary_parts.append(f"Key point: {top_sentence}")
        
        result = ' '.join(summary_parts) if summary_parts else "The conversation covered various topics but no clear summary could be generated."
        print(f"  ✅ Frequency summary created: {len(result)} characters")
        return result
    
    except Exception as e:
        print(f"  ❌ Frequency summary failed: {str(e)}")
        return "Summary generation failed, but the conversation contained meaningful exchanges."

def summarize_folder(folder_path: str = "backend/data/") -> Dict[str, dict]:
    """Summarize all text files in a folder"""
    print(f"📁 Summarizing all files in: {folder_path}")
    summaries = {}
    
    try:
        files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]
        print(f"📄 Found {len(files)} text files: {files}")
        
        for filename in files:
            print(f"📝 Processing {filename}...")
            file_path = os.path.join(folder_path, filename)
            try:
                summary = generate_summary(file_path)
                summaries[filename] = summary
                print(f"✅ {filename} processed successfully")
            except Exception as e:
                print(f"❌ Error processing {filename}: {str(e)}")
                summaries[filename] = {"error": str(e)}
                
    except Exception as e:
        print(f"❌ Error accessing folder: {str(e)}")
        return {"error": f"Could not access folder: {str(e)}"}
    
    print(f"🎉 Folder summarization complete: {len(summaries)} files processed")
    return summaries