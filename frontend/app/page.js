"use client";

import { useState } from 'react';

export default function Home() {
  const [homeTeam, setHomeTeam] = useState('');
  const [awayTeam, setAwayTeam] = useState('');
  const [hour, setHour] = useState('');
  const [day, setDay] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [bettingTips, setBettingTips] = useState(null);

  const handlePredict = async () => {
    // Fetch the match prediction
    const resPrediction = await fetch('http://127.0.0.1:5000/predict_match', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        home_team: homeTeam,
        away_team: awayTeam,
        hour: parseInt(hour),
        day: parseInt(day),
      }),
    });
    const predictionData = await resPrediction.json();
    setPrediction(predictionData);

    // Fetch the betting tips
    const resTips = await fetch('http://127.0.0.1:5000/generate_tips', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        home_team: homeTeam,
        away_team: awayTeam,
      }),
    });
    const tipsData = await resTips.json();
    setBettingTips(tipsData);
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold">Premier League Match Predictor</h1>
      <div className="mt-4">
        <input
          className="border p-2 mr-2"
          placeholder="Home Team"
          value={homeTeam}
          onChange={(e) => setHomeTeam(e.target.value)}
        />
        <input
          className="border p-2 mr-2"
          placeholder="Away Team"
          value={awayTeam}
          onChange={(e) => setAwayTeam(e.target.value)}
        />
        <input
          className="border p-2 mr-2"
          type="number"
          placeholder="Hour"
          value={hour}
          onChange={(e) => setHour(e.target.value)}
        />
        <input
          className="border p-2 mr-2"
          type="number"
          placeholder="Day (0=Monday, 6=Sunday)"
          value={day}
          onChange={(e) => setDay(e.target.value)}
        />
        <button
          className="bg-blue-500 text-white p-2 rounded"
          onClick={handlePredict}
        >
          Predict Match
        </button>
      </div>

      {prediction && (
        <div className="mt-4">
          <h2 className="text-xl font-bold">Prediction:</h2>
          <p>{prediction.prediction}</p>
        </div>
      )}

      {bettingTips && (
        <div className="mt-4">
          <h2 className="text-xl font-bold">Betting Tips:</h2>
          <p>
            <strong>{homeTeam}</strong> Record: {bettingTips.home_record}
          </p>
          <p>
            <strong>{awayTeam}</strong> Record: {bettingTips.away_record}
          </p>
          <p>
            Average Goals Scored by <strong>{homeTeam}</strong>:{' '}
            {bettingTips.avg_goals_home_team.toFixed(1)}
          </p>
          <p>
            Average Goals Scored by <strong>{awayTeam}</strong>:{' '}
            {bettingTips.avg_goals_away_team.toFixed(1)}
          </p>
          <p>
            In all meetings between <strong>{homeTeam}</strong> and{' '}
            <strong>{awayTeam}</strong>:
          </p>
          <p>
            - <strong>{homeTeam}</strong> scored an average of{' '}
            {bettingTips.avg_goals_home_in_meetings.toFixed(1)} goals.
          </p>
          <p>
            - <strong>{awayTeam}</strong> scored an average of{' '}
            {bettingTips.avg_goals_away_in_meetings.toFixed(1)} goals.
          </p>
        </div>
      )}
    </div>
  );
}
