#!/bin/bash

echo ""
echo "Stopping Job Matcher..."
docker compose down
echo ""
echo "Done! All services stopped."
echo "Run ./start.sh to start again."
echo ""
