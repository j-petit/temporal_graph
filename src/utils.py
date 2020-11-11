import matplotlib.pyplot as plt
import matplotlib.dates
from datetime import datetime



def plot_occurances(occurances):

    plt.plot_date(x=[occ[1] for occ in occurances], y=[occ[1] for occ in occurances], ydate=False)
    plt.show()
