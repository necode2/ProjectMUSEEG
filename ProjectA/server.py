"""
==================================================================
Server.py
This is the backend server that:
1) Connects to the Cyton+Daisy EEG board (or a synthetic board if connection fails)
2) Loads the trained GRU model for mood prediction
3) Exposes a /predict API endpoint that:
   - Fetches the latest EEG data
   - Preprocesses it (filtering, epoching, normalization)
   - Runs it through the GRU to get a mood prediction
   - Returns the mood as a probability (0.0 to 1.0)

To Run, make sure terminal is in ProjectA directory and run:
    /opt/anaconda3/bin/uvicorn server:app --reload --port 8000

This will start the FastAPI server on http://localhost:8000. 
The frontend can then call http://localhost:8000/predict to get mood predictions in real-time.
==================================================================
"""
import hashlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import torch
import numpy as np
from GRU_v1 import EEG_GRU  # import existing class
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
import mne
import joblib
import uuid
from pydantic import BaseModel
from site_SQL import init_db, get_user, save_user, save_mood_reading, save_feedback, get_mood_history
from dotenv import load_dotenv
from site_SQL import init_db, get_user, save_user, save_mood_reading, save_feedback, get_mood_history, update_consent
import os

# check to see if paths exist
if not os.path.exists("best_gru.pt"):
    print("ERROR: best_gru.pt not found.")
    print("Download from: https://huggingface.co/ruuune/BaseMUSEEG/tree/main")
    sys.exit(1)

if not os.path.exists("eeg_scaler.pkl"):
    print("ERROR: eeg_scaler.pkl not found.")
    print("Download from: https://huggingface.co/ruuune/BaseMUSEEG/tree/main")
    sys.exit(1)

scaler = joblib.load("/Users/noorelbanna/Desktop/ProjectMUSEEG/ProjectA/eeg_scaler.pkl") # Load the same scaler used during training

# Load trained model once at startup
model = EEG_GRU(input_size=16, hidden_size=64, num_layers=2, dropout=0.3)
model.load_state_dict(torch.load("/Users/noorelbanna/Desktop/ProjectMUSEEG/Experiment/StimuliSet/epochs/best_gru.pt", weights_only=True))
model.eval()

init_db()  # make sure database and tables exist before we start handling requests
app = FastAPI()
# This lets HTML file talk to Python (browser security thing)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

active_sessions = {} # session_id --> "board": serial poart, "id": random uuid for session

# recieves info from frontend
class ConnectRequest(BaseModel):
    serial_port: str 
    nickname: str       
    genres: list[str]  
    moods: list[str]
    consent: bool

@app.post("/connect")
def connect(request: ConnectRequest):
    # generate user_id from nickname + serial port
    user_id = hashlib.sha256(
        (request.nickname + request.serial_port).encode()
    ).hexdigest()[:16]
    
    # check if returning or new user
    existing = get_user(user_id)
    if existing:
        is_returning = True
    else:
        # save new user
        save_user(user_id, request.nickname, request.genres, request.moods)
        is_returning = False
    # checking consent and updating it in the database
    update_consent(user_id, request.consent)

    # session id
    session = str(uuid.uuid4())[:8]  # generate a random session ID
    # getting stream of data from brainflow
    PARAMS = BrainFlowInputParams()
    PARAMS.serial_port = request.serial_port 

    try:
        board_ID = BoardIds.CYTON_DAISY_BOARD
        board = BoardShim(board_ID, PARAMS)

        if board.is_prepared():
            board.stop_stream()
            board.release_session()

        board.prepare_session()
        print("Successfully connected to Cyton+Daisy board.")
        is_real_eeg = True
    except Exception as e:
        print(f"Error connecting to Cyton+Daisy board: {e}")
        print("Using synthetic board for testing instead.")
        SYNTHETIC_PARAMS = BrainFlowInputParams()  # empty params for synthetic board
        board_ID = BoardIds.SYNTHETIC_BOARD.value
        board = BoardShim(board_ID, SYNTHETIC_PARAMS)

        if board.is_prepared():
            board.stop_stream()
            board.release_session()

        board.prepare_session()
        print("Successfully connected to synthetic board.")
        is_real_eeg = False


        

    active_sessions[session] = {
        "board": board,
        "eeg_channels": BoardShim.get_eeg_channels(board_ID),
        "board_id": board_ID,
        "user_id":      user_id,
        "is_real_eeg": is_real_eeg,
        "consent": request.consent
    }

    board.start_stream()
    return {
        "session_id":   session,
        "status":       "connected",
        "returning":    is_returning, # frontend uses this for welcome back message
        "user_id":      user_id,
        "is_real_eeg": is_real_eeg
        }


