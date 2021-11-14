import os
import re
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import random
from scipy import interpolate
from random import gauss

from sklearn.model_selection import train_test_split

# -----------------------------------------------------------------------------

def dataset(N_ft, y_id):
    """ Prepares dataset

     Args:
         N_ft: number of features
         y_id: id of target value (from 0 to 5)

     Returns:
         X: numpy array of features
         y: naumpy array of target values
         X_names: array of the fields for interpolation
         y_names: array of the target parameters
     """
 
    path = os.getcwd()
    path = path + '\..\dataset_random'
    
    names = os.listdir(path)
    N_sm = len(names)
    
    y = np.zeros((N_sm,6), dtype = float) 
    # Description for y[:,i]: 
    # 0) k_K - mean anisotropy constant (% of 5.3e+6 J/m3)
    # 1) k_K_sd - standard deviation (SD) of k_K (% of k_K)
    # 2) th_std - easy axis inclination from OOP (SD, deg.)
    # 3) vol_fr_200 - volume fraction of [200] misalignment (%)
    # 4) vol_fr_111 - volume fraction of [111] misalignment (%)
    # 5) vol_fr_K0  - volume fraction of grains with K = 0 (%)
    
    y_names = ['$K_{m}$', '$K_{sd}$', '\u03B8$_{sd}$', '$V_{200}$', '$V_{111}$', '$V_{K=0}$']
    
    j = 0
    for name in names:
        extract = re.findall(r'\d+(?:\.\d+)?', name)
        y[j,:] = [round(float(i), 2) for i in extract]
        j = j + 1

    if y_id == 0:
        H = np.linspace(-10, 10, N_ft)
    else:
        H = np.linspace(-1.4, 1.3, N_ft)

    if y_id == 1:
        X = np.zeros((N_sm, N_ft+1), dtype=float)
    else:
        X = np.zeros((N_sm, N_ft), dtype=float)

    j = 0
    print('\nLoading data...\n')
    for name in names:
        file = path + '\\' + name
        with open(file) as f:
            lines = f.readlines()
            del(lines[0])
        N_lines = len(lines)
        
        H_ex = np.zeros((N_lines), dtype = float)
        M_ex = np.zeros((N_lines), dtype = float)
        
        i = 0
        for line in lines:
            extract = line.split()
            H_ex[i] = extract[9]
            M_ex[i] = extract[6]
            i = i + 1
            
        H_ex = np.flipud(H_ex)
        M_ex = np.flipud(M_ex)
        
        if y_id != 0:
            H_a = 2*(y[j,0]/100*5.3e+6)/1.43*(4*3.1416e-7)
            H_ex = H_ex/H_a

    # Generate random numbers for noise
    #     min_val = gauss(1, 0.03)
    #     max_val = gauss(1, 0.03)
        min_val = random.uniform(0.985, 1.01)
        max_val = random.uniform(0.985, 1.01)
        if y_id ==1:
            X[j,:-1] = np.interp(H, H_ex, M_ex) / 1.43
            X[j, :-1] = (X[j, :-1] - (min_val - max_val) / 2) / ((min_val + max_val) / 2)
            X[j,-1] = y[j,0]
        else:
            X[j, :] = np.interp(H, H_ex, M_ex) / 1.43
            X[j, :] = (X[j, :] - (min_val - max_val) / 2) / ((min_val + max_val) / 2)

        if name == "96.2_2.36_8.43_4.63_5.32_2.17.txt":
            interp_file = open('interpolation.txt', 'w')
            for p in range(len(H)):
                interp_file.write(f'{H[p]} {X[j,p]}\n')
            interp_file.close()
        j = j + 1
        
    print('\033[31m\033[1mDataset is uploaded:\033[0m')
    print(f' - {N_sm} samples')
    print(f' - {N_ft} features')

    X_names=[]
    for i in range(len(H)):
        X_names.append(round(H[i], 2))

    if y_id == 1:
        X_names.append("K")

    return X, y, X_names, y_names

# -----------------------------------------------------------------------------


def prediction_plots(y_train, y_fit, y_test, y_pred, name):
    """ Function makes plots 'y_fit' vs. 'y_train' and 'y_pred' vs. 'y_test' """

    plt.figure(figsize=(6,5), dpi = 500)
    plt.scatter(y_train, y_fit, s = 10, color = 'blue', marker = 'o', label = 'Train data')
    plt.scatter(y_test, y_pred, s = 20, color = 'red', marker = 'o', label = 'Test data')
    plt.xlabel(r'Simulated ' + name, size = 18)
    plt.ylabel(r'Predicted ' + name, size = 18)
    plt.legend(fontsize = 14)

    max_y = np.max(y_test)
    if max_y < np.max(y_pred):
        max_y = np.max(y_pred)
    max_y = max_y*1.05
    
    '''
    min_y = np.min(y_test)
    if min_y > np.min(y_pred):
        min_y = np.min(y_pred)
    min_y = min_y*0.9
    '''
    
    min_y = 0.0

    plt.plot([min_y, max_y], [min_y, max_y], color = 'black', linewidth = 1)

    plt.gca().set_aspect('equal')
    plt.xlim(min_y, max_y)
    plt.ylim(min_y, max_y)

    plt.savefig('Prediction.png', transparent=True)

# -----------------------------------------------------------------------------


def plot_history(history, max_y):
    """ Function makes history plots """

    plt.figure()
    plt.xlabel('Epoch')
    plt.ylabel('Mean Abs Error')
    plt.plot(history.epoch, np.array(history.history['mae']) * max_y,
             label='Train')
    plt.plot(history.epoch, np.array(history.history['val_mae']) * max_y,
             label='Val')
    plt.legend()
    plt.ylim([0, max(history.history['val_mae']) * max_y])
    plt.savefig('EPOCHS.png', transparent=True)


