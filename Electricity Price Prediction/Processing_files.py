import pandas as pd
import numpy as np

# Load the electricity price CSV files for each year into a list
file_paths = [
    r"C:\Users\User\Desktop\Machine Learning Project\price data\Day-ahead Prices_2017.csv",
    r"C:\Users\User\Desktop\Machine Learning Project\price data\Day-ahead Prices_2018.csv",
    r"C:\Users\User\Desktop\Machine Learning Project\price data\Day-ahead Prices_2019.csv",
    r"C:\Users\User\Desktop\Machine Learning Project\price data\Day-ahead Prices_2020.csv",
    r"C:\Users\User\Desktop\Machine Learning Project\price data\Day-ahead Prices_2021.csv",
    r"C:\Users\User\Desktop\Machine Learning Project\price data\Day-ahead Prices_2022.csv",
    r"C:\Users\User\Desktop\Machine Learning Project\price data\Day-ahead Prices_2023.csv",
    r"C:\Users\User\Desktop\Machine Learning Project\price data\Day-ahead Prices_2024.csv"
]

# Combine all the DataFrames into a single DataFrame
df_list = [pd.read_csv(file_path, encoding='utf-8') for file_path in file_paths]
df = pd.concat(df_list, ignore_index=True)

# Load the temperature data
temp_df = pd.read_csv(r"C:\Users\User\Desktop\Machine Learning Project\Helsinki Kaisaniemi_ 1.1.2017 - 2.10.2024_da3b9e7a-61a1-49f0-9f11-265c45122578.csv", encoding='utf-8')

# Convert the 'Year', 'Month', 'Day', and 'Time [UTC]' columns into a single datetime column in temp_df
temp_df['datetime'] = pd.to_datetime(temp_df[['Year', 'Month', 'Day']].astype(str).agg('-'.join, axis=1) + ' ' + temp_df['Time [UTC]'])

# Drop unnecessary columns from temp_df
temp_df = temp_df.drop(['Observation station', 'Year', 'Month', 'Day', 'Time [UTC]'], axis=1)

# Rename columns for clarity
temp_df.rename(columns={'Average temperature [Â°C]': 'Average temperature [°C]', 'Wind speed [m/s]': 'Wind speed [m/s]'}, inplace=True)

# Split the 'MTU (UTC)' column to extract the start time (before the ' - ' symbol) in df
df['Datetime'] = pd.to_datetime(df['MTU (UTC)'].str.split(' - ').str[0], format='%d.%m.%Y %H:%M')

# Ensure 'Datetime' is in the correct format to match the temperature 'datetime'
df['Datetime'] = df['Datetime'].dt.floor('H')  # Round down to the nearest hour

# Merge the temperature data with electricity prices using 'Datetime'
df = pd.merge(df, temp_df, left_on='Datetime', right_on='datetime', how='left')

# The table for electricity prices has data for the entire year 2024. We'll drop everything up to 2.10.2024
df = df.head(67951)

df["Average temperature [°C]"] = pd.to_numeric(df["Average temperature [°C]"], errors='coerce')
df["Wind speed [m/s]"] = pd.to_numeric(df["Wind speed [m/s]"], errors='coerce')

# Clean up the DataFrame by dropping unnecessary columns
df_clean = df.drop(['BZN|FI', 'Currency', 'MTU (UTC)', 'datetime'], axis=1, errors='ignore')

# Keep the columns of interest, including wind speed
df_clean = df_clean[['Datetime', 'Day-ahead Price [EUR/MWh]', 'Average temperature [°C]', 'Wind speed [m/s]']]

# Save the DataFrame with the original datetime format to a CSV file
df_clean.to_csv(r'C:\Users\User\Desktop\Machine Learning Project\processed_data.csv', index=False)

# Calculate cyclical features for the date
df['Day of Year'] = df['Datetime'].dt.dayofyear
df['Hour of Day'] = df['Datetime'].dt.hour

# Create a new DataFrame for cyclical features and relevant data
df_cyclical = df[['Day of Year', 'Hour of Day', 'Day-ahead Price [EUR/MWh]', 'Average temperature [°C]', 'Wind speed [m/s]']].copy()

# Save the processed data with cyclical features to a new CSV file
df_cyclical.to_csv(r'C:\Users\User\Desktop\Machine Learning Project\processed_data_cyclical.csv', index=False)

# Optional: View the resulting merged DataFrame
print("DataFrame with original datetime format:")
print(df_clean.tail(5))
print("\nDataFrame with cyclical features:")
print(df_cyclical.tail(5))