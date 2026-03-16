import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings("ignore")

# ── Load data ──────────────────────────────────────────────────────────────────
df = pd.read_csv("data/clean/stats_clean.csv")

# ── Filter: PL attackers/midfielders with 5+ goals ────────────────────────────
pl = df[
    (df["competition"] == "Premier League") &
    (df["goals"] >= 5) &
    (df["position"].isin(["Forward", "Attacking Midfielder", "Midfielder", "Winger"]))
].copy().reset_index(drop=True)

# Also filter for players with shots > 0 for conversion metrics
pl_shots = pl[pl["shots"] > 0].copy()

print(f"PL attackers with 5+ goals: {len(pl)}")

# ── Colour map by team ─────────────────────────────────────────────────────────
teams = pl["team"].unique()
colours = plt.cm.tab20.colors
team_colour = {team: colours[i % 20] for i, team in enumerate(teams)}

# ══════════════════════════════════════════════════════════════════════════════
# PLOT 1: Top 15 PL scorers — horizontal bar chart
# ══════════════════════════════════════════════════════════════════════════════
top15 = pl.nlargest(15, "goals").sort_values("goals")

fig, ax = plt.subplots(figsize=(10, 7))
bars = ax.barh(top15["name"], top15["goals"],
               color=[team_colour[t] for t in top15["team"]])
ax.set_xlabel("Goals", fontsize=12)
ax.set_title("Top 15 Premier League Scorers 2024/25", fontsize=14, fontweight="bold")
ax.spines[["top", "right"]].set_visible(False)

# Add value labels
for bar, val in zip(bars, top15["goals"]):
    ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
            str(int(val)), va="center", fontsize=10)

# Legend for teams
handles = [mpatches.Patch(color=team_colour[t], label=t) for t in top15["team"].unique()]
ax.legend(handles=handles, fontsize=8, loc="lower right")
plt.tight_layout()
plt.savefig("output/figures/01_top15_scorers.png", dpi=150)
plt.close()
print("✅ Plot 1 saved")

# ══════════════════════════════════════════════════════════════════════════════
# PLOT 2: Goals vs xG scatter — who over/underperforms?
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 8))

for _, row in pl.iterrows():
    ax.scatter(row["xg"], row["goals"],
               color=team_colour[row["team"]], s=80, alpha=0.8, zorder=3)
    if row["goals"] >= 10 or abs(row["goals_vs_xg"]) >= 4:
        ax.annotate(row["last_name"], (row["xg"], row["goals"]),
                    textcoords="offset points", xytext=(6, 4), fontsize=8)

# Diagonal line = perfectly on xG
max_val = max(pl["xg"].max(), pl["goals"].max()) + 2
ax.plot([0, max_val], [0, max_val], "k--", linewidth=1, alpha=0.5, label="Goals = xG")
ax.set_xlabel("Expected Goals (xG)", fontsize=12)
ax.set_ylabel("Actual Goals", fontsize=12)
ax.set_title("Goals vs Expected Goals — PL Attackers 2024/25\nAbove the line = outperforming xG", 
             fontsize=13, fontweight="bold")
ax.spines[["top", "right"]].set_visible(False)
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig("output/figures/02_goals_vs_xg.png", dpi=150)
plt.close()
print("✅ Plot 2 saved")

# ══════════════════════════════════════════════════════════════════════════════
# PLOT 3: Shot conversion % — top 15 most clinical
# ══════════════════════════════════════════════════════════════════════════════
top_conv = pl_shots.nlargest(15, "shot_conv").sort_values("shot_conv")

fig, ax = plt.subplots(figsize=(10, 7))
bars = ax.barh(top_conv["name"], top_conv["shot_conv"],
               color=[team_colour[t] for t in top_conv["team"]])
ax.set_xlabel("Shot Conversion %", fontsize=12)
ax.set_title("Most Clinical Finishers — Shot Conversion % 2024/25\n(PL players with 5+ goals)",
             fontsize=13, fontweight="bold")
ax.spines[["top", "right"]].set_visible(False)
for bar, val in zip(bars, top_conv["shot_conv"]):
    ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
            f"{val:.1f}%", va="center", fontsize=10)
plt.tight_layout()
plt.savefig("output/figures/03_shot_conversion.png", dpi=150)
plt.close()
print("✅ Plot 3 saved")

