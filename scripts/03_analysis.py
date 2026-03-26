import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import plotly.graph_objects as go
import plotly.io as pio
import unicodedata
import warnings
warnings.filterwarnings("ignore")


pio.templates.default = "plotly_white"


df = pd.read_csv("data/clean/stats_clean.csv")


name_overrides = {
    "Joao Pedro": "Joao Pedro",
    "João Pedro": "Joao Pedro",
    "Rayan Aït-Nouri": "Aït-Nouri",
    "Matheus Cunha": "Cunha",
    "Rodrigo Muniz": "Muniz",
    "Erling Haaland": "Haaland",
    "Mohamed Salah": "Salah",
    "Cole Palmer": "Palmer",
    "Alexander Isak": "Isak",
    "Ollie Watkins": "Watkins",
    "Chris Wood": "C. Wood",
    "Dominic Solanke": "Solanke",
    "Bryan Mbeumo": "Mbeumo",
    "Yoane Wissa": "Wissa",
    "Nicolas Jackson": "N. Jackson",
    "Jamie Vardy": "Vardy",
    "Danny Welbeck": "Welbeck",
    "Raúl Jiménez": "Jiménez",
    "Callum Wilson": "C. Wilson",
    "Taiwo Awoniyi": "Awoniyi",
    "Carlos Vinícius": "Vinícius",
    "Richarlison": "Richarlison",
    "Igor Thiago": "Igor Thiago",
    "Bruno Guimarães": "Bruno G.",
    "Anthony Gordon": "Gordon",
    "Harvey Barnes": "Barnes",
    "Bukayo Saka": "Saka",
    "Viktor Gyökeres": "Gyökeres",
    "Dominik Szoboszlai": "Szoboszlai",
    "Hugo Ekitiké": "Ekitiké",
    "Cody Gakpo": "Gakpo",
    "Phil Foden": "Foden",
    "Enzo Fernández": "E. Fernández",
    "Jean-Philippe Mateta": "Mateta",
    "Ismaïla Sarr": "I. Sarr",
    "Lukas Nmecha": "Nmecha",
    "Dominic Calvert-Lewin": "DCL",
    "Antoine Semenyo": "Semenyo",
}


def normalise(s):
    return unicodedata.normalize("NFC", s.strip().lower())


name_overrides_normalised = {normalise(k): v for k, v in name_overrides.items()}


def get_display_name(full_name):
    if full_name in name_overrides:
        return name_overrides[full_name]
    key = normalise(full_name)
    if key in name_overrides_normalised:
        return name_overrides_normalised[key]
    parts = full_name.strip().split()
    return parts[-1] if parts else full_name


pl = df[
    (df["competition"] == "Premier League") &
    (df["goals"] >= 5) &
    (df["position"].isin(["Forward", "Midfielder"]))
].copy().reset_index(drop=True)


pl_shots = pl[pl["shots"] > 0].copy()
print(f"PL attackers with 5+ goals: {len(pl)}")


teams = df["team"].unique()
colours = plt.cm.tab20.colors
team_colour = {team: colours[i % 20] for i, team in enumerate(teams)}


# ── PLOT 1: Lollipop — Top 15 scorers (matplotlib PNG) ────────────────────────
top15 = pl.nlargest(15, "goals").sort_values("goals")
fig, ax = plt.subplots(figsize=(10, 7))
names = [get_display_name(n) for n in top15["name"]]
goals = top15["goals"].values
colors = [team_colour[t] for t in top15["team"]]

for i, (name, val, col) in enumerate(zip(names, goals, colors)):
    ax.plot([0, val], [i, i], color=col, linewidth=2.5, alpha=0.7, zorder=2)
    ax.scatter(val, i, color=col, s=180, zorder=3, edgecolors="white", linewidths=1.5)
    ax.text(val + 0.2, i, str(int(val)), va="center", fontsize=9.5, fontweight="bold", color=col)

ax.set_yticks(range(len(names)))
ax.set_yticklabels(names, fontsize=10)
ax.set_xlabel("Goals", fontsize=12)
ax.set_title("Top 15 Premier League Scorers 2025/26", fontsize=14, fontweight="bold")
ax.spines[["top", "right", "left"]].set_visible(False)
ax.tick_params(left=False)
ax.set_xlim(0, goals.max() + 3)
ax.xaxis.grid(True, alpha=0.3, linestyle="--")
ax.set_axisbelow(True)
handles = [mpatches.Patch(color=team_colour[t], label=t) for t in top15["team"].unique()]
ax.legend(handles=handles, fontsize=8, loc="lower right")
plt.tight_layout()
plt.savefig("output/figures/01_top15_scorers.png", dpi=150)
plt.close()
print("✅ Plot 1 saved (PNG)")


