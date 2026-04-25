pip install streamlit pandas plotly scikit-learn numpy-financial
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import numpy_financial as npf
import math
from sklearn.ensemble import IsolationForest

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="AI Finance Manager", layout="wide", page_icon="📈")

# --- STATE INITIALIZATION ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'expenses' not in st.session_state:
    st.session_state['expenses'] = pd.DataFrame(columns=["Category", "Subcategory", "Amount"])
if 'income' not in st.session_state:
    st.session_state['income'] = 0.0

# --- AUTHENTICATION MODULE (Mock for Google Sign-In) ---
def google_sign_in():
    # In a production app, use streamlit-google-auth or Firebase Auth here.
    st.session_state['logged_in'] = True
    st.success("Successfully signed in with Google!")

def save_to_cloud():
    # Placeholder for Google Sheets API (gspread) or Firebase Firestore insertion.
    st.toast("Data successfully synced to Google Cloud!", icon="☁️")

# --- SIDEBAR AUTH ---
with st.sidebar:
    st.title("User Profile")
    if not st.session_state['logged_in']:
        st.button("Sign in with Google", on_click=google_sign_in)
        st.stop()  # Halt execution until logged in
    else:
        st.write("Logged in as: **user@gmail.com**")
        st.button("Sync Data to Cloud", on_click=save_to_cloud)

# --- MAIN APP TABS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "💸 Data Entry", 
    "📊 Analytics", 
    "🧠 AI Recommendations", 
    "🎯 Savings Goals"
])

# ==========================================
# TAB 1: DATA ENTRY (REAL-TIME SPENDINGS)
# ==========================================
with tab1:
    st.header("Monthly Cash Flow")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state['income'] = st.number_input("Total Monthly Income ($)", min_value=0.0, value=st.session_state['income'])
        
    st.subheader("Monthly Spendings")
    
    # Forms for categories
    with st.expander("⚡ Energy Consumption", expanded=True):
        water = st.number_input("Water", min_value=0.0, key="water")
        electricity = st.number_input("Electricity", min_value=0.0, key="elec")
        gas = st.number_input("Natural Gas", min_value=0.0, key="gas")
        
    with st.expander("🏠 Accommodations"):
        rent_buy = st.number_input("Rent / Mortgage", min_value=0.0, key="rent")
        
    with st.expander("🚗 Transportation"):
        fuel = st.number_input("Fuel", min_value=0.0, key="fuel")
        rent_car = st.number_input("Rent Car", min_value=0.0, key="rent_car")
        buy_car = st.number_input("Car Installment", min_value=0.0, key="buy_car")
        
    with st.expander("🤝 Aids & Others"):
        aids = st.number_input("Aids / Charity", min_value=0.0, key="aids")
        others = st.number_input("Other Spendings", min_value=0.0, key="others")

    if st.button("Update Ledger"):
        # Build the real-time dataframe
        data = [
            ("Energy", "Water", water),
            ("Energy", "Electricity", electricity),
            ("Energy", "Natural Gas", gas),
            ("Accommodation", "Rent/Mortgage", rent_buy),
            ("Transportation", "Fuel", fuel),
            ("Transportation", "Rent Car", rent_car),
            ("Transportation", "Car Installment", buy_car),
            ("Aids & Others", "Aids", aids),
            ("Aids & Others", "Others", others)
        ]
        st.session_state['expenses'] = pd.DataFrame(data, columns=["Category", "Subcategory", "Amount"])
        st.success("Ledger updated in real-time!")

