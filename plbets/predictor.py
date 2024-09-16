import pandas as pd
from plbets.data_loader import DataLoader
from plbets.model import BettingModel

class MatchPredictor:
    def __init__(self):
        self.data_loader = DataLoader("data/matches.csv")
        self.model = BettingModel()
        self.teams = [
            "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton",
            "Chelsea", "Crystal Palace", "Everton", "Fulham", "Leeds United",
            "Leicester City", "Liverpool", "Manchester City", "Manchester United",
            "Newcastle United", "Nottingham Forest", "Southampton", "Tottenham",
            "West Ham United", "Wolves"
        ]
        self.team_codes = {team: i for i, team in enumerate(self.teams)}
        self.predictors = ["h/a", "opp", "hour", "day"] + [f"{c}_rolling" for c in ["gf", "ga", "sh", "sot", "dist", "fk", "pk", "pkatt"]]
        self.matches_rolling = None  # Initialize as None, to be computed later

    def load_data_if_needed(self):
        """Load the data and calculate rolling averages if not already loaded."""
        if self.matches_rolling is None:
            matches = self.data_loader.load_data()

            # Define columns for rolling averages
            cols = ["gf", "ga", "sh", "sot", "dist", "fk", "pk", "pkatt"]
            new_cols = [f"{c}_rolling" for c in cols]

            # Apply rolling averages to the data
            matches_rolling = matches.groupby("team").apply(lambda x: self.rolling_averages(x, cols, new_cols))
            matches_rolling = matches_rolling.droplevel('team')  # Drop the extra index level added by groupby
            matches_rolling.index = range(matches_rolling.shape[0])  # Reset index
            self.matches_rolling = matches_rolling

    def rolling_averages(self, group, cols, new_cols):
        """Calculate rolling averages for team form over the last 5 matches."""
        group = group.sort_values("date")
        rolling_stats = group[cols].rolling(5, closed='left').mean()
        group[new_cols] = rolling_stats
        group = group.dropna(subset=new_cols)
        return group
    
    def generate_tips(self, home_team, away_team):
        # Ensure data is loaded and rolling averages are calculated
        self.load_data_if_needed()

        # Filter home games for the selected home team
        home_games = self.matches_rolling[(self.matches_rolling["team"] == home_team) & (self.matches_rolling["h/a"] == 1)]
        last_5_home_games = home_games.sort_values("date").tail(5)
        
        # Filter away games for the selected away team
        away_games = self.matches_rolling[(self.matches_rolling["team"] == away_team) & (self.matches_rolling["h/a"] == 0)]
        last_5_away_games = away_games.sort_values("date").tail(5)

        # Calculate the average goals scored in the last 5 home games for the home team
        avg_goals_home_team = last_5_home_games["gf"].mean()

        # Calculate the average goals scored in the last 5 away games for the away team
        avg_goals_away_team = last_5_away_games["gf"].mean()

        # Handle NaN values by replacing them with 0 or a placeholder
        avg_goals_home_team = avg_goals_home_team if not pd.isna(avg_goals_home_team) else 0
        avg_goals_away_team = avg_goals_away_team if not pd.isna(avg_goals_away_team) else 0

        # Calculate home team's record in their last 5 home games (Wins, Draws, Losses)
        home_wins = (last_5_home_games["result"] == 'W').sum()
        home_draws = (last_5_home_games["result"] == 'D').sum()
        home_losses = (last_5_home_games["result"] == 'L').sum()

        # Calculate away team's record in their last 5 away games (Wins, Draws, Losses)
        away_wins = (last_5_away_games["result"] == 'W').sum()
        away_draws = (last_5_away_games["result"] == 'D').sum()
        away_losses = (last_5_away_games["result"] == 'L').sum()

        # Ensure proper filtering of matches between the home and away teams
        all_meetings = self.matches_rolling[
            ((self.matches_rolling["team"] == home_team) & (self.matches_rolling["opponent"] == away_team)) |
            ((self.matches_rolling["team"] == away_team) & (self.matches_rolling["opponent"] == home_team))
        ]

        # Calculate average goals in all previous meetings between the home team and away team
        avg_goals_home_in_meetings = all_meetings[all_meetings["team"] == home_team]["gf"].mean()
        avg_goals_away_in_meetings = all_meetings[all_meetings["team"] == away_team]["gf"].mean()

        # Handle NaN values in the meetings
        avg_goals_home_in_meetings = avg_goals_home_in_meetings if not pd.isna(avg_goals_home_in_meetings) else 0
        avg_goals_away_in_meetings = avg_goals_away_in_meetings if not pd.isna(avg_goals_away_in_meetings) else 0

        # Generate tips as a dictionary
        tips = {
            "home_record": f"{home_wins} Wins, {home_draws} Draws, {home_losses} Losses",
            "away_record": f"{away_wins} Wins, {away_draws} Draws, {away_losses} Losses",
            "avg_goals_home_team": avg_goals_home_team,
            "avg_goals_away_team": avg_goals_away_team,
            "avg_goals_home_in_meetings": avg_goals_home_in_meetings,
            "avg_goals_away_in_meetings": avg_goals_away_in_meetings
        }

        return tips

    def predict_match(self, home_team, away_team, hour, day):
        # Ensure data is loaded and rolling averages are calculated
        self.load_data_if_needed()

        # Get the latest rolling averages for the home and away teams
        home_team_data = self.matches_rolling[self.matches_rolling["team"] == home_team].sort_values("date").iloc[-1]
        away_team_code = self.team_codes[away_team]

        # Create a row for the prediction (using home team's rolling stats)
        match_data = {
            "h/a": 1,  # Home team = 1
            "opp": away_team_code,
            "hour": hour,
            "day": day,
            # Add rolling averages for the home team
            "gf_rolling": home_team_data.get("gf_rolling", 0),
            "ga_rolling": home_team_data.get("ga_rolling", 0),
            "sh_rolling": home_team_data.get("sh_rolling", 0),
            "sot_rolling": home_team_data.get("sot_rolling", 0),
            "dist_rolling": home_team_data.get("dist_rolling", 0),
            "fk_rolling": home_team_data.get("fk_rolling", 0),
            "pk_rolling": home_team_data.get("pk_rolling", 0),
            "pkatt_rolling": home_team_data.get("pka_rolling", 0)
        }

        # Convert the match_data into a DataFrame for prediction
        match_df = pd.DataFrame([match_data])

        # Make a prediction
        pred = self.model.model.predict(match_df[self.predictors])

        # Interpret the prediction: 1 = Win, 0 = Draw, -1 = Loss
        if pred[0] == 1:
            prediction = "Home win"
        elif pred[0] == 0:
            prediction = "Draw"
        else:
            prediction = "Home loss"

        result = {
            "prediction": prediction
        }

        return result
