from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
import numpy as np
from sklearn.preprocessing import StandardScaler

import ml

# --- Preparing the data ------------------------------------------------------
N_ft = 101  # number of features
y_id = 0  # id for target value

# Options for y_id:
# 0: k_K - mean anisotropy constant (% of 5.3e+6 J/m3)
# 1: k_K_sd - standard deviation (SD) of k_K (% of k_K)
# 2: th_std - easy axis inclination from OOP (SD, deg.)
# 3: vol_fr_200 - volume fraction of [200] misalignment (%)
# 4: vol_fr_111 - volume fraction of [111] misalignment (%)
# 5: vol_fr_K0  - volume fraction of grains with K = 0 (%)

# Import dataset
X, y, X_names, y_names = ml.dataset(N_ft, y_id)

N_sm = np.shape(X)[0]  # number of samples

y = np.array(y[:, y_id])
y = y.reshape([N_sm, 1])
max_y = np.max(y)

name = y_names[y_id]  # name of target value


# --- Creating the model ------------------------------------------------------
def baseline_model():
    model = Sequential()
    model.add(Dense(300, input_dim=N_ft, kernel_initializer='uniform', activation='relu'))
    model.add(Dense(1, kernel_initializer='uniform'))

    model.compile(loss='mean_squared_error', optimizer='adam', metrics=['mae'])
    return model


# --- Running the model ------------------------------------------------------
EPOCHS = 600

model = baseline_model()
x_train, x_test, y_train, y_test = ml.split(X, y, 0.2, 14264)

# Standartization and normalization
scaler = StandardScaler()
scaler.fit(x_train)
x_train = scaler.transform(x_train)
x_test = scaler.transform(x_test)
y_train = y_train / max_y
y_test = y_test / max_y

# Fit the model and get history
history = model.fit(x_train, y_train, epochs=EPOCHS,
                    validation_split=0.2, verbose=1)
ml.plot_history(history, max_y)  # plot history

# Predict target values
y_fit = model.predict(x_train).flatten()
y_pred = model.predict(x_test).flatten()

# Renormalization
y_train = y_train * max_y
y_test = y_test * max_y
y_fit = y_fit * max_y
y_pred = y_pred * max_y

ml.prediction_plots(y_train, y_fit, y_test, y_pred, name)  # plot predictions
