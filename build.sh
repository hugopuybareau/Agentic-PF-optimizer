#build.sh

set -e
echo "Starting to build docker-compose services..."
docker-compose up -d --build

# clean old log files
if [ -f all-services.log ]; then
    echo "Removing old all-services.log..."
    rm all-services.log
fi

echo "Tailing logs live to all-services.log (Ctrl+C to stop tailing; services keep running)..."
docker-compose logs -f > all-services.log
 