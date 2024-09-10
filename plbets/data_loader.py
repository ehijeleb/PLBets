import pandas as pd

class DataLoader:
    def __init__(self, filepath):
        self.filepath = filepath
    
    def load_data(self):
        # Convert necessary columns to appropriate formats
        matches = pd.read_csv(self.filepath, index_col=0) 
        matches["date"] = pd.to_datetime(matches["date"]) 
        matches["h/a"] = matches["venue"].astype("category").cat.codes #Home(1) or Away(0)
        matches["opp"] = matches["opponent"].astype("category").cat.codes #Opponent as numbers
        matches["hour"] = matches["time"].str.replace(":.+", "", regex=True).astype("int") #Game hour
        matches["day"] = matches["date"].dt.dayofweek # Day of the week (0=Monday, 6=sunday)
        matches["target"] = (matches["result"] == "W").astype("int") #Create the target column for prediction (Win=1, Not Win=0)
        
        return matches
