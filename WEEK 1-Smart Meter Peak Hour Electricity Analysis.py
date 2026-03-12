import pandas as pd
from sklearn.linear_model import LinearRegression
import plotly.express as px
import streamlit as st

# Path of dataset file
DATA_PATH = "D:\Hack-O-Week\Jan\Week 1\electricityloaddiagrams20112014\LD2011_2014.txt"

# Moving average window to smooth noise (3 hourly values)
SMOOTH_WINDOW = 3

# Evening peak hours (5 PM to 10 PM)
PEAK_HOURS = list(range(17, 23))

# Load the txt dataset 
@st.cache_data
def load_data():

    # Read text file:
    df = pd.read_csv(DATA_PATH, sep=";", decimal=",")

    df.rename(columns={df.columns[0]: "timestamp"}, inplace=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Set timestamp as index for time-series operations
    df.set_index("timestamp", inplace=True)

    return df

# Load full dataset (370 meters)
df = load_data()

# Convert kW readings (15 min) into kWh by dividing by 4
df_kwh = df / 4

# Convert 15-minute readings into hourly consumption
hourly_df = df_kwh.resample("H").sum()

# Select one meter for analysis (example MT_001)
meter_name = hourly_df.columns[0]
meter_df = hourly_df[[meter_name]].reset_index()
meter_df.columns = ["timestamp", "kwh"]


# Take only last 7 days because recent data gives better peak prediction
last_week = meter_df[
    meter_df["timestamp"] >= meter_df["timestamp"].max() - pd.Timedelta(days=7)
]

# Apply moving average smoothing to remove sudden spikes/noise
last_week["kwh_smooth"] = last_week["kwh"].rolling(
    SMOOTH_WINDOW, min_periods=1
).mean()

# Extract hour feature (important because electricity depends on time of day)
last_week["hour"] = last_week["timestamp"].dt.hour

# Extract weekday feature (weekday vs weekend consumption differs)
last_week["dayofweek"] = last_week["timestamp"].dt.dayofweek

# Train model only on evening peak hour records
train = last_week[last_week["hour"].isin(PEAK_HOURS)]

# Input features for model
X = train[["hour", "dayofweek"]]

# Target is smoothed electricity usage
y = train["kwh_smooth"]

# Linear Regression learns relationship between time and consumption
model = LinearRegression()
model.fit(X, y)

# Predict upcoming evening peak hours
future = pd.DataFrame({
    "hour": PEAK_HOURS,
    "dayofweek": [last_week["dayofweek"].iloc[-1]] * len(PEAK_HOURS)
})

future["pred_kwh"] = model.predict(future)

st.title("Smart Meter Peak Hour Electricity Analysis")

# Plot actual vs smoothed consumption
fig1 = px.line(
    last_week,
    x="timestamp",
    y=["kwh", "kwh_smooth"],
    title=f"Hourly Consumption Trend for {meter_name}"
)
st.plotly_chart(fig1, use_container_width=True)

# Plot predicted evening peaks
fig2 = px.bar(
    future,
    x="hour",
    y="pred_kwh",
    title="Predicted Evening Peak Electricity Usage"
)
st.plotly_chart(fig2, use_container_width=True)
