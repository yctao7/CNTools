import os
import sys
import torch
import pandas as pd
import functools
import logging
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import pickle
import scipy
import seaborn as sns
from sklearn.model_selection import train_test_split
import time
import tqdm


N_PARALLEL_PROCESSES = 8 #@param
TRAIN_SIZE_FRACTION = 0.989 #@param
N_TOPICS_LIST = [6] #@param
DIFFERENCE_PENALTY = [0.0025]
RADIUS = 81 # 45, 64, 81

PATH_TO_MODELS = f'./models/diabetes/'
PATH_TO_RESULTS = f'./results/diabetes/'
PATH_TO_SPLEEN_DF_PKL = f'./data/diabetes/diabetes_df.pkl'
PATH_TO_SPLEEN_FEATURES_PKL = f'./data/diabetes/diabetes_cells_features_{RADIUS}.pkl'


def Spatial_LDA():
    pass