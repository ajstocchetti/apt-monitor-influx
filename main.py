import os
import time
from datetime import datetime
from dotenv import load_dotenv

import board
import adafruit_si7021
import adafruit_sht31d

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS


load_dotenv()
influx_addr = os.getenv('INFLUX_ADDR', '192.168.1.5:8086')
influx_token = os.getenv('INFLUX_TOKEN')
influx_bucket = os.getenv('INFLUX_BUCKET', 'home-monitor-01')
influx_org = os.getenv('INFLUX_ORG', 'home-monitor')
device_location = os.getenv('SENSOR_LOC')

# initialize our sensor...
sensor = None
device_type = os.getenv('SENSOR_TYPE')
if device_type == 'si7021':
    sensor = adafruit_si7021.SI7021(board.I2C())
elif device_type == 'sht31d':
    sensor = sensor = adafruit_sht31d.SHT31D(board.I2C())
# verify that sensor was initiated
if sensor is None:
    raise Exception(f"Invalid device type: {device_type}")


def getReading():
    now = datetime.utcnow().isoformat()
    # both si7021 and sht31d have same api
    return getReadingsi7021() + (device_type, now)

def getReadingsi7021():
    tempC = sensor.temperature
    humidity = sensor.relative_humidity
    return (tempC, humidity)

def saveToInflux(tempC, humidity, device_type, ts = datetime.utcnow().isoformat()):
    with InfluxDBClient(url=influx_addr, token=influx_token, org=influx_org) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        data = {
            "measurement": "interior-climate",
            "tags": {
                "location": device_location,
                "sensor": device_type,
            },
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
    (tempC, hum) = readings
    tempF = celciusToFarenheit(tempC)
    print("\nTemperature: %0.1f F [%0.1f C]" % (tempF, tempC))
    print("Humidity: %0.1f %%" % hum)

def celciusToFarenheit(tempC):
    return 9.0/5.0 * tempC + 32

while True:
    try:
        (tempC, hum, device_type, now) = getReading()
        saveToInflux(tempC, hum, device_type, now)
    except Exception as ex:
        print("Error reading/writing:")
        print(ex)
    time.sleep(55) # seconds
