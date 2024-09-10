from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score

class BettingModel:
    def __init__(self, n_estimators=100, min_samples_split=10, random_state=1):
        self.model = RandomForestClassifier(n_estimators=n_estimators, min_samples_split=min_samples_split, random_state=random_state)
    
    def train(self, train_data, predictors, target):
        self.model.fit(train_data[predictors], train_data[target])
    
    def evaluate(self, test_data, predictors, target):
        preds = self.model.predict(test_data[predictors])
        precision = precision_score(test_data[target], preds)
        return preds, precision
