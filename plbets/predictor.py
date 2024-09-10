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
        """Calculate rolling averages for team form over the last 5 matches."""
        group = group.sort_values("date")  # Sort games by date
        rolling_stats = group[cols].rolling(5, closed='left').mean()  # Rolling average for last 5 games
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

    def generate_tips(self, home_team, away_team, matches_rolling):
        # Filter home games for the selected home team
        home_games = matches_rolling[(matches_rolling["team"] == home_team) & (matches_rolling["h/a"] == 1)]
        last_5_home_games = home_games.sort_values("date").tail(5)
        
        # Filter away games for the selected away team
        away_games = matches_rolling[(matches_rolling["team"] == away_team) & (matches_rolling["h/a"] == 0)]
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




        # Ensure proper filtering of matches between Arsenal and Tottenham (correct opponent matching)
        all_meetings = matches_rolling[
            ((matches_rolling["team"] == home_team) & (matches_rolling["opponent"] == away_team)) |
            ((matches_rolling["team"] == away_team) & (matches_rolling["opponent"] == home_team))
        ]

        # Calculate average goals in all previous meetings between the home team and away team
        avg_goals_home_in_meetings = all_meetings[all_meetings["team"] == home_team]["gf"].mean()
        avg_goals_away_in_meetings = all_meetings[all_meetings["team"] == away_team]["gf"].mean()


        # Generate tips
        print(f"\nBetting Tips:")
        print(f"- Home record for {home_team} in the last 5 home games: {home_wins} Wins, {home_draws} Draws, {home_losses} Losses.")
        print(f"- Away record for {away_team} in the last 5 away games: {away_wins} Wins, {away_draws} Draws, {away_losses} Losses.")
        print(f"- {home_team} has scored an average of {avg_goals_home_team:.2f} goals in their last 5 home games.")
        print(f"- {away_team} has scored an average of {avg_goals_away_team:.2f} goals in their last 5 away games.")
        
        if not all_meetings.empty:
            print(f"- In all previous meetings between {home_team} and {away_team}, {home_team} has scored an average of {avg_goals_home_in_meetings:.2f} goals.")
            print(f"- {away_team} has scored an average of {avg_goals_away_in_meetings:.2f} goals in all their meetings.")
        else:
            print(f"- No historical meetings between {home_team} and {away_team} are available in the dataset.")




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
        train_data = matches_rolling[matches_rolling["date"] < '2022-06-01']
        test_data = matches_rolling[matches_rolling["date"] > '2023-06-01']

        # Define predictors and target
        target = "target"

        self.model.train(train_data, self.predictors, target)
        preds, precision = self.model.evaluate(test_data, self.predictors, target)
        print(f"Model Precision: {precision:.2f}")

        # Team selection and match prediction
        home_team, away_team, hour, day = self.get_team_selection()
        self.predict_match(home_team, away_team, hour, day, matches_rolling)

        # Generate betting tips
        self.generate_tips(home_team, away_team, matches_rolling)

    
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