"""
Data Generator for DS Sprint Skill-Based Assessment 2
Challenge ID: CH24 - MANUFACTURING QUALITY INSIGHT
Organization: PrimeForge Manufacturing Ltd.

Generates realistic raw manufacturing datasets including all specified data quality challenges:
1. Missing process readings
2. Duplicate batch records
3. Inconsistent defect labels
4. Extreme sensor values
5. Unmatched material lots
"""

import numpy as np
import pandas as pd
import random
from pathlib import Path

# Seed for reproducibility
np.random.seed(42)
random.seed(42)

DATA_RAW_DIR = Path("data/raw")
DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)

N_BATCHES = 1250

# 1. Machines dataset
# machine, age band, operating hours
machines_data = [
    {"machine": "MCH_01", "machine_type": "CNC Milling", "age_band": "< 2 Years", "operating_hours": 1120},
    {"machine": "MCH_02", "machine_type": "CNC Milling", "age_band": "2-5 Years", "operating_hours": 3240},
    {"machine": "MCH_03", "machine_type": "CNC Milling", "age_band": "> 5 Years", "operating_hours": 6450},
    {"machine": "MCH_04", "machine_type": "Hydraulic Press", "age_band": "< 2 Years", "operating_hours": 980},
    {"machine": "MCH_05", "machine_type": "Hydraulic Press", "age_band": "2-5 Years", "operating_hours": 3810},
    {"machine": "MCH_06", "machine_type": "Hydraulic Press", "age_band": "> 5 Years", "operating_hours": 7120},
    {"machine": "MCH_07", "machine_type": "Precision Lathe", "age_band": "> 5 Years", "operating_hours": 5890},
    {"machine": "MCH_08", "machine_type": "Precision Lathe", "age_band": "2-5 Years", "operating_hours": 2900},
    {"machine": "MCH_09", "machine_type": "Precision Lathe", "age_band": "< 2 Years", "operating_hours": 1420},
    {"machine": "MCH_10", "machine_type": "Die Casting", "age_band": "< 2 Years", "operating_hours": 870},
    {"machine": "MCH_11", "machine_type": "Die Casting", "age_band": "> 5 Years", "operating_hours": 6780},
    {"machine": "MCH_12", "machine_type": "Die Casting", "age_band": "2-5 Years", "operating_hours": 3540},
]
df_machines = pd.DataFrame(machines_data)
df_machines.to_csv(DATA_RAW_DIR / "machines.csv", index=False)
print(f"Generated machines.csv: {len(df_machines)} records")

# 2. Materials dataset
# supplier, material grade, lot
suppliers = ["Supplier_Alpha", "Supplier_Beta", "Supplier_Gamma", "Supplier_Delta"]
material_grades = ["Grade_A", "Grade_B", "Grade_C"]

lots_data = []
N_LOTS = 300
for i in range(1, N_LOTS + 1):
    lot_id = f"LOT_{i:04d}"
    supp = random.choice(suppliers)
    # Delta and Gamma supply more Grade C
    if supp in ["Supplier_Delta", "Supplier_Gamma"]:
        grade = random.choices(material_grades, weights=[0.2, 0.4, 0.4])[0]
    else:
        grade = random.choices(material_grades, weights=[0.5, 0.35, 0.15])[0]
    
    # Material properties
    tensile = round(np.random.normal(520 if grade == "Grade_A" else (480 if grade == "Grade_B" else 430), 20), 1)
    impurity = round(np.random.normal(0.4 if grade == "Grade_A" else (0.8 if grade == "Grade_B" else 1.6), 0.2), 2)
    impurity = max(0.05, impurity)
    
    lots_data.append({
        "lot": lot_id,
        "supplier": supp,
        "material_grade": grade,
        "tensile_strength_mpa": tensile,
        "impurity_pct": impurity
    })

df_materials = pd.DataFrame(lots_data)
df_materials.to_csv(DATA_RAW_DIR / "materials.csv", index=False)
print(f"Generated materials.csv: {len(df_materials)} records")

