import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ── IPL TEAM COLOURS ────────────────────────────────────────────
TEAM_COLORS = {
    "Mumbai Indians":                "#005DA0",
    "Chennai Super Kings":           "#F7C010",
    "Royal Challengers Bangalore":   "#EC1C24",
    "Royal Challengers Bengaluru":   "#EC1C24",
    "Kolkata Knight Riders":         "#3A225D",
    "Rajasthan Royals":              "#EA1A85",
    "Sunrisers Hyderabad":           "#F7700E",
    "Delhi Daredevils":              "#0078BC",
    "Delhi Capitals":                "#0078BC",
    "Kings XI Punjab":               "#DCDDDF",
    "Punjab Kings":                  "#ED1B24",
    "Deccan Chargers":               "#FDB933",
    "Kochi Tuskers Kerala":          "#F26522",
    "Pune Warriors":                 "#1C4F9C",
    "Rising Pune Supergiant":        "#6F2DA8",
    "Rising Pune Supergiants":       "#6F2DA8",
    "Gujarat Lions":                 "#E8461A",
    "Gujarat Titans":                "#1C4966",
    "Lucknow Super Giants":          "#A72056",
}

DEFAULT_COLOR = "#00FFFF"

# ── CRICKET VOCABULARY MAP ───────────────────────────────────────
CRICKET_VOCAB = {
    # stat labels
    "Total Runs":       "Runs Plundered",
    "Balls Played":     "Deliveries Faced",
    "Strike Rate":      "SR",
    "Economy Rate":     "Economy",
    "Wickets":          "Scalps",
    "Matches":          "Outings",
    "Average":          "Batting Avg",
    "Balls Bowled":     "Deliveries Sent",
    "Runs Conceded":    "Runs Leaked",
    # menu labels
    "Player Analysis":  "Batter Profiles",
    "Team Analysis":    "Team HQ",
    "Insights":         "The Dressing Room",
    "Player Battle":    "Head to Head",
    "Venue Intelligence": "Ground Report",
    "Bowler Analytics": "Bowling Attack",
    "Knockout Filter":  "Pressure Cooker",
    "Live Scores":      "Live Action",
}

# ── COMMENTARY TAGS ──────────────────────────────────────────────
def sr_tag(sr):
    """Return emoji + label based on strike rate."""
    if sr >= 180:  return ("🔥", "Carnage!")
    if sr >= 150:  return ("⚡", "Explosive!")
    if sr >= 130:  return ("💪", "Aggressive")
    if sr >= 110:  return ("📈", "Steady")
    if sr >= 80:   return ("🐢", "Cautious")
    return ("🛡️", "Anchor")

def economy_tag(econ):
    if econ <= 6:   return ("🎯", "Stranglehold")
    if econ <= 7:   return ("💎", "Economical")
    if econ <= 8:   return ("⚖️", "Balanced")
    if econ <= 9:   return ("🔓", "Expensive")
    return ("💣", "Getting hit")

def runs_tag(runs):
    if runs >= 4000: return ("👑", "Legend")
    if runs >= 2500: return ("🏆", "Elite")
    if runs >= 1500: return ("⭐", "Star")
    if runs >= 800:  return ("📊", "Contributor")
    return ("🌱", "Rising")

def team_color(team_name):
    return TEAM_COLORS.get(team_name, DEFAULT_COLOR)

# ── SHARED CHART STYLE ───────────────────────────────────────────
DARK_BG    = "#0e1117"
GRID_COLOR = "rgba(255,255,255,0.08)"  # not used in mpl, for HTML
GRID_MPL   = "#1e2530"
TEXT_COLOR = "#e0e0e0"
ACCENT     = "#00FFFF"
ACCENT2    = "#FFE66D"
ACCENT3    = "#FF6B6B"

