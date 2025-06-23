import pandas as pd
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

# === 1. Load your CSV ===
def load_data(csv_file):
    df = pd.read_csv(csv_file)
    # Ensure uppercase consistency
    df['masked_word'] = df['masked_word'].str.upper()
    df['target_word'] = df['target_word'].str.upper()
    return df['masked_word'], df['target_word']

# === 2. Train Naive Bayes ===
def train_model(X_text, y_labels):
    vectorizer = CountVectorizer(analyzer='char', binary=True)
    X_vec = vectorizer.fit_transform(X_text)

    model = MultinomialNB()
    model.fit(X_vec, y_labels)
    return model, vectorizer

# === 3. Save model + vectorizer ===
def save_model(model, vectorizer, filename='hangman_model.pkl'):
    with open(filename, 'wb') as f:
        pickle.dump((model, vectorizer), f)
    print(f"✅ Model saved to {filename}")

# === 4. Main training script ===
if __name__ == "__main__":
    csv_path = 'hangman_guess_dataset.csv'  # ← replace with your real CSV filename
    X, y = load_data(csv_path)
    model, vectorizer = train_model(X, y)
    save_model(model, vectorizer)
