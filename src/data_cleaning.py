"""
Data Cleaning and Consolidation Pipeline
Challenge ID: CH24 - MANUFACTURING QUALITY INSIGHT
PrimeForge Manufacturing Ltd.

Handles all 5 Data Quality Conditions:
1. Deduplication of batch records
2. Standardization of inconsistent defect labels & quality status
3. Outlier detection and treatment for extreme sensor readings
4. Imputation of missing process readings
5. Reconciliation of unmatched material lots
"""

import pandas as pd
import numpy as np
from pathlib import Path

DATA_RAW_DIR = Path("data/raw")
DATA_CLEANED_DIR = Path("data/cleaned")
DATA_CLEANED_DIR.mkdir(parents=True, exist_ok=True)

def load_raw_data():
    df_prod = pd.read_csv(DATA_RAW_DIR / "production.csv")
    df_mach = pd.read_csv(DATA_RAW_DIR / "machines.csv")
    df_proc = pd.read_csv(DATA_RAW_DIR / "process.csv")
    df_mat = pd.read_csv(DATA_RAW_DIR / "materials.csv")
    df_insp = pd.read_csv(DATA_RAW_DIR / "inspection.csv")
    return df_prod, df_mach, df_proc, df_mat, df_insp

def standardize_defect_label(label):
    if pd.isna(label):
        return "None"
    l = str(label).strip().lower()
    if "scratch" in l:
        return "Surface Scratch"
    elif "dim" in l:
        return "Dimensional Error"
    elif "poros" in l:
        return "Porosity"
    elif "crack" in l:
        return "Cracks"
    elif "contam" in l or "particle" in l:
        return "Contamination"
    elif "none" in l or "pass" in l:
        return "None"
    else:
        return "Other"

def standardize_status(status):
    if pd.isna(status):
        return "Passed"
    s = str(status).strip().upper()
    if "PASS" in s:
        return "Passed"
    elif "REWORK" in s:
        return "Rework"
    elif "REJECT" in s:
        return "Rejected"
    return "Passed"

def clean_data():
    print("=== Loading Raw Datasets ===")
    df_prod, df_mach, df_proc, df_mat, df_insp = load_raw_data()
    print(f"Production raw count: {len(df_prod)}")
    print(f"Machines raw count: {len(df_mach)}")
    print(f"Process raw count: {len(df_proc)}")
    print(f"Materials raw count: {len(df_mat)}")
    print(f"Inspection raw count: {len(df_insp)}")

    # 1. Deduplication of Production Batches
    initial_prod = len(df_prod)
    df_prod = df_prod.drop_duplicates(subset=["batch"]).reset_index(drop=True)
    dups_removed = initial_prod - len(df_prod)
    print(f"[Condition 1: Duplicates] Removed {dups_removed} duplicate production records. Cleaned production batches: {len(df_prod)}")

    # 2. Standardize Inconsistent Defect Labels & Quality Status
    df_insp["defect_type_clean"] = df_insp["defect_type"].apply(standardize_defect_label)
    df_insp["quality_status_clean"] = df_insp["quality_status"].apply(standardize_status)
    print(f"[Condition 2: Inconsistent Labels] Standardized {df_insp['defect_type'].nunique()} raw labels into canonical categories:")
    print(df_insp["defect_type_clean"].value_counts())

    # 3. Clean Process Data: Treat Extreme Outliers & Impute Missing
    # Identify extreme sensor values outside feasible physical bounds
    # Realistic operational envelopes:
    # Temperature: [150°C, 300°C]
    # Pressure: [3.0 Bar, 10.0 Bar]
    # Speed: [800 RPM, 2400 RPM]
    
    outliers_temp = ((df_proc["temperature"] < 100) | (df_proc["temperature"] > 400)).sum()
    outliers_press = ((df_proc["pressure"] < 2.0) | (df_proc["pressure"] > 15.0)).sum()
    outliers_speed = ((df_proc["speed"] < 500) | (df_proc["speed"] > 3000)).sum()
    print(f"[Condition 3: Extreme Sensor Values] Identified outliers -> Temp: {outliers_temp}, Pressure: {outliers_press}, Speed: {outliers_speed}")

    # Set extreme outliers to NaN so they get imputed properly
    df_proc.loc[(df_proc["temperature"] < 100) | (df_proc["temperature"] > 400), "temperature"] = np.nan
    df_proc.loc[(df_proc["pressure"] < 2.0) | (df_proc["pressure"] > 15.0), "pressure"] = np.nan
    df_proc.loc[(df_proc["speed"] < 500) | (df_proc["speed"] > 3000), "speed"] = np.nan

    # Check missing values before imputation
    missing_temp = df_proc["temperature"].isna().sum()
    missing_press = df_proc["pressure"].isna().sum()
    missing_speed = df_proc["speed"].isna().sum()
    print(f"[Condition 4: Missing Readings] Total missing/invalid -> Temp: {missing_temp}, Pressure: {missing_press}, Speed: {missing_speed}")

    # Impute missing with median
    med_temp = df_proc["temperature"].median()
    med_press = df_proc["pressure"].median()
    med_speed = df_proc["speed"].median()

    df_proc["temperature"] = df_proc["temperature"].fillna(med_temp)
    df_proc["pressure"] = df_proc["pressure"].fillna(med_press)
    df_proc["speed"] = df_proc["speed"].fillna(med_speed)

    # 4. Unmatched Material Lots
    unmatched_lots = ~df_prod["lot"].isin(df_mat["lot"])
    unmatched_count = unmatched_lots.sum()
    print(f"[Condition 5: Unmatched Material Lots] Identified {unmatched_count} batches with unmatched material lots")

    # Impute missing material attributes for unmatched lots
    mean_tensile = df_mat["tensile_strength_mpa"].mean()
    mean_impurity = df_mat["impurity_pct"].mean()

    # 5. Merge Datasets at Batch Level
    # Production + Machines
    df_merged = df_prod.merge(df_mach, on="machine", how="left")
    
    # + Process
    df_merged = df_merged.merge(df_proc, on="batch", how="left")
    
    # + Materials
    df_merged = df_merged.merge(df_mat, on="lot", how="left")
    # Fill unmatched material info
    df_merged["supplier"] = df_merged["supplier"].fillna("Unknown_Supplier")
    df_merged["material_grade"] = df_merged["material_grade"].fillna("Grade_B (Default)")
    df_merged["tensile_strength_mpa"] = df_merged["tensile_strength_mpa"].fillna(mean_tensile)
    df_merged["impurity_pct"] = df_merged["impurity_pct"].fillna(mean_impurity)

    # + Inspection
    df_merged = df_merged.merge(
        df_insp[["batch", "defect_type_clean", "defect_count", "quality_status_clean"]],
        on="batch",
        how="left"
    )

    # Calculate Key Derived Metrics
    df_merged["defect_rate"] = df_merged["defect_count"] / df_merged["quantity"]
    df_merged["defect_rate_pct"] = (df_merged["defect_rate"] * 100).round(2)
    # High defect flag (binary classification target: defect_rate >= 4.0%)
    df_merged["high_defect_risk"] = (df_merged["defect_rate"] >= 0.040).astype(int)

    # Output Cleaned Dataset
    output_csv = DATA_CLEANED_DIR / "cleaned_manufacturing_quality.csv"
    df_merged.to_csv(output_csv, index=False)
    print(f"\n[DONE] Saved cleaned master dataset to: {output_csv}")
    print(f"Total Cleaned Records: {len(df_merged)}, Total Features: {len(df_merged.columns)}")
    print(df_merged.head())
    return df_merged

if __name__ == "__main__":
    clean_data()
