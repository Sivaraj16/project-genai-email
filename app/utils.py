import re

def clean_text(text):
    text = re.sub(r'<[^>]*?>', '', text)  # Remove HTML tags
    text = re.sub(r'http[s]?://\S+', '', text)  # Remove URLs
    text = re.sub(r'[^a-zA-Z0-9.,\n ]', '', text)  # Keep commas and periods
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces
    return text
