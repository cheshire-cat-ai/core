@echo off
set choice=%1

if "%choice%" == "up" (
    docker compose up -d
) else if "%choice%" == "down" (
    docker compose down
) else if "%choice%" == "stop" (
    docker compose stop
) else if "%choice%" == "build" (
    docker compose build --no-cache
) else (
    echo "Invalid command"
)
