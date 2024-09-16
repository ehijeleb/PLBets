from flask import Flask, request, jsonify, render_template
from plbets.predictor import MatchPredictor

app = Flask(__name__)

# Initialize MatchPredictor object
predictor = MatchPredictor()

# Route to serve the homepage
@app.route('/')
def home():
    return render_template('index.html')  # Ensure index.html is in the 'templates' folder

# Load data and train the model once when the first request comes in
@app.route('/predict', methods=['POST'])
def predict_match():
    # Only load the data and train the model if it hasn't been loaded yet
    if not hasattr(predictor, 'matches_rolling'):
        matches = predictor.data_loader.load_data()
        cols = ["gf", "ga", "sh", "sot", "dist", "fk", "pk", "pkatt"]
        new_cols = [f"{c}_rolling" for c in cols]

        matches_rolling = matches.groupby("team").apply(lambda x: predictor.rolling_averages(x, cols, new_cols))
        matches_rolling = matches_rolling.droplevel('team')
        matches_rolling.index = range(matches_rolling.shape[0])

        predictor.matches_rolling = matches_rolling

        # Split the data into training and test sets
        train_data = matches_rolling[matches_rolling["date"] < '2022-06-01']
        test_data = matches_rolling[matches_rolling["date"] > '2023-06-01']

        # Define predictors and target
        target = "target"

        # Train the model
        predictor.model.train(train_data, predictor.predictors, target)

        # Evaluate the model using the test data
        preds, precision = predictor.model.evaluate(test_data, predictor.predictors, target, average="macro")
        print(f"Model Precision: {precision:.2f}")

    # Now proceed with the prediction
    data = request.json
    home_team = data.get('home_team')
    away_team = data.get('away_team')
    hour = data.get('hour')
    day = data.get('day')

    if not home_team or not away_team or hour is None or day is None:
        return jsonify({"error": "Missing required parameters"}), 400

    result = predictor.predict_match(home_team, away_team, hour, day, predictor.matches_rolling)
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

    # Return the tips as a JSON response
    return jsonify(tips)



if __name__ == "__main__":
    app.run(debug=True)