# ══════════════════════════════════════════════════════════════════════════════
# PLOT 4: xG per shot vs shot conversion — quality vs efficiency
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 8))

for _, row in pl_shots.iterrows():
    ax.scatter(row["xg_per_shot"], row["shot_conv"],
               color=team_colour[row["team"]], s=80, alpha=0.8, zorder=3)
    if row["goals"] >= 10 or row["shot_conv"] >= 25 or row["xg_per_shot"] >= 0.18:
        ax.annotate(row["last_name"], (row["xg_per_shot"], row["shot_conv"]),
                    textcoords="offset points", xytext=(6, 4), fontsize=8)

ax.axvline(pl_shots["xg_per_shot"].median(), color="gray", linestyle="--", alpha=0.5)
ax.axhline(pl_shots["shot_conv"].median(), color="gray", linestyle="--", alpha=0.5)
ax.set_xlabel("xG per Shot (shot quality)", fontsize=12)
ax.set_ylabel("Shot Conversion %", fontsize=12)
ax.set_title("Shot Quality vs Shot Conversion — PL Attackers 2024/25\nDashed lines = median",
             fontsize=13, fontweight="bold")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("output/figures/04_xg_per_shot_vs_conversion.png", dpi=150)
plt.close()
print("✅ Plot 4 saved")

# ══════════════════════════════════════════════════════════════════════════════
# PLOT 5: Minutes per goal — most efficient scorers
# ══════════════════════════════════════════════════════════════════════════════
pl_mpg = pl[pl["mins_per_goal"].notna()].nsmallest(15, "mins_per_goal").sort_values("mins_per_goal", ascending=False)

fig, ax = plt.subplots(figsize=(10, 7))
bars = ax.barh(pl_mpg["name"], pl_mpg["mins_per_goal"],
               color=[team_colour[t] for t in pl_mpg["team"]])
ax.set_xlabel("Minutes per Goal", fontsize=12)
ax.set_title("Most Efficient Scorers — Minutes per Goal 2024/25\n(Lower = more efficient)",
             fontsize=13, fontweight="bold")
ax.spines[["top", "right"]].set_visible(False)
for bar, val in zip(bars, pl_mpg["mins_per_goal"]):
    ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
            f"{val:.0f}", va="center", fontsize=10)
plt.tight_layout()
plt.savefig("output/figures/05_mins_per_goal.png", dpi=150)
plt.close()
print("✅ Plot 5 saved")

# ══════════════════════════════════════════════════════════════════════════════
# PLOT 6: PCA Composite Clinicality Score (Unit 5)
# ══════════════════════════════════════════════════════════════════════════════
features = ["goals", "xg", "shot_conv", "xg_per_shot", "goals_vs_xg"]
pl_pca = pl_shots[features + ["name", "team"]].dropna()

scaler = StandardScaler()
X_scaled = scaler.fit_transform(pl_pca[features])

pca = PCA(n_components=1)
pl_pca = pl_pca.copy()
pl_pca["clinicality_score"] = pca.fit_transform(X_scaled)

# Normalise to 0–100
min_s = pl_pca["clinicality_score"].min()
max_s = pl_pca["clinicality_score"].max()
pl_pca["clinicality_score"] = ((pl_pca["clinicality_score"] - min_s) / (max_s - min_s)) * 100

top_clinical = pl_pca.nlargest(15, "clinicality_score").sort_values("clinicality_score")

fig, ax = plt.subplots(figsize=(10, 7))
bars = ax.barh(top_clinical["name"], top_clinical["clinicality_score"],
               color=[team_colour[t] for t in top_clinical["team"]])
ax.set_xlabel("Clinicality Score (0–100)", fontsize=12)
ax.set_title("Who Are the Premier League's Most Clinical Attackers?\nComposite Score: Goals + xG + Conversion + Shot Quality (PCA)",
             fontsize=12, fontweight="bold")
ax.spines[["top", "right"]].set_visible(False)
for bar, val in zip(bars, top_clinical["clinicality_score"]):
    ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
            f"{val:.1f}", va="center", fontsize=10)
plt.tight_layout()
plt.savefig("output/figures/06_clinicality_score.png", dpi=150)
plt.close()
print("✅ Plot 6 saved")

print("\n🏆 Top 10 most clinical PL attackers:")
print(pl_pca.nlargest(10, "clinicality_score")[["name", "team", "goals", "xg", "shot_conv", "clinicality_score"]].to_string(index=False))
