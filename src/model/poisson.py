import numpy as np
from scipy.stats import poisson


def predict_match(lambda_home, lambda_away):
    
    home_probabilities = {}
    away_probabilities = {}

    target_coverage = 0.9999
    max_home_goals = 0
    max_away_goals = 0
    matrix_coverage = 0.0

    while target_coverage > matrix_coverage:
        home_coverage = poisson.cdf(max_home_goals, lambda_home)
        away_coverage = poisson.cdf(max_away_goals, lambda_away)
        matrix_coverage = home_coverage * away_coverage
        
        if matrix_coverage < target_coverage:
            max_home_goals += 1
            max_away_goals += 1

    for goals in range(max_home_goals + 1):
        probability = poisson.pmf(goals, lambda_home)
        home_probabilities[goals] = probability 

    for goals in range(max_away_goals + 1):
        probability = poisson.pmf(goals, lambda_away)
        away_probabilities[goals] = probability

    scores_probabilities = {}

    for home_goals in range(max_home_goals + 1):
        for away_goals in range(max_away_goals + 1):
            scores_probabilities[(home_goals, away_goals)] = home_probabilities[home_goals] * away_probabilities[away_goals]

    home_win = 0
    away_win = 0
    draw = 0 

    for (home_goals, away_goals), probability in scores_probabilities.items():
        if home_goals > away_goals:
            home_win += probability
        elif home_goals < away_goals:
            away_win += probability
        else:
            draw += probability

    prediction = {
        "home_win": home_win,
        "draw": draw,
        "away_win": away_win,
        "scores_probabilities": scores_probabilities,
        "matrix_coverage": matrix_coverage
    }

    return prediction



