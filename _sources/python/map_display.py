"""
creates a folium map with data from WSPR-TV and HYSPLIT
"""

import sys

# for running in container with these local sources
sys.path.append("/opt/project/_sources/python")

import folium
import numpy as np
from pathlib import Path
from wsprtv import WsprTvCsv

def create_map(
        wsprcsvfile,
        hysplitfiles,
        ):

    if type(hysplitfiles) is not list:
        hysplitfiles = [hysplitfiles]
    
    # read wspr csv file
    wspr = WsprTvCsv(wsprcsvfile)

    # find the center of the map based on average
    # track point locations
    lat_center = np.mean(wspr.lat(degrees=True))
    lon_center = np.mean(wspr.lon(degrees=True))
