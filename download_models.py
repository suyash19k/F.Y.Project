# download_models.py
# A one-time script to download and save the upgraded Hugging Face models.

from transformers import pipeline
import os

# Define the target directory for the models
MODELS_BASE_DIR = "./ai_models"

def download_and_save_models():
    """
    Downloads the specified sentiment and emotion models from Hugging Face
    and saves them to the local 'ai_models' directory.
    """
    print("--- Starting Download of Upgraded AI Models ---")

    # --- 1. Downloading the new, more nuanced Sentiment model ---
    sentiment_model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    sentiment_save_path = os.path.join(MODELS_BASE_DIR, "sentiment_model")
    
    print(f"\nDownloading sentiment model: '{sentiment_model_name}'...")
    if not os.path.exists(sentiment_save_path):
        os.makedirs(sentiment_save_path)
        
    pipeline(
        "sentiment-analysis",
        model=sentiment_model_name
    ).save_pretrained(sentiment_save_path)
    print(f"Sentiment model saved to '{sentiment_save_path}'")


    # --- 2. Downloading the new, more accurate Emotion model ---
    emotion_model_name = "SamLowe/roberta-base-go_emotions"
    emotion_save_path = os.path.join(MODELS_BASE_DIR, "emotion_model")

    print(f"\nDownloading emotion model: '{emotion_model_name}'...")
    if not os.path.exists(emotion_save_path):
        os.makedirs(emotion_save_path)

    pipeline(
        "text-classification",
        model=emotion_model_name
    ).save_pretrained(emotion_save_path)
    print(f"Emotion model saved to '{emotion_save_path}'")


    print("\n--- All models have been downloaded successfully. ---")
    print("Your project is now ready to use the local AI models.")

if __name__ == "__main__":
    download_and_save_models()