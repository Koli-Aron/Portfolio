import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor
import matplotlib.pyplot as plt

# Load the data
df = pd.read_csv(r"C:\Users\User\Desktop\Machine Learning Project\processed_data_cyclical.csv")

lower_price_limit = -30  # Set the lower price limit
upper_price_limit = 200  # Set the upper price limit

# Convert target variable to numeric and handle non-numeric values
df["Day-ahead Price [EUR/MWh]"] = pd.to_numeric(df["Day-ahead Price [EUR/MWh]"], errors='coerce')

df = df[(df['Day-ahead Price [EUR/MWh]'] >= lower_price_limit) & (df['Day-ahead Price [EUR/MWh]'] <= upper_price_limit)]

# Prepare features and target variable
X = df.drop("Day-ahead Price [EUR/MWh]", axis=1)
y = df["Day-ahead Price [EUR/MWh]"]

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)

# Create a scaler
scaler = StandardScaler()

# Normalize the data
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Random Forest Model
rf_model = RandomForestRegressor(n_estimators=1000, random_state=42)
rf_model.fit(X_train_scaled, y_train)
y_pred_rf = rf_model.predict(X_test_scaled)

# XGBoost Model
xgb_model = XGBRegressor(n_estimators=1000, random_state=42)
xgb_model.fit(X_train_scaled, y_train)
y_pred_xgb = xgb_model.predict(X_test_scaled)

# Average Prediction
y_pred_avg = (y_pred_rf + y_pred_xgb) / 2

# Calculate performance metrics
mse_rf = mean_absolute_error(y_test, y_pred_rf)
r2_rf = r2_score(y_test, y_pred_rf)
print("Random Forest - Mean Absolute Error:", mse_rf)
print("Random Forest - R² Score:", r2_rf)

mse_xgb = mean_absolute_error(y_test, y_pred_xgb)
r2_xgb = r2_score(y_test, y_pred_xgb)
print("XGBoost - Mean Absolute Error:", mse_xgb)
print("XGBoost - R² Score:", r2_xgb)

mse_avg = mean_absolute_error(y_test, y_pred_avg)
r2_avg = r2_score(y_test, y_pred_avg)
print("Averaged Prediction - Mean Absolute Error:", mse_avg)
print("Averaged Prediction - R² Score:", r2_avg)

median_test = np.median(y_test)

# Calculate the medians of the predictors
median_rf = np.median(y_pred_rf)
median_xgb = np.median(y_pred_xgb)
median_avg = np.median(y_pred_avg)

# Print the results
print("Median Electricity Price (Random Forest Predictions):", median_rf)
print("Median Electricity Price (XGB Predictions):", median_xgb)
print("Median Electricity Price (Averaged Predictions):", median_avg)
print("Median Electricity Price (Test Data):", median_test)

plt.figure(figsize=(10, 6))
plt.plot(y_test.values, label='Actual Prices', color='black', linestyle='-', linewidth=2)  # Actual test data
plt.plot(y_pred_avg, label='Averaged Predictions', color='orange', linestyle='-.', linewidth=1.5)  # Averaged predictions

plt.title('Electricity Price Prediction: Actual vs Random Forest vs XGBoost vs Averaged Predictions (Entire Data Range)')
plt.xlabel('Test Data Points')
plt.ylabel('Electricity Price [EUR/MWh]')
plt.legend()
plt.grid(True)

plt.savefig(r"C:\Users\User\Desktop\Machine Learning Project\entire_data_range_with_avg_plot.png", bbox_inches='tight')
plt.close()

# Plot only the data range 6000 to 6600
plt.figure(figsize=(10, 6))
plt.plot(y_test.values[6000:6600], label='Actual Prices', color='black', linestyle='-', linewidth=2)  # Actual test data
plt.plot(y_pred_avg[6000:6600], label='Averaged Predictions', color='orange', linestyle='-.', linewidth=1)  # Averaged predictions

plt.title('Electricity Price Prediction: Actual vs Averaged Predictions (Data Points 6000 to 6600)')
plt.xlabel('Test Data Points')
plt.ylabel('Electricity Price [EUR/MWh]')
plt.legend()
plt.grid(True)

# Save the plot for the data range 6000 to 6600
plt.savefig(r"C:\Users\User\Desktop\Machine Learning Project\data_range_6000_to_6600_with_avg_plot.png", bbox_inches='tight')
plt.close()

print("Plots saved successfully.")
