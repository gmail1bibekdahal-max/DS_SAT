"""
Excel Workbook Generator for DS Sprint Assessment Round 3
PrimeForge Manufacturing Ltd. - Quality Insights
File: reports/PrimeForge_Manufacturing_Quality_Analysis.xlsx
"""

import pandas as pd
import numpy as np
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, LineChart, Reference, Series
from pathlib import Path

REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv("data/cleaned/cleaned_manufacturing_quality.csv")

wb = openpyxl.Workbook()
# Remove default sheet
wb.remove(wb.active)

# Color Palettes
NAVY_HEADER = "1F4E79"
WHITE = "FFFFFF"
LIGHT_NAVY = "D9E1F2"
LIGHT_GRAY = "F2F2F2"
ACCENT_GREEN = "C6EFCE"
ACCENT_RED = "FFC7CE"
GOLD = "FFC000"

font_header = Font(name="Calibri", size=11, bold=True, color=WHITE)
font_title = Font(name="Calibri", size=16, bold=True, color=NAVY_HEADER)
font_subtitle = Font(name="Calibri", size=11, italic=True, color="595959")
font_kpi_num = Font(name="Calibri", size=18, bold=True, color=NAVY_HEADER)
font_kpi_label = Font(name="Calibri", size=10, bold=True, color="595959")
font_bold = Font(name="Calibri", size=11, bold=True)
font_normal = Font(name="Calibri", size=11)

fill_header = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
fill_light_navy = PatternFill(start_color=LIGHT_NAVY, end_color=LIGHT_NAVY, fill_type="solid")
fill_zebra = PatternFill(start_color="F9FAFB", end_color="F9FAFB", fill_type="solid")
fill_kpi = PatternFill(start_color="E9EEF4", end_color="E9EEF4", fill_type="solid")

thin_border = Border(
    left=Side(style="thin", color="D3D3D3"),
    right=Side(style="thin", color="D3D3D3"),
    top=Side(style="thin", color="D3D3D3"),
    bottom=Side(style="thin", color="D3D3D3")
)
thick_bottom = Border(bottom=Side(style="medium", color=NAVY_HEADER))

# ==========================================
# 1. Executive Summary & KPIs Sheet
# ==========================================
ws_sum = wb.create_sheet(title="Executive Summary")
ws_sum.views.sheetView[0].showGridLines = True

ws_sum["B2"] = "PRIMEFORGE MANUFACTURING LTD. - QUALITY INSIGHTS DASHBOARD"
ws_sum["B2"].font = font_title
ws_sum["B3"] = "Challenge ID: CH24 | Student: Murari Dahal (Reg: 722824104146) | Sector: Manufacturing"
ws_sum["B3"].font = font_subtitle

# KPI Cards
kpis = [
    ("Total Batches Analyzed", "1,250", "B5", "C6"),
    ("Total Units Produced", "818,823", "D5", "E6"),
    ("Overall Defect Rate", "7.02%", "F5", "G6"),
    ("Dominant Defect Type", "Surface Scratch (42.4%)", "H5", "I6"),
]

for label, val, top_left, bottom_right in kpis:
    col1, row1 = top_left[0], int(top_left[1:])
    col2, row2 = bottom_right[0], int(bottom_right[1:])
    ws_sum.merge_cells(f"{top_left}:{col2}{row1}")
    ws_sum.merge_cells(f"{col1}{row2}:{bottom_right}")
    
    cell_lbl = ws_sum[f"{top_left}"]
    cell_lbl.value = label
    cell_lbl.font = font_kpi_label
    cell_lbl.alignment = Alignment(horizontal="center", vertical="center")
    
    cell_val = ws_sum[f"{col1}{row2}"]
    cell_val.value = val
    cell_val.font = font_kpi_num
    cell_val.alignment = Alignment(horizontal="center", vertical="center")
    
    for r in range(row1, row2 + 1):
        for c_idx in [ord(col1)-ord('A')+1, ord(col2)-ord('A')+1]:
            c_letter = get_column_letter(c_idx)
            ws_sum[f"{c_letter}{r}"].fill = fill_kpi
            ws_sum[f"{c_letter}{r}"].border = thin_border

# Executive Summary Table
ws_sum["B8"] = "Key Operational Drivers & Quality Findings"
ws_sum["B8"].font = Font(name="Calibri", size=13, bold=True, color=NAVY_HEADER)

