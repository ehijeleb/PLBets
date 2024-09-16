from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score

class BettingModel:

    #Constructor method to initialise the RandomForestClassifiers with specified parameters
    def __init__(self, n_estimators=100, min_samples_split=10, random_state=1):
        #Initialising the RandomForest model with the provided hyperparameters
        self.model = RandomForestClassifier(n_estimators=n_estimators, min_samples_split=min_samples_split, random_state=random_state)

    #Method to train the RandomForest model on the provided data
    def train(self, train_data, predictors, target):
        #Fit the model on the training data using the specified predictors and target variable 
        self.model.fit(train_data[predictors], train_data[target])
 
    #Method to evaluate tge nidek i btge test data
    def evaluate(self, test_data, predictors, target):
        #Use the model to predict the target variable based on the test data
        preds = self.model.predict(test_data[predictors])

        #calcualate the precision score, comparing predictions with the true target values
        precision = precision_score(test_data[target], preds, average=average)

        #Return both the predictions and the precision score
        return preds, precision