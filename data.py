import random
import pandas as pd

# Dữ liệu gốc
WORD_CATEGORIES = {
    'animals': ['ELEPHANT', 'GIRAFFE', 'PENGUIN', 'DOLPHIN', 'BUTTERFLY', 'KANGAROO', 'OCTOPUS', 'RHINOCEROS'],
    'countries': ['AUSTRALIA', 'CANADA', 'BRAZIL', 'FRANCE', 'JAPAN', 'GERMANY', 'ITALY', 'MEXICO'],
    'fruits': ['PINEAPPLE', 'STRAWBERRY', 'WATERMELON', 'BANANA', 'ORANGE', 'GRAPE', 'CHERRY', 'MANGO'],
    'technology': ['COMPUTER', 'SMARTPHONE', 'INTERNET', 'SOFTWARE', 'DATABASE', 'ALGORITHM', 'PROGRAMMING', 'ARTIFICIAL'],
    'sports': ['BASKETBALL', 'FOOTBALL', 'TENNIS', 'SWIMMING', 'CYCLING', 'VOLLEYBALL', 'BASEBALL', 'HOCKEY'],
    'movies': ['ADVENTURE', 'COMEDY', 'THRILLER', 'ROMANCE', 'MYSTERY', 'FANTASY', 'DOCUMENTARY', 'ANIMATION']
}

# Hàm che ngẫu nhiên một số ký tự
def mask_word(word, num_mask=3):
    word = word.upper()
    word_list = list(word)
    indices = list(range(len(word)))
    random.shuffle(indices)
    masked_indices = indices[:num_mask]
    for idx in masked_indices:
        word_list[idx] = '_'
    return ''.join(word_list)

# Tạo dataset
data = []
for category, word_list in WORD_CATEGORIES.items():
    for word in word_list:
        for _ in range(3):  # Tạo 3 phiên bản bị che mỗi từ
            num_mask = random.randint(2, max(2, len(word) // 2))
            masked = mask_word(word, num_mask=num_mask)
            data.append({
                'masked_word': masked,
                'target_word': word
            })

df = pd.DataFrame(data)
print(df.head())

# Lưu ra CSV
df.to_csv('hangman_guess_dataset.csv', index=False)
print("✅ Đã lưu dataset tại hangman_guess_dataset.csv")
