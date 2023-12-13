#!/bin/bash

choice=$1
compose=$2

if [ -z "$compose" ]
then
  compose="docker-compose.yml"
elif [ "$compose" = "full" ]
then
  compose="docker-compose-full.yml"
fi


case $choice in
  "up")
    docker compose -f $compose up -d
    ;;
  "down")
    docker compose -f $compose down
    ;;
  "stop")
    docker compose -f $compose stop
    ;;
  "build")
    docker compose -f $compose build --no-cache
    ;;
  *)
    echo "Invalid command"
    ;;
esac