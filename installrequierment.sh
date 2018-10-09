#!/bin/bash
sudo apt install -y python3-pip
pip3 install requests BeautifulSoup4
pip3 install flask flask-jsonpify flask-sqlalchemy flask-restful
pip3 install -U flask-cors