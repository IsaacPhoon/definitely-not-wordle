import { useCallback, useEffect, useState } from "react";
import {
  createGame,
  isAuthenticated,
  login,
  register,
  submitGuess,
} from "./api";
import GameBoard from "./components/GameBoard";
import Keyboard from "./components/Keyboard";
import "./App.css";

const COLOR_PRIORITY = { green: 3, yellow: 2, gray: 1 };

function AuthForm({ onAuth }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLogin, setIsLogin] = useState(true);
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      if (isLogin) {
        await login(email, password);
      } else {
        await register(email, password);
      }
      onAuth();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="auth-container">
      <h1>Definitely Not Wordle</h1>
      <form className="auth-form" onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        {error && <p className="auth-error">{error}</p>}
        <button type="submit">{isLogin ? "Log In" : "Sign Up"}</button>
        <p className="auth-toggle">
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <span onClick={() => setIsLogin(!isLogin)}>
            {isLogin ? "Sign Up" : "Log In"}
          </span>
        </p>
      </form>
    </div>
  );
}

function Toast({ message }) {
  if (!message) return null;
  return <div className="toast">{message}</div>;
}

function GameOverModal({ status, targetWord, onPlayAgain }) {
  if (!status || status === "in_progress") return null;
  return (
    <div className="modal-overlay">
      <div className="modal">
        <h2>{status === "won" ? "You Win!" : "Game Over"}</h2>
        {status === "lost" && (
          <p className="modal-word">
            The word was <strong>{targetWord?.toUpperCase()}</strong>
          </p>
        )}
        <button className="modal-button" onClick={onPlayAgain}>
          Play Again
        </button>
      </div>
    </div>
  );
}

export default function App() {
  const [authed, setAuthed] = useState(isAuthenticated());
  const [gameId, setGameId] = useState(null);
  const [guesses, setGuesses] = useState([]);
  const [currentGuess, setCurrentGuess] = useState("");
  const [gameStatus, setGameStatus] = useState("in_progress");
  const [targetWord, setTargetWord] = useState(null);
  const [letterStates, setLetterStates] = useState({});
  const [toast, setToast] = useState("");
  const [shake, setShake] = useState(false);
  const [loading, setLoading] = useState(false);

  function showToast(msg) {
    setToast(msg);
    setTimeout(() => setToast(""), 1500);
  }

  async function startGame() {
    const game = await createGame();
    setGameId(game.id);
    setGuesses([]);
    setCurrentGuess("");
    setGameStatus("in_progress");
    setTargetWord(null);
    setLetterStates({});
  }

  useEffect(() => {
    if (authed) startGame();
  }, [authed]);

  const handleKey = useCallback(
    async (key) => {
      if (gameStatus !== "in_progress" || loading) return;

      if (key === "Backspace") {
        setCurrentGuess((prev) => prev.slice(0, -1));
        return;
      }

      if (key === "Enter") {
        if (currentGuess.length !== 5) {
          showToast("Not enough letters");
          setShake(true);
          setTimeout(() => setShake(false), 600);
          return;
        }

        setLoading(true);
        try {
          const data = await submitGuess(gameId, currentGuess);
          const newGuess = data.guess;
          const newGame = data.game;

          setGuesses((prev) => [...prev, newGuess]);
          setCurrentGuess("");

          setLetterStates((prev) => {
            const updated = { ...prev };
            for (let i = 0; i < 5; i++) {
              const letter = newGuess.word[i];
              const color = newGuess.result[i];
              const existing = updated[letter];
              if (
                !existing ||
                COLOR_PRIORITY[color] > COLOR_PRIORITY[existing]
              ) {
                updated[letter] = color;
              }
            }
            return updated;
          });

          setGameStatus(newGame.status);
          if (newGame.target_word) {
            setTargetWord(newGame.target_word);
          }
        } catch (err) {
          showToast(err.message);
          setShake(true);
          setTimeout(() => setShake(false), 600);
        } finally {
          setLoading(false);
        }
        return;
      }

      if (/^[a-zA-Z]$/.test(key)) {
        setCurrentGuess((prev) =>
          prev.length < 5 ? prev + key.toLowerCase() : prev
        );
      }
    },
    [currentGuess, gameId, gameStatus, loading]
  );

  useEffect(() => {
    function onKeyDown(e) {
      if (e.ctrlKey || e.metaKey || e.altKey) return;
      if (e.key === "Backspace" || e.key === "Enter" || /^[a-zA-Z]$/.test(e.key)) {
        handleKey(e.key);
      }
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [handleKey]);

  if (!authed) {
    return <AuthForm onAuth={() => setAuthed(true)} />;
  }

  return (
    <div className="game">
      <header className="header">
        <h1>Definitely Not Wordle</h1>
      </header>
      <Toast message={toast} />
      <GameBoard guesses={guesses} currentGuess={currentGuess} shake={shake} />
      <Keyboard letterStates={letterStates} onKey={handleKey} />
      <GameOverModal
        status={gameStatus}
        targetWord={targetWord}
        onPlayAgain={startGame}
      />
    </div>
  );
}