def apply_dark_style(fig, ax, title="", xlabel="", ylabel=""):
    """Apply consistent dark cricket theme to any matplotlib figure."""
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_BG)

    # spines
    for spine in ax.spines.values():
        spine.set_color("#2a2f3a")
        spine.set_linewidth(0.5)

    # grid
    ax.grid(True, color=GRID_MPL, linewidth=0.5, linestyle="--", alpha=0.6)
    ax.set_axisbelow(True)

    # ticks + labels
    ax.tick_params(colors=TEXT_COLOR, labelsize=9)
    ax.xaxis.label.set_color(TEXT_COLOR)
    ax.yaxis.label.set_color(TEXT_COLOR)

    if title:
        ax.set_title(title, color=TEXT_COLOR, fontsize=11, fontweight="bold", pad=12)
    if xlabel:
        ax.set_xlabel(xlabel, color="#aaaaaa", fontsize=9)
    if ylabel:
        ax.set_ylabel(ylabel, color="#aaaaaa", fontsize=9)

    return fig, ax


def dark_line_chart(x, y, title="", xlabel="Over", ylabel="Runs",
                    color=ACCENT, label="", figsize=(10, 4)):
    """Dark-themed line chart with peak annotation."""
    fig, ax = plt.subplots(figsize=figsize)
    apply_dark_style(fig, ax, title, xlabel, ylabel)

    ax.plot(x, y, color=color, linewidth=2.5, marker="o",
            markersize=4, markerfacecolor=color, zorder=3)
    ax.fill_between(x, y, alpha=0.12, color=color)

    # annotate peak
    if len(y) > 0:
        peak_idx = int(np.argmax(y))
        peak_val = y.iloc[peak_idx] if hasattr(y, "iloc") else y[peak_idx]
        peak_x   = x.iloc[peak_idx] if hasattr(x, "iloc") else x[peak_idx]
        ax.annotate(
            f"  Peak: {int(peak_val)}",
            xy=(peak_x, peak_val),
            color=ACCENT2,
            fontsize=8,
            fontweight="bold",
        )

    if label:
        ax.legend([label], facecolor="#1a1f2a", labelcolor=TEXT_COLOR,
                  fontsize=8, framealpha=0.8)

    plt.tight_layout()
    return fig


def dark_bar_chart(categories, values, title="", xlabel="", ylabel="",
                   color=ACCENT, highlight_max=True, figsize=(10, 4),
                   horizontal=False):
    """Dark-themed bar chart with optional max highlight."""
    fig, ax = plt.subplots(figsize=figsize)
    apply_dark_style(fig, ax, title, xlabel, ylabel)

    colors = [color] * len(values)
    if highlight_max and len(values) > 0:
        max_idx = int(np.argmax(values))
        colors[max_idx] = ACCENT2   # gold highlight on top bar

    if horizontal:
        bars = ax.barh(categories, values, color=colors, height=0.6)
        for bar in bars:
            w = bar.get_width()
            ax.text(w + max(values) * 0.01, bar.get_y() + bar.get_height() / 2,
                    f"{int(w)}", va="center", color=TEXT_COLOR, fontsize=8)
    else:
        bars = ax.bar(categories, values, color=colors, width=0.6)
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + max(values) * 0.01,
                    f"{int(h)}", ha="center", color=TEXT_COLOR, fontsize=8)

    plt.tight_layout()
    return fig


def dark_pie_chart(labels, sizes, title="", colors=None, figsize=(5, 4)):
    """Dark-themed pie chart."""
    DEFAULT_COLORS = [ACCENT, ACCENT2, ACCENT3, "#A8E6CF", "#C7CEEA",
                      "#FF8B94", "#4ECDC4"]
    if colors is None:
        colors = DEFAULT_COLORS[:len(labels)]

    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_BG)

    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, autopct="%1.0f%%",
        colors=colors,
        textprops={"color": TEXT_COLOR, "fontsize": 8},
        pctdistance=0.82,
        wedgeprops={"linewidth": 0.5, "edgecolor": DARK_BG},
    )
    for at in autotexts:
        at.set_color("white")
        at.set_fontsize(8)

    if title:
        ax.set_title(title, color=TEXT_COLOR, fontsize=10, fontweight="bold")

    plt.tight_layout()
    return fig