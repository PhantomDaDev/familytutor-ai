import io
import base64
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from datetime import datetime, timedelta
from core.database import (
    get_child, get_subject_stats, get_topic_accuracy,
    get_daily_activity, get_streak, get_recent_sessions
)

PALETTE = {
    "bg": "#0f0e17",
    "surface": "#1a1828",
    "accent1": "#7c6af7",
    "accent2": "#f7a66a",
    "accent3": "#6af7c8",
    "accent4": "#f76a8a",
    "text": "#fffffe",
    "muted": "#a7a9be",
}

SUBJECT_COLORS = ["#7c6af7", "#f7a66a", "#6af7c8", "#f76a8a", "#f7e66a", "#6aaff7"]

def _fig_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=140, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    data = base64.b64encode(buf.read()).decode()
    plt.close(fig)
    return data


def chart_subject_accuracy(child_id: int) -> str:
    stats = get_subject_stats(child_id)
    if not stats:
        return ""
    subjects = [s["subject"] for s in stats]
    accuracy = []
    for s in stats:
        if s["total_q"] and s["total_q"] > 0:
            accuracy.append(round(s["total_correct"] / s["total_q"] * 100))
        else:
            accuracy.append(0)

    fig, ax = plt.subplots(figsize=(6, 3.2))
    fig.patch.set_facecolor(PALETTE["surface"])
    ax.set_facecolor(PALETTE["surface"])

    colors = SUBJECT_COLORS[:len(subjects)]
    bars = ax.barh(subjects, accuracy, color=colors, height=0.55, zorder=3)
    ax.set_xlim(0, 115)
    ax.set_xlabel("Accuracy (%)", color=PALETTE["muted"], fontsize=9)
    ax.tick_params(colors=PALETTE["muted"], labelsize=9)
    ax.spines[:].set_visible(False)
    ax.xaxis.grid(True, color="#2d2b3d", linewidth=0.5, zorder=0)
    ax.set_axisbelow(True)
    for bar, val in zip(bars, accuracy):
        ax.text(val + 2, bar.get_y() + bar.get_height() / 2,
                f"{val}%", va="center", color=PALETTE["text"], fontsize=9, fontweight="bold")
    ax.tick_params(axis="y", colors=PALETTE["text"])
    fig.tight_layout(pad=0.8)
    return _fig_base64(fig)


def chart_daily_activity(child_id: int) -> str:
    activity = get_daily_activity(child_id, days=14)
    if not activity:
        return ""

    days = [a["day"] for a in activity]
    totals = [a["total"] or 0 for a in activity]
    corrects = [a["correct"] or 0 for a in activity]

    x = np.arange(len(days))
    fig, ax = plt.subplots(figsize=(6, 3))
    fig.patch.set_facecolor(PALETTE["surface"])
    ax.set_facecolor(PALETTE["surface"])

    ax.bar(x, totals, color=PALETTE["accent1"], alpha=0.4, label="Total questions", zorder=3)
    ax.bar(x, corrects, color=PALETTE["accent1"], label="Correct", zorder=4)

    short_days = [d[-5:] for d in days]
    ax.set_xticks(x)
    ax.set_xticklabels(short_days, rotation=45, ha="right", fontsize=8, color=PALETTE["muted"])
    ax.tick_params(axis="y", colors=PALETTE["muted"], labelsize=8)
    ax.spines[:].set_visible(False)
    ax.yaxis.grid(True, color="#2d2b3d", linewidth=0.5, zorder=0)
    ax.set_axisbelow(True)
    ax.legend(fontsize=8, facecolor=PALETTE["bg"], edgecolor="none",
              labelcolor=PALETTE["muted"], framealpha=0.8)
    fig.tight_layout(pad=0.8)
    return _fig_base64(fig)


def chart_topic_heatmap(child_id: int) -> str:
    topics = get_topic_accuracy(child_id)
    if not topics:
        return ""

    labels = [f"{t['subject'][:3].upper()} - {t['topic'][:18]}" for t in topics]
    accuracy = []
    for t in topics:
        if t["total_q"] and t["total_q"] > 0:
            accuracy.append(round(t["total_correct"] / t["total_q"] * 100))
        else:
            accuracy.append(0)

    # Sort by accuracy
    pairs = sorted(zip(accuracy, labels), key=lambda x: x[0])
    accuracy = [p[0] for p in pairs]
    labels = [p[1] for p in pairs]

    colors = []
    for a in accuracy:
        if a >= 80:
            colors.append(PALETTE["accent3"])
        elif a >= 50:
            colors.append(PALETTE["accent2"])
        else:
            colors.append(PALETTE["accent4"])

    fig, ax = plt.subplots(figsize=(6, max(2.5, len(labels) * 0.45)))
    fig.patch.set_facecolor(PALETTE["surface"])
    ax.set_facecolor(PALETTE["surface"])

    bars = ax.barh(labels, accuracy, color=colors, height=0.6, zorder=3)
    ax.set_xlim(0, 115)
    ax.set_xlabel("Accuracy (%)", color=PALETTE["muted"], fontsize=9)
    ax.spines[:].set_visible(False)
    ax.xaxis.grid(True, color="#2d2b3d", linewidth=0.5, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", colors=PALETTE["text"], labelsize=8)
    ax.tick_params(axis="x", colors=PALETTE["muted"], labelsize=8)
    for bar, val in zip(bars, accuracy):
        ax.text(val + 2, bar.get_y() + bar.get_height() / 2,
                f"{val}%", va="center", color=PALETTE["text"], fontsize=8)

    legend_patches = [
        mpatches.Patch(color=PALETTE["accent3"], label="Strong >=80%"),
        mpatches.Patch(color=PALETTE["accent2"], label="Developing 50-79%"),
        mpatches.Patch(color=PALETTE["accent4"], label="Needs work <50%"),
    ]
    ax.legend(handles=legend_patches, fontsize=7.5, facecolor=PALETTE["bg"],
              edgecolor="none", labelcolor=PALETTE["muted"], framealpha=0.8,
              loc="lower right")
    fig.tight_layout(pad=0.8)
    return _fig_base64(fig)


def get_report_data(child_id: int) -> dict:
    child = get_child(child_id)
    stats = get_subject_stats(child_id)
    streak = get_streak(child_id)
    recent = get_recent_sessions(child_id, limit=5)
    topics = get_topic_accuracy(child_id)

    total_q = sum(s["total_q"] or 0 for s in stats)
    total_correct = sum(s["total_correct"] or 0 for s in stats)
    overall_acc = round(total_correct / total_q * 100) if total_q > 0 else 0

    weak_topics = []
    strong_topics = []
    for t in topics:
        if t["total_q"] and t["total_q"] >= 3:
            acc = t["total_correct"] / t["total_q"] * 100
            if acc < 50:
                weak_topics.append(t["topic"])
            elif acc >= 80:
                strong_topics.append(t["topic"])

    return {
        "child": child,
        "stats": stats,
        "streak": streak,
        "recent": recent,
        "total_questions": total_q,
        "total_correct": total_correct,
        "overall_accuracy": overall_acc,
        "weak_topics": weak_topics[:3],
        "strong_topics": strong_topics[:3],
        "chart_subjects": chart_subject_accuracy(child_id),
        "chart_activity": chart_daily_activity(child_id),
        "chart_topics": chart_topic_heatmap(child_id),
    }
