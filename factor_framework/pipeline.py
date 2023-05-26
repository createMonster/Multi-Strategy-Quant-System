from scipy.stats import rankdata

class Factor():

    def __init__(self, formula, data):
        self.formula = formula
        self.data = data
        self.weights = None
        
    def calculate_weight(self):
        pass

    def neutralize(self):
        pass

    def rank(self, vector):
        """Take in a vector values, return ranks in [0, 1]"""
        ranks = rankdata(vector)
        normalized_ranks = (ranks - 1) / (len(vector) - 1)

        return normalized_ranks


class Backtest():
    
    def __init__(self, historical_data, weights, start_dt, end_dt) -> None:
        self.historical_data = historical_data
        self.weights = weights
        self.start_dt = start_dt
        self.end_dt = end_dt

    def calculate_metrics(self):
        pass

    def plot(self):
        pass

    