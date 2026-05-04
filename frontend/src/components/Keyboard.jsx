const ROWS = [
  ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
  ["a", "s", "d", "f", "g", "h", "j", "k", "l"],
  ["Enter", "z", "x", "c", "v", "b", "n", "m", "Backspace"],
];

export default function Keyboard({ letterStates, onKey }) {
  return (
    <div className="keyboard">
      {ROWS.map((row, i) => (
        <div className="keyboard-row" key={i}>
          {row.map((key) => {
            const color = letterStates[key];
            const colorClass = color ? `key-${color}` : "";
            const isWide = key === "Enter" || key === "Backspace";
            return (
              <button
                key={key}
                className={`key ${colorClass} ${isWide ? "key-wide" : ""}`}
                onClick={() => onKey(key)}
              >
                {key === "Backspace" ? "Del" : key}
              </button>
            );
          })}
        </div>
      ))}
    </div>
  );
}
