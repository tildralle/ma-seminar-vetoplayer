import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
import pickle
import os
from src.yolk_functions import *

import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

plt.rcParams['text.usetex'] = True
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['font.size'] = 30
plt.rcParams['lines.linewidth'] = 2.5
mpl.rcParams['lines.markersize'] = 12
plt.rcParams['figure.figsize'] = (10, 10)
plt.style.use('tableau-colorblind10')

# Params

#save_dir = "yolk_pictures/"
save_dir = "/home/til/Documents/latex/vetoplayer_term_paper/pics"
format = "pdf"
colorblind = False

country = "Portugal"
year = 1995

# Plotting

CB_color_cycle = ['#377eb8', '#ff7f00', '#4daf4a',
                  '#f781bf', '#a65628', '#984ea3',
                  '#999999', '#e41a1c', '#dede00']

with open('parliament_bib.pkl', 'rb') as file:
    parliament_bib = pickle.load(file)

def plot_parliament(parliament):
    country = parliament["country"]
    elec_year = parliament["election_date"].year
    minorty_status = parliament["cabinet"]["minority_cab"]

    print(f"{country}, {elec_year}, {int(minorty_status)}")

    parliament_stance = True
    cabinet_stance = True

    eco = parliament["member"]["stance_eco"]
    soc = parliament["member"]["stance_soc"]

    if len(eco) == 0:
        parliament_stance = False
        print("Parliament position can not be determined. No plotting.")
    elif pd.isna(eco).any():
        parliament_stance = False
        print("Parliament position can not be determined. No plotting.")
    elif len(soc) == 0:
        parliament_stance = False
        print("Parliament position can not be determined. No plotting.")
    elif pd.isna(soc).any():
        parliament_stance = False
        print("Parliament position can not be determined. No plotting.")

    try:
        eco_cabinet = parliament["cabinet"]["stance_eco"]
        soc_cabinet = parliament["cabinet"]["stance_soc"]
        eco_soc_cabinet = (np.mean(eco_cabinet), np.mean(soc_cabinet))
    except:
        print("Cabinet position can not be determined. No plotting.")
        cabinet_stance = False

    if parliament_stance and cabinet_stance:
        eco_soc_mean = (np.mean(eco), np.mean(soc))
        eco_soc_median = (np.median(eco), np.median(soc))

        points = [(e,s) for e,s in zip(eco,soc)]

        yolk_center, yolk_radius = parliament["yolk"]["center"], parliament["yolk"]["radius"] #calculate_yolk(points, accuracy=0.1)

        if colorblind:
            median_color = "black"
            yolk_color = "black"
        else:
            median_color = CB_color_cycle[0]
            yolk_color = CB_color_cycle[7]

        points = list(dict.fromkeys(points)) # delete duplicate points 
        median_lines = get_median_lines(points, only_in_bounds=False)

        fig, ax = plt.subplots(constrained_layout=True)

        for n, (e, s) in enumerate(zip(eco, soc)):
            party_id = parliament["member"]["manifesto_id"][n]
            if party_id in parliament["cabinet"]["manifesto_id"]:
                marker = "X"
            else:
                marker = "X"
            ax.plot(e, s, marker, color="black")
            if parliament["member"]["name"][n] == "PS":
                ax.annotate(parliament["member"]["name"][n], (e-2.75,s+0.25))
            else:
                ax.annotate(parliament["member"]["name"][n], (e+0.25,s+0.25))
        
        for n, m in enumerate(median_lines):
            x, y = transform_points(*m)
            if n == len(median_lines)-1:
                ax.plot(x, y, color=median_color, label="Median Lines")
            else:
                ax.plot(x, y, color=median_color)

        if yolk_radius != 100000:
            x, y = circle(yolk_center, yolk_radius)
            ax.plot(x,y, label="Yolk", color=yolk_color, linestyle="dashed")

        if len(yolk_center) != 0:
            ax.plot(yolk_center[0], yolk_center[1], "o", color=yolk_color, label="Yolk Center")

        # ax.plot(eco_soc_cabinet[0], eco_soc_cabinet[1], "^", color=CB_color_cycle[1], label="Cabinet \n Position")

        # ax.plot(eco_soc_mean[0], eco_soc_mean[1], "s", color=CB_color_cycle[2], label="Parliamentary \n Mean")
        # ax.plot(eco_soc_median[0], eco_soc_median[1], "*", color=CB_color_cycle[5], label="Parliamentary Median")

        ax.set_xlabel("Economy")
        ax.set_ylabel("Society")

        x, y = zip(*points)
        min_x, max_x = min(x), max(x)
        min_y, max_y = min(y), max(y)

        ax.set_xlim(min_x-11,max_x+5)
        ax.set_ylim(min_y-5,max_y+5)

        ax.legend(loc="upper left")

        #ax.set_title(f"{country}, {elec_year}")
        ax.grid()
        ax.set_aspect("equal")
        ax.set_box_aspect(1) 

        if not os.path.isdir(save_dir):
            os.makedirs(save_dir, exist_ok=True)

        plt.savefig(f"{save_dir}/{country}_{elec_year}.{format}")

for key in parliament_bib.keys():
    parliament = parliament_bib[key]
    if parliament["election_date"].year < 1995:
        continue

    if parliament["country"] == country and parliament["election_date"].year == year:
        plot_parliament(parliament)
        break