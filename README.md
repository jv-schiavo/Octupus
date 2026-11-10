# Football Match Prediction | Poisson Model

A data science project to estimate football match outcomes using historical results, team attacking and defensive strengths, and the Poisson distribution.

The project starts with **Brazilian Série A 2025** as a controlled environment for developing and validating the methodology. The longer-term goal is to forecast cross-league matches, including **Boca Juniors vs Atlético-MG**, while accounting for differences between competitions.

> **Status:** Work in progress. Predictions are probabilistic estimates, not guaranteed outcomes. Cross-league forecasts are a future milestone, not a validated capability of the current baseline.

## Objectives

- Build a reproducible pipeline from raw match results to model-ready data.
- Estimate expected goals (λ) for each team before kickoff.
- Calculate probabilities for exact scores and home win / draw / away win.
- Evaluate predictions against historical results without using future information.
- Compare the transparent baseline with more advanced statistical models.
- Eventually support neutral venues and teams from different leagues.

## Current approach

### 1. Data pipeline

The project follows a **Medallion architecture**:

| Layer | Purpose |
| --- | --- |
| **Bronze** | Preserve original source data unchanged. |
| **Silver** | Parse, standardise and validate fixtures, teams, dates and scores. |
| **Gold** | Build historical team and league statistics for modelling. |

The initial dataset is the **2025 Brazilian Série A season** (380 matches, 20 teams). The pipeline validates match counts, team coverage and essential fields before producing processed data.

### 2. Expected goals (λ)

The baseline estimates scoring rates from league averages and team strengths:

\[
\lambda_{home}=\mu_{home}\times A_{home}\times D_{away}
\]

\[
\lambda_{away}=\mu_{away}\times A_{away}\times D_{home}
\]

Where:

- `μ_home` / `μ_away`: league-average home / away goals per match.
- `A_home`: home team's average home goals scored divided by league-average home goals.
- `D_away`: away team's average away goals conceded divided by league-average home goals.
- `A_away`: away team's average away goals scored divided by league-average away goals.
- `D_home`: home team's average home goals conceded divided by league-average away goals.

A strength greater than 1 represents above-average attacking output or defensive vulnerability, depending on the factor.

**Important:** All averages and strengths for a historical prediction must use matches **strictly before** the prediction date. The baseline is intended for within-league comparisons; its parameters should not be transferred directly between leagues.

### 3. Score probabilities

For goals `k` and expected goals `λ`, the Poisson probability mass function is:

\[
P(X=k)=\frac{e^{-\lambda}\lambda^k}{k!}
\]

Assuming the two teams' goal counts are independent:

\[
P(H=i,A=j)=P(H=i)\times P(A=j)
\]

Summing the score matrix gives:

- **Home win:** sum of cells where `i > j`.
- **Draw:** sum of cells where `i = j`.
- **Away win:** sum of cells where `i < j`.

The goal-range cutoff should be selected so that the retained probability mass meets the desired coverage (target: **≥ 0.9999**). Home and away cutoffs may differ. Report or account for any omitted tail probability.

## Technology

- **Python** — core modelling and pipeline logic
- **pandas / NumPy** — data cleaning, transformations and calculations
- **SciPy** — Poisson probability functions and statistical methods (as needed)
- **Jupyter Notebook** — exploration and model development
- **Git / GitHub** — version control and documentation

Future options: `scikit-learn` or `statsmodels` for Poisson regression; SQL and Power BI or Streamlit for reporting.

## Data and repository organisation

A recommended layout (adjust to match the repository as implementation evolves):

```text
.
├── README.md
├── data/
│   ├── raw/              # Bronze: original source files
│   ├── processed/        # Silver: validated fixtures
│   └── gold/             # Gold: model-ready features
├── notebooks/            # Exploration and experiments
├── src/                  # Reusable parsing and prediction functions
├── tests/                # Data and model tests
└── reports/              # Backtest metrics and figures
```

Initial source: `brazil_serie_a_2025.txt`. Processed match data is exported as CSV under `data/processed/`.

## How to reproduce

The project is being developed incrementally, so a stable command-line interface has not yet been finalised.

1. Clone the repository and create a Python virtual environment.
2. Install the dependencies used by the notebooks/scripts.
3. Place the permitted raw source file in `data/raw/`.
4. Run parsing and validation, confirming **380 fixtures and 20 teams** for Série A 2025.
5. Generate model-ready features using only games before each target match.
6. Calculate each team's λ, generate the score-probability matrix, and aggregate outcomes.
7. Run historical evaluation and save the results.

> Add exact setup commands and entry points once the codebase is consolidated. Avoid committing API keys or restricted third-party datasets.

## Validation and evaluation

**Data quality checks**

- Expected season size and number of distinct teams.
- Valid fixture dates, team identifiers and non-negative integer scores.
- No duplicate fixtures or missing required fields.
- No match used to generate its own pre-match features.
- Consistent treatment of home, away and neutral fixtures.

**Model evaluation (planned)**

- Chronological backtesting, not random splitting of matches.
- Compare against simple baseline probabilities.
- Brier score and multiclass log loss for 1X2 predictions.
- Calibration analysis: do events predicted at 60% occur about 60% of the time?
- Exact-score performance and sensitivity to the goal-range cutoff.

The model should only be described as better when it improves out-of-sample results—not merely because its formulas are more complex.

## Known limitations and edge cases

- **Cross-league differences:** Brazilian and Argentine goal rates are not directly comparable; continental fixtures and an appropriate shared-strength framework are required.
- **Small samples:** Early-season estimates can be unstable; smoothing or regularisation may be needed.
- **Zero or near-zero averages:** Guard against division by zero and extreme strength ratios.
- **Independent goals:** Basic Poisson may misrepresent low-scoring draws; Dixon–Coles is a possible improvement.
- **Neutral venues:** A nominal home team does not necessarily have home advantage.
- **Knockout rules:** Predictions for 90 minutes are different from probabilities of advancing or winning a trophy after extra time and penalties.
- **Squad changes and recent form:** A season-wide average may not reflect current team strength.
- **Data leakage:** Features must be calculated as of the prediction cutoff, including for historical backtests.
- **Truncated score matrix:** Ensure sufficient coverage or explicitly handle the remaining tail mass.

## Roadmap

- [x] Define the first use case and Poisson baseline.
- [x] Parse and validate the 2025 Série A dataset (380 matches, 20 teams).
- [x] Implement initial attack/defence strength and λ calculations.
- [x] Build scoreline probabilities and match-outcome aggregation.
- [ ] Refactor the pipeline into reusable, tested modules.
- [ ] Add chronological backtesting and probability calibration reports.
- [ ] Compare the baseline with Poisson regression estimated by maximum likelihood.
- [ ] Evaluate Dixon–Coles and time-weighted team strengths.
- [ ] Expand data coverage to Argentine football and CONMEBOL competitions.
- [ ] Develop a defensible cross-league comparison method.
- [ ] Add a dashboard and automated data refresh.

## Learning goals

This project is also an exercise in building statistical models **from first principles**: understanding the mathematics, implementing the calculations, testing assumptions and interpreting results before relying on higher-level machine learning libraries.

## Disclaimer

For educational and analytical purposes only. Results are uncertain and should not be treated as guaranteed forecasts or betting advice.
