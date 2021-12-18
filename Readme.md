Setup CircuitPython: https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi

```bash
cd ~
sudo pip3 install --upgrade adafruit-python-shell
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py
sudo python3 raspi-blinka.py
```


# Setup as service
```bash
cp climatemonitor.system /lib/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable climatemonitor.service
```