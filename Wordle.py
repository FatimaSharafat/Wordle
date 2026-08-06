"""
CS-100: Computational Problem Solving with Python
Lab 10 - Wordle

Requires a file named 'five_letter_words_no_repeats.txt' in the same folder,
containing one 5-letter English word per line (no repeated letters).

This script builds the full game: file-based secret word selection, guess
validation, green/yellow/gray feedback, 2D-array (by-index) grid tracking,
and colored tile display.
"""

import random

WORDS_FILE = "five_letter_words_no_repeats.txt"


# --------------------------------------------------------------
# Provided tile-display function
# --------------------------------------------------------------
def display_tiles(guess, statuses):
    tile_colors = {
        "green":  "\033[42m\033[97m",
        "yellow": "\033[43m\033[97m",
        "gray":   "\033[100m\033[97m"
    }
    reset_color = "\033[0m"

    for i in range(5):
        letter = guess[i].upper()
        color_code = tile_colors[statuses[i]]
        print(color_code + "  " + letter + "  " + reset_color, end=" ")
    print()
    print()


# --------------------------------------------------------------
# Step 1: File operations & validation
# --------------------------------------------------------------
def count_words_in_file(filename):
    file = open(filename)
    count = 0
    for line in file:
        count += 1
    file.close()
    return count


def get_secret_word(filename):
    total = count_words_in_file(filename)
    random_line = random.randint(0, total - 1)

    file = open(filename)
    current_line = 0
    for line in file:
        if current_line == random_line:
            file.close()
            return line.strip().lower()
        current_line += 1
    file.close()


def is_valid_guess(guess, filename):
    if len(guess) != 5:
        return False
    if not guess.isalpha():
        return False

    file = open(filename)
    for line in file:
        if line.strip().lower() == guess:
            file.close()
            return True
    file.close()
    return False


# --------------------------------------------------------------
# Step 2: Feedback logic (green, yellow, gray)
# --------------------------------------------------------------
def check_greens(guess, secret_word):
    statuses = []
    for i in range(5):
        if guess[i] == secret_word[i]:
            statuses.append("green")
        else:
            statuses.append(None)
    return statuses


def check_yellows(guess, secret_word, statuses):
    for i in range(5):
        if statuses[i] is None:
            if guess[i] in secret_word:
                statuses[i] = "yellow"
    return statuses


def check_grays(statuses):
    for i in range(5):
        if statuses[i] is None:
            statuses[i] = "gray"
    return statuses


def get_feedback(guess, secret_word):
    statuses = check_greens(guess, secret_word)
    statuses = check_yellows(guess, secret_word, statuses)
    statuses = check_grays(statuses)
    return statuses


# --------------------------------------------------------------
# Step 3: 2D array pre-allocation and by-index updating
# --------------------------------------------------------------
def create_empty_grid(rows, cols, placeholder):
    grid = []
    for r in range(rows):
        row = []
        for c in range(cols):
            row.append(placeholder)
        grid.append(row)
    return grid


def update_grids_by_index(guess_grid, status_grid, guess, statuses, row_index):
    for col in range(5):
        guess_grid[row_index][col] = guess[col]
        status_grid[row_index][col] = statuses[col]


# --------------------------------------------------------------
# Step 4: main game loop
# --------------------------------------------------------------
def play_wordle():
    secret_word = get_secret_word(WORDS_FILE)

    guess_grid = create_empty_grid(6, 5, "")
    status_grid = create_empty_grid(6, 5, None)

    attempts_used = 0
    won = False

    while attempts_used < 6 and not won:
        guess = input("Enter your guess: ").strip().lower()

        if not is_valid_guess(guess, WORDS_FILE):
            print("Please enter a valid 5-letter English word.")
            continue

        statuses = get_feedback(guess, secret_word)
        update_grids_by_index(guess_grid, status_grid, guess, statuses, attempts_used)
        display_tiles(guess, statuses)

        attempts_used += 1

        if guess == secret_word:
            won = True

    if won:
        print("Congratulations! You guessed the word in", attempts_used, "attempts.")
        print("The word was:", secret_word)
    else:
        print("Game Over!")
        print("The word was:", secret_word)

    print()
    print("Full game history:")
    for row in range(attempts_used):
        this_guess = "".join(guess_grid[row])
        this_statuses = status_grid[row]
        display_tiles(this_guess, this_statuses)


if __name__ == "__main__":
    play_wordle()
