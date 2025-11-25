import datetime
#from fastkml import kml
#import folium
#import io
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import interpolate as spi
import zipfile

class HysplitShapefile():

    _df = None
    _tracks = None
    _zipfile = None

    def __init__(
            self,
            hysplitzipfile,
            ):

        self._zipfile = hysplitzipfile
        
        dfatt = None
        dftxt = None
        
        with zipfile.ZipFile(hysplitzipfile) as f:
            for _f in f.filelist:
                if (Path(_f.filename).suffix == '.txt'):
                    cols=['TRAJNUM','LON','LAT','FLUX']
                    dftxt = pd.read_csv(f.open(_f),names=cols,skipfooter=1,engine='python')
            
                if (Path(_f.filename).suffix == '.att'):
                    cols = ['TRAJNUM','YYYYMMDD','TIME','LEVEL']
                    parse = lambda x: datetime.strptime(x, '%Y%m%d %H%M')
                    dfatt = pd.read_csv(
                        f.open(_f),
                        names=cols,
                        comment='#',
                        parse_dates = {'datetime':['YYYYMMDD', 'TIME']},
                        #parse_dates = {'datetime':[[1,2]]},
                        date_format = '%Y%m%d %H%M',
                    )
        df = pd.merge(left=dfatt,right=dftxt,how='left')
        df['TRAJID'] = (df['TRAJNUM']/1000).to_numpy().astype(int)
        self._df = df
        
        self._tracks = np.unique((self._df['TRAJNUM'].to_numpy()/1000).astype(int))

    def get_track(
            self,
            trkid,
            ):
        """
        returns a pandas data frame with the specified trackid
        """
        df = self._df
        dftraj = df[df['TRAJID']==trkid]
        return dftraj

    def get_llh(
            self,
            trackid,
            timestamp,
            degrees=False,
            ):
        """
        return the lat/lon/height for the given trackid at the given timestamp

        does not interpolate, only returns existing time values

        lat/lon is stored in degrees
        """
        trk = self.get_track(trackid)
        llh = trk[['LAT','LON','LEVEL']]
        llht = llh[trk['datetime']==timestamp].to_numpy().T # 3x1 numpy array
        if not degrees:
            llht[0:2] = np.radians(llht[0:2])
        return llht

    def start_time(self):
        """
        return the start time of this hysplit model
        """
        return self._df['datetime'].iloc[0]

    def end_time(self):
        """
        return the end time of this hysplit model
        """
        return self._df['datetime'].iloc[-1]
    
    @property
    def tracks(self):
        return self._tracks

    @property
    def zipfile(self):
        return self._zipfile


# hysplitpath = Path('/opt/project/_sources/launches/smore-002/tracking/predictions/')
# kmzfile = hysplitpath / 'HYSPLITtraj_1627.kmz'

# # open the kmz file and find the kml files insize
# zip = zipfile.ZipFile(kmzfile)
# zipfiles = zip.namelist() # list of files in zip file
# kmlfiles = []
# for _zf in zipfiles:
#     ext = Path(_zf).suffix
#     if '.kml' in ext:
#         kmlfiles.append(_zf)

# # assume only one kml file in the kmz
# if len(kmlfiles)>1:
#     raise

# with zipfile.ZipFile(kmzfile, 'r') as f:
#     kmlstring = f.read(kmlfiles[0])

# k = kml.KML.from_string(kmlstring)
    
# #uv run k2g HYSPLITtraj_1627_01.kml "/opt/project/_sources/launches/smore-002/tracking/predictions/_kmzx"

# geojsonfile = hysplitpath / "_kmzx" / "style.json"
# map = folium.Map(location=[0, 0], zoom_start=2)
# with open(geojsonfile,'r') as f:
#     json = f.read()
#     folium.GeoJson(json).add_to(map)

# # Display the map
# map.save(hysplitpath / 'test.html')

# ### zipped shape files
# ### open the zip file and parse into dataframe
# import datetime

# dfatt = None
# dftxt = None
# hysplitzipfile = hysplitpath / 'gis_1627.zip'
# with zipfile.ZipFile(hysplitzipfile) as f:
#     for _f in f.filelist:
#         if (Path(_f.filename).suffix == '.txt'):
#             cols=['TRAJNUM','LON','LAT','FLUX']
#             dftxt = pd.read_csv(f.open(_f),names=cols,skipfooter=1,engine='python')
                    
#         if (Path(_f.filename).suffix == '.att'):
#             cols = ['TRAJNUM','YYYYMMDD','TIME','LEVEL']
#             parse = lambda x: datetime.strptime(x, '%Y%m%d %H%M')
#             dfatt = pd.read_csv(
#                 f.open(_f),
#                 names=cols,
#                 comment='#',
#                 parse_dates = {'datetime':['YYYYMMDD', 'TIME']},
#                 #parse_dates = {'datetime':[[1,2]]},
#                 date_format = '%Y%m%d %H%M',
#             )
# df = pd.merge(left=dfatt,right=dftxt,how='left')        


        
# Brute forcing shape files
# cols=['TRAJNUM','LON','LAT','FLUX']
# dftxt = pd.read_csv(hysplitpath/'GIS_traj_121367_01.txt',names=cols,skipfooter=1,engine='python')
# cols = ['TRAJNUM','YYYYMMDD','TIME','LEVEL']
# parse = lambda x: datetime.strptime(x, '%Y%m%d %H%M')
# # time should be HHMM, but gets parsed into thousands
# dfatt = pd.read_csv(
#     'GIS_traj_121367_01.att',
#     names=cols,
#     comment='#',
#     parse_dates = {'datetime':['YYYYMMDD', 'TIME']},
#     #parse_dates = {'datetime':[[1,2]]},
#     date_format = '%Y%m%d %H%M',
# )
# df = pd.merge(left=dfatt,right=dftxt,how='left')

# the thousands indicates the trajectory number
# then counts count up track numbers
