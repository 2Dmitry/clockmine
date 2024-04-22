git pull

dc="docker compose -f docker-compose.yml -f docker-compose.dev.yml -f docker-compose.local.yml"

${dc} up --build --remove-orphans -d
