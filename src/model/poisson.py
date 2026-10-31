import numpy as np
from scipy.stats import poisson

lambda_home = 1.5
home_probabilities = {}

lambda_away = 1.1
away_probabilities = {}

for goals in range(6):
    probability = poisson.pmf(goals, lambda_home)
    home_probabilities[goals] = probability 

for goals in range(6):
    probability = poisson.pmf(goals, lambda_away)
    away_probabilities[goals] = probability

score_probabilities = {}

for home_goals in range(6):
    for away_goals in range(6):
        score_probabilities[(home_goals, away_goals)] = home_probabilities[home_goals] * away_probabilities[away_goals]
        
#print(f"Score Probability: {score_probabilities[(2,1)]:.2%}")

home_win_probability = 0
away_win_probability = 0
draw_probability = 0 

for (home_goals, away_goals), probability in score_probabilities.items():
    if home_goals > away_goals:
        home_win_probability += probability
    elif home_goals < away_goals:
        away_win_probability += probability
    else:
        draw_probability += probability

#print(f"Home Win Probability: {home_win_probability:.2%}")
      
#print(f"Away Win Probability: {away_win_probability:.2%}")

#print(f"Draw Probability: {draw_probability:.2%}")

total_coverage = (home_win_probability + away_win_probability + draw_probability)

print(f"Total Coverage: {total_coverage:.2%}")