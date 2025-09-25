# dreams/ai_pipeline.py

import re
import nltk
from collections import Counter
from transformers import pipeline
from pathlib import Path
from django.conf import settings

# --- Pre-download NLTK data on module load ---
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("NLTK 'punkt' tokenizer not found. Downloading...")
    nltk.download('punkt', quiet=True)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    print("NLTK 'stopwords' not found. Downloading...")
    nltk.download('stopwords', quiet=True)
# -----------------------------------------------

# --- Model Loading Configuration ---
AI_MODELS_DIR = settings.BASE_DIR / 'ai_models'
SENTIMENT_MODEL_PATH = AI_MODELS_DIR / 'sentiment_model'
EMOTION_MODEL_PATH = AI_MODELS_DIR / 'emotion_model'

# --- Lazy Loading of Models ---
_sentiment_pipe = None
_emotion_pipe = None

def get_pipelines():
    """
    Loads the Hugging Face pipelines from the specified local model paths.
    """
    global _sentiment_pipe, _emotion_pipe
    try:
        if _sentiment_pipe is None:
            print(f"Loading sentiment model from local path: {SENTIMENT_MODEL_PATH}")
            _sentiment_pipe = pipeline("sentiment-analysis", model=SENTIMENT_MODEL_PATH)
        
        if _emotion_pipe is None:
            print(f"Loading emotion model from local path: {EMOTION_MODEL_PATH}")
            _emotion_pipe = pipeline("text-classification", model=EMOTION_MODEL_PATH, top_k=None)
            
        return _sentiment_pipe, _emotion_pipe
    except Exception as e:
        print(f"CRITICAL ERROR: Could not load AI models from 'ai_models' directory. {e}")
        return None, None

# --- Risk Rules ---
RISK_RULES = {
    "PTSD": {"fear": 0.6, "sadness": 0.3, "surprise": 0.2, "disgust": 0.1},
    "Depression": {"sadness": 0.7, "grief": 0.4, "remorse": 0.2, "neutral": 0.1},
    "Anxiety": {"fear": 0.7, "nervousness": 0.5, "confusion": 0.2, "surprise": 0.1},
}

# --- Keyword Extraction ---
def extract_keywords(text, top_k=10):
    try:
        stop_words = set(nltk.corpus.stopwords.words("english"))
        text = re.sub(r"[^a-zA-Z\s]", "", text.lower())
        tokens = nltk.word_tokenize(text)
        meaningful_tokens = [t for t in tokens if t not in stop_words and len(t) > 2]
        counts = Counter(meaningful_tokens)
        return [w for w, _ in counts.most_common(top_k)]
    except Exception as e:
        print(f"Error during keyword extraction: {e}")
        return []

# --- MAIN ANALYSIS FUNCTION ---
def analyze_dream(text: str) -> dict:
    sentiment_pipe, emotion_pipe = get_pipelines()
    if not sentiment_pipe or not emotion_pipe:
        return {
            "error": "AI models are not available. Please check server logs.",
            "sentiment_label": "Error", "emotion_summary": {}, "analysis_json": {},
            "potential_condition": "Error", "risk_level": "Unknown",
        }
    try:
        text_short = text[:512]
        sent = sentiment_pipe(text_short)[0]
        emotions_raw = emotion_pipe(text_short)
        
        if isinstance(emotions_raw, list) and isinstance(emotions_raw[0], list):
            emotions_raw = emotions_raw[0]
        emo_scores = {d["label"].lower(): d["score"] for d in emotions_raw}

        sentiment_mapping = {'LABEL_0': 'Negative', 'LABEL_1': 'Neutral', 'LABEL_2': 'Positive'}
        sentiment_label = sentiment_mapping.get(sent.get('label'), sent.get('label'))

        risks = {}
        for cond, weights in RISK_RULES.items():
            score = 0.0
            for emo, w in weights.items():
                score += emo_scores.get(emo, 0.0) * w
            risks[cond] = round(score, 4)
        top_condition = max(risks.items(), key=lambda kv: kv[1])[0]
        top_score = risks[top_condition]

        if top_score >= 0.5: risk_level = "High"
        elif top_score >= 0.25: risk_level = "Moderate"
        else: risk_level = "Low"
        potential_condition = top_condition if top_score > 0.25 else "None"

        analysis_details = {
            "sentiment_details": {'label': sentiment_label, 'score': sent.get('score')},
            "emotion_scores": emo_scores,
            "risk_scores_by_condition": risks,
            "top_condition_details": {"name": top_condition, "score": top_score},
            "extracted_keywords": extract_keywords(text),
        }

        return {
            "sentiment_label": sentiment_label,
            "emotion_summary": emo_scores,
            "analysis_json": analysis_details,
            "potential_condition": potential_condition,
            "risk_level": risk_level,
        }
    except Exception as e:
        print(f"An error occurred during analysis: {e}")
        return {
            "error": f"An error occurred during analysis: {e}",
            "sentiment_label": "Error", "emotion_summary": {}, "analysis_json": {"error": str(e)},
            "potential_condition": "Error", "risk_level": "Unknown",
        }