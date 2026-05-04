# definitely-not-wordle

A fast, clean Wordle-like with accounts, stats, and a history you can actually browse.

**Live site:** `https://definitely-not-wordle.isaacphoon.dev/`

## Highlights

- **Play instantly**: Jump in as a guest, or sign up / log in to save your progress.
- **Player stats**: Track streaks, games played, and win rate.
- **Game history**: Browse completed games in a scrollable history modal.
- **Responsive layout**: Designed to stay usable and balanced across mobile, tablet, and desktop.

## Tech stack

- **Frontend**: React + Vite
- **Backend**: FastAPI + SQLModel + Postgres
- **Auth**: JWT
- **Password hashing**: Argon2

## How to play

Guess the hidden word in a limited number of tries. Each guess gives letter-by-letter feedback to help you narrow down the answer.

## Roadmap ideas (Might add!)

- Daily challenge mode with shareable results
- Expanded word lists and optional difficulty settings