# 3. Production dataset
# batch, line, shift, quantity (also contains machine, lot)
lines = ["Line_1", "Line_2", "Line_3", "Line_4"]
shifts = ["Shift_A", "Shift_B", "Shift_C"]  # Shift_A: Morning, Shift_B: Evening, Shift_C: Night
machines_list = df_machines["machine"].tolist()

batches = [f"BATCH_{1000 + i}" for i in range(N_BATCHES)]
production_rows = []

for b_id in batches:
    line = random.choice(lines)
    shift = random.choice(shifts)
    qty = int(np.random.normal(650, 80))
    qty = max(350, min(1000, qty))
    
    # Match machine by line affinity (some machines on specific lines)
    if line == "Line_1":
        machine = random.choice(["MCH_01", "MCH_04", "MCH_09"])
    elif line == "Line_2":
        machine = random.choice(["MCH_02", "MCH_05", "MCH_08"])
    elif line == "Line_3":
        machine = random.choice(["MCH_03", "MCH_07", "MCH_11"]) # Older machines on Line 3
    else:
        machine = random.choice(["MCH_06", "MCH_10", "MCH_12"])
        
    # Unmatched material lots condition: 35 batches will have unmatched lots
    if random.random() < 0.03:
        lot = f"LOT_{random.randint(9000, 9999)}"  # Unmatched
    else:
        lot = f"LOT_{random.randint(1, N_LOTS):04d}"
        
    production_rows.append({
        "batch": b_id,
        "line": line,
        "shift": shift,
        "quantity": qty,
        "machine": machine,
        "lot": lot
    })

df_production = pd.DataFrame(production_rows)

# Condition: Duplicate batch records (~30 duplicates)
duplicates = df_production.sample(n=30, random_state=42)
df_production_with_dups = pd.concat([df_production, duplicates], ignore_index=True)
# Shuffle rows
df_production_with_dups = df_production_with_dups.sample(frac=1.0, random_state=42).reset_index(drop=True)
df_production_with_dups.to_csv(DATA_RAW_DIR / "production.csv", index=False)
print(f"Generated production.csv: {len(df_production_with_dups)} records (with duplicates)")

# 4. Process dataset
# batch, temperature, pressure, speed
# Influenced by machine condition, line, shift
process_rows = []
for idx, row in df_production.iterrows():
    b_id = row["batch"]
    line = row["line"]
    shift = row["shift"]
    machine = row["machine"]
    m_info = df_machines[df_machines["machine"] == machine].iloc[0]
    
    # Base conditions
    temp = np.random.normal(205.0, 8.0)
    pressure = np.random.normal(5.8, 0.4)
    speed = np.random.normal(1500.0, 75.0)
    
    # Night shift (Shift_C) has higher thermal variance and speed variance
    if shift == "Shift_C":
        temp += np.random.normal(6.5, 4.0)
        speed += np.random.normal(30.0, 50.0)
        pressure -= np.random.uniform(0.1, 0.4)
        
    # Older machines have higher temperature drift and erratic pressure
    if m_info["age_band"] == "> 5 Years":
        temp += np.random.uniform(5.0, 15.0)
        pressure += np.random.normal(0.3, 0.6)
        
    # Condition: Extreme sensor values (outliers) in ~2% of records
    is_extreme = random.random() < 0.025
    if is_extreme:
        choice = random.choice(["temp_high", "temp_low", "press_high", "press_low", "speed_high"])
        if choice == "temp_high":
            temp = random.choice([850.0, 999.0, 1200.0])
        elif choice == "temp_low":
            temp = random.choice([-50.0, -99.0, 0.0])
        elif choice == "press_high":
            pressure = random.choice([45.0, 88.0, 110.0])
        elif choice == "press_low":
            pressure = random.choice([-15.0, 0.0])
        elif choice == "speed_high":
            speed = random.choice([9999.0, 15000.0])

    # Condition: Missing process readings (~5% missing in each column independently)
    temp_val = np.nan if random.random() < 0.05 else round(temp, 2)
    press_val = np.nan if random.random() < 0.05 else round(pressure, 2)
    speed_val = np.nan if random.random() < 0.04 else round(speed, 1)
    
    process_rows.append({
        "batch": b_id,
        "temperature": temp_val,
        "pressure": press_val,
        "speed": speed_val
    })

