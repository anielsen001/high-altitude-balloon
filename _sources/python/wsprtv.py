"""
This is code to ready WSPRtv.com downloaded files
"""

import numpy as np
import pandas as pd
from pathlib import Path
from scipy import interpolate as spi

class WsprTvCsv:
    """
    Class to read CSV files from WSPR Telemetry viewer
    The format of the WSPR TV CSV files is in flux. 
    """

    _df = None # pandas data frame

    def __init__(self,csvtrackfile):
        df = pd.read_csv(csvtrackfile)
        df.sort_values('#',inplace=True)
        df.set_index('#',inplace=True)
        t = pd.to_datetime(df['UTC Time'])
        df['datetime'] = t

        # create lat/lon/alt columns in radians, radians, meters
        df['lat'] = np.radians(df['Lat (°)'])
        df['lon'] = np.radians(df['Lon (°)'])
        df['alt'] = df['Altitude (km)'] * 1000.0

        self._df = df

    def llh(
            self,
            degrees = False,
            fill_nan = True,
            drop_nan = False,
    ):
        """
        returns lat/lon/height in
        as a 3xN numpy array

        will return lat/lon in radians or degrees
        altitude in meters

        if fill_nan, will interpolate nans to nearby values

        if drop_nan, will drop any data points that contain nan
        """
        if drop_nan:
            df = self._df.dropna()
        else:
            df = self._df
        
        # is Nx3, we convert to 3xN
        _llh = df[['lat','lon','alt']].to_numpy().copy().T

        if degrees:
            _llh[0:2,:] = np.degrees(_llh[0:2,:])

        # nans may occur in height information if only
        # first wspr transmission was made and received
        if fill_nan:
            _h = _llh[-1,:]
            nan_bool = np.isnan(_h)
            good_h = _h[~nan_bool]
            good_h_idx = (~nan_bool).nonzero()[0]
            itp = spi.CubicSpline(good_h_idx,good_h,)
            _h[nan_bool] = itp(nan_bool.nonzero()[0])
            _llh[-1,:] = _h

        return _llh

    def lat(
            self,
            degrees = False,
    ):
        """
        return latittude values for the track
        """
        _lat = self._df['lat'].to_numpy()

        if degrees:
            _lat = np.degrees(_lat)

        return _lat

        
    def lon(
            self,
            degrees = False,
    ):
        """
        return longitude values for the track
        """
        _lon = self._df['lon'].to_numpy()

        if degrees:
            _lon= np.degrees(_lon)

        return _lon

    def times(
            self,
            ):
        """
        return the datetime objects for each spot
        """
        _dt = self._df['datetime']
        return _dt

