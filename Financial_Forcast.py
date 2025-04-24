import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

# Set page config
st.set_page_config(page_title="10-Year Financial Forecast", layout="wide")
st.title("📊 10-Year Financial Forecast & Fundraising Simulator")

# Sidebar Inputs
st.sidebar.header("Input Parameters")

initial_revenue = st.sidebar.number_input("Initial Revenue ($)", value=500000.0, step=10000.0)
initial_marketing = st.sidebar.number_input("Initial Marketing Cost ($)", value=100000.0, step=5000.0)
initial_rnd = st.sidebar.number_input("Initial R&D Cost ($)", value=80000.0, step=5000.0)
initial_hr = st.sidebar.number_input("Initial HR Cost ($)", value=150000.0, step=5000.0)

# Asset and Liability Inputs
initial_cash = st.sidebar.number_input("Initial Cash ($)", value=100000.0)
initial_inventory = st.sidebar.number_input("Inventory ($)", value=40000.0)
initial_receivables = st.sidebar.number_input("Accounts Receivable ($)", value=50000.0)
initial_equipment = st.sidebar.number_input("Non-current Asset: Equipment ($)", value=200000.0)

initial_ap = st.sidebar.number_input("Accounts Payable ($)", value=30000.0)
initial_unearned = st.sidebar.number_input("Unearned Revenue ($)", value=20000.0)
initial_long_term_debt = st.sidebar.number_input("Long-term Debt ($)", value=100000.0)

years = 10

# Constants
inflation_rate = 0.04
marketing_growth = 0.10
rnd_growth = 0.15
hr_growth = 0.06
sales_decline_due_to_inflation = 0.01
sales_growth_due_to_expansion = 0.05
equipment_growth = 0.05
depreciation_years = 10

# Initialize forecast DataFrame
df = pd.DataFrame(index=range(1, years+1))
df.index.name = "Year"

# Revenue Forecast
revenue = [initial_revenue]
for i in range(1, years):
    new_revenue = revenue[-1] * (1 + sales_growth_due_to_expansion - sales_decline_due_to_inflation)
    revenue.append(new_revenue)
df["Revenue"] = revenue

# Cost Forecasts
marketing_cost = [initial_marketing * (1 + marketing_growth) ** i for i in range(years)]
rnd_cost = [initial_rnd * (1 + rnd_growth) ** i for i in range(years)]
hr_cost = [initial_hr * (1 + hr_growth) ** i for i in range(years)]
df["Marketing"] = marketing_cost
df["R&D"] = rnd_cost
df["HR"] = hr_cost

# Equipment investment and depreciation
equipment = [initial_equipment * (1 + equipment_growth) ** i for i in range(years)]
depreciation = [equipment[i]/depreciation_years for i in range(years)]
df["Depreciation"] = depreciation

# EBITDA Calculation
df["Operating Cost"] = df["Marketing"] + df["R&D"] + df["HR"]
df["EBITDA"] = df["Revenue"] - df["Operating Cost"]

# Track EBITDA %
df["EBITDA %"] = (df["EBITDA"] / df["Revenue"] * 100).round(2)

# Identify Year for 10% EBITDA and capital need trigger
ebitda_trigger_year = df[df["EBITDA %"] >= 10].index.min()

net_revenue = df["Revenue"] - df["Operating Cost"]
capital_needed_year = net_revenue[net_revenue < 0].index.min()

# Display Forecast Table
st.subheader("Forecast Table")
st.dataframe(df.style.format("{:.2f}"))

# Charts
st.subheader("📈 Key Forecast Charts")
fig, ax = plt.subplots(figsize=(10, 4))
df[["Revenue", "Operating Cost", "EBITDA"]].plot(ax=ax)
plt.ylabel("$ Value")
plt.title("Revenue, Operating Cost & EBITDA Over Time")
st.pyplot(fig)

# Display Triggers
st.subheader("🚨 Financial Milestones")
if not pd.isna(ebitda_trigger_year):
    st.success(f"✅ EBITDA reaches 10% in Year {ebitda_trigger_year}")
else:
    st.warning("⚠️ EBITDA does not reach 10% within 10 years")

if not pd.isna(capital_needed_year):
    st.error(f"💸 Capital financing needed in Year {capital_needed_year} (Net revenue goes negative)")
else:
    st.info("✅ Net revenue stays positive in all years")

# Export Option
st.subheader("📤 Export Forecast")
output = BytesIO()
df.to_excel(output, index=True, engine='openpyxl')
st.download_button(
    label="Download Forecast as Excel",
    data=output.getvalue(),
    file_name="financial_forecast.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.caption("Model assumes compound growth for cost and revenue, fixed-term receivables/payables handled implicitly.")
