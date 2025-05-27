from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import random
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Word categories
WORD_CATEGORIES = {
    'animals': ['ELEPHANT', 'GIRAFFE', 'PENGUIN', 'DOLPHIN', 'BUTTERFLY', 'KANGAROO', 'OCTOPUS', 'RHINOCEROS'],
    'countries': ['AUSTRALIA', 'CANADA', 'BRAZIL', 'FRANCE', 'JAPAN', 'GERMANY', 'ITALY', 'MEXICO'],
    'fruits': ['PINEAPPLE', 'STRAWBERRY', 'WATERMELON', 'BANANA', 'ORANGE', 'GRAPE', 'CHERRY', 'MANGO'],
    'technology': ['COMPUTER', 'SMARTPHONE', 'INTERNET', 'SOFTWARE', 'DATABASE', 'ALGORITHM', 'PROGRAMMING',
                   'ARTIFICIAL'],
    'sports': ['BASKETBALL', 'FOOTBALL', 'TENNIS', 'SWIMMING', 'CYCLING', 'VOLLEYBALL', 'BASEBALL', 'HOCKEY'],
    'movies': ['ADVENTURE', 'COMEDY', 'THRILLER', 'ROMANCE', 'MYSTERY', 'FANTASY', 'DOCUMENTARY', 'ANIMATION']
}


def get_hangman_stages():
    return [
        '',  # 0 wrong guesses
        'Head',  # 1 wrong guess
        'Head + Body',  # 2 wrong guesses
        'Head + Body + Left Arm',  # 3 wrong guesses
        'Head + Body + Both Arms',  # 4 wrong guesses
        'Head + Body + Both Arms + Left Leg',  # 5 wrong guesses
        'Head + Body + Both Arms + Both Legs'  # 6 wrong guesses (game over)
    ]


@app.route('/')
def index():
    return render_template('index.html', categories=WORD_CATEGORIES.keys())


@app.route('/start_game', methods=['POST'])
def start_game():
    category = request.form.get('category')
    if category not in WORD_CATEGORIES:
        return redirect(url_for('index'))

    # Initialize game session
    word = random.choice(WORD_CATEGORIES[category])
    session['word'] = word
    session['category'] = category
    session['guessed_letters'] = []
    session['wrong_guesses'] = 0
    session['lives'] = 10
    session['game_over'] = False
    session['game_won'] = False

    return redirect(url_for('game'))


@app.route('/game')
def game():
    if 'word' not in session:
        return redirect(url_for('index'))

    word = session['word']
    guessed_letters = session.get('guessed_letters', [])
    wrong_guesses = session.get('wrong_guesses', 0)
    lives = session.get('lives', 10)
    game_over = session.get('game_over', False)
    game_won = session.get('game_won', False)
    category = session.get('category', '')

    # Create display word with guessed letters
    display_word = []
    for letter in word:
        if letter in guessed_letters:
            display_word.append(letter)
        else:
            display_word.append('_')

    # Create alphabet for buttons
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
                           hangman_stage=get_hangman_stages()[min(wrong_guesses, 6)])


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
        session['lives'] = session.get('lives', 10) - 1

    # Check win condition
    if all(letter in guessed_letters for letter in word):
        session['game_won'] = True
        session['game_over'] = True

    # Check lose condition
    if session.get('wrong_guesses', 0) >= 6:
        session['game_over'] = True

    return redirect(url_for('game'))


@app.route('/reset_game')
def reset_game():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)