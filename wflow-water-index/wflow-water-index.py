import argparse
import datetime
import math
from netCDF4 import Dataset
import numpy as np
import threading
import queue

# Worker 類別，負責處理資料


class Worker(threading.Thread):
    def __init__(self, req, res, num):
        threading.Thread.__init__(self)
        self.req = req
        self.res = res
        self.num = num
        self.running = True

    def run(self):
        while self.running or not self.req.empty():
            try:
                data = self.req.get(timeout=1)
                x, y, cx, cy, array = data
                res.put((x, y, np.max(array), np.count_nonzero(array > 0.01)))
                req.task_done()
                # print("Worker %d: %f,%f" % (self.num, x, y))
            except queue.Empty:
                print("Worker %d: Nothing to do, wait 1 second" % (self.num))

    def stop(self):
        self.running = False


def get_range(v, low, high):
    dim = v.get_dims()[0].size
    d = (v[1]-v[0])/2
    i0 = None
    i1 = dim
    for i in range(0, dim):
        if i0 is None and v[i]+d >= low:
            i0 = i
        if v[i]-d <= high:
            i1 = i
    if not i0:
        i0 = 0
    return [i0, i1]


def get_skip_index(v_time):
    dim = v_time.get_dims()[0].size
    n0 = v_time[0]
    for i in range(1, dim):
        if (v_time[i] - n0) >= 1440:
            return i
    return 0


parser = argparse.ArgumentParser()
parser.add_argument("--input", help="source NC filename")
parser.add_argument("--output", help="output XYM ascii filename")
parser.add_argument(
    "--bbox", help="bounding box to filter grids, format as x1,y1,x2,y2")
parser.add_argument(
    "--skip", help="skip data of first N steps when model is warming up, default = 24 hour")
args = parser.parse_args()

input_filename = args.input if args.input else "wflow.nc"
print("Input file:", input_filename)
output_filename = args.output if args.output else "flow.asc"
print("Output file:", output_filename)

bbox = list(map(lambda s: float(s), args.bbox.split(','))
            ) if args.bbox else [-180.0, -90.0, 180, 90.0]
print("Bounding box:", bbox)

wflow = Dataset(input_filename, "r")

print("NETCDF metadata")
# print(wflow.dimensions)
# print(wflow.variables)

v_time = wflow.variables['time']
# print(v_time[:])
skip = args.skip if args.skip else get_skip_index(v_time)
print("Will skip first", skip, "steps")

v_lon = wflow.variables['x']
v_lat = wflow.variables['y']

dx = (v_lon[1]-v_lon[0])/2
dy = (v_lat[1]-v_lat[0])/2

lon_range = get_range(v_lon, bbox[0], bbox[2])
lat_range = get_range(v_lat, bbox[1], bbox[3])

v_data = wflow.variables['flow_simulated']

print("Loading data...")
# cache all data in memory
time = v_time[:]
lon = v_lon[:]
lat = v_lat[:]
data = v_data[:, lat_range[0]:lat_range[1], lon_range[0]:lon_range[1]]

print("Start processing...")
dim_t = wflow.dimensions['time'].size

tt = dim_t - skip

max_v = np.empty([lon.size, lat.size])
count_0_01_v = np.empty([lon.size, lat.size])

progress = dict(processed=0, queued=0, total_grid=(
    lon_range[1]-lon_range[0])*(lat_range[1]-lat_range[0]))

# prepare for multithread
req = queue.Queue()
res = queue.Queue()
workers = [Worker(req, res, 1), Worker(req, res, 2)]
for i in range(0, len(workers)):
    workers[i].start()


def processing_res():
    while workers[0].is_alive() or workers[1].is_alive() or not res.empty():
        try:
            result = res.get(timeout=1)
            (x, y, m, c) = result
            max_v[x, y] = m
            count_0_01_v[x, y] = 1.0 * c / tt
            progress["processed"] += 1
            res.task_done()
        except queue.Empty:
            print("Response worker: Nothing to do, wait 1 second")
        if (progress["processed"] % 1000 == 0):
            print("processed:", progress)
    print("processed:", progress)


threading.Thread(target=processing_res, daemon=True).start()

for x in range(lon_range[0], lon_range[1]):
    cx = lon[x]
    print(cx, "queued:", progress)
    for y in range(lat_range[0], lat_range[1]):
        cy = lat[y]
        id = 'x'+f'{cx:.4f}'+'y'+f'{cy:.4f}'

        vt = np.array(data[skip:dim_t, y, x])
        req.put((x, y, cx, cy, vt))
        progress["queued"] += 1
#        max_v[x,y]=np.max(vt)
#        count_0_1_v=np.count_nonzero(vt>0.01)
wflow.close()

for i in range(0, len(workers)):
    workers[i].stop()

for i in range(0, len(workers)):
    workers[i].join()

res.join()

print("grid with flow value: ",np.count_nonzero(max_v > 0))
print("count with flow value: ",np.count_nonzero(count_0_01_v > 0))

with open(output_filename, 'w') as out_file:
    for x in range(lon_range[0], lon_range[1]):
        cx = lon[x]
        for y in range(lat_range[0], lat_range[1]):
            cy = lat[y]
            m = max_v[x, y]
            c = count_0_01_v[x, y]
            if m > 0 or c > 0:
                out_file.write("%f,%f,%f,%f\n" % (cx, cy, m, c))
