function ScoreCircle({ score }) {
  const safeScore = Math.max(0, Math.min(100, Number(score) || 0));

  const progressStyle = {
    background: `conic-gradient(
      #2563eb ${safeScore * 3.6}deg,
      #e5e7eb ${safeScore * 3.6}deg
    )`,
  };

  return (
    <div className="score-wrapper">
      <div className="score-circle" style={progressStyle}>
        <div className="score-inner">
          <span>{safeScore}</span>
          <small>/100</small>
        </div>
      </div>

      <h3>Resume Score</h3>
    </div>
  );
}

export default ScoreCircle;