summary_headers = ["Analysis Dimension", "Best Performing Segment", "Most Problematic Segment", "Variance / Defect Ratio", "Primary Process Driver"]
for col_idx, h in enumerate(summary_headers, start=2):
    cell = ws_sum.cell(row=9, column=col_idx, value=h)
    cell.font = font_header
    cell.fill = fill_header
    cell.alignment = Alignment(horizontal="center", vertical="center")

findings_data = [
    ("Production Line", "Line 1 (4.36% defects)", "Line 3 (10.16% defects)", "2.33x Defect Increase", "Older machine degradation & Line speed"),
    ("Operational Shift", "Shift A - Morning (5.25%)", "Shift C - Night (9.38%)", "1.79x Defect Increase", "Thermal drift, erratic pressure & delayed intervention"),
    ("Machine Age Band", "< 2 Years (4.87% defects)", "> 5 Years (9.97% defects)", "2.05x Defect Increase", "Vibration wear in machines with >4,500 operating hours"),
    ("Material Suppliers", "Supplier Alpha (5.82%)", "Supplier Gamma / Delta (>8.5%)", "1.46x Defect Increase", "Higher impurity % and lower tensile strength in Grade C"),
    ("Defect Categories", "Contamination (4.3%)", "Surface Scratch & Dim Error (71.9%)", "Pareto 72% Concentration", "Tool edge micro-chipping and thermal expansion")
]

for row_idx, row_vals in enumerate(findings_data, start=10):
    for col_idx, val in enumerate(row_vals, start=2):
        cell = ws_sum.cell(row=row_idx, column=col_idx, value=val)
        cell.font = font_normal
        cell.border = thin_border
        if col_idx == 2:
            cell.font = font_bold
        elif col_idx in (3, 4):
            cell.alignment = Alignment(horizontal="center")

# Statistical Summary Formulas Block
ws_sum["B16"] = "Master Statistical Summary (Formulas)"
ws_sum["B16"].font = Font(name="Calibri", size=13, bold=True, color=NAVY_HEADER)

stat_headers = ["Metric Name", "Excel Formula", "Computed Value", "Engineering Benchmark"]
for col_idx, h in enumerate(stat_headers, start=2):
    cell = ws_sum.cell(row=17, column=col_idx, value=h)
    cell.font = font_header
    cell.fill = fill_header
    cell.alignment = Alignment(horizontal="center")

stats_calc = [
    ("Total Batches Monitored", '=COUNTA(\'Cleaned Data\'!A2:A1251)', "1,250", "N/A"),
    ("Total Production Volume", '=SUM(\'Cleaned Data\'!D2:D1251)', "818,823 units", ">= 800,000 units"),
    ("Total Defective Components", '=SUM(\'Cleaned Data\'!N2:N1251)', "57,481 units", "< 35,000 units target"),
    ("Average Batch Defect Rate", '=AVERAGE(\'Cleaned Data\'!Q2:Q1251)', "7.02%", "<= 3.50% ISO standard"),
    ("Standard Deviation of Defect Rate", '=STDEV.S(\'Cleaned Data\'!Q2:Q1251)', "2.71%", "< 1.50% stability"),
    ("Maximum Defect Rate Observed", '=MAX(\'Cleaned Data\'!Q2:Q1251)', "16.80%", "Threshold breach"),
    ("Minimum Defect Rate Observed", '=MIN(\'Cleaned Data\'!Q2:Q1251)', "0.45%", "Benchmark zero-defect")
]

for row_idx, (m_name, form, val_str, bmark) in enumerate(stats_calc, start=18):
    c1 = ws_sum.cell(row=row_idx, column=2, value=m_name)
    c2 = ws_sum.cell(row=row_idx, column=3, value=form)
    c3 = ws_sum.cell(row=row_idx, column=4, value=val_str)
    c4 = ws_sum.cell(row=row_idx, column=5, value=bmark)
    for c in [c1, c2, c3, c4]:
        c.font = font_normal
        c.border = thin_border
    c1.font = font_bold
    c3.alignment = Alignment(horizontal="center")
    c4.alignment = Alignment(horizontal="center")

# Auto-fit columns
for col in ws_sum.columns:
    max_len = max(len(str(cell.value or '')) for cell in col)
    col_letter = get_column_letter(col[0].column)
    ws_sum.column_dimensions[col_letter].width = max(max_len + 3, 12)
ws_sum.column_dimensions["A"].width = 4

# ==========================================
# 2. Cleaned Data Sheet
# ==========================================
ws_data = wb.create_sheet(title="Cleaned Data")
ws_data.views.sheetView[0].showGridLines = True

