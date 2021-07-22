from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session
from urllib.request import Request, urlopen  # Python 3
from urllib.parse import urljoin
import pandas as pd
import datetime
import json,sys,argparse

parser = argparse.ArgumentParser()
parser.add_argument("--host", help="host to access, defaults to https://gateway.floodaware.tw")
parser.add_argument("--dataset", help="dataset to extract, simulated/timeseries/catchment-basins/rainfall-01h-merged")
parser.add_argument("--output", help="output csv filename, defaults to output.csv")
parser.add_argument("--timerange", help="timerange to query, with format 'from=2020-08-31T00.00.00&to=2020-09-01T00.00.00' if not provided will extract latest")
parser.add_argument("--username", help="username to access data")
parser.add_argument("--password", help="password to access data")
parser.add_argument("--client_id", help="client_id to access data")
parser.add_argument("--client_secret", help="client_secret to access data")
args=parser.parse_args()

host=args.host if args.host else "https://gateway.floodaware.tw"
outputfile=args.output if args.output else "output.csv"
dataset=args.dataset

if not dataset:
  sys.exit("please provide a dataset name")

print("Fetch data from ",host, ", downloading" ,dataset)


username=args.username
client_id=args.client_id
password=args.password
client_secret=args.client_secret
timerange=args.timerange

oauth = OAuth2Session(client=LegacyApplicationClient(client_id=client_id))
token = oauth.fetch_token(token_url='https://gateway.floodaware.tw/auth-center/oauth/token',
        username=username, password=password, client_id=client_id,
        client_secret=client_secret)

access_token=token['access_token']

timepath="time-zero" if timerange else "latest"
timequery=timerange if timerange else ""

url=urljoin(host,'fewstaiwan-dataflow-dataset-service/api/v1/datasets/')
url=urljoin(url, dataset + '/')
url=urljoin(url, timepath) 

print("Connecting to url:", url, timequery)

# open a connection to a URL using urllib
#req = Request('https://gateway.floodaware.tw/fewstaiwan-dataflow-dataset-service/api/v1/datasets/simulated/timeseries/catchment-basins/rainfall-01h-merged/latest')
req = Request(url + "?" + timequery)
req.add_header('Accept', 'application/json')
req.add_header('Authorization', 'bearer ' + access_token)
resp = urlopen(req)
content = resp.read()
print ("result code: " + str(resp.getcode()))
json_data = json.loads(content.decode('utf-8'))

list=[]
datalist=json_data['data'] if timequery else [json_data['data']]
for dataset in datalist:
  for location in dataset['PiTimeSeriesArray']:
    row=dict()
    row['Location Names']=location['Header']['LocationName']
    row['Location Ids']=location['Header']['LocationId']
    row['Time(UTC)']=location['Header']['ParameterId']+'_'+location['Header']['QualifierId']
    for event in location['Events']:
      dt=datetime.datetime.strptime(event['Date'], "%Y-%m-%dT%H:%M:%S.%fZ")
      dts=dt.strftime('%Y-%m-%d %H:%M:%S')
      row[dts]=event['Value']
    list.append(row)

pd_data = pd.DataFrame.from_records(list).transpose()

pd_data.to_csv(outputfile, header=False)

print("Data has been written to ", outputfile)
