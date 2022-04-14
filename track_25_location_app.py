import urllib.request
import json
import numpy as np
import time
import pandas as pd

from tract_25_location_functions import *

minute_counter = 0
bus_list = []
target_route = 25


while minute_counter < 60:
    data = queryFullData()

    id_list = getVehicleIDsFromRoute(data,target_route)

    for id in id_list:
        if id not in bus_ID_list(bus_list):
            nBus=Bus(id)
            nBus.locateData(data, minute_counter)
            nBus.grab_start_details()
            bus_list.append(nBus)

    for bus in bus_list:
        if bus.getBusID() not in id_list:
            bus.setRecording(False)
        else:
            bus.locateData(data, minute_counter)
            bus.update_location()
            bus.updateApproaches()
            print(bus.locationEntries)

    print(minute_counter)
    time.sleep(30)
    minute_counter += 0.5

print('finished-exporting now')
df = busListToDataFrame(bus_list)
print(df)
df.to_csv(r"C:\Users\nhwil\Desktop\gtfs-playground\recordingExport1.csv")


print('finished')
