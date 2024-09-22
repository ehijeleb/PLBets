from flask import Flask, request, jsonify
from plbets.predictor import MatchPredictor
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app) 

# Initialize MatchPredictor object
predictor = MatchPredictor()



@app.route('/train_model', methods=['POST'])
def train_model():
    # Call the train_model method to train the model
    predictor.train_model()
    return jsonify({"message": "Model trained successfully"}), 200

@app.route('/predict_match', methods=['POST'])
def predict_match():
    data = request.json
    home_team = data.get('home_team')
    away_team = data.get('away_team')
    hour = data.get('hour')
    day = data.get('day')

    if not home_team or not away_team or hour is None or day is None:
        return jsonify({"error": "Missing required parameters"}), 400

    # Ensure the model is trained before making predictions
    predictor.train_model()

    # Call the prediction function
    result = predictor.predict_match(home_team, away_team, hour, day)
    return jsonify(result)




# Route to generate betting tips
@app.route('/generate_tips', methods=['POST'])
def generate_tips():
    # Load the data if it hasn't been loaded yet
    if not hasattr(predictor, 'matches_rolling'):
        matches = predictor.data_loader.load_data()

        # Define columns for rolling averages
        cols = ["gf", "ga", "sh", "sot", "dist", "fk", "pk", "pkatt"]
        new_cols = [f"{c}_rolling" for c in cols]

        # Apply rolling averages to the data
        matches_rolling = matches.groupby("team").apply(lambda x: predictor.rolling_averages(x, cols, new_cols))
        matches_rolling = matches_rolling.droplevel('team')  # Drop the extra index level added by groupby
        matches_rolling.index = range(matches_rolling.shape[0])  # Reset index

        predictor.matches_rolling = matches_rolling

    # Retrieve data from the request
    data = request.json
    home_team = data.get('home_team')
    away_team = data.get('away_team')

    if not home_team or not away_team:
        return jsonify({"error": "Missing required parameters"}), 400

    # Call the generate_tips method on the predictor instance
    tips = predictor.generate_tips(home_team, away_team)

    # Get the referee from the latest match between the two teams
    latest_match = predictor.matches_rolling[
        ((predictor.matches_rolling["team"] == home_team) & 
         (predictor.matches_rolling["opponent"] == away_team)) |
        ((predictor.matches_rolling["team"] == away_team) & 
         (predictor.matches_rolling["opponent"] == home_team))
    ].iloc[-1]


    # Return the tips as a JSON response
    return jsonify(tips)



@app.route('/get_referees', methods=['GET'])
def get_referees():
    # Load the referee dataset
    referee_data = pd.read_csv('data/referee.csv')

    # Extract referee details (name and stats)
    referees = referee_data.to_dict(orient="records")

    # Return the list of referees with stats as JSON
    return jsonify({"referees": referees})






if __name__ == "__main__":
    app.run(debug=True)
