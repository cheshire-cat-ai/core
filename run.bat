@echo off
set choice=%1
set compose=%2

if "%compose%" == "full" (
    set compose="docker-compose-full.yml"
) else (
    set compose="docker-compose.yml"
)

if "%choice%" == "up" (
    docker compose -f %compose% up -d
) else if "%choice%" == "down" (
    docker compose -f %compose% down
) else if "%choice%" == "stop" (
    docker compose -f %compose% stop
) else if "%choice%" == "build" (
    docker compose -f %compose% build --no-cache
) else (
    echo "Invalid command"
)
