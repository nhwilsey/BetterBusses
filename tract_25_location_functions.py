import urllib.request
import json
import numpy as np
import pandas as pd



class Bus:
    def __init__(self, vID):
        self.vID = vID
        self.recording = True
        self.locationEntries = []
        self.stop_approaches = []
        self.timeQuery = -1
        self.locationUpdate=True

    def get_recording(self):
        #getter for the recroding value
        return self.recording

    def getBusID(self):
        #getter for the vehicle id
        return self.vID

    def setRecording(self, value):
        self.recording = value

    def grab_start_details(self):
        #grab the base details of the route - run after self.query_api()
        self.direction = self.data['MonitoredVehicleJourney']['DirectionRef']
        self.line = self.data['MonitoredVehicleJourney']['LineRef']
        self.journeyID = self.data['MonitoredVehicleJourney']['FramedVehicleJourneyRef']['DatedVehicleJourneyRef']

        # stopcodes = []
        # code = self.data['MonitoredVehicleJourney']['MonitoredCall']['StopPointRef']
        # stopcodes.append(code)
        # for stop in self.data['MonitoredVehicleJourney']['OnwardCalls']['OnwardCall']:
        #     stopcodes.append(stop['StopPointRef'])
        # entry = {'vehicleid': vehicleID, 'time_recorded': data['RecordedAtTime'], 'speed' = np.nan, 'direction': data['MonitoredVehicleJourney']['DirectionRef'], 'lat': data['MonitoredVehicleJourney']['VehicleLocation']['Latitude'], 'long': data['MonitoredVehicleJourney']['VehicleLocation']['Longitude'], 'line': data['MonitoredVehicleJourney']['LineRef'], 'next_stop_codes': stopcodes}

    def locateData(self, data, timeCount):
        if self.recording == True:
            if self.timeQuery != timeCount:
                for entry in data:
                    if entry['MonitoredVehicleJourney']['VehicleRef'] == self.vID:
                        self.data = entry
                        break


    def query_api(self, timeCount):
        #queries the api and grabs the necessary data
        #currently data is quieried in full with queryFullData() function

        if self.recording == True:
            if self.timeQuery != timeCount:
                link='https://api.511.org/transit/VehicleMonitoring?api_key=69c337cc-f428-4089-9996-48fb1f9492eb&agency=SF&Format=json&vehicleID='+str(self.vID)
                with urllib.request.urlopen(link) as url:
                    data = json.loads(url.read().decode('utf-8-sig'))

                try:
                    data=data['Siri']['ServiceDelivery']['VehicleMonitoringDelivery']['VehicleActivity'][0]
                    self.data=data
                except KeyError as e:
                    print('error' + str(e))
                    self.recording = False



    def update_location(self):
        #verify self.recording is true
        #enters the latitude,longitude, and time recorded as a dictionary into self.locationEntries
        if self.recording == True:
            time = self.data['RecordedAtTime']
            if self.locationEntries == [] or self.locationEntries[-1]['recordedTime'] != time:
                entry={
                    'recordedTime': time,
                    'lat': self.data['MonitoredVehicleJourney']['VehicleLocation']['Latitude'],
                    'long': self.data['MonitoredVehicleJourney']['VehicleLocation']['Latitude'],
                }
                self.locationEntries.append(entry)
                self.locationUpdate = True
            else:
                self.locationUpdate = False


    def updateApproaches(self):
        if self.recording == True:
            if self.locationUpdate == True:
                approaches_list = []
                try:
                    approaches_list = [self.data['MonitoredVehicleJourney']['MonitoredCall']['StopPointRef']]

                    if self.data['MonitoredVehicleJourney']['OnwardCalls']['OnwardCall'] != []:
                        for onwardcall in self.data['MonitoredVehicleJourney']['OnwardCalls']['OnwardCall']:
                            approaches_list.append(onwardcall['StopPointRef'])
                except KeyError as e:
                    print(self.data)
                    print('key error in approaches_list' + str(e))

                self.stop_approaches.append(approaches_list)


    def exportDict(self):
        exportDict = {
            'vID': self.vID,
            'line': self.line,
            'journeyID': self.journeyID,
            'direction': self.direction,
            'locationEntries': self.locationEntries,
            'approachEntries': self.stop_approaches,
        }
        return exportDict












        # 'speed' = np.nan
        # self.direction = data['MonitoredVehicleJourney']['DirectionRef']
        # 'lat': data['MonitoredVehicleJourney']['VehicleLocation']['Latitude']
        # 'long': data['MonitoredVehicleJourney']['VehicleLocation']['Longitude']
        # self.line = data['MonitoredVehicleJourney']['LineRef']


def getVehicleIDsFromStop(stopCode):
    #returns a list of the vehicle codes that are being live tracked for the given stop code
    link='https://api.511.org/transit/StopMonitoring?api_key=69c337cc-f428-4089-9996-48fb1f9492eb&agency=SF&stopCode='+str(stopCode)+'&Format=json'
    with urllib.request.urlopen(link) as url:
        data = json.loads(url.read().decode('utf-8-sig'))

    vehicleIDList = []

    if data['ServiceDelivery']['StopMonitoringDelivery']['MonitoredStopVisit'] != []:
        for visit in data['ServiceDelivery']['StopMonitoringDelivery']['MonitoredStopVisit']:
            id = visit['MonitoredVehicleJourney']['VehicleRef']
            vehicleIDList.append(id)

    return vehicleIDList


def getVehicleIDsFromRoute(data, target_route):
    #returns a list of vehicle IDs with the target route
    vehicleIDList = []
    for entry in data:
        if entry['MonitoredVehicleJourney']['LineRef'] == str(target_route):
            id = entry['MonitoredVehicleJourney']['VehicleRef']
            vehicleIDList.append(id)

    return vehicleIDList


def bus_ID_list(bus_list):
    #return a list of all bus ids in use
    #bus_list must be a list of busses
    id_list = []
    for bus in bus_list:
        id_list.append(bus.getBusID())
    return id_list

def queryFullData():
    link='https://api.511.org/transit/VehicleMonitoring?api_key=69c337cc-f428-4089-9996-48fb1f9492eb&agency=SF&Format=json'
    with urllib.request.urlopen(link) as url:
        data = json.loads(url.read().decode('utf-8-sig'))

    data=data['Siri']['ServiceDelivery']['VehicleMonitoringDelivery']['VehicleActivity']

    return data


def busListToDataFrame(bus_list):
    busdf = pd.DataFrame(columns=['vID','line','journeyID','direction','locationEntries','approachEntries'])
    for bus in bus_list:
        dict = bus.exportDict()
        busdf = busdf.append(dict, ignore_index = True)
    return busdf
