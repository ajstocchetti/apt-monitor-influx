import time
from monitor import readAndSave

while True:
    readAndSave()
    time.sleep(60) # seconds
