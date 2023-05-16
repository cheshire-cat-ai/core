#!/bin/bash

###################################################
# 00 - Prerequisites
###################################################
sudo apt-get -y update && sudo apt-get -y upgrade
sudo apt-get -y install gcc make perl
sudo apt-get -y install git

sudo apt-get -y install snapd
sudo snap install core; sudo snap refresh core

sudo snap install docker

sudo apt-get -y install docker-compose 
sudo apt-get upgrade docker-compose



###################################################
# 01 - Installation
###################################################
cd

git clone https://github.com/pieroit/cheshire-cat.git
cd cheshire-cat
cp .env.example .env

sudo docker-compose down
git pull origin main
sudo docker-compose build --no-cache
sudo docker-compose up


read -p "Go to http://localhost:3000 and http://localhost:3000/settings"
