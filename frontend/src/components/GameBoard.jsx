import { useEffect, useState } from "react";

function Tile({ letter, color, position, revealed }) {
  const [animState, setAnimState] = useState("idle");

  useEffect(() => {
    if (!revealed) return;
    const flipDelay = position * 300;
    const timer1 = setTimeout(() => setAnimState("flip-out"), flipDelay);
    const timer2 = setTimeout(() => setAnimState("flip-in"), flipDelay + 250);
    const timer3 = setTimeout(() => setAnimState("done"), flipDelay + 500);
    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
    };
  }, [revealed, position]);

  const showColor = animState === "flip-in" || animState === "done";
  const bgClass = showColor ? `tile-${color}` : "";
  const filledClass = letter && !showColor ? "tile-filled" : "";
  const animClass =
    animState === "flip-out"
      ? "tile-flip-out"
      : animState === "flip-in"
        ? "tile-flip-in"
        : "";

  return (
    <div className={`tile ${bgClass} ${filledClass} ${animClass}`}>
      {letter}
    </div>
  );
}

export default function GameBoard({ guesses, currentGuess, shake }) {
  const rows = [];

  for (let i = 0; i < 6; i++) {
    if (i < guesses.length) {
      const guess = guesses[i];
      rows.push(
        <div className="board-row" key={i}>
          {guess.word.split("").map((letter, j) => (
            <Tile
              key={j}
              letter={letter}
              color={guess.result[j]}
              position={j}
              revealed={true}
            />
          ))}
        </div>
      );
    } else if (i === guesses.length) {
      const letters = currentGuess.split("");
      rows.push(
        <div
          className={`board-row ${shake ? "row-shake" : ""}`}
          key={i}
        >
          {Array.from({ length: 5 }, (_, j) => (
            <Tile
              key={j}
              letter={letters[j] || ""}
              color={null}
              position={j}
              revealed={false}
            />
          ))}
        </div>
      );
    } else {
      rows.push(
        <div className="board-row" key={i}>
          {Array.from({ length: 5 }, (_, j) => (
            <Tile key={j} letter="" color={null} position={j} revealed={false} />
          ))}
        </div>
      );
    }
  }

  return <div className="board">{rows}</div>;
}
