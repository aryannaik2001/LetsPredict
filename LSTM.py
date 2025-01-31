import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
import datetime as dt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
# Load Data
company = 'GOOG' #Here we can have AAPL or META or any other company listed in US stock market
start = dt.datetime(2012,1,1)
end = dt.datetime(2022,1,1)
data = yf.download(company, start=start, end=end)

# Prepare Data
scaler = MinMaxScaler (feature_range=(0,1))
scaled_data = scaler.fit_transform (data['Close'].values.reshape(-1,1))
prediction_days = 60
x_train = []
y_train = []
for x in range (prediction_days, len(scaled_data)):
	x_train.append(scaled_data[x-prediction_days:x, 0])
	y_train.append(scaled_data[x, 0])
x_train, y_train = np.array(x_train), np.array(y_train)
x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
# Build The Model
model = Sequential()
model.add(LSTM(units=50, return_sequences=True, input_shape=(x_train. shape [1], 1)))
model.add(Dropout (0.2))
model.add(LSTM(units=50, return_sequences=True))
model.add(Dropout (0.2))
model.add(LSTM(units=50))
model.add(Dropout (0.2))
model.add(Dense (units=1)) # Prediction of the next closing value

model.compile(optimizer='adam', loss='mean_squared_error')
model.fit(x_train, y_train, epochs=25, batch_size=32)
'''Test The Model Accuracy on Existing Data '''
# Load Test Data
test_start = dt.datetime(2022,1,1)
test_end = dt.datetime.now()
test_data = yf.download(company, test_start, test_end)
test_data.index = pd.to_datetime(test_data.index)
actual_prices = test_data['Close'].values

total_dataset = pd.concat((data['Close'], test_data['Close']), axis=0)
model_inputs = total_dataset [len (total_dataset) - len(test_data) - prediction_days:].values
model_inputs = model_inputs.reshape(-1, 1)
model_inputs = scaler.transform(model_inputs)
# Make Predictions on Test Data
x_test = []
for x in range(prediction_days, len (model_inputs)):
	x_test.append(model_inputs [x-prediction_days:x, 0])
x_test = np.array(x_test)
x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
predicted_prices = model.predict(x_test)
predicted_prices = scaler.inverse_transform (predicted_prices)

# Calculate RMSE
rmse = np.sqrt(mean_squared_error(actual_prices, predicted_prices))
# Calculate MAE
mae = mean_absolute_error(actual_prices, predicted_prices)
# Calculate R²
r2 = r2_score(actual_prices, predicted_prices)

print(f'RMSE: {rmse}')
print(f'MAE: {mae}')
print(f'R²: {r2}')

plt.figure(figsize=(12, 6))
plt.plot(test_data.index, actual_prices, color="black", label=f"Actual {company} Price")
plt.plot(test_data.index, predicted_prices, color='green', label=f"Predicted {company} Price")
plt.title(f"{company} Share Price")
plt.xlabel('Date')
plt.ylabel(f'{company} Share Price')
plt.legend()

# Rotate and align the tick labels so they look better
plt.gcf().autofmt_xdate()

# Use a nicer date format for the x axis
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d'))

# Add gridlines for better readability
plt.grid(True, which='both', linestyle='--', linewidth=0.5)

plt.tight_layout()
plt.show()




