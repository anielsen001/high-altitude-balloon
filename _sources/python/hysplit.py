from fastkml import kml
import folium
import io
from pathlib import Path
import zipfile


hysplitpath = Path('/opt/project/_sources/launches/smore-002/tracking/predictions/')
kmzfile = hysplitpath / 'HYSPLITtraj_1627.kmz'

# open the kmz file and find the kml files insize
zip = zipfile.ZipFile(kmzfile)
zipfiles = zip.namelist() # list of files in zip file
kmlfiles = []
for _zf in zipfiles:
    ext = Path(_zf).suffix
    if '.kml' in ext:
        kmlfiles.append(_zf)

# assume only one kml file in the kmz
if len(kmlfiles)>1:
    raise

with zipfile.ZipFile(kmzfile, 'r') as f:
    kmlstring = f.read(kmlfiles[0])

k = kml.KML.from_string(kmlstring)
    
#uv run k2g HYSPLITtraj_1627_01.kml "/opt/project/_sources/launches/smore-002/tracking/predictions/_kmzx"

geojsonfile = hysplitpath / "_kmzx" / "style.json"
map = folium.Map(location=[0, 0], zoom_start=2)
with open(geojsonfile,'r') as f:
    json = f.read()
    folium.GeoJson(json).add_to(map)

# Display the map
map.save(hysplitpath / 'test.html')


import datetime

# Brute forcing shape files
cols=['TRAJNUM','LAT','LON','FLUX']
dftxt = pd.read_csv('GIS_traj_121367_01.txt',names=cols,skipfooter=1,engine='python')
cols = ['TRAJNUM','YYYYMMDD','TIME','LEVEL']
parse = lambda x: datetime.strptime(x, '%Y%m%d %H%M')
# time should be HHMM, but gets parsed into thousands
dfatt = pd.read_csv(
    'GIS_traj_121367_01.att',
    names=cols,
    comment='#',
    #parse_dates = {'datetime':[['YYYYMMDD', 'TIME']]},
    parse_dates = {'datetime':[[1,2]]},
    date_format = '%Y%m%d %H%M',
)
df = pd.merge(left=dfatt,right=dftxt,how='left')

# the thousands indicates the trajectory number
# then counts count up track numbers
