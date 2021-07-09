import argparse,datetime,math
import geojson
from netCDF4 import Dataset

def get_range(v,low,high):
    dim=v.get_dims()[0].size 
    d=(v[1]-v[0])/2
    i0=None
    i1=dim
    for i in range(0,dim):
        if i0 is None and v[i]+d >= low:
            i0=i
        if v[i]-d <= high:
            i1=i
    if not i0: i0=0
    return [i0,i1]

parser = argparse.ArgumentParser()
parser.add_argument("--input", help="source NC filename")
parser.add_argument("--output", help="output geojson filename")
parser.add_argument("--bbox", help="bounding box to filter grids, format as x1,y1,x2,y2")
args=parser.parse_args()

input_filename=args.input if args.input else "QPESUMS.nc"
print("Input file:", input_filename)
output_filename=args.output if args.output else "QPESUMS.json"
print("Output file:", output_filename)

bbox=list(map(lambda s:float(s),args.bbox.split(','))) if args.bbox else [-180.0,-90.0,180,90.0]
print("Bounding box:", bbox)

qpesums = Dataset(input_filename, "r")

print("NETCDF metadata")
print(qpesums.dimensions)
print(qpesums.variables)

v_time=qpesums.variables['time']
## print(v_time[:])

v_lon=qpesums.variables['x']
v_lat=qpesums.variables['y']

dx=(v_lon[1]-v_lon[0])/2
dy=(v_lat[1]-v_lat[0])/2

lon_range=get_range(v_lon,bbox[0],bbox[2])
lat_range=get_range(v_lat,bbox[1],bbox[3])

v_data=qpesums.variables['precipitation_observed']

## cache all data in memory
time=v_time[:]
lon=v_lon[:]
lat=v_lat[:]
data=v_data[:]

dim_t=qpesums.dimensions['time'].size

features=[]
for x in range(lon_range[0],lon_range[1]):
    for y in range(lat_range[0],lat_range[1]):
        cx=lon[x]
        cy=lat[y]
        id='x'+f'{cx:.4f}'+'y'+f'{cy:.4f}'
        rect=geojson.Polygon([[(cx-dx,cy-dy),(cx+dx,cy-dy),(cx+dx,cy+dy),(cx-dx,cy+dy),(cx-dx,cy-dy)]])
        properties={}
     
## dump only last hour for now:
##        for t in range(0,dim_t):
        for t in range(0,1):
            ts=datetime.datetime.fromtimestamp(time[dim_t-t-1]*60,datetime.timezone.utc).isoformat()
            properties['time_t'+str(t)]=ts
            v=float(data[dim_t-t-1,y,x])
            if math.isnan(v):
                print("Skip no data grid at t" + str(t), id)
            else:
                properties['value_t'+str(t)]=float(data[dim_t-t-1,y,x])
        feature=geojson.Feature(
          geometry=rect,
          properties=properties,
          id=id
        )
        features.append(feature)
        if not feature.is_valid: print(feature.id, feature.is_valid) 

qpesums.close()

output=geojson.FeatureCollection(features)
print("Geojson is_valid:", output.is_valid)

file_output=geojson.dumps(output)
with open(output_filename,'w') as f:
    f.write(file_output)
