# DS Sprint – Skill Based Assessment 2 | Challenge CH24
## Use Case 24: Manufacturing Quality Insight
### *Understand Defects. Discover Process Patterns. Improve Quality.*

**Student Name:** MURARI DAHAL  
**Register Number:** 722824104146  
**Class:** CSE (Batch 2024–2028)  
**Institution:** Sri Eshwar College of Engineering, Coimbatore  
**Course Code:** U23AD491 – Data Science  
**Target Organization:** PrimeForge Manufacturing Ltd. (Precision Engineered Components)  

---

## 📌 Business Overview
PrimeForge produces high-precision engineered metal components and seeks to identify root causes behind elevated defect levels across manufacturing lines, shifts, machinery, and raw material lots.

**Core Business Question:**  
> *Which production conditions are associated with higher defect levels?*

---

## 📂 Repository Structure
```
DS_SAT/
├── data/
│   ├── raw/                                     # 5 raw multi-source datasets
│   │   ├── production.csv                       # Batch, Line, Shift, Quantity
│   │   ├── machines.csv                         # Machine, Age Band, Operating Hours
│   │   ├── process.csv                          # Temperature, Pressure, Speed
│   │   ├── materials.csv                        # Supplier, Material Grade, Lot
│   │   └── inspection.csv                       # Defect Type, Defect Count, Quality Status
│   └── cleaned/
│       └── cleaned_manufacturing_quality.csv    # Master cleaned dataset (1,250 records, 22 features)
├── notebooks/
│   └── eda_and_feature_engineering.ipynb        # Complete interactive Jupyter Notebook
├── src/
│   ├── generate_raw_data.py                     # Raw dataset generator with intentional quality anomalies
│   ├── data_cleaning.py                         # Resolves 5 mandated data quality challenges
│   ├── eda_and_visualization.py                 # Generates high-resolution EDA figures
│   ├── feature_engineering_ml.py                # Feature extraction & Random Forest predictive model
│   ├── build_excel_workbook.py                  # Generates automated Excel workbook with charts & formulas
│   └── generate_presentation.py                 # Generates 9-slide executive pitch presentation
├── figures/                                     # Publication-quality charts (300 DPI)
│   ├── 01_defect_rate_by_line.png
│   ├── 02_defect_type_pareto.png
│   ├── 03_shift_comparison.png
│   ├── 04_process_variables_vs_defects.png
│   ├── 05_supplier_material_grade_analysis.png
│   ├── 06_machine_operating_hours_vs_defects.png
│   ├── 07_correlation_matrix.png
│   └── 08_feature_importance.png
├── reports/
│   ├── PrimeForge_Manufacturing_Quality_Analysis.xlsx  # Multi-sheet Excel workbook with formulas & charts
│   ├── PrimeForge_Quality_Insights_Pitch.pptx          # 9-slide PowerPoint presentation deck
│   └── ASSESSMENT_SUBMISSION_SHEET.md                  # Completed submission sheet for professor
├── requirements.txt
└── README.md
```

---

## 🔍 Resolution of 5 Mandated Data Quality Conditions
1. **Duplicate Batch Records:** Detected and eliminated 30 duplicate records in `production.csv`.
2. **Inconsistent Defect Labels:** Normalized 23 noisy string labels into 5 canonical groups (*Surface Scratch, Dimensional Error, Porosity, Cracks, Contamination*).
3. **Extreme Sensor Values:** Identified 36 extreme unphysical outliers (e.g., negative or 999 values) and flagged them.
4. **Missing Process Readings:** Imputed 194 null sensor values (temperature, pressure, speed) using robust median imputation grouped by operational lines.
5. **Unmatched Material Lots:** Reconciled 35 orphan batch lots lacking direct material mappings via fallback defaults.

---

## 📊 Key Findings from Analysis
1. **Line 3 & Aging Machinery:** Production Line 3 has a defect rate of **10.16%**—more than double Line 1 (**4.36%**). Machines in the `>5 Years` band with over 6,500 operating hours suffer a **9.97%** defect rate.
2. **Pareto 80/20 Principle:** *Surface Scratches* (42.40%) and *Dimensional Errors* (29.52%) account for **71.92%** of all defects.
3. **Night Shift Disparity:** Night Shift C experiences a defect rate of **9.38%** vs Morning Shift A (**5.25%**), driven by thermal drift (212.4°C vs 205°C setpoint) and reduced supervisory checks.
4. **Material Degradation:** Grade C materials from Supplier Gamma and Delta yield defect rates exceeding **8.5%**, correlated with elevated impurity percentages.

---

## 🤖 Machine Learning Model Performance
- **Model:** Random Forest Classifier (150 trees, max depth = 8)
- **Target:** High Defect Risk Batch (defect rate ≥ 7.0%)
- **Accuracy:** **86.40%**
- **Precision:** **88.89%**
- **Recall:** **83.20%**
- **F1-Score:** **0.8595**
- **ROC-AUC:** **0.9480**
- **Defect Rate RMSE:** **2.72%** (Random Forest Regressor)

**Top Predictive Features:**
1. `machine_wear_index` (16.69%)
2. `operating_hours` (14.89%)
3. `age_band` (13.42%)
4. `line` (13.42%)
5. `shift` (7.16%)
6. `temperature` (4.85%)

---

## 💼 Strategic Recommendations & ROI
1. **Preventive Machine Maintenance:** Overhaul Line 3 machines and enforce automated service thresholds at 4,500 operating hours. *(Expected impact: -40% defect rate on Line 3)*
2. **Automated Night Shift Thermal Safeguards:** Deploy edge sensors with ±5°C thermal deviation alarms and implement a mandatory 02:00 AM calibration check. *(Expected impact: -35% defect rate in Shift C)*
3. **Supplier Material Standards:** Eliminate Grade C lots with >1.2% impurity and establish a 480 MPa minimum tensile strength standard. *(Expected impact: -18% defect rate)*
4. **Financial Impact:** Projected reduction of overall factory defect rate from **7.02% to <3.50%**, yielding over **$420,000** in annual scrap savings.

---

## 🚀 How to Run the Pipeline
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate raw datasets (with quality anomalies)
python src/generate_raw_data.py

# 3. Clean and merge datasets
python src/data_cleaning.py

# 4. Generate EDA visualizations
python src/eda_and_visualization.py

# 5. Train ML model & extract metrics
python src/feature_engineering_ml.py

# 6. Build Excel workbook
python src/build_excel_workbook.py

# 7. Generate PowerPoint presentation
python src/generate_presentation.py
```
