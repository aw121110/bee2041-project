import json
import pandas as pd


def parse_stats(filepath, competition):
    with open(filepath, "r") as f:
        data = json.load(f)
    
    players = []
    for player in data["player"]["attack"]["overall"]:
        p = {
            "competition":     competition,
            "player_id":       player.get("player_id"),
            "name":            player.get("player"),
            "first_name":      player.get("first_name"),
            "last_name":       player.get("last_name"),
            "team":            player.get("contestantName"),
            "position":        player.get("squad_position"),
            "age":             player.get("age"),
            "apps":            player.get("apps"),
            "mins_played":     player.get("mins_played"),
            "goals":           player.get("goals"),
            "xg":              player.get("xg"),
            "goals_vs_xg":     player.get("goals_vs_xg"),
            "shots":           player.get("shots"),
            "shots_on_target": player.get("shots_on_target"),
            "shot_conv":       player.get("shot_conv"),
            "xg_per_shot":     player.get("xg_per_shot"),
        }
        players.append(p)
    return pd.DataFrame(players)


# Parse PL only
df = parse_stats("data/raw/opta_pl_stats.json", "Premier League")

# Convert numeric columns
numeric_cols = ["mins_played", "goals", "xg", "shots", "shot_conv", "xg_per_shot", "goals_vs_xg"]
df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

# Add mins per goal
df["mins_per_goal"] = df["mins_played"] / df["goals"].replace(0, float("nan"))

# Save
df.to_csv("data/clean/stats_clean.csv", index=False)

print(f"✅ PL dataset: {len(df)} players")
print("\nFirst 5 rows:")
print(df[["name", "team", "goals", "xg", "shot_conv", "mins_per_goal"]].head())
