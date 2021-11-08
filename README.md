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


#### dataflow-api tools

Tools to get data from FEWS Taiwan dataflow API

##### Install
1. clone this project to local folder
2. enter dataflow-api-tools folder `cd FondUS-Python-SDK/dataflow-api-tools`
3. run pip to install required dependency `python3 -m pip install -r requirements.txt`
4. run `python3 dataflow-api2csv --help` to check the usage
```
```
$ python3 dataflow-api2csv.py --help
usage: dataflow-api2csv.py [-h] [--host HOST] [--dataset DATASET] [--output OUTPUT] [--timerange TIMERANGE] [--username USERNAME] [--password PASSWORD]
                           [--client_id CLIENT_ID] [--client_secret CLIENT_SECRET]

optional arguments:
  -h, --help            show this help message and exit
  --host HOST           host to access, defaults to https://gateway.floodaware.tw
  --dataset DATASET     dataset to extract, simulated/timeseries/catchment-basins/rainfall-01h-merged
  --output OUTPUT       output csv filename, defaults to output.csv
  --timerange TIMERANGE
                        timerange to query, with format 'from=2020-08-31T00.00.00&to=2020-09-01T00.00.00' if not provided will extract latest
  --username USERNAME   username to access data
  --password PASSWORD   password to access data
  --client_id CLIENT_ID
                        client_id to access data
  --client_secret CLIENT_SECRET
                        client_secret to access data

```

#### wflow-water-index tools

Tools to parse wflow output netcdf data and do basic analysis to calculate % with water flowing of each grid cell


##### Install
1. clone this project to local folder
2. enter wflow-water-index folder `cd FondUS-Python-SDK/wflow-water-index`
3. run pip to install required dependency `python3 -m pip install -r requirements.txt`
4. run `python3 wflow-water-index --help` to check the usage

```
usage: wflow-water-index.py [-h] [--input INPUT] [--output OUTPUT] [--bbox BBOX] [--skip SKIP]

optional arguments:
  -h, --help       show this help message and exit
  --input INPUT    source NC filename
  --output OUTPUT  output XYM ascii filename
  --bbox BBOX      bounding box to filter grids, format as x1,y1,x2,y2
  --skip SKIP      skip data of first N steps when model is warming up, default = 24 hour
```

