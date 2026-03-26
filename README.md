# Beyond Goals: Who Are the Premier League's Most Clinical Attackers?

BEE2041 Empirical Project — Adam Wilkes

## Live Blog
[View the blog here](https://aw121110.github.io/bee2041-project/)

## Setup

Install dependencies:

pip install -r requirements.txt


Set your Opta API token:

export OPTA_TOKEN=your_token_here


## Replication

Run scripts in order:

python scripts/01_scrape.py
python scripts/02_clean.py
python scripts/03_analysis.py
python scripts/04_causal.py


Cleaned data is in `data/clean/`. Output figures are saved to `output/figures/`.

## Data
Scraped from Opta Analyst (theanalyst.com), 2025/26 season to March 2026.
582 PL players scraped, filtered to 54 qualifying attackers (5+ goals).