def preprocess_raw_eeg(raw_array):
    """
    raw_array: numpy array shape (channels, samples) in microvolts
    returns:   tensor shape (1, timesteps, channels) ready for GRU
    """
    fs = 125

    # Step 1: µV → V
    data = raw_array / 1e6

    # Step 2: Wrap in MNE
    info = mne.create_info(
        ch_names=[f'EEG{i+1}' for i in range(16)],
        sfreq=fs, ch_types='eeg'
    )
    raw = mne.io.RawArray(data, info, verbose=False)

    # Step 3 & 4: Filter
    raw.notch_filter(60, verbose=False)
    raw.filter(l_freq=0.5, h_freq=40, verbose=False)

    # Step 5: CAR
    raw.set_eeg_reference('average', verbose=False)

    # Step 6: Epoch
    epochs = mne.make_fixed_length_epochs(
        raw, duration=2.0, overlap=1.0, verbose=False
    )
    epoch_data = epochs.get_data() # (n_windows, channels, timesteps)
    x = epoch_data.transpose(0, 2, 1) # (n_windows, timesteps, channels)

    # Step 7: Normalize
    x_2d = x.reshape(-1, x.shape[2]) # flatten to (timesteps, channels)
    x_scaled = scaler.transform(x_2d) 
    x = x_scaled.reshape(x.shape)

    # Step 8: Take the most recent epoch, add batch dim
    latest = x[-1:] # (1, timesteps, channels)
    return torch.tensor(latest, dtype=torch.float32)

@app.get("/predict")
def predict(session_id: str):
    session = active_sessions.get(session_id)
    if not session:
        return {"mood": None, "status": "invalid session"}
    
    board = session["board"]
    EEG_CHANNELS = session["eeg_channels"]

    test_eeg = board.get_current_board_data(250)  # get data
    test_eeg = test_eeg[EEG_CHANNELS]

    if test_eeg.shape[1] < 250:
        return {"mood": None, "status": "buffering", "samples": test_eeg.shape[1]}
    
    x = preprocess_raw_eeg(test_eeg)  # preprocess it to get it ready for the model
    
    
    with torch.no_grad():
        logit = model(x)
        probability = torch.sigmoid(logit).item()  # converts logit → 0.0–1.0

    # save mood reading after every prediction
    if session["is_real_eeg"] and session["consent"]:  # only save real EEG readings, not synthetic ones
        save_mood_reading(session_id, session["user_id"], probability)

    return { 
        "mood": probability, 
        "status": "ok",
        "is_real_eeg": session["is_real_eeg"] }  # 1.0 = very positive, 0.0 = very negative


class FeedbackRequest(BaseModel):
    session_id:   str
    track_id:     str
    track_title:  str
    feedback_type: str   # "like" or "dislike"
    mood_at_time: float

@app.post("/feedback")
def submit_feedback(request: FeedbackRequest):
    session = active_sessions.get(request.session_id)
    if not session:
        return {"status": "invalid session"}
    
    if session["is_real_eeg"]:  # only save feedback for real EEG sessions, not synthetic ones
        save_feedback(
            request.session_id,
            session["user_id"],
            request.track_id,
            request.track_title,
            request.feedback_type,
            request.mood_at_time
        )
    
    return {
        "status": "ok", 
        "is_real_eeg": session["is_real_eeg"]
        }

@app.get("/mood_history")
def mood_history_endpoint(user_id: str): 
    # query mood_readings table for this user
    return get_mood_history(user_id)
