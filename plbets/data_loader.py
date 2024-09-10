import pandas as pd

class DataLoader:
    def __init__(self, filepath):
        self.filepath = filepath
    
    def load_data(self):
        # Load and preprocess your matches data
        matches = pd.read_csv(self.filepath, index_col=0)
        matches["date"] = pd.to_datetime(matches["date"])
        matches["h/a"] = matches["venue"].astype("category").cat.codes
        matches["opp"] = matches["opponent"].astype("category").cat.codes
        matches["hour"] = matches["time"].str.replace(":.+", "", regex=True).astype("int")
        matches["day"] = matches["date"].dt.dayofweek
        matches["target"] = (matches["result"] == "W").astype("int")
        
        return matches
