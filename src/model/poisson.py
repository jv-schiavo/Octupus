import numpy as np
from scipy.stats import poisson

lambda_home = 1.5
home_probabilities = {}

lambda_away = 1.1
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

print(max_home_goals)
print(max_away_goals)
print(f"Matrix Coverage: {matrix_coverage:.2%}")

for goals in range(max_home_goals + 1):
    probability = poisson.pmf(goals, lambda_home)
    home_probabilities[goals] = probability 

for goals in range(max_away_goals + 1):
    probability = poisson.pmf(goals, lambda_away)
    away_probabilities[goals] = probability

score_probabilities = {}

for home_goals in range(max_home_goals + 1):
    for away_goals in range(max_away_goals + 1):
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


