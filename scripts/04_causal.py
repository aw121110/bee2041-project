import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from econml.dml import LinearDML
import plotly.graph_objects as go
import plotly.io as pio
import warnings
warnings.filterwarnings("ignore")

pio.templates.default = "plotly_white"

df = pd.read_csv("data/clean/stats_clean.csv")

name_overrides = {
    "Joao Pedro": "Joao Pedro", "João Pedro": "Joao Pedro",
    "Erling Haaland": "Haaland", "Mohamed Salah": "Salah",
    "Cole Palmer": "Palmer", "Alexander Isak": "Isak",
    "Ollie Watkins": "Watkins", "Chris Wood": "C. Wood",
    "Bryan Mbeumo": "Mbeumo", "Yoane Wissa": "Wissa",
    "Nicolas Jackson": "N. Jackson", "Danny Welbeck": "Welbeck",
    "Richarlison": "Richarlison", "Son Heung-min": "Son",
    "Igor Thiago": "Igor Thiago", "Anthony Gordon": "Gordon",
    "Bukayo Saka": "Saka", "Viktor Gyökeres": "Gyökeres",
    "Hugo Ekitiké": "Ekitiké", "Cody Gakpo": "Gakpo",
    "Phil Foden": "Foden", "Jean-Philippe Mateta": "Mateta",
    "Dominic Calvert-Lewin": "DCL", "Antoine Semenyo": "Semenyo",
    "Rodrigo Muniz": "Muniz", "Matheus Cunha": "Cunha",
    "Dominic Solanke": "Solanke", "Raúl Jiménez": "Jiménez",
    "Callum Wilson": "C. Wilson", "Taiwo Awoniyi": "Awoniyi",
    "Jamie Vardy": "Vardy", "Lyle Foster": "Foster",
    "Harvey Barnes": "Barnes", "Dominik Szoboszlai": "Szoboszlai",
}

def get_display_name(full_name):
    if full_name in name_overrides:
        return name_overrides[full_name]
    parts = full_name.strip().split()
    return parts[-1] if parts else full_name

# ── Filter PL attackers ────────────────────────────────────────────────────────
pl = df[
    (df["competition"] == "Premier League") &
    (df["goals"] >= 5) &
    (df["shots"] > 0) &
    (df["position"].isin(["Forward", "Midfielder"]))
].copy().reset_index(drop=True)

print(f"PL attackers with 5+ goals: {len(pl)}")

pl["is_forward"] = (pl["position"] == "Forward").astype(int)

features = ["mins_played", "shots", "xg_per_shot", "is_forward"]
pl_model = pl[features + ["goals", "shot_conv", "name", "team"]].dropna().copy()

print(f"Players after dropna: {len(pl_model)}")
print(f"Shot conversion range: {pl_model['shot_conv'].min():.1f}% – {pl_model['shot_conv'].max():.1f}%")
print(f"Goals range: {pl_model['goals'].min()} – {pl_model['goals'].max()}")

Y = pl_model["goals"].values.astype(float)
T = pl_model["shot_conv"].values.astype(float)
W = pl_model[features].values.astype(float)

scaler = StandardScaler()
W_scaled = scaler.fit_transform(W)

# ── Double ML (LinearDML with RF nuisance models) ─────────────────────────────
print("\nFitting Double ML model...")
np.random.seed(42)
dml = LinearDML(
    model_y=RandomForestRegressor(n_estimators=200, max_depth=5, random_state=42),
    model_t=RandomForestRegressor(n_estimators=200, max_depth=5, random_state=42),
    random_state=42,
    cv=5,
)
dml.fit(Y, T, X=None, W=W_scaled)

ate = float(dml.ate())
ate_interval = dml.ate_interval(alpha=0.05)
lb = float(ate_interval[0])
ub = float(ate_interval[1])

print(f"\n📊 Double ML Results")
print(f"ATE of Shot Conversion on Goals: {ate:.4f}")
print(f"95% CI: [{lb:.4f}, {ub:.4f}]")
print(f"Interpretation: A 1pp increase in shot conversion causes ~{ate:.3f} additional goals,")
print(f"holding minutes, shots, chance quality and position constant.")
print(f"\nMedian shot conversion: {np.median(T):.2f}%")

