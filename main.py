import os
from dotenv import load_dotenv
import time
from datetime import datetime
import board
import adafruit_si7021
import json
#from influxdb import InfluxDBClient

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


'''
TODO: setup requirements.txt file
#pip install influxdb
pip install influxdb-client
adafruit-circuitpython-si7021
'''

load_dotenv()
influx_addr = os.getenv('INFLUXADDR', '192.168.1.5:8086')
DEVICE_LOCATION = os.getenv('ROOM')
influx_bucket = 'home-monitor-01'
influx_org = 'home-monitor'
influx_token = os.getenv('INFLUX_TOKEN')
#influx_user = os.getenv('INFLUXUSER')
#influx_pw = os.getenv('INFLUXPW')
#influx_port = 8086

# Create library object using our Bus I2C port
sensor = adafruit_si7021.SI7021(board.I2C())


def getReading():
    now = datetime.utcnow().isoformat()
    tempC = sensor.temperature
    humidity = sensor.relative_humidity
    return (tempC, humidity, now)

def saveToInfluxBoooo(tempC, humidity, ts = datetime.utcnow().isoformat()):
    data = [{
            "measurement": "interior-climate",
            "tags": { "location": DEVICE_LOCATION },
            "time": ts,
            "fields": {
                "tempC": tempC,
                "humidity": humidity
            }
    }]
    client = InfluxDBClient(INFLUX_ADDR, influx_port, influx_user, influx_pw, bucket_name)
    client.write_points(data)
    print(data)

def saveToInflux(tempC, humidity, ts = datetime.utcnow().isoformat()):
    with InfluxDBClient(url=influx_addr, token=influx_token, org=influx_org) as client:
        # blah blah
        write_api = client.write_api(write_options=SYNCHRONOUS)
        data = {
            "measurement": "interior-climate",
            "tags": { "location": DEVICE_LOCATION },
            "time": ts,
            "fields": {
                "tempC": tempC,
                "humidity": humidity
                }
            }
        write_api.write(influx_bucket, influx_org, data)
        print('wrote data')
        client.close()

def printReadings(readings):
    (tempC, hum, now) = readings
    tempF = 9.0/5.0 * tempC + 32
    print("\nTemperature: %0.1f F [%0.1f C]" % (tempF, tempC))
    print("Humidity: %0.1f %%" % hum)


while True:
    #printReadings(getReading())
    (tempC, hum, now) = getReading()
    saveToInflux(tempC, hum, now)
    time.sleep(55)


