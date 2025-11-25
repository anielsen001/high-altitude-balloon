import datetime
#from fastkml import kml
#import folium
#import io
import pandas as pd
from pathlib import Path
import zipfile

class HysplitShapefile():

    _df = None

    def __init__(
            self,
            hysplitzipfile,
            ):
        dfatt = None
        dftxt = None
        #hysplitzipfile = hysplitpath / 'gis_1627.zip'
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
        self._df = df


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
