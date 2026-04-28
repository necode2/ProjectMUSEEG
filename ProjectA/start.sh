#!/bin/bash

# 1. Move to the server directory and start it in the background
cd ProjectA
/opt/anaconda3/bin/uvicorn server:app --reload --port 8000 &

# 2. Wait for the server to initialize (e.g., 5 seconds)
sleep 5

# 3. Move to the site directory and start it
cd ProjectA
python -m http.server 3000 
