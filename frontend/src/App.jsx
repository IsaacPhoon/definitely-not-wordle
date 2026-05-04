import { useCallback, useEffect, useState } from "react";
import { Navigate, Route, Routes, useNavigate } from "react-router-dom";
import {
  createGame,
  getStats,
  isAuthenticated,
  isGuest,
  login,
  loginAsGuest,
  logout,
  register,
  submitGuess,
} from "./api";
import GameBoard from "./components/GameBoard";
import Keyboard from "./components/Keyboard";
import "./App.css";

const COLOR_PRIORITY = { green: 3, yellow: 2, gray: 1 };

function AuthPage() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isLogin, setIsLogin] = useState(true);
  const [error, setError] = useState("");

  if (isAuthenticated()) return <Navigate to="/" replace />;

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      if (isLogin) {
        await login(username, password);
      } else {
        await register(username, password);
      }
      navigate("/");
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleGuest() {
    setError("");
    try {
      await loginAsGuest();
      navigate("/");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="auth-container">
      <h1>Definitely Not Wordle</h1>
      <form className="auth-form" onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
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
      <div className="auth-divider">or</div>
      <button className="guest-button" onClick={handleGuest}>
        Play as Guest
      </button>
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

function GamePage() {
  const navigate = useNavigate();
  const [gameId, setGameId] = useState(null);
  const [guesses, setGuesses] = useState([]);
  const [currentGuess, setCurrentGuess] = useState("");
  const [gameStatus, setGameStatus] = useState("in_progress");
  const [targetWord, setTargetWord] = useState(null);
  const [letterStates, setLetterStates] = useState({});
  const [toast, setToast] = useState("");
  const [shake, setShake] = useState(false);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [stats, setStats] = useState(null);

  if (!isAuthenticated()) return <Navigate to="/login" replace />;

  async function fetchStats() {
    const data = await getStats();
    setStats(data);
  }

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
    setShowModal(false);
  }

  useEffect(() => {
    startGame();
    fetchStats();
  }, []);

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
              if (!existing || COLOR_PRIORITY[color] > COLOR_PRIORITY[existing]) {
                updated[letter] = color;
              }
            }
            return updated;
          });

          if (newGame.status !== "in_progress") {
            setGameStatus(newGame.status);
            if (newGame.target_word) setTargetWord(newGame.target_word);
            fetchStats();
            setTimeout(() => setShowModal(true), 1800);
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

  const guest = isGuest();

  function handleSignOut() {
    logout();
    navigate("/login");
  }

  const winPct = stats && stats.games_played > 0
    ? Math.round((stats.games_won / stats.games_played) * 100)
    : null;

  return (
    <>
      <header className="header">
        <div className="stat-group">
          <div className={`stat ${stats?.current_streak > 0 ? "stat--accent" : ""}`}>
            <span className="stat-value">{stats?.current_streak ?? "—"}</span>
            <span className="stat-label">Streak</span>
          </div>
          <div className="stat-divider" />
          <div className="stat">
            <span className="stat-value">{stats?.max_streak ?? "—"}</span>
            <span className="stat-label">Best</span>
          </div>
        </div>

        <h1>
          <span className="header-title-full">Definitely Not Wordle</span>
          <span className="header-title-short">DNW</span>
        </h1>

        <div className="header-right">
          <div className="stat-group">
            <div className="stat">
              <span className="stat-value">{stats?.games_played ?? "—"}</span>
              <span className="stat-label">Played</span>
            </div>
            <div className="stat-divider" />
            <div className="stat">
              <span className="stat-value">{winPct != null ? `${winPct}%` : "—"}</span>
              {winPct != null && (
                <div className="win-bar">
                  <div className="win-bar-fill" style={{ width: `${winPct}%` }} />
                </div>
              )}
              <span className="stat-label">Win %</span>
            </div>
          </div>
          <button className="header-btn" onClick={handleSignOut}>
            {guest ? "Sign In" : "Sign Out"}
          </button>
        </div>
      </header>
      <div className="game">
        <Toast message={toast} />
        <GameBoard key={gameId} guesses={guesses} currentGuess={currentGuess} shake={shake} />
        <Keyboard letterStates={letterStates} onKey={handleKey} />
        {showModal && (
          <GameOverModal
            status={gameStatus}
            targetWord={targetWord}
            onPlayAgain={startGame}
          />
        )}
      </div>
    </>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<AuthPage />} />
      <Route path="/" element={<GamePage />} />
    </Routes>
  );
}