df_process = pd.DataFrame(process_rows)
# Add some extra rows with batch duplicates or re-ordered
df_process.to_csv(DATA_RAW_DIR / "process.csv", index=False)
print(f"Generated process.csv: {len(df_process)} records (with missing and extreme values)")

# 5. Inspection dataset
# batch, defect type, defect count, quality status
# Driven by underlying physics: Line 3/4, Shift C, Older machines, Grade C material, High temp/pressure variance
defect_raw_labels = {
    "Surface Scratch": ["Surface Scratch", "surface_scratch", "SURFACE SCRATCH", "Scratch", "scratch_defect"],
    "Dimensional Error": ["Dimensional Error", "dimensional error", "DIMENSIONAL", "Dim Error", "dim_error"],
    "Porosity": ["Porosity", "porosity", "POROSITY", "porosity_defect"],
    "Cracks": ["Cracks", "Crack", "hairline_crack", "CRACK", "cracks_structural"],
    "Contamination": ["Contamination", "contamination", "CONTAM", "foreign_particle"]
}

inspection_rows = []
for idx, row in df_production.iterrows():
    b_id = row["batch"]
    line = row["line"]
    shift = row["shift"]
    machine = row["machine"]
    lot = row["lot"]
    qty = row["quantity"]
    
    m_info = df_machines[df_machines["machine"] == machine].iloc[0]
    mat_match = df_materials[df_materials["lot"] == lot]
    
    # Calculate defect probability and expected defect count
    base_rate = 0.022 # 2.2% base defect rate
    
    # Line impact
    if line == "Line_3":
        base_rate += 0.028
    elif line == "Line_4":
        base_rate += 0.020
    elif line == "Line_2":
        base_rate += 0.006
        
    # Shift impact
    if shift == "Shift_C":
        base_rate += 0.025
    elif shift == "Shift_B":
        base_rate += 0.008
        
    # Machine age impact
    if m_info["age_band"] == "> 5 Years":
        base_rate += 0.030
    elif m_info["age_band"] == "2-5 Years":
        base_rate += 0.010
        
    # Material quality impact
    if not mat_match.empty:
        mat_grade = mat_match.iloc[0]["material_grade"]
        if mat_grade == "Grade_C":
            base_rate += 0.024
        elif mat_grade == "Grade_B":
            base_rate += 0.008
    else:
        # Unmatched lots have slight uncertainty/higher rate
        base_rate += 0.020
        
    # Generate actual defect count using Poisson/Binomial distribution
    defect_count = np.random.binomial(qty, min(0.20, base_rate))
    
    # Determine dominant defect type and quality status
    if defect_count == 0:
        dominant_type = "None"
        quality_status = "Passed"
    else:
        # Defect type probabilities (Pareto: Surface Scratch & Dimensional Error dominate)
        dtype_weights = [0.42, 0.28, 0.16, 0.09, 0.05]
        category = random.choices(list(defect_raw_labels.keys()), weights=dtype_weights)[0]
        # Pick an inconsistent label representation
        dominant_type = random.choice(defect_raw_labels[category])
        
        defect_rate = defect_count / qty
        if defect_rate < 0.03:
            quality_status = random.choice(["Passed", "passed", "PASS"])
        elif defect_rate < 0.06:
            quality_status = random.choice(["Rework", "rework", "REWORK"])
        else:
            quality_status = random.choice(["Rejected", "rejected", "REJECT"])

    inspection_rows.append({
        "batch": b_id,
        "defect_type": dominant_type,
        "defect_count": defect_count,
        "quality_status": quality_status
    })

df_inspection = pd.DataFrame(inspection_rows)
df_inspection.to_csv(DATA_RAW_DIR / "inspection.csv", index=False)
print(f"Generated inspection.csv: {len(df_inspection)} records (with inconsistent defect labels)")

print("All 5 raw datasets generated successfully in data/raw/!")
