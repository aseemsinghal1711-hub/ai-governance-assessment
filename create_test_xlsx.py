"""Generate a sample bias testing results Excel file for testing the document processor."""
from openpyxl import Workbook

wb = Workbook()

# Sheet 1: Summary
ws1 = wb.active
ws1.title = "Summary"
ws1.append(["Bias Testing Results - Loan AI v2.3"])
ws1.append(["Test Date", "2026-04-15"])
ws1.append(["Tested By", "Data Science Team"])
ws1.append([])
ws1.append(["Metric", "Value", "Threshold", "Status"])
ws1.append(["Disparate Impact (Gender)", "0.92", ">= 0.80", "PASS"])
ws1.append(["Disparate Impact (Age)", "0.78", ">= 0.80", "FAIL"])
ws1.append(["Demographic Parity", "0.04", "<= 0.05", "PASS"])
ws1.append(["Equalized Odds", "0.06", "<= 0.05", "FAIL"])

# Sheet 2: Detail by attribute
ws2 = wb.create_sheet("By Attribute")
ws2.append(["Attribute", "Approval Rate", "Sample Size", "Notes"])
ws2.append(["Male", "73%", "12450", "Reference group"])
ws2.append(["Female", "68%", "11890", "Within tolerance"])
ws2.append(["Age 18-25", "61%", "8200", "Below threshold - investigation required"])
ws2.append(["Age 26-45", "76%", "18500", "Reference group"])
ws2.append(["Age 46-65", "72%", "9600", "Within tolerance"])
ws2.append(["Age 66+", "58%", "1200", "Below threshold - small sample"])

wb.save("sample_bias_results.xlsx")
print("Created sample_bias_results.xlsx")