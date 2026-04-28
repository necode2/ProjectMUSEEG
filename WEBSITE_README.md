# MUSEEG Interactive Site

An EEG-adaptive music player that uses real-time brainwave data to personalize music recommendations. MUSEEG reads your emotional state via EEG, plays music through YouTube, and uses your feedback to fine tune your experience.

---

## How It Works

MUSEEG combines two data streams to adapt music in real time:

- **EEG signals** — a GRU neural network processes live brainwave data from an OpenBCI Cyton+Daisy board to predict emotional state
- **Explicit feedback** — like and dislike buttons log your reactions alongside your EEG state at that moment

---

## Requirements

- Python 3.10+ (I'm using version 3.13.5)
- OpenBCI Cyton+Daisy board (or runs in synthetic mode for demonstration)
- YouTube Data API key
- Anthropic API key
- A modern browser (Chrome recommended)

---

## Installation

**1 — Clone the repository**
```bash
git clone https://github.com/yourusername/neurotune
cd neurotune
```

**2 — Install Python dependencies**
```bash
pip install fastapi uvicorn brainflow mne torch numpy joblib python-dotenv pydantic requests
```
**3 — Download Model Files**

Download the required model files from Hugging Face 
and place them in the project root directory:

[Download from Hugging Face](https://huggingface.co/ruuune/BaseMUSEEG/tree/main)

Required files:
- best_gru.pt
- eeg_scaler.pkl

you may need to change their file path in `server.py`

**4 — Get your API keys**

- YouTube Data API → [Google Cloud Console](https://console.cloud.google.com)
  - Enable YouTube Data API v3
  - Create an API key under Credentials

- Anthropic API → [Anthropic Console](https://console.anthropic.com)
  - Create an API key (currently functionality with Claude is turned off)

**5 Get your Serial Port**
- Windows → open DeviceManager and look under Ports "(COM&LPT)" 
- Mac → open terminal and type `ls /dev/tty.*` to get a list of ports in use
---


## Running the App

Make sure your terminal is in the project directory, then run:

```bash
./start.sh
```

This starts both servers:
- FastAPI server at `http://localhost:8000`
- HTML file server at `http://localhost:3000`

Then open your browser and go to:
```
http://localhost:3000/site_beta.html
```

---

## Setup

1. Enter your nickname, serial port, and API keys
2. Pick your preferred genres and target mood
3. Review the data consent options
4. Start listening

If no EEG device is detected, the app falls back to synthetic data for demonstration purposes. Note that sessions using synthetic data are not saved.

---

## Project Structure

```
ProjectA/
    site_beta.html    — frontend interface
    site_beta.js      — frontend logic
    styles.css        — styling
    server.py         — FastAPI server, EEG processing, GRU inference
    GRU_v1.py         — GRU model architecture
    site_SQL.py       — SQLite database functions
    start.sh          — startup script
```

---

## Data & Privacy

MUSEEG collects EEG mood readings and music feedback only with your explicit consent. All data is stored locally in a SQLite database on the host machine. You will be prompted for consent each time you open the program.

---

## Research Notes

This project is under active development. Current model outputs a binary positive/negative mood classification. Planned extensions include multi-dimensional EEU output (valence, arousal, stress) and audio feature correlation analysis via Spotify and Web Audio API.

---
## Site Walkthrough