# ── PLOT 2: Goals vs xG — Plotly HTML ─────────────────────────────────────────
pl_plot = pl.copy()
pl_plot["display_name"] = pl_plot["name"].apply(get_display_name)
pl_plot["Club"] = pl_plot["team"]
pl_plot["Goals"] = pl_plot["goals"]
pl_plot["Expected Goals (xG)"] = pl_plot["xg"].round(2)
pl_plot["Goals vs xG"] = pl_plot["goals_vs_xg"].round(2)
pl_plot["Shot Conversion (%)"] = pl_plot["shot_conv"].round(1)

fig2 = go.Figure()

for team in pl_plot["Club"].unique():
    sub = pl_plot[pl_plot["Club"] == team]
    fig2.add_trace(go.Scatter(
        x=sub["Expected Goals (xG)"],
        y=sub["Goals"],
        mode="markers+text",
        name=team,
        text=sub["display_name"],
        textposition="top center",
        textfont=dict(size=9),
        marker=dict(size=11, line=dict(width=1.5, color="white")),
        customdata=sub[["Club", "Goals", "Expected Goals (xG)", "Goals vs xG", "Shot Conversion (%)"]].values,
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "Club: %{customdata[0]}<br>"
            "Goals: %{customdata[1]}<br>"
            "Expected Goals (xG): %{customdata[2]}<br>"
            "Goals vs xG: %{customdata[3]}<br>"
            "Shot Conversion (%): %{customdata[4]}<br>"
            "<extra></extra>"
        ),
        hovertext=sub["name"],
    ))

max_val = max(pl_plot["Expected Goals (xG)"].max(), pl_plot["Goals"].max()) + 2
fig2.add_shape(type="line", x0=0, y0=0, x1=max_val, y1=max_val,
               line=dict(color="black", width=1.5, dash="dash"))
fig2.add_annotation(
    x=max_val * 0.7, y=max_val * 0.7 + 1.5,
    text="Goals = xG", showarrow=False,
    font=dict(size=11, color="gray")
)
fig2.update_layout(
    height=700,
    font_family="Inter, sans-serif",
    title="Goals vs Expected Goals — PL Attackers 2025/26",
    title_font_size=16,
    plot_bgcolor="white",
    paper_bgcolor="#f4f6f9",
    hoverlabel=dict(bgcolor="white", font_size=13),
    margin=dict(l=60, r=60, t=60, b=60),
    xaxis=dict(
        title="Expected Goals (xG)",
        showgrid=True, gridcolor="#eeeeee",
        range=[-0.5, pl_plot["Expected Goals (xG)"].max() + 3],
        title_font_size=13, tickfont_size=11, dtick=2,
    ),
    yaxis=dict(
        title="Actual Goals",
        showgrid=True, gridcolor="#eeeeee",
        range=[-0.5, pl_plot["Goals"].max() + 3],
        title_font_size=13, tickfont_size=11, dtick=2,
    ),
    legend=dict(title="Club", orientation="v", font_size=10),
)
fig2.write_html("output/figures/02_goals_vs_xg.html", include_plotlyjs="cdn", full_html=True)
print("✅ Plot 2 saved (HTML)")


# ── PLOT 4: xG per shot vs conversion — Plotly HTML ───────────────────────────
pl_shots_plot = pl_shots.copy()
pl_shots_plot["display_name"] = pl_shots_plot["name"].apply(get_display_name)
med_x = pl_shots_plot["xg_per_shot"].median()
med_y = pl_shots_plot["shot_conv"].median()

pl_shots_plot["Profile"] = pl_shots_plot.apply(
    lambda r: (
        "Elite (High Quality + High Conversion)" if r["xg_per_shot"] >= med_x and r["shot_conv"] >= med_y
        else "Pure Finisher (Low Quality, High Conversion)" if r["xg_per_shot"] < med_x and r["shot_conv"] >= med_y
        else "Chance Merchant (High Quality, Low Conversion)" if r["xg_per_shot"] >= med_x and r["shot_conv"] < med_y
        else "Struggling (Low Quality + Low Conversion)"
    ), axis=1
)

quadrant_colours = {
    "Elite (High Quality + High Conversion)": "#27ae60",
    "Pure Finisher (Low Quality, High Conversion)": "#3d85c8",
    "Chance Merchant (High Quality, Low Conversion)": "#f5a623",
    "Struggling (Low Quality + Low Conversion)": "#e94560",
}

pl_shots_plot["Club"] = pl_shots_plot["team"]
pl_shots_plot["Goals"] = pl_shots_plot["goals"]
pl_shots_plot["xG Per Shot"] = pl_shots_plot["xg_per_shot"].round(3)
pl_shots_plot["Shot Conversion (%)"] = pl_shots_plot["shot_conv"].round(1)

fig4 = go.Figure()

