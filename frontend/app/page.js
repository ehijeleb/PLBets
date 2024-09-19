"use client";

import { useState } from 'react';

export default function Home() {
  const [homeTeam, setHomeTeam] = useState('');
  const [awayTeam, setAwayTeam] = useState('');
  const [hour, setHour] = useState('');
  const [day, setDay] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [bettingTips, setBettingTips] = useState(null);

  // List of Premier League teams
  const teams = [
    'Arsenal', 'Aston Villa', 'Bournemouth', 'Brentford', 'Brighton', 'Chelsea', 'Crystal Palace', 'Everton',
    'Fulham', 'Leeds United', 'Leicester City', 'Liverpool', 'Manchester City', 'Manchester United',
    'Newcastle United', 'Nottingham Forest', 'Southampton', 'Tottenham Hotspur', 'West Ham United', 'Wolves'
  ];

  const daysOfWeek = [
    { label: 'Monday', value: 0 },
    { label: 'Tuesday', value: 1 },
    { label: 'Wednesday', value: 2 },
    { label: 'Thursday', value: 3 },
    { label: 'Friday', value: 4 },
    { label: 'Saturday', value: 5 },
    { label: 'Sunday', value: 6 },
  ];

  const matchTimes = [
    { label: '12:30 PM', value: 12 },
    { label: '3:00 PM', value: 15 },
    { label: '5:30 PM', value: 17 },
    { label: '7:45 PM', value: 19 },
  ];

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
    <div className="bg-white text-black min-h-screen flex flex-col items-center justify-center">
      <h1 className="text-3xl font-bold mb-8">Premier League Match Predictor</h1>
      <div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-md">
        {/* Dropdown for selecting home team */}
        <select
          className="border p-2 my-2 w-full rounded-lg"
          value={homeTeam}
          onChange={(e) => setHomeTeam(e.target.value)}
        >
          <option value="">Select Home Team</option>
          {teams.map((team) => (
            <option key={team} value={team}>
              {team}
            </option>
          ))}
        </select>

        {/* Dropdown for selecting away team */}
        <select
          className="border p-2 my-2 w-full rounded-lg"
          value={awayTeam}
          onChange={(e) => setAwayTeam(e.target.value)}
        >
          <option value="">Select Away Team</option>
          {teams.map((team) => (
            <option key={team} value={team}>
              {team}
            </option>
          ))}
        </select>

        {/* Dropdown for selecting match day */}
        <select
          className="border p-2 my-2 w-full rounded-lg"
          value={day}
          onChange={(e) => setDay(e.target.value)}
        >
          <option value="">Select Day of the Week</option>
          {daysOfWeek.map((day) => (
            <option key={day.value} value={day.value}>
              {day.label}
            </option>
          ))}
        </select>

        {/* Dropdown for selecting match time */}
        <select
          className="border p-2 my-2 w-full rounded-lg"
          value={hour}
          onChange={(e) => setHour(e.target.value)}
        >
          <option value="">Select Match Time</option>
          {matchTimes.map((time) => (
            <option key={time.value} value={time.value}>
              {time.label}
            </option>
          ))}
        </select>

        <button
          className="bg-blue-500 text-white p-2 w-full rounded-lg mt-4"
          onClick={handlePredict}
        >
          Predict Match
        </button>
      </div>

      {prediction && (
        <div className="mt-8">
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