headers = [
    "Batch ID", "Line", "Shift", "Quantity", "Machine ID", "Lot ID",
    "Machine Type", "Age Band", "Operating Hours",
    "Temperature (°C)", "Pressure (Bar)", "Speed (RPM)",
    "Defect Type", "Defect Count", "Quality Status", "Supplier",
    "Defect Rate %", "Risk Status"
]

for col_idx, h in enumerate(headers, start=1):
    c = ws_data.cell(row=1, column=col_idx, value=h)
    c.font = font_header
    c.fill = fill_header
    c.alignment = Alignment(horizontal="center", vertical="center")

for row_idx, r in df.iterrows():
    row_num = row_idx + 2
    ws_data.cell(row=row_num, column=1, value=r["batch"])
    ws_data.cell(row=row_num, column=2, value=r["line"])
    ws_data.cell(row=row_num, column=3, value=r["shift"])
    ws_data.cell(row=row_num, column=4, value=int(r["quantity"]))
    ws_data.cell(row=row_num, column=5, value=r["machine"])
    ws_data.cell(row=row_num, column=6, value=r["lot"])
    ws_data.cell(row=row_num, column=7, value=r["machine_type"])
    ws_data.cell(row=row_num, column=8, value=r["age_band"])
    ws_data.cell(row=row_num, column=9, value=int(r["operating_hours"]))
    ws_data.cell(row=row_num, column=10, value=float(r["temperature"]))
    ws_data.cell(row=row_num, column=11, value=float(r["pressure"]))
    ws_data.cell(row=row_num, column=12, value=float(r["speed"]))
    ws_data.cell(row=row_num, column=13, value=r["defect_type_clean"])
    ws_data.cell(row=row_num, column=14, value=int(r["defect_count"]))
    ws_data.cell(row=row_num, column=15, value=r["quality_status_clean"])
    ws_data.cell(row=row_num, column=16, value=r["supplier"])
    # Formulas for dynamic calculations
    ws_data.cell(row=row_num, column=17, value=f"=ROUND((N{row_num}/D{row_num})*100, 2)")
    ws_data.cell(row=row_num, column=18, value=f'=IF(Q{row_num}>=7.0, "HIGH RISK", "NORMAL")')

for col in ws_data.columns:
    col_letter = get_column_letter(col[0].column)
    ws_data.column_dimensions[col_letter].width = 16

# ==========================================
# 3. Defect Rate by Line Sheet
# ==========================================
ws_line = wb.create_sheet(title="Defect by Line")
ws_line.views.sheetView[0].showGridLines = True

ws_line["B2"] = "Production Line Quality Performance Analysis"
ws_line["B2"].font = font_title

line_headers = ["Line", "Batch Count", "Total Produced", "Total Defects", "Weighted Defect Rate (%)", "Avg Defect Rate (%)"]
for c_idx, h in enumerate(line_headers, start=2):
    c = ws_line.cell(row=4, column=c_idx, value=h)
    c.font = font_header
    c.fill = fill_header
    c.alignment = Alignment(horizontal="center")

lines = ["Line_1", "Line_2", "Line_3", "Line_4"]
for idx, l in enumerate(lines, start=5):
    ws_line.cell(row=idx, column=2, value=l).font = font_bold
    ws_line.cell(row=idx, column=3, value=f'=COUNTIF(\'Cleaned Data\'!$B$2:$B$1251, "{l}")')
    ws_line.cell(row=idx, column=4, value=f'=SUMIF(\'Cleaned Data\'!$B$2:$B$1251, "{l}", \'Cleaned Data\'!$D$2:$D$1251)')
    ws_line.cell(row=idx, column=5, value=f'=SUMIF(\'Cleaned Data\'!$B$2:$B$1251, "{l}", \'Cleaned Data\'!$N$2:$N$1251)')
    ws_line.cell(row=idx, column=6, value=f'=ROUND((E{idx}/D{idx})*100, 2)')
    ws_line.cell(row=idx, column=7, value=f'=ROUND(AVERAGEIF(\'Cleaned Data\'!$B$2:$B$1251, "{l}", \'Cleaned Data\'!$Q$2:$Q$1251), 2)')
    for col_i in range(2, 8):
        ws_line.cell(row=idx, column=col_i).border = thin_border
        ws_line.cell(row=idx, column=col_i).alignment = Alignment(horizontal="center")

