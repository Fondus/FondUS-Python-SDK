# FondUS-Python-SDK
Public SDK to access some common open Hydro data-services

### Tools
----
#### qpesums-netcdf-tools

Tools to handle QPESUMS netcdf data

##### Install
1. clone this project to local folder
2. enter qpesums-netcdf-tools folder `cd FondUS-Python-SDK/qpesums-netcdf-tools`
3. run pip to install required dependency `python3 -m pip install -r requirements.txt`
4. run `python3 qpesums_netcdf_convert --help` to check the usage
```
$ python3 qpesums_netcdf_convert.py --help
usage: qpesums_netcdf_convert.py [-h] [--input INPUT] [--output OUTPUT]
                                 [--bbox BBOX]

optional arguments:
  -h, --help       show this help message and exit
  --input INPUT    source NC filename
  --output OUTPUT  output geojson filename
  --bbox BBOX      bounding box to filter grids, format as x1,y1,x2,y2
```

example: `python3 qpesums_netcdf_convert.py --input /tmp/QPESUMS-test.nc --bbox 122.5,22,123.5,23` will generate the geojson grid polygon with qpesums precipitation_observed last data as `QPESUMS.json`
