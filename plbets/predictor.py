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

    def rolling_averages(self, group, cols, new_cols):
        """Calculate rolling averages for team form over the last 3 matches."""
        group = group.sort_values("date")  # Sort games by date
        rolling_stats = group[cols].rolling(3, closed='left').mean()  # Rolling average for last 3 games
        group[new_cols] = rolling_stats
        group = group.dropna(subset=new_cols)  # Drop rows with missing rolling averages
        return group

    def get_team_selection(self):
        print("\nPremier League Teams:")
        for i, team in enumerate(self.teams, 1):
            print(f"{i}. {team}")
        
        home_team_index = int(input("Select the home team (enter the number): ")) - 1
        away_team_index = int(input("Select the away team (enter the number): ")) - 1
        
        home_team = self.teams[home_team_index]
        away_team = self.teams[away_team_index]

        # Get hour input from the user
        hour = int(input("Enter the match hour (0-23, e.g., 15 for 3 PM): "))
        
        # Get day of the week input from the user
        print("\nDays of the week (0 = Monday, 6 = Sunday):")
        day = int(input("Enter the day of the week for the match (0-6): "))

        return home_team, away_team, hour, day

    def run(self):
        matches = self.data_loader.load_data()

        # Define columns for rolling averages
        cols = ["gf", "ga", "sh", "sot", "dist", "fk", "pk", "pkatt"]
        new_cols = [f"{c}_rolling" for c in cols]
        
        # Apply rolling averages to the data
        matches_rolling = matches.groupby("team").apply(lambda x: self.rolling_averages(x, cols, new_cols))
        matches_rolling = matches_rolling.droplevel('team')  # Drop the extra index level added by groupby
        matches_rolling.index = range(matches_rolling.shape[0])  # Reset index
        
        # Split into training and testing sets
        train_data = matches_rolling[matches_rolling["date"] < '2022-01-01']
        test_data = matches_rolling[matches_rolling["date"] > '2022-01-01']
        
        # Define predictors and target
        target = "target"
        
        self.model.train(train_data, self.predictors, target)
        preds, precision = self.model.evaluate(test_data, self.predictors, target)
        print(f"Model Precision: {precision:.2f}")
        
        # Team selection and match prediction
        home_team, away_team, hour, day = self.get_team_selection()
        self.predict_match(home_team, away_team, hour, day, matches_rolling)
    
    def predict_match(self, home_team, away_team, hour, day, matches_rolling):
        # Get the latest rolling averages for the home and away teams
        home_team_data = matches_rolling[matches_rolling["team"] == home_team].sort_values("date").iloc[-1]
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

        if pred[0] == 1:
            print(f"\nPrediction: {home_team} will win the match against {away_team}!")
        else:
            print(f"\nPrediction: {home_team} will not win the match against {away_team}.")
