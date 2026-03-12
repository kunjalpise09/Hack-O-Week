import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA

# Dataset path
DATA_PATH = "D:\Hack-O-Week\Jan\Week 2\Occupancy_Estimation.csv"

st.title("Classroom Usage Forecasting")

# LOAD DATA
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)

    # Create timestamp
    df["timestamp"] = pd.to_datetime(df["Date"] + " " + df["Time"])
    df.set_index("timestamp", inplace=True)

    # Use occupancy as proxy for electricity draw
    df = df[["Room_Occupancy_Count"]]

    return df

df = load_data()

# RESAMPLE TO HOURLY 
hourly_df = df.resample("H").mean()

# Use last 3 days for better trend visibility
recent = hourly_df.last("3D")

series = recent["Room_Occupancy_Count"]

#ARIMA MODEL 
model = ARIMA(series, order=(1,1,1))
model_fit = model.fit()

#  FORECAST NEXT HOUR 
forecast = model_fit.get_forecast(steps=1)
pred = forecast.predicted_mean
conf_int = forecast.conf_int()

#  PLOT
fig = plt.figure(figsize=(10,5))

# Plot recent usage
plt.plot(series.index, series.values, linewidth=2, label="Recent Classroom Usage")

# Plot forecast point
plt.scatter(pred.index, pred.values, s=80, label="Next-Hour Prediction")

# Confidence interval
plt.fill_between(
    conf_int.index,
    conf_int.iloc[:,0],
    conf_int.iloc[:,1],
    alpha=0.25,
    label="Confidence Interval"
)

plt.xlabel("Time")
plt.ylabel("Estimated Electricity Draw (Occupancy Based)")
plt.title("Next-Hour Room Electricity Forecast")
plt.legend()
plt.grid(True)

st.pyplot(fig)

# Show numeric result 
st.subheader("Next Hour Prediction")
st.write("Predicted Usage:", round(pred.values[0],2))
st.write("Confidence Interval:",
         round(conf_int.iloc[0,0],2),
         "to",
         round(conf_int.iloc[0,1],2))
