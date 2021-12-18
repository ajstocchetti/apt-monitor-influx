import os
import time
from datetime import datetime
from dotenv import load_dotenv

import board
import adafruit_si7021

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


load_dotenv()
influx_addr = os.getenv('INFLUXADDR', '192.168.1.5:8086')
influx_token = os.getenv('INFLUX_TOKEN')
influx_bucket = os.getenv('INFLUXBUCKET', 'home-monitor-01')
influx_org = os.getenv('INFLUXORG', 'home-monitor')
device_location = os.getenv('SENSOR_LOC')

# Create library object using our Bus I2C port
sensor = adafruit_si7021.SI7021(board.I2C())


def getReading():
    now = datetime.utcnow().isoformat()
    tempC = sensor.temperature
    humidity = sensor.relative_humidity
    return (tempC, humidity, now)

def saveToInflux(tempC, humidity, ts = datetime.utcnow().isoformat()):
    with InfluxDBClient(url=influx_addr, token=influx_token, org=influx_org) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        data = {
            "measurement": "interior-climate",
            "tags": { "location": device_location },
            "time": ts,
            "fields": {
                "tempF": celciusToFarenheit(tempC),
                "humidity": humidity
            }
        }
        write_api.write(influx_bucket, influx_org, data)
        client.close()
        print('wrote data to influx...')

def printReadings(readings):
    (tempC, hum, now) = readings
    tempF = celciusToFarenheit(tempC)
    print("\nTemperature: %0.1f F [%0.1f C]" % (tempF, tempC))
    print("Humidity: %0.1f %%" % hum)

def celciusToFarenheit(tempC):
    return 9.0/5.0 * tempC + 32

while True:
    (tempC, hum, now) = getReading()
    saveToInflux(tempC, hum, now)
    time.sleep(55) # seconds