# ── Counterfactual analysis ────────────────────────────────────────────────────
median_conv = float(np.median(T))
pl_model["actual_goals"] = Y
pl_model["counterfactual_goals"] = (Y + ate * (median_conv - T)).round(1)
pl_model["causal_advantage"] = (ate * (pl_model["shot_conv"] - median_conv)).round(2)
pl_model["display_name"] = pl_model["name"].apply(get_display_name)
pl_model["Club"] = pl_model["team"]
pl_model["Shot Conversion (%)"] = pl_model["shot_conv"].round(1)
pl_model["Actual Goals"] = pl_model["actual_goals"].astype(int)
pl_model["Goals At Median Conversion"] = pl_model["counterfactual_goals"]
pl_model["Causal Finishing Advantage"] = pl_model["causal_advantage"]

pl_model.to_csv("data/clean/causal_results.csv", index=False)

print("\nTop 10 players by causal finishing advantage:")
print(pl_model.nlargest(10, "causal_advantage")[
    ["name", "team", "shot_conv", "actual_goals", "counterfactual_goals", "causal_advantage"]
].to_string(index=False))

# ── PLOT 11: Counterfactual goals chart — Plotly HTML ─────────────────────────
top_n = pl_model.nlargest(15, "actual_goals").sort_values("causal_advantage", ascending=True).reset_index(drop=True)

fig11 = go.Figure()

fig11.add_trace(go.Bar(
    y=top_n["display_name"],
    x=top_n["Goals At Median Conversion"],
    name=f"Goals At Median Conversion ({median_conv:.1f}%)",
    orientation="h",
    marker=dict(color="#d0dce8", line=dict(width=0)),
    customdata=top_n[[
        "Club", "Actual Goals", "Goals At Median Conversion",
        "Shot Conversion (%)", "Causal Finishing Advantage"
    ]].values,
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "Club: %{customdata[0]}<br>"
        "Actual Goals: %{customdata[1]}<br>"
        "Goals At Median Conversion: %{customdata[2]}<br>"
        "Shot Conversion (%): %{customdata[3]}<br>"
        "Causal Finishing Advantage: %{customdata[4]} goals<br>"
        "<extra></extra>"
    ),
    hovertext=top_n["name"],
))

fig11.add_trace(go.Bar(
    y=top_n["display_name"],
    x=top_n["Actual Goals"],
    name="Actual Goals",
    orientation="h",
    marker=dict(
        color=[
            "#27ae60" if v > 0.1 else "#e94560" if v < -0.1 else "#888888"
            for v in top_n["causal_advantage"]
        ],
        opacity=0.85,
        line=dict(width=0),
    ),
    customdata=top_n[[
        "Club", "Actual Goals", "Goals At Median Conversion",
        "Shot Conversion (%)", "Causal Finishing Advantage"
    ]].values,
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "Club: %{customdata[0]}<br>"
        "Actual Goals: %{customdata[1]}<br>"
        "Goals At Median Conversion: %{customdata[2]}<br>"
        "Shot Conversion (%): %{customdata[3]}<br>"
        "Causal Finishing Advantage: %{customdata[4]} goals<br>"
        "<extra></extra>"
    ),
    hovertext=top_n["name"],
))

fig11.update_layout(
    barmode="overlay",
    height=600,
    font_family="Inter, sans-serif",
    title="Causal Finishing Advantage — Actual vs Counterfactual Goals (Double ML)",
    title_font_size=15,
    plot_bgcolor="white",
    paper_bgcolor="#f4f6f9",
    hoverlabel=dict(bgcolor="white", font_size=13),
    margin=dict(l=20, r=60, t=60, b=80),
    xaxis=dict(
        title="Goals",
        showgrid=True, gridcolor="#eeeeee",
        title_font_size=13, tickfont_size=11,
    ),
    yaxis=dict(tickfont_size=11),
    legend=dict(
        orientation="h",
        yanchor="bottom", y=-0.18,
        xanchor="center", x=0.5,
        font_size=11,
    ),
)
fig11.write_html("output/figures/11_causal_counterfactual.html", include_plotlyjs="cdn", full_html=True)
print("✅ Plot 11 saved (HTML)")