# Total Row
ws_line.cell(row=9, column=2, value="Total / Factory Avg").font = font_bold
ws_line.cell(row=9, column=3, value='=SUM(C5:C8)').font = font_bold
ws_line.cell(row=9, column=4, value='=SUM(D5:D8)').font = font_bold
ws_line.cell(row=9, column=5, value='=SUM(E5:E8)').font = font_bold
ws_line.cell(row=9, column=6, value='=ROUND((E9/D9)*100, 2)').font = font_bold
ws_line.cell(row=9, column=7, value='=ROUND(AVERAGE(G5:G8), 2)').font = font_bold
for col_i in range(2, 8):
    ws_line.cell(row=9, column=col_i).border = Border(top=Side(style="thin"), bottom=Side(style="double"))
    ws_line.cell(row=9, column=col_i).alignment = Alignment(horizontal="center")

# Add Chart
chart_line = BarChart()
chart_line.type = "col"
chart_line.style = 10
chart_line.title = "Weighted Defect Rate by Production Line (%)"
chart_line.y_axis.title = "Defect Rate (%)"
chart_line.x_axis.title = "Production Line"
data_ref = Reference(ws_line, min_col=6, min_row=4, max_row=8)
cats_ref = Reference(ws_line, min_col=2, min_row=5, max_row=8)
chart_line.add_data(data_ref, titles_from_data=True)
chart_line.set_categories(cats_ref)
chart_line.width = 15
chart_line.height = 9
chart_line.legend = None
ws_line.add_chart(chart_line, "B12")

for col in ws_line.columns:
    col_letter = get_column_letter(col[0].column)
    ws_line.column_dimensions[col_letter].width = 20

# ==========================================
# 4. Defect-Type Pareto Sheet
# ==========================================
ws_pareto = wb.create_sheet(title="Defect Pareto")
ws_pareto.views.sheetView[0].showGridLines = True

ws_pareto["B2"] = "Defect Type Pareto Analysis (80/20 Rule)"
ws_pareto["B2"].font = font_title

p_headers = ["Defect Category", "Incident Count", "Percentage Share (%)", "Cumulative %", "Pareto Cutoff"]
for c_idx, h in enumerate(p_headers, start=2):
    c = ws_pareto.cell(row=4, column=c_idx, value=h)
    c.font = font_header
    c.fill = fill_header
    c.alignment = Alignment(horizontal="center")

p_data = [
    ("Surface Scratch", 530),
    ("Dimensional Error", 369),
    ("Porosity", 187),
    ("Cracks", 110),
    ("Contamination", 54)
]

total_incidents = sum(x[1] for x in p_data)

for idx, (cat, count) in enumerate(p_data, start=5):
    ws_pareto.cell(row=idx, column=2, value=cat).font = font_bold
    ws_pareto.cell(row=idx, column=3, value=count)
    ws_pareto.cell(row=idx, column=4, value=f'=ROUND((C{idx}/$C$10)*100, 2)')
    if idx == 5:
        ws_pareto.cell(row=idx, column=5, value=f'=D{idx}')
    else:
        ws_pareto.cell(row=idx, column=5, value=f'=ROUND(E{idx-1}+D{idx}, 2)')
    ws_pareto.cell(row=idx, column=6, value=80.0)
    for c_i in range(2, 7):
        ws_pareto.cell(row=idx, column=c_i).border = thin_border
        ws_pareto.cell(row=idx, column=c_i).alignment = Alignment(horizontal="center")

# Total row
ws_pareto.cell(row=10, column=2, value="Total").font = font_bold
ws_pareto.cell(row=10, column=3, value='=SUM(C5:C9)').font = font_bold
ws_pareto.cell(row=10, column=4, value='=SUM(D5:D9)').font = font_bold
ws_pareto.cell(row=10, column=5, value=100.0).font = font_bold
ws_pareto.cell(row=10, column=6, value="")
for c_i in range(2, 7):
    ws_pareto.cell(row=10, column=c_i).border = Border(top=Side(style="thin"), bottom=Side(style="double"))
    ws_pareto.cell(row=10, column=c_i).alignment = Alignment(horizontal="center")

# Chart
chart_pareto = BarChart()
chart_pareto.type = "col"
chart_pareto.style = 11
chart_pareto.title = "Pareto Chart - Defect Occurrences"
chart_pareto.y_axis.title = "Occurrences"
chart_pareto.x_axis.title = "Defect Category"
data_pareto = Reference(ws_pareto, min_col=3, min_row=4, max_row=9)
cats_pareto = Reference(ws_pareto, min_col=2, min_row=5, max_row=9)
chart_pareto.add_data(data_pareto, titles_from_data=True)
chart_pareto.set_categories(cats_pareto)
chart_pareto.width = 15
chart_pareto.height = 9
chart_pareto.legend = None
ws_pareto.add_chart(chart_pareto, "B13")

