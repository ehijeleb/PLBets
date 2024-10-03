"use client";

import { useState, useEffect } from "react";

export default function Home() {
  const [homeTeam, setHomeTeam] = useState("");
  const [awayTeam, setAwayTeam] = useState("");
  const [hour, setHour] = useState("");
  const [day, setDay] = useState("");
  const [referee, setReferee] = useState(""); 
  const [referees, setReferees] = useState([]); 
  const [prediction, setPrediction] = useState(null);
  const [bettingTips, setBettingTips] = useState(null);

  const teams = [
    "Arsenal",
    "Aston Villa",
    "Bournemouth",
    "Brentford",
    "Brighton",
    "Chelsea",
    "Crystal Palace",
    "Everton",
    "Fulham",
    "Leeds United",
    "Leicester City",
    "Liverpool",
    "Manchester City",
    "Manchester United",
    "Newcastle United",
    "Nottingham Forest",
    "Southampton",
    "Tottenham Hotspur",
    "West Ham United",
    "Wolves",
  ];

  const daysOfWeek = [
    { label: "Monday", value: 0 },
    { label: "Tuesday", value: 1 },
    { label: "Wednesday", value: 2 },
    { label: "Thursday", value: 3 },
    { label: "Friday", value: 4 },
    { label: "Saturday", value: 5 },
    { label: "Sunday", value: 6 },
  ];

  const matchTimes = [
    { label: "12:30 PM", value: 12 },
    { label: "3:00 PM", value: 15 },
    { label: "5:30 PM", value: 17 },
    { label: "7:45 PM", value: 19 },
  ];

  useEffect(() => {
    const fetchReferees = async() => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/get_referees`);
        const data = await res.json();
        console.log("Fetched Referees:", data.referees);
        setReferees(data.referees);
      } catch (error) {
        console.error("error fetching referees", error);
      }
    };
     fetchReferees();
  }, []);
      

  const handlePredict = async () => {
    const resPrediction = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/predict_match`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
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

    const resTips = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/generate_tips`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        home_team: homeTeam,
        away_team: awayTeam,
        referee: referee,
      }),
    });
    const tipsData = await resTips.json();
    setBettingTips(tipsData);
  };

  return (
    <div className="bg-gray-100 text-black min-h-screen flex flex-col items-center justify-center p-4">
      <h1 className="text-4xl font-bold mb-8">PLBets</h1>

      <div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-md space-y-4">
        <div className="flex flex-col space-y-4">
          <select
            className="border p-2 w-full rounded-lg"
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

          <select
            className="border p-2 w-full rounded-lg"
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

          <select
            className="border p-2 w-full rounded-lg"
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

          <select
            className="border p-2 w-full rounded-lg"
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

          <select
            className="border p-2 w-full rounded-lg"
            value={referee}
            onChange={(e) => setReferee(e.target.value)}
          >
            <option value="">Select Referee</option>
            {referees.map((ref, index) => (
              <option key={index} value={ref.referee}>
                {ref.referee}
              </option>
            ))}
          </select>
        </div>

        <button
          className="bg-blue-500 text-white p-2 w-full rounded-lg mt-4 hover:bg-blue-600 transition"
          onClick={handlePredict}
        >
          Predict Match
        </button>
      </div>

      {prediction && (
        <div className="bg-white p-6 rounded-lg shadow-lg mt-8 w-full max-w-md text-center">
          <h2 className="text-2xl font-bold mb-4">Prediction:</h2>
          <p className="text-lg">{prediction.prediction}</p>
        </div>
      )}

      {bettingTips && (
        <div className="bg-white p-6 rounded-lg shadow-lg mt-4 w-full max-w-md">
          <h2 className="text-2xl font-bold mb-4 text-center">Betting Tips:</h2>

          <div className="py-4 text-center">
          <p className="text-lg">
            <strong>{homeTeam}'s</strong> Current Form:
          </p>
          <p>{bettingTips.home_record}</p>
          </div>

          <div className="py-4 text-center">
          <p className="text-lg">
            <strong>{awayTeam}'s</strong> Current Form:
          </p>
          <p>{bettingTips.away_record}</p>
          </div>

          <div className="py-4 text-center">
          <p className="text-lg">
            In <strong>{homeTeam}'s</strong> Last five games, they have scored an average of 
            {" "} {bettingTips.avg_goals_home_team.toFixed(1)} goals
          </p>
          <p className="text-lg">
          In <strong>{awayTeam}'s</strong> Last five games, they have scored an average of 
          {" "} {bettingTips.avg_goals_away_in_meetings.toFixed(1)} goals
          </p>
          </div>

          <div className="text-center space-y-2">
          <p className="text-lg">
            Since we have been collecting data, in all meetings between <strong>{homeTeam}</strong> {""}
            and {" "} <strong>{awayTeam}</strong>:
          </p>
          <ul>
            <li>
              <strong>{homeTeam}</strong> scored an average of{" "}
              {bettingTips.avg_goals_home_in_meetings.toFixed(1)} goals.
            </li>
            <li>
              <strong>{awayTeam}</strong> scored an average of{" "}
              {bettingTips.avg_goals_away_in_meetings.toFixed(1)} goals.
            </li>
          </ul>
          </div>

          {bettingTips.referee && (
            <div className="mt-4 py-4 text-center">
              <h2 className="text-2xl font-bold">Referee Stats</h2>
              <p>Referee: {bettingTips.referee.name}</p>
              <p>Fouls per game: {bettingTips.referee.fouls_pg}</p>
              <p>Penalties per game: {bettingTips.referee.pen_pg}</p>
              <p>Yellow cards per game: {bettingTips.referee.yel_pg}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
