#!/bin/bash

choice=$1

case $choice in
  "up")
    docker compose up -d
    ;;
  "down")
    docker compose down
    ;;
  "stop")
    docker compose stop
    ;;
  "build")
    docker compose build --no-cache
    ;;
  *)
    echo "Invalid command"
    ;;
esac