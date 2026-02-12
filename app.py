import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import date

# -------------------------------------------------
# ⚙️ CONFIGURATION
# -------------------------------------------------
st.set_page_config(page_title="Deepak's Fitness Dashboard", layout="wide")

FILE_NAME = "deepak_fitness_data.csv"

PROTEIN_TARGET = 160
CALORIE_TARGET = 2800

st.title("Deepak's Fitness Analytics Dashboard 💪")

# -------------------------------------------------
# 📁 CREATE FILE IF NOT EXISTS
# -------------------------------------------------
if not os.path.exists(FILE_NAME):
    df_init = pd.DataFrame(columns=[
        "Date","Weight","Calories","Protein","Carbs","Fats",
        "Steps","Water_L","Sleep_Hrs","Workout_Type",
        "Workout_Done","Volume"
    ])
    df_init.to_csv(FILE_NAME, index=False)

# Load data
df = pd.read_csv(FILE_NAME)

# -------------------------------------------------
# 📥 SIDEBAR DATA ENTRY
# -------------------------------------------------
st.sidebar.header("Add Daily Entry")

with st.sidebar.form("daily_form"):
    entry_date = st.date_input("Date", date.today())
    weight = st.number_input("Weight (kg)", 40.0, 150.0, step=0.1)
    calories = st.number_input("Calories", 0)
    protein = st.number_input("Protein (g)", 0)
    carbs = st.number_input("Carbs (g)", 0)
    fats = st.number_input("Fats (g)", 0)
    steps = st.number_input("Steps", 0)
    water = st.number_input("Water (Liters)", 0.0, 10.0, step=0.1)
    sleep = st.number_input("Sleep (Hours)", 0.0, 12.0, step=0.1)
    workout_type = st.selectbox("Workout Type", ["Push","Pull","Legs","Rest"])
    workout_done = st.selectbox("Workout Done?", [1,0])
    volume = st.number_input("Total Volume", 0)

    submitted = st.form_submit_button("Save Entry")

    if submitted:
        new_row = {
            "Date": entry_date,
            "Weight": weight,
            "Calories": calories,
            "Protein": protein,
            "Carbs": carbs,
            "Fats": fats,
            "Steps": steps,
            "Water_L": water,
            "Sleep_Hrs": sleep,
            "Workout_Type": workout_type,
            "Workout_Done": workout_done,
            "Volume": volume
        }

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(FILE_NAME, index=False)
        st.success("Entry Saved Successfully!")

# -------------------------------------------------
# 📊 PROCESS DATA
# -------------------------------------------------
if not df.empty:

    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")

    # 7-day moving average
    df["7_day_avg_weight"] = df["Weight"].rolling(7).mean()

    # Weekly grouping
    df["Week"] = df["Date"].dt.isocalendar().week
    weekly = df.groupby("Week").mean(numeric_only=True)

    # -------------------------------------------------
    # 📊 KPI SECTION
    # -------------------------------------------------
    st.subheader("Key Metrics")

    col1, col2, col3, col4 = st.columns(4)

    current_weight = df["Weight"].iloc[-1]
    avg_protein = df["Protein"].mean()
    workout_consistency = df["Workout_Done"].mean() * 100
    avg_sleep = df["Sleep_Hrs"].mean()

    col1.metric("Current Weight", f"{round(current_weight,1)} kg")
    col2.metric("Avg Protein",
                f"{round(avg_protein,1)} g",
                delta=round(avg_protein - PROTEIN_TARGET,1))
    col3.metric("Workout Consistency",
                f"{round(workout_consistency,1)}%")
    col4.metric("Avg Sleep",
                f"{round(avg_sleep,1)} hrs")

    # -------------------------------------------------
    # 📈 WEIGHT TREND
    # -------------------------------------------------
    st.subheader("Weight Trend (with 7-Day Moving Average)")
    fig1 = px.line(
        df,
        x="Date",
        y=["Weight","7_day_avg_weight"],
        markers=True
    )
    st.plotly_chart(fig1, use_container_width=True)

    # -------------------------------------------------
    # 🍗 PROTEIN INTAKE
    # -------------------------------------------------
    st.subheader("Protein Intake")
    fig2 = px.bar(df, x="Date", y="Protein")
    st.plotly_chart(fig2, use_container_width=True)

    # -------------------------------------------------
    # 🔥 CALORIES TREND
    # -------------------------------------------------
    st.subheader("Calories Trend")
    fig3 = px.line(df, x="Date", y="Calories", markers=True)
    st.plotly_chart(fig3, use_container_width=True)

    # -------------------------------------------------
    # 🏋️ WORKOUT DISTRIBUTION
    # -------------------------------------------------
    st.subheader("Workout Distribution")
    fig4 = px.pie(df, names="Workout_Type")
    st.plotly_chart(fig4, use_container_width=True)

    # -------------------------------------------------
    # 📅 WEEKLY SUMMARY TABLE
    # -------------------------------------------------
    st.subheader("Weekly Summary (Averages)")
    st.dataframe(weekly)

else:
    st.info("No data available. Add your first entry from the sidebar.")
