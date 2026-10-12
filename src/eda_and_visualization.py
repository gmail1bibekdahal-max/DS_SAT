"""
EDA and Visualization Pipeline
Challenge ID: CH24 - MANUFACTURING QUALITY INSIGHT
PrimeForge Manufacturing Ltd.

Answers all 6 analytical questions:
1. Which lines have higher defect rates?
2. Which defect types dominate? (Pareto Analysis)
3. How do shifts differ?
4. Which process readings vary with defects?
5. Do material suppliers differ?
6. Does machine operating time relate to quality?
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Styling configuration
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.size"] = 10
plt.rcParams["axes.titlesize"] = 12
plt.rcParams["axes.titleweight"] = "bold"

FIGURES_DIR = Path("figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv("data/cleaned/cleaned_manufacturing_quality.csv")
print(f"Loaded cleaned data with {len(df)} records for EDA.")

# Color palette
PALETTE = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]

# ==========================================
# 1. Defect Rate by Production Line
# ==========================================
print("\n--- 1. Defect Rate by Line ---")
line_stats = df.groupby("line").agg(
    total_qty=("quantity", "sum"),
    total_defects=("defect_count", "sum"),
    avg_defect_rate_pct=("defect_rate_pct", "mean"),
    std_defect_rate_pct=("defect_rate_pct", "std")
).reset_index()
line_stats["weighted_defect_rate_pct"] = (line_stats["total_defects"] / line_stats["total_qty"] * 100).round(2)
print(line_stats)

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(line_stats["line"], line_stats["avg_defect_rate_pct"], color=["#2b5c8f", "#3a7ebf", "#d9534f", "#e06d53"], edgecolor="black", width=0.55)
ax.set_title("Average Defect Rate by Production Line", pad=15)
ax.set_xlabel("Production Line", fontweight="bold")
ax.set_ylabel("Average Defect Rate (%)", fontweight="bold")
ax.set_ylim(0, max(line_stats["avg_defect_rate_pct"]) * 1.25)
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.15, f"{yval:.2f}%", ha="center", va="bottom", fontweight="bold", fontsize=10)
plt.tight_layout()
plt.savefig(FIGURES_DIR / "01_defect_rate_by_line.png", dpi=300)
plt.close()

# ==========================================
# 2. Defect Type Pareto Analysis
# ==========================================
print("\n--- 2. Defect Type Pareto Analysis ---")
defect_counts = df[df["defect_type_clean"] != "None"]["defect_type_clean"].value_counts().reset_index()
defect_counts.columns = ["defect_type", "count"]
defect_counts["cumulative_sum"] = defect_counts["count"].cumsum()
defect_counts["cumulative_pct"] = (defect_counts["cumulative_sum"] / defect_counts["count"].sum() * 100).round(2)
print(defect_counts)

fig, ax1 = plt.subplots(figsize=(9, 5.5))
ax2 = ax1.twinx()

bars = ax1.bar(defect_counts["defect_type"], defect_counts["count"], color="#2b5c8f", edgecolor="black", width=0.55)
line = ax2.plot(defect_counts["defect_type"], defect_counts["cumulative_pct"], color="#d9534f", marker="o", linewidth=2.5, markersize=7)

ax1.set_xlabel("Defect Category", fontweight="bold")
ax1.set_ylabel("Occurrence Count", color="#2b5c8f", fontweight="bold")
ax2.set_ylabel("Cumulative Percentage (%)", color="#d9534f", fontweight="bold")
ax2.set_ylim(0, 110)
ax2.axhline(80, color="gray", linestyle="--", linewidth=1.2, label="80% Cutoff (Pareto)")

for bar in bars:
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 10, f"{int(yval)}", ha="center", va="bottom", fontsize=9)

for i, txt in enumerate(defect_counts["cumulative_pct"]):
    ax2.annotate(f"{txt:.1f}%", (defect_counts["defect_type"][i], txt + 2.5), ha="center", color="#d9534f", fontweight="bold")

plt.title("Defect Type Pareto Analysis (80/20 Rule)", pad=15)
ax2.legend(loc="lower right")
plt.tight_layout()
plt.savefig(FIGURES_DIR / "02_defect_type_pareto.png", dpi=300)
plt.close()

# ==========================================
# 3. Shift Comparison
# ==========================================
print("\n--- 3. Shift Comparison ---")
shift_stats = df.groupby("shift").agg(
    batch_count=("batch", "count"),
    avg_defect_rate_pct=("defect_rate_pct", "mean"),
    avg_temperature=("temperature", "mean"),
    avg_pressure=("pressure", "mean"),
    avg_speed=("speed", "mean")
).reset_index()
print(shift_stats)

fig, ax = plt.subplots(figsize=(8, 5))
shift_order = ["Shift_A", "Shift_B", "Shift_C"]
shift_labels = ["Shift A (Morning)", "Shift B (Evening)", "Shift C (Night)"]
shift_rates = [df[df["shift"] == s]["defect_rate_pct"].mean() for s in shift_order]

colors = ["#28a745", "#ffc107", "#dc3545"]
bars = ax.bar(shift_labels, shift_rates, color=colors, edgecolor="black", width=0.5)
ax.set_title("Defect Rate Comparison Across Shifts", pad=15)
ax.set_ylabel("Average Defect Rate (%)", fontweight="bold")
ax.set_ylim(0, max(shift_rates) * 1.25)
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.15, f"{yval:.2f}%", ha="center", va="bottom", fontweight="bold", fontsize=10)
plt.tight_layout()
plt.savefig(FIGURES_DIR / "03_shift_comparison.png", dpi=300)
plt.close()

# ==========================================
# 4. Process Variable Analysis
# ==========================================
print("\n--- 4. Process Variable Analysis ---")
fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

# Temperature vs Defect Rate
sns.scatterplot(data=df, x="temperature", y="defect_rate_pct", hue="high_defect_risk", palette={0: "#2b5c8f", 1: "#d9534f"}, alpha=0.6, ax=axes[0])
axes[0].set_title("Temperature vs Defect Rate")
axes[0].set_xlabel("Temperature (°C)", fontweight="bold")
axes[0].set_ylabel("Defect Rate (%)", fontweight="bold")

# Pressure vs Defect Rate
sns.scatterplot(data=df, x="pressure", y="defect_rate_pct", hue="high_defect_risk", palette={0: "#2b5c8f", 1: "#d9534f"}, alpha=0.6, ax=axes[1])
axes[1].set_title("Pressure vs Defect Rate")
axes[1].set_xlabel("Pressure (Bar)", fontweight="bold")
axes[1].set_ylabel("Defect Rate (%)", fontweight="bold")

# Speed vs Defect Rate
sns.scatterplot(data=df, x="speed", y="defect_rate_pct", hue="high_defect_risk", palette={0: "#2b5c8f", 1: "#d9534f"}, alpha=0.6, ax=axes[2])
axes[2].set_title("Speed vs Defect Rate")
axes[2].set_xlabel("Speed (RPM)", fontweight="bold")
axes[2].set_ylabel("Defect Rate (%)", fontweight="bold")

plt.tight_layout()
plt.savefig(FIGURES_DIR / "04_process_variables_vs_defects.png", dpi=300)
plt.close()

# ==========================================
# 5. Supplier and Material Grade Analysis
# ==========================================
print("\n--- 5. Supplier and Material Grade Analysis ---")
supp_stats = df.groupby(["supplier", "material_grade"])["defect_rate_pct"].mean().unstack()
print(supp_stats)

fig, ax = plt.subplots(figsize=(9, 5))
supp_stats.plot(kind="bar", ax=ax, colormap="viridis", edgecolor="black", width=0.7)
ax.set_title("Defect Rate Across Material Suppliers and Grades", pad=15)
ax.set_xlabel("Material Supplier", fontweight="bold")
ax.set_ylabel("Average Defect Rate (%)", fontweight="bold")
ax.legend(title="Material Grade")
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig(FIGURES_DIR / "05_supplier_material_grade_analysis.png", dpi=300)
plt.close()

# ==========================================
# 6. Machine Operating Time and Age Band
# ==========================================
print("\n--- 6. Machine Operating Time Analysis ---")
mach_stats = df.groupby("age_band").agg(
    avg_defect_rate_pct=("defect_rate_pct", "mean"),
    avg_operating_hours=("operating_hours", "mean"),
    batch_count=("batch", "count")
).reindex(["< 2 Years", "2-5 Years", "> 5 Years"]).reset_index()
print(mach_stats)

fig, ax = plt.subplots(figsize=(8, 5))
sns.boxplot(data=df, x="age_band", y="defect_rate_pct", order=["< 2 Years", "2-5 Years", "> 5 Years"], palette="Blues", ax=ax)
ax.set_title("Defect Rate Distribution by Machine Age Band", pad=15)
ax.set_xlabel("Machine Age Band", fontweight="bold")
ax.set_ylabel("Defect Rate (%)", fontweight="bold")
plt.tight_layout()
plt.savefig(FIGURES_DIR / "06_machine_operating_hours_vs_defects.png", dpi=300)
plt.close()

# ==========================================
# 7. Correlation Heatmap
# ==========================================
num_cols = ["quantity", "operating_hours", "temperature", "pressure", "speed", "tensile_strength_mpa", "impurity_pct", "defect_count", "defect_rate_pct"]
corr = df[num_cols].corr()

fig, ax = plt.subplots(figsize=(9, 7))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", cbar=True, ax=ax, square=True)
ax.set_title("Pearson Correlation Matrix: Process & Quality Parameters", pad=15)
plt.tight_layout()
plt.savefig(FIGURES_DIR / "07_correlation_matrix.png", dpi=300)
plt.close()

print("\nAll 7 EDA figures successfully generated and saved to figures/!")