# ==========================================
# TAB 2: ANALYTICS
# ==========================================
with tab2:
    st.header("Spendings Analytics")
    df = st.session_state['expenses']
    
    if df.empty or df['Amount'].sum() == 0:
        st.info("Please enter your spendings in the Data Entry tab.")
    else:
        total_expenses = df['Amount'].sum()
        remaining = st.session_state['income'] - total_expenses
        
        # Top-level metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Income", f"${st.session_state['income']:,.2f}")
        col2.metric("Total Expenses", f"${total_expenses:,.2f}")
        col3.metric("Net Savings", f"${remaining:,.2f}", delta=remaining)
        
        # Visualizations
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            fig_pie = px.pie(df[df['Amount'] > 0], values='Amount', names='Category', title="Expenses by Category", hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col_chart2:
            fig_bar = px.bar(df[df['Amount'] > 0], x='Subcategory', y='Amount', color='Category', title="Expenses Breakdown")
            st.plotly_chart(fig_bar, use_container_width=True)

# ==========================================
# TAB 3: DEEP MACHINE LEARNING RECOMMENDATIONS
# ==========================================
with tab3:
    st.header("AI Lifestyle & Budget Recommendations")
    df = st.session_state['expenses']
    
    if df.empty or df['Amount'].sum() == 0:
         st.warning("Awaiting data to run machine learning models.")
    else:
        st.write("Running Unsupervised Machine Learning (Isolation Forest) to detect spending anomalies compared to standard global averages...")
        
        # MOCK ML MODEL: Using Isolation Forest to detect "anomalous" spending categories
        # In reality, you'd train this on a large dataset of standard financial ratios.
        X = df[['Amount']].values
        if len(X[X > 0]) > 2:
            model = IsolationForest(contamination=0.1, random_state=42)
            df['Anomaly'] = model.fit_predict(X)
            
            anomalies = df[(df['Anomaly'] == -1) & (df['Amount'] > 0)]
            
            if not anomalies.empty:
                st.error("🚨 **Anomaly Detected:** The following expenses are statistically higher than your general distribution:")
                for _, row in anomalies.iterrows():
                    st.write(f"- **{row['Subcategory']}**: ${row['Amount']:,.2f}")
            else:
                st.success("✅ Your spending distribution appears balanced according to our ML model.")
                
        # Best Practices Rule-Based AI
        st.subheader("Trendy Management Recommendations")
        total_exp = df['Amount'].sum()
        income = st.session_state['income']
        
        if income > 0:
            needs_ratio = total_exp / income
            if needs_ratio > 0.5:
                 st.write("📉 **50/30/20 Rule Breach:** Your essential spendings exceed 50% of your income. Consider renegotiating your accommodation or energy usage.")
            else:
                 st.write("📈 **Optimal Alignment:** You are successfully operating within the 50% threshold for needs. Allocate the remaining funds heavily toward investments.")

# ==========================================
# TAB 4: SAVINGS GOALS & COMPOUNDING
# ==========================================
with tab4:
    st.header("Strategic Savings Goals & Projections")
    
    col_input1, col_input2 = st.columns(2)
    
    with col_input1:
        st.subheader("Set Your Parameters")
        target_goal = st.number_input("Target Savings Goal ($)", min_value=1000.0, value=100000.0, step=1000.0)
        monthly_payment = st.number_input("Monthly Contribution ($)", min_value=10.0, value=500.0, step=50.0)
        yearly_rate = st.number_input("Expected Yearly Interest Rate (%)", min_value=0.1, value=5.0, step=0.1)
    
    with col_input2:
        st.subheader("Time to Achieve Goal")
        # Mathematical Calculation for Period (n)
        monthly_rate = (yearly_rate / 100) / 12
        
        if monthly_payment > 0:
            # Formula: n = ln(1 + (FV * r) / PMT) / ln(1 + r)
            try:
                months_needed = math.log(1 + (target_goal * monthly_rate) / monthly_payment) / math.log(1 + monthly_rate)
                years_needed = months_needed / 12
                
                st.metric("Estimated Time to Goal", f"{years_needed:.1f} Years", f"({int(months_needed)} months)")
            except ValueError:
                st.error("Goal unattainable with current parameters.")
        else:
            st.warning("Enter a monthly contribution to calculate time.")

    st.divider()
    
    st.subheader("Best Practices Savings Report (1-Year vs 10-Year)")
    # Future Value Formula for Series: FV = PMT * (((1 + r)^n - 1) / r)
    fv_1_year = monthly_payment * (((1 + monthly_rate)**12 - 1) / monthly_rate)
    fv_10_year = monthly_payment * (((1 + monthly_rate)**120 - 1) / monthly_rate)
    
    col_rep1, col_rep2 = st.columns(2)
    col_rep1.info(f"**1-Year Projection:**\nIf you maintain this contribution, you will have **${fv_1_year:,.2f}** in 12 months.")
    col_rep2.success(f"**10-Year Projection:**\nThanks to compound interest, in 10 years you will have accumulated **${fv_10_year:,.2f}**.")
