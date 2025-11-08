import numpy as np
import pandas as pd
from pathlib import Path
import simplekml

# trackfile = Path('/opt/project/_sources/launches/smore-002/launch/KF8EEZ_109_20251106-20251106.csv')
trackfile = Path('/opt/project/_sources/launches/smore-002/launch/KF8EEZ_109_20251106-20251108.csv')
df = pd.read_csv(trackfile)
df.sort_values('#',inplace=True)
df.set_index('#',inplace=True)

# get times and convert to iso formatted time stamps
t =  pd.to_datetime(df['Time UTC'])
# dt = (t - t[1]).dt.total_seconds().to_numpy()
ts = ts = [ _t.isoformat() for _t in t]

# get llh positon spots
llh = df[['Lat (°)','Lon (°)', 'Altitude (km)',]].bfill().to_numpy()
# llh[:,0:2] = np.radians(llh[:,0:2]) # convert lat/lon to radians
llh[:,-1] *= 1000.0 # convert to meters, Nan in height means 2D spot, no altitude


coord = [ (_lon, _lat, _h) for _lat, _lon, _h in llh ]

# this should plot a track, but the gx:Track type returns error in google earth and windy
# kml = simplekml.Kml()
# doc = kml.newdocument(name = 'KF8EEZ')
# doc.lookat.gxtimespan.begin = ts[0]
# doc.lookat.gxtimespan.end = ts[-1]
# doc.lookat.longitude = coord[-1][0]
# doc.lookat.latitude = coord[-1][1]

# fol = doc.newfolder(name = 'KF8EEZ')
# trk = fol.newgxtrack(name='2D track data')
# trk.newwhen(ts)

# trk.newgxcoord(coord)

# kml.save('/opt/project/kf8eez.kml')


# this plots points and seems to work with windy and google eartth
kml = simplekml.Kml()
style = simplekml.Style()
style.labelstyle.color = simplekml.Color.red  # Make the text red
style.labelstyle.scale = 2  # Make the text twice as big
style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png'
for _ts,_c in zip(ts,coord):
    pnt = kml.newpoint(name = str(_ts))
    pnt.coords = [_c]
    pnt.style = style


kml.save('/opt/project/kf8eez.kml')
