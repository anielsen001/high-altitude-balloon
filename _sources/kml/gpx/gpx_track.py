import numpy as np
import pandas as pd
from pathlib import Path
import gpxpy


# trackfile = Path('/opt/project/_sources/launches/smore-002/launch/KF8EEZ_109_20251106-20251106.csv')
# trackfile = Path('/opt/project/_sources/launches/smore-002/launch/KF8EEZ_109_20251106-20251108.csv')
trackpath = Path('/opt/project/_sources/launches/smore-002/tracking/spots')
trackfile = trackpath / 'KF8EEZ_109.csv'
df = pd.read_csv(trackfile)
df.sort_values('#',inplace=True)
df.set_index('#',inplace=True)

# get times and convert to iso formatted time stamps
t =  pd.to_datetime(df['UTC Time'])
# dt = (t - t[1]).dt.total_seconds().to_numpy()
ts = ts = [ _t.isoformat() for _t in t]

# get llh positon spots
llh = df[['Lat (°)','Lon (°)', 'Altitude (km)',]].bfill().to_numpy()
# llh[:,0:2] = np.radians(llh[:,0:2]) # convert lat/lon to radians
llh[:,-1] *= 1000.0 # convert to meters, Nan in height means 2D spot, no altitude


coord = [ (_lon, _lat, _h) for _lat, _lon, _h in llh ]

# https://github.com/tkrajina/gpxpy
# create a gpx file
gpx = gpxpy.gpx.GPX()
gpx_track = gpxpy.gpx.GPXTrack()
gpx.tracks.append(gpx_track)
# Create first segment in our GPX track:
gpx_segment = gpxpy.gpx.GPXTrackSegment()
gpx_track.segments.append(gpx_segment)

# create points

for _t,_c in zip(t,coord):
    pnt = gpxpy.gpx.GPXTrackPoint(
        longitude = _c[0],
        latitude = _c[1],
        elevation = _c[2],
        time = _t,
    )
    gpx_segment.points.append(pnt)

gpxfilename = trackpath / 'KF8EEZ.gpx'

with open(gpxfilename,'w') as f:
    f.write(gpx.to_xml())