for profile, colour in quadrant_colours.items():
    sub = pl_shots_plot[pl_shots_plot["Profile"] == profile]
    if sub.empty:
        continue
    fig4.add_trace(go.Scatter(
        x=sub["xG Per Shot"],
        y=sub["Shot Conversion (%)"],
        mode="markers+text",
        name=profile,
        text=sub["display_name"],
        textposition="top center",
        textfont=dict(size=9),
        marker=dict(size=11, color=colour, line=dict(width=1.5, color="white")),
        customdata=sub[["Club", "Goals", "xG Per Shot", "Shot Conversion (%)", "Profile"]].values,
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "Club: %{customdata[0]}<br>"
            "Goals: %{customdata[1]}<br>"
            "xG Per Shot: %{customdata[2]}<br>"
            "Shot Conversion (%): %{customdata[3]}<br>"
            "Profile: %{customdata[4]}<br>"
            "<extra></extra>"
        ),
        hovertext=sub["name"],
    ))

fig4.add_vline(x=med_x, line_dash="dash", line_color="gray", opacity=0.5)
fig4.add_hline(y=med_y, line_dash="dash", line_color="gray", opacity=0.5)
fig4.update_layout(
    height=650,
    font_family="Inter, sans-serif",
    title="Shot Quality vs Conversion — PL Attackers 2025/26",
    title_font_size=16,
    plot_bgcolor="white",
    paper_bgcolor="#f4f6f9",
    hoverlabel=dict(bgcolor="white", font_size=13),
    margin=dict(l=60, r=60, t=60, b=120),
    xaxis=dict(
        title="xG Per Shot (Chance Quality)",
        showgrid=True, gridcolor="#eeeeee",
        title_font_size=13, tickfont_size=11,
    ),
    yaxis=dict(
        title="Shot Conversion (%)",
        showgrid=True, gridcolor="#eeeeee",
        title_font_size=13, tickfont_size=11,
    ),
    legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5),
)
fig4.write_html("output/figures/04_xg_per_shot_vs_conversion.html", include_plotlyjs="cdn", full_html=True)
print("✅ Plot 4 saved (HTML)")


# ── PLOT 6: Radial bar — Clinicality Score (matplotlib PNG) ───────────────────
features = ["goals", "xg", "shot_conv", "xg_per_shot", "goals_vs_xg"]
pl_pca = pl_shots[features + ["name", "last_name", "team"]].dropna().copy()
scaler = StandardScaler()
X_scaled = scaler.fit_transform(pl_pca[features])
pca = PCA(n_components=1)
pl_pca["clinicality_score"] = pca.fit_transform(X_scaled)
min_s = pl_pca["clinicality_score"].min()
max_s = pl_pca["clinicality_score"].max()
pl_pca["clinicality_score"] = ((pl_pca["clinicality_score"] - min_s) / (max_s - min_s)) * 100

top_clinical = pl_pca.nlargest(12, "clinicality_score").sort_values("clinicality_score", ascending=True)
names_r = [get_display_name(n) for n in top_clinical["name"]]
scores = top_clinical["clinicality_score"].values
bar_colors = [team_colour[t] for t in top_clinical["team"]]

fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
N = len(names_r)
angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
width = 2 * np.pi / N * 0.8
ax.bar(angles, scores, width=width, color=bar_colors,
       alpha=0.85, edgecolor="white", linewidth=1.5, zorder=3)

for r in [25, 50, 75, 100]:
    ax.plot(np.linspace(0, 2*np.pi, 300), [r]*300,
            color="gray", linewidth=0.5, alpha=0.4, zorder=1)
    ax.text(0, r + 2, str(r), ha="center", va="bottom", fontsize=7, color="gray")

ax.set_xticks(angles)
ax.set_xticklabels(names_r, fontsize=9.5, fontweight="bold")
ax.set_yticks([])
ax.set_ylim(0, 115)
ax.spines["polar"].set_visible(False)
ax.set_facecolor("#f9f9f9")
fig.patch.set_facecolor("#f9f9f9")
ax.set_title("Most Clinical PL Attackers 2025/26\nComposite Clinicality Score (PCA, 0–100)",
             fontsize=13, fontweight="bold", pad=25)

for angle, score in zip(angles, scores):
    ax.text(angle, score - 8, f"{score:.0f}",
            ha="center", va="center", fontsize=8, color="white", fontweight="bold")

handles = [mpatches.Patch(color=team_colour[t], label=t) for t in top_clinical["team"].unique()]
ax.legend(handles=handles, fontsize=7.5, loc="upper right",
          bbox_to_anchor=(1.3, 1.1), title="Club", title_fontsize=8)
plt.tight_layout()
plt.savefig("output/figures/06_clinicality_score.png", dpi=150, bbox_inches="tight")
plt.close()
print("✅ Plot 6 saved (PNG)")

print("\n🏆 Top 10 most clinical PL attackers:")
print(pl_pca.nlargest(10, "clinicality_score")[["name", "team", "goals", "xg", "shot_conv", "clinicality_score"]].to_string(index=False))

pl_pca.to_csv("data/clean/clinicality_scores.csv", index=False)
