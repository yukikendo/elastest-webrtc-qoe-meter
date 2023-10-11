#!/bin/bash

#apprtcのディレクトリに書き換えて使ってください
cd /home/ohzahata-qoe/Documents/GitHub/apprtc

#sudo docker build . --tag apprtc:latest
docker build . --tag apprtc:latest
#sudo docker run -p 443:443 -p 8080:8080 -p 8089:8089 --rm -ti apprtc:latest
docker run -p 443:443 -p 8080:8080 -p 8089:8089 --rm -ti apprtc:latest