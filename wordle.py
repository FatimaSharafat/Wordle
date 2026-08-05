"""
Wordle
=======
A command-line clone of Wordle. Guess the secret five-letter word in
six tries. After each guess every letter is marked:
 green - correct letter, correct position
 yellow - correct letter, wrong position
 gray - letter not in the word
Duplicate letters are handled the way the original game does: a letter
is only marked green/yellow as many times as it actually appears in
the target word (see `score_guess` and its tests for the classic
duplicate-letter edge cases).
"""
from __future__ import annotations
import random
from enum import Enum
from typing import Dict, List, Optional
WORD_LENGTH = 5
MAX_GUESSES = 6
# Self-contained word lists so the game has no external dependencies
# or network calls.
ANSWER_WORDS = [
 "about", "above", "actor", "adult", "after", "again", "agent", "agree",
 "ahead", "alarm", "album", "alert", "alike", "alive", "allow", "alone",
 "along", "alter", "among", "anger", "angle", "angry", "apart", "apple",
 "apply", "arena", "argue", "arise", "array", "aside", "asset", "audio",
 "audit", "avoid", "await", "award", "aware", "badly", "baker", "bases",
 "basic", "beach", "began", "begin", "being", "below", "bench", "birth",
 "black", "blade", "blame", "blank", "blind", "block", "blood", "board",
 "boost", "booth", "bound", "brain", "brand", "bread", "break", "breed",
 "brief", "bring", "broad", "broke", "brown", "build", "built", "buyer",
 "cable", "camel", "canal", "candy", "cargo", "carry", "carve", "catch",
 "cause", "chain", "chair", "chart", "chase", "cheap", "check", "chest",
 "chief", "child", "chose", "civil", "claim", "class", "clean", "clear",
 "climb", "clock", "close", "cloud", "coach", "coast", "could", "count",
 "court", "cover", "craft", "crash", "cream", "crime", "cross", "crowd",
 "crown", "curve", "cycle", "daily", "dance", "dealt", "death", "debut",
 "delay", "depth", "doubt", "dozen", "draft", "drama", "drawn", "dream",
 "dress", "drill", "drink", "drive", "drove", "eager", "early", "earth",
 "eight", "elite", "empty", "enemy", "enjoy", "enter", "entry", "equal",
 "error", "event", "every", "exact", "exist", "extra", "faith", "false",
 "fault", "fiber", "field", "fifth", "fifty", "fight", "final", "first",
 "fixed", "flash", "fleet", "floor", "fluid", "focus", "force", "forth",
 "forty", "forum", "found", "frame", "fresh", "front", "fruit", "fully",
 "funny", "giant", "given", "glass", "globe", "going", "grace", "grade",
 "grand", "grant", "grass", "great", "green", "gross", "group", "grown",
 "guard", "guess", "guest", "guide", "happy", "harsh", "heart", "heavy",
 "hence", "horse", "hotel", "house", "human", "ideal", "image", "index",
 "inner", "input", "issue", "joint", "judge", "known", "label", "large",
 "laser", "later", "laugh", "layer", "learn", "least", "leave", "legal",
 "level", "light", "limit", "local", "logic", "loose", "lower", "lucky",
 "lunch", "lying", "magic", "major", "maker", "march", "match", "maybe",
 "mayor", "meant", "media", "metal", "might", "minor", "minus", "mixed",
 "model", "money", "month", "moral", "motor", "mount", "mouse", "mouth",
 "moved", "movie", "music", "needs", "never", "newly", "night", "noise",
 "north", "noted", "novel", "nurse", "occur", "ocean", "offer", "often",
 "order", "other", "ought", "outer", "owner", "panel", "paper", "party",
 "peace", "phase", "phone", "photo", "piece", "pilot", "pitch", "place",
 "plain", "plane", "plant", "plate", "point", "pound", "power", "press",
 "price", "pride", "prime", "print", "prior", "prize", "proof", "proud",
 "prove", "queen", "quick", "quiet", "quite", "radio", "raise", "range",
 "rapid", "ratio", "reach", "ready", "realm", "rebel", "refer", "relax",
 "reply", "right", "rigid", "river", "robot", "roman", "rough", "round",
 "route", "royal", "rural", "scale", "scene", "scope", "score", "sense",
 "serve", "seven", "shade", "shake", "shall", "shape", "share", "sharp",
 "sheet", "shelf", "shell", "shift", "shine", "shirt", "shock", "shoot",
 "short", "shown", "sight", "silly", "since", "sixth", "sixty", "sized",
 "skill", "sleep", "slide", "small", "smart", "smile", "smith", "smoke",
 "solid", "solve", "sorry", "sound", "south", "space", "spare", "speak",
 "speed", "spend", "spent", "split", "spoke", "sport", "staff", "stage",
 "stake", "stand", "start", "state", "steam", "steel", "steep", "stick",
 "still", "stock", "stone", "stood", "store", "storm", "story", "strip",
 "stuck", "study", "stuff", "style", "sugar", "suite", "super", "sweet",
 "table", "taken", "taste", "taxes", "teach", "teeth", "texas", "thank",
 "theft", "their", "theme", "there", "these", "thick", "thing", "think",
 "third", "those", "three", "threw", "throw", "tight", "timer", "times",
 "tired", "title", "today", "topic", "total", "touch", "tough", "tower",
 "track", "trade", "train", "treat", "trend", "trial", "tribe", "trick",
 "tried", "tries", "truck", "truly", "trust", "truth", "twice", "under",
 "undue", "union", "unity", "until", "upper", "upset", "urban", "usage",
 "usual", "valid", "value", "video", "virus", "visit", "vital", "voice",
 "waste", "watch", "water", "wheel", "where", "which", "while", "white",
 "whole", "whose", "woman", "women", "world", "worry", "worse", "worth",
 "would", "wound", "write", "wrong", "wrote", "yield", "young", "youth",
]
VALID_GUESSES = set(ANSWER_WORDS)
class LetterResult(Enum):
 GREEN = "green"
 YELLOW = "yellow"
 GRAY = "gray"
_COLOR_CODES = {
 LetterResult.GREEN: "\033[42m\033[30m",
 LetterResult.YELLOW: "\033[43m\033[30m",
 LetterResult.GRAY: "\033[100m\033[37m",
}
_RESET = "\033[0m"
def score_guess(guess: str, target: str) -> List[LetterResult]:
 """
 Compare a guess to the target word and return a per-letter result.
 Two passes, matching how Wordle itself resolves duplicate letters:
 1. Mark exact position matches green and remove them from the pool
 of target letters still available to match.
 2. For every remaining letter, mark it yellow if it's still in the
 pool (and consume one occurrence), otherwise gray.
 """
 guess = guess.lower()
 target = target.lower()
 result = [LetterResult.GRAY] * WORD_LENGTH
 remaining: Dict[str, int] = {}
 for i, letter in enumerate(target):
 if guess[i] == letter:
 result[i] = LetterResult.GREEN
 else:
 remaining[letter] = remaining.get(letter, 0) + 1
 for i, letter in enumerate(guess):
 if result[i] == LetterResult.GREEN:
 continue
 if remaining.get(letter, 0) > 0:
 result[i] = LetterResult.YELLOW
 remaining[letter] -= 1
 return result
def render_guess(guess: str, results: List[LetterResult], use_color: bool = True) -> str:
 """Render a scored guess as a colored terminal row, or a plain-text fallback."""
 if not use_color:
 symbols = {LetterResult.GREEN: "G", LetterResult.YELLOW: "Y", LetterResult.GRAY: "_"}
 return " ".join(f"{ch.upper()}({symbols[r]})" for ch, r in zip(guess, results))
 return "".join(f"{_COLOR_CODES[r]} {ch.upper()} {_RESET}" for ch, r in zip(guess, results))
def is_valid_guess(guess: str) -> bool:
 return len(guess) == WORD_LENGTH and guess.isalpha()
def play(target: Optional[str] = None, use_color: bool = True) -> bool:
 """Run one interactive game in the terminal. Returns True if the player wins."""
 target = (target or random.choice(ANSWER_WORDS)).lower()
 print(f"Guess the {WORD_LENGTH}-letter word. You have {MAX_GUESSES} tries.\n")
 for attempt in range(1, MAX_GUESSES + 1):
 guess = input(f"Guess {attempt}/{MAX_GUESSES}: ").strip().lower()
 if not is_valid_guess(guess):
 print(f"Please enter a {WORD_LENGTH}-letter word using only letters.")
 continue
 if guess not in VALID_GUESSES:
 print("Not in word list, try again.")
 continue
 results = score_guess(guess, target)
 print(render_guess(guess, results, use_color))
 if guess == target:
 print(f"\nYou got it in {attempt}/{MAX_GUESSES}!")
 return True
 print(f"\nOut of guesses. The word was: {target.upper()}")
 return False
def main() -> None:
 play()
if __name__ == "__main__":
 main()
