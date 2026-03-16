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

# Parse both competitions
df_pl  = parse_stats("data/raw/opta_pl_stats.json", "Premier League")
df_ucl = parse_stats("data/raw/opta_ucl_stats.json", "Champions League")

# Combine into one DataFrame
df = pd.concat([df_pl, df_ucl], ignore_index=True)

# Basic cleaning
df["mins_played"]     = pd.to_numeric(df["mins_played"], errors="coerce")
df["goals"]           = pd.to_numeric(df["goals"],       errors="coerce")
df["xg"]              = pd.to_numeric(df["xg"],          errors="coerce")
df["shots"]           = pd.to_numeric(df["shots"],       errors="coerce")
df["shot_conv"]       = pd.to_numeric(df["shot_conv"],   errors="coerce")
df["xg_per_shot"]     = pd.to_numeric(df["xg_per_shot"], errors="coerce")
df["goals_vs_xg"]     = pd.to_numeric(df["goals_vs_xg"], errors="coerce")

# Add mins per goal (only for players with at least 1 goal)
df["mins_per_goal"] = df["mins_played"] / df["goals"].replace(0, float("nan"))

# Save clean data
df.to_csv("data/clean/stats_clean.csv", index=False)

print(f"✅ Combined dataset: {len(df)} players")
print(f"   PL players:  {len(df_pl)}")
print(f"   UCL players: {len(df_ucl)}")
print("\nFirst 5 rows:")
print(df[["name", "team", "competition", "goals", "xg", "shot_conv", "mins_per_goal"]].head())
