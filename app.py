from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import random
import pickle
import numpy as np

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'


# Load AI model and vectorizer
with open('hangman_model.pkl', 'rb') as f:
    model, vectorizer = pickle.load(f)

# Categories
WORD_CATEGORIES = {
    'animals': ['ELEPHANT', 'GIRAFFE', 'PENGUIN', 'DOLPHIN', 'BUTTERFLY', 'KANGAROO', 'OCTOPUS', 'RHINOCEROS'],
    'countries': ['AUSTRALIA', 'CANADA', 'BRAZIL', 'FRANCE', 'JAPAN', 'GERMANY', 'ITALY', 'MEXICO'],
    'fruits': ['PINEAPPLE', 'STRAWBERRY', 'WATERMELON', 'BANANA', 'ORANGE', 'GRAPE', 'CHERRY', 'MANGO'],
    'technology': ['COMPUTER', 'SMARTPHONE', 'INTERNET', 'SOFTWARE', 'DATABASE', 'ALGORITHM', 'PROGRAMMING',
                   'ARTIFICIAL'],
    'sports': ['BASKETBALL', 'FOOTBALL', 'TENNIS', 'SWIMMING', 'CYCLING', 'VOLLEYBALL', 'BASEBALL', 'HOCKEY'],
    'movies': ['ADVENTURE', 'COMEDY', 'THRILLER', 'ROMANCE', 'MYSTERY', 'FANTASY', 'DOCUMENTARY', 'ANIMATION']
}

# Hangman stages
def get_hangman_stages():
    return [
        '',  # 0 wrong guesses
        'Head',
        'Head + Body',
        'Head + Body + Left Arm',
        'Head + Body + Both Arms',
        'Head + Body + Both Arms + Left Leg',
        'Head + Body + Both Arms + Both Legs'
    ]
# AI Prediction function
def predict_word_ai(masked_word, wrong_letters, category, top_k=3):
    input_str = masked_word + '|' + ''.join(sorted(wrong_letters))
    X_test = vectorizer.transform([input_str])
    probs = model.predict_proba(X_test)[0]
    class_labels = model.classes_

    # Get top predictions by probability
    top_indices = np.argsort(probs)[::-1]

    # Words allowed for this category
    allowed_words = set(WORD_CATEGORIES.get(category.lower(), []))

    # Filter out predictions:
    # - That contain any wrong letters
    # - That are not in the selected category
    results = []
    for idx in top_indices:
        word = class_labels[idx]
        if (word in allowed_words) and all(letter not in word for letter in wrong_letters):
            results.append((word, round(probs[idx], 4)))
        if len(results) >= top_k:
            break

    return results



# Home page
@app.route('/')
def index():
    return render_template('index.html', categories=WORD_CATEGORIES.keys())

# Start a new game
@app.route('/start_game', methods=['POST'])
def start_game():
    category = request.form.get('category')
    if category not in WORD_CATEGORIES:
        return redirect(url_for('index'))

    word = random.choice(WORD_CATEGORIES[category])
    session['word'] = word
    session['category'] = category
    session['guessed_letters'] = []
    session['wrong_guesses'] = 0
    session['lives'] = 6
    session['game_over'] = False
    session['game_won'] = False

    return redirect(url_for('game'))

# Game screen
@app.route('/game')
def game():
    if 'word' not in session:
        return redirect(url_for('index'))

    word = session['word']
    guessed_letters = session.get('guessed_letters', [])
    wrong_guesses = session.get('wrong_guesses', 0)
    lives = session.get('lives', 6)
    game_over = session.get('game_over', False)
    game_won = session.get('game_won', False)
    category = session.get('category', '')

    # Create masked word for player
    display_word = []
    for letter in word:
        if letter in guessed_letters:
            display_word.append(letter)
        else:
            display_word.append('_')

    # Prepare input for AI
    masked_word_str = ''.join(display_word)
    wrong_letters = [l for l in guessed_letters if l not in word]
    ai_predictions = predict_word_ai(masked_word_str, wrong_letters, category.lower())

    # Alphabet for guessing
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    return render_template('game.html',
                           word=word,
                           display_word=display_word,
                           guessed_letters=guessed_letters,
                           alphabet=alphabet,
                           wrong_guesses=wrong_guesses,
                           lives=lives,
                           game_over=game_over,
                           game_won=game_won,
                           category=category.title(),
                           hangman_stage=get_hangman_stages()[min(wrong_guesses, 6)],
                           ai_predictions=ai_predictions)

# Process letter guess
@app.route('/guess', methods=['POST'])
def guess():
    if 'word' not in session or session.get('game_over'):
        return jsonify({'error': 'No active game'})

    letter = request.form.get('letter', '').upper()
    if not letter or len(letter) != 1 or not letter.isalpha():
        return jsonify({'error': 'Invalid letter'})

    word = session['word']
    guessed_letters = session.get('guessed_letters', [])

    if letter in guessed_letters:
        return jsonify({'error': 'Letter already guessed'})

    guessed_letters.append(letter)
    session['guessed_letters'] = guessed_letters

    if letter not in word:
        session['wrong_guesses'] = session.get('wrong_guesses', 0) + 1
        session['lives'] = session.get('lives', 6) - 1

    # Win condition
    if all(l in guessed_letters for l in word):
        session['game_won'] = True
        session['game_over'] = True

    # Lose condition
    if session.get('wrong_guesses', 0) >= 6:
        session['game_over'] = True

    return redirect(url_for('game'))

# Reset game
@app.route('/reset_game')
def reset_game():
    session.clear()
    return redirect(url_for('index'))

# Run server
if __name__ == '__main__':
    app.run(debug=True)
