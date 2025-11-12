import fastkml
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

if len(kmlfiles)>1:
    raise 

with zipfile.ZipFile(kmzfile, 'r') as f:
    kmlfile = f.read('HYSPLITtraj_1627_01.kml')

map = folium.Map(location=[0, 0], zoom_start=2)
folium.Kml(io.BytesIO(kml_file)).add_to(map)

# Display the map
map.save(hysplitpath / 'test.html')
