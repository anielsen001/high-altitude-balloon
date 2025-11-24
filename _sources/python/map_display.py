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
    llhd = wspr.llh(degrees=True,fill_nan=False)
    latd = llhd[0,:]
    lond = llhd[1,:]
    times = wspr.times()

    # find the center of the map based on average
    # track point locations
    lat_center = np.nanmean(latd)
    lon_center = np.nanmean(lond)

    lat_max = np.nanmax(latd)
    lat_min = np.nanmin(latd)
    lon_max = np.nanmax(lond)
    lon_min = np.nanmin(lond)

    sw = [lat_min, lon_min]
    ne = [lat_max, lon_max]

    # create a folium map
    # default folium EPSG is EPSG:3857 or web-mercator
    # GPS is EPSG:4326 or WGS-84
    # however, the plots show correctly using EPSG:3857
    m = folium.Map(
        location = [lat_center,lon_center],
        #crs = 'EPSG4326',
    )
    m.fit_bounds([sw,ne])

    # draw the spots on the map as markers
    for ii in range(len(times)):
        _t = times.iloc[ii]
        _llh = llhd[0:3,ii]
        if np.isnan(_llh[2]):
            fillcolor = '#F54927'
        else:
            fillcolor = '#21B55D'
        marker = folium.vector_layers.CircleMarker(
            _llh[0:2],
            tooltip = str(_t),
            radius=5,
            fill=True,
            fillColor=fillcolor,
            fillOpacity=1.0,
            )
        marker.add_to(m)

    # draw the track as a reference
    llhgood = wspr.llh(degrees=True,drop_nan=True)
    track = folium.vector_layers.PolyLine(
        llhgood[0:2,:].T,
        ).add_to(m)
    
    # return the folium map object
    return m

if __name__=="__main__":
    m = create_map(
        '_sources/launches/smore-002/tracking/spots/KF8EEZ_109.csv',
        'blah')