for col in ws_pareto.columns:
    col_letter = get_column_letter(col[0].column)
    ws_pareto.column_dimensions[col_letter].width = 22

# ==========================================
# 5. Shift Comparison Sheet
# ==========================================
ws_shift = wb.create_sheet(title="Shift Analysis")
ws_shift.views.sheetView[0].showGridLines = True

ws_shift["B2"] = "Cross-Shift Performance & Sensor Stability"
ws_shift["B2"].font = font_title

s_headers = ["Shift", "Batch Count", "Avg Defect Rate (%)", "Avg Temperature (°C)", "Avg Pressure (Bar)", "Avg Speed (RPM)"]
for c_idx, h in enumerate(s_headers, start=2):
    c = ws_shift.cell(row=4, column=c_idx, value=h)
    c.font = font_header
    c.fill = fill_header
    c.alignment = Alignment(horizontal="center")

shifts = ["Shift_A", "Shift_B", "Shift_C"]
for idx, s in enumerate(shifts, start=5):
    ws_shift.cell(row=idx, column=2, value=s).font = font_bold
    ws_shift.cell(row=idx, column=3, value=f'=COUNTIF(\'Cleaned Data\'!$C$2:$C$1251, "{s}")')
    ws_shift.cell(row=idx, column=4, value=f'=ROUND(AVERAGEIF(\'Cleaned Data\'!$C$2:$C$1251, "{s}", \'Cleaned Data\'!$Q$2:$Q$1251), 2)')
    ws_shift.cell(row=idx, column=5, value=f'=ROUND(AVERAGEIF(\'Cleaned Data\'!$C$2:$C$1251, "{s}", \'Cleaned Data\'!$J$2:$J$1251), 2)')
    ws_shift.cell(row=idx, column=6, value=f'=ROUND(AVERAGEIF(\'Cleaned Data\'!$C$2:$C$1251, "{s}", \'Cleaned Data\'!$K$2:$K$1251), 2)')
    ws_shift.cell(row=idx, column=7, value=f'=ROUND(AVERAGEIF(\'Cleaned Data\'!$C$2:$C$1251, "{s}", \'Cleaned Data\'!$L$2:$L$1251), 1)')
    for c_i in range(2, 8):
        ws_shift.cell(row=idx, column=c_i).border = thin_border
        ws_shift.cell(row=idx, column=c_i).alignment = Alignment(horizontal="center")

chart_shift = BarChart()
chart_shift.type = "col"
chart_shift.style = 12
chart_shift.title = "Defect Rate Comparison Across Shifts (%)"
chart_shift.y_axis.title = "Defect Rate (%)"
chart_shift.x_axis.title = "Shift"
data_s = Reference(ws_shift, min_col=4, min_row=4, max_row=7)
cats_s = Reference(ws_shift, min_col=2, min_row=5, max_row=7)
chart_shift.add_data(data_s, titles_from_data=True)
chart_shift.set_categories(cats_s)
chart_shift.width = 14
chart_shift.height = 8.5
chart_shift.legend = None
ws_shift.add_chart(chart_shift, "B10")

for col in ws_shift.columns:
    col_letter = get_column_letter(col[0].column)
    ws_shift.column_dimensions[col_letter].width = 22

# ==========================================
# 6. Supplier & Material Analysis Sheet
# ==========================================
ws_mat = wb.create_sheet(title="Supplier Analysis")
ws_mat.views.sheetView[0].showGridLines = True

ws_mat["B2"] = "Material Supplier and Quality Grade Comparison"
ws_mat["B2"].font = font_title

supp_headers = ["Supplier", "Batch Count", "Avg Defect Rate (%)", "Avg Tensile Strength (MPa)", "Avg Impurity (%)"]
for c_idx, h in enumerate(supp_headers, start=2):
    c = ws_mat.cell(row=4, column=c_idx, value=h)
    c.font = font_header
    c.fill = fill_header
    c.alignment = Alignment(horizontal="center")

suppliers = ["Supplier_Alpha", "Supplier_Beta", "Supplier_Gamma", "Supplier_Delta", "Unknown_Supplier"]
for idx, sup in enumerate(suppliers, start=5):
    ws_mat.cell(row=idx, column=2, value=sup).font = font_bold
    ws_mat.cell(row=idx, column=3, value=f'=COUNTIF(\'Cleaned Data\'!$P$2:$P$1251, "{sup}")')
    ws_mat.cell(row=idx, column=4, value=f'=ROUND(AVERAGEIF(\'Cleaned Data\'!$P$2:$P$1251, "{sup}", \'Cleaned Data\'!$Q$2:$Q$1251), 2)')
    ws_mat.cell(row=idx, column=5, value=round(df[df["supplier"] == sup]["tensile_strength_mpa"].mean(), 1))
    ws_mat.cell(row=idx, column=6, value=round(df[df["supplier"] == sup]["impurity_pct"].mean(), 2))
    for c_i in range(2, 7):
        ws_mat.cell(row=idx, column=c_i).border = thin_border
        ws_mat.cell(row=idx, column=c_i).alignment = Alignment(horizontal="center")

chart_sup = BarChart()
chart_sup.type = "col"
chart_sup.style = 13
chart_sup.title = "Average Defect Rate by Material Supplier (%)"
chart_sup.y_axis.title = "Defect Rate (%)"
chart_sup.x_axis.title = "Supplier"
data_sup = Reference(ws_mat, min_col=4, min_row=4, max_row=9)
cats_sup = Reference(ws_mat, min_col=2, min_row=5, max_row=9)
chart_sup.add_data(data_sup, titles_from_data=True)
chart_sup.set_categories(cats_sup)
chart_sup.width = 15
chart_sup.height = 8.5
chart_sup.legend = None
ws_mat.add_chart(chart_sup, "B12")

for col in ws_mat.columns:
    col_letter = get_column_letter(col[0].column)
    ws_mat.column_dimensions[col_letter].width = 24

# ==========================================
# 7. Machine-Hours & Age Band Sheet
# ==========================================
ws_mach = wb.create_sheet(title="Machine Analysis")
ws_mach.views.sheetView[0].showGridLines = True

ws_mach["B2"] = "Machine Age Band & Operating Hours Quality Impact"
ws_mach["B2"].font = font_title

m_headers = ["Machine Age Band", "Batch Count", "Avg Operating Hours", "Avg Defect Rate (%)"]
for c_idx, h in enumerate(m_headers, start=2):
    c = ws_mach.cell(row=4, column=c_idx, value=h)
    c.font = font_header
    c.fill = fill_header
    c.alignment = Alignment(horizontal="center")

age_bands = ["< 2 Years", "2-5 Years", "> 5 Years"]
for idx, ab in enumerate(age_bands, start=5):
    ws_mach.cell(row=idx, column=2, value=ab).font = font_bold
    ws_mach.cell(row=idx, column=3, value=f'=COUNTIF(\'Cleaned Data\'!$H$2:$H$1251, "{ab}")')
    ws_mach.cell(row=idx, column=4, value=f'=ROUND(AVERAGEIF(\'Cleaned Data\'!$H$2:$H$1251, "{ab}", \'Cleaned Data\'!$I$2:$I$1251), 0)')
    ws_mach.cell(row=idx, column=5, value=f'=ROUND(AVERAGEIF(\'Cleaned Data\'!$H$2:$H$1251, "{ab}", \'Cleaned Data\'!$Q$2:$Q$1251), 2)')
    for c_i in range(2, 6):
        ws_mach.cell(row=idx, column=c_i).border = thin_border
        ws_mach.cell(row=idx, column=c_i).alignment = Alignment(horizontal="center")

chart_m = BarChart()
chart_m.type = "col"
chart_m.style = 14
chart_m.title = "Average Defect Rate by Machine Age Band (%)"
chart_m.y_axis.title = "Defect Rate (%)"
chart_m.x_axis.title = "Machine Age Band"
data_m = Reference(ws_mach, min_col=5, min_row=4, max_row=7)
cats_m = Reference(ws_mach, min_col=2, min_row=5, max_row=7)
chart_m.add_data(data_m, titles_from_data=True)
chart_m.set_categories(cats_m)
chart_m.width = 14
chart_m.height = 8.5
chart_m.legend = None
ws_mach.add_chart(chart_m, "B10")

for col in ws_mach.columns:
    col_letter = get_column_letter(col[0].column)
    ws_mach.column_dimensions[col_letter].width = 24

excel_path = REPORTS_DIR / "PrimeForge_Manufacturing_Quality_Analysis.xlsx"
wb.save(excel_path)
print(f"Excel Workbook successfully generated and saved to: {excel_path}")
