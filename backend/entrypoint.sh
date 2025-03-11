#!/bin/sh
if [ "$RUN_WEBSOCKETS" = "true" ]; then
    exec uvicorn websockets_server:app --host 0.0.0.0 --port 8001 --reload
else
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
fi

