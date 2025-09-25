# Use Python 3.10 slim as base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential libsndfile1 ffmpeg

# Upgrade pip and install requirements
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Download NLTK stopwords (only if you need them)
RUN python -c "import nltk; nltk.download('stopwords')"
RUN python -m nltk.downloader punkt stopwords wordnet
# Expose Django port
EXPOSE 8000

# Start app using Gunicorn
CMD ["gunicorn", "dream_analyzer.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
