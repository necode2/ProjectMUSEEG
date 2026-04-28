// TODO: Add section where user can volunteer data to help improve the model, 
// e.g. "Help us understand how EEG relates to music preferences! 
// You can choose to share your feedback and EEG data anonymously with our research team. 
// This will help us train better models in the future. [Yes, share my data] [No, keep it private]"

const GENRES = ['lo-fi','ambient','jazz','classical','indie','electronic','hip-hop','r&b','pop','folk','soul','cinematic'];
const MOODS  = ['calm','focused','energized','happy','motivated','relaxed'];

let nickname = ''; // user's nickname, set in connectToEEG()
let sessionId = null;   // set after /connect succeeds, used in every /predict call
let ytApiKey     = ''; // YouTube API key entered by user
let claudeApiKey = ''; // Anthropic API key entered by user
let selectedGenres = []; // genres the user picked
let selectedMoods  = []; // target mood the user picked

let ytPlayer   = null; // the YouTube player object
let queue      = []; // list of tracks to play
let currentIdx = 0; // which track in the queue is playing
let serialPort = ''; // serial port for EEG connection, set in connectToEEG()
let feedbackLog  = []; // history of likes/dislikes with EEG snapshots
let moodHistory  = []; // history of valence scores over time
let userConsent = null; // whether the user has consented to share their data for research

let isLoadingRecs = false; // prevents Claude being called twice at once

// Current EEG values — updated by injectEEGData() or simulateEEGTick()
let eegCurrent = {
    mood: 0.5 // mood tracker, 0 = negative, 1 = positive
    // TODO: (once update model) 
    // valence: 0.5,   // 0 = very negative, 1 = very positive
    // arousal: 0.5,   // 0 = very calm,     1 = very energised
    //stress:  0.3    // 0 = no stress,      1 = very stressed
};

// must get user session and connect to board before allowing them to start the music player
async function connectToEEG(serialPort, nickname, genres, moods) {
    try {
        const response = await fetch('http://localhost:8000/connect', {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json'  // ← tells server to expect JSON
            },
            body: JSON.stringify({ 
                serial_port: serialPort, 
                nickname: nickname,
                genres: genres,
                moods: moods, 
                consent: userConsent
            })  // ← data goes here
        });

        const data = await response.json();
        if (data.status === 'connected') {
            sessionId = data.session_id;
            return { 
                success:   true, 
                returning: data.returning,  // comes from server response
                user_id:   data.user_id,
                is_real_eeg: data.is_real_eeg
            };
        } else {
            return { success: false, returning: false };
        } 
    } catch(e) {
        console.error("Error connecting to EEG server:", e);
        return { success: false, returning: false };
    }
}

// SETUP, genre and mood buttons when page loads
// TODO: make this more elegant with a framework or at least helper functions, but keeping it vanilla for simplicity now
(function buildSetupUI() {
    const genreGrid = document.getElementById('genre-grid');
    GENRES.forEach(genre => {
        const btn = document.createElement('button');
        btn.className = 'genre-button';

        btn.textContent = genre;
        btn.onclick = () => {
            btn.style.fontWeight = btn.style.fontWeight === 'bold' ? '' : 'bold';
            btn.style.backgroundColor = btn.style.fontWeight === 'bold' ? '#d0f0c0' : ''; // light green when selected
            // rebuild selectedGenres from all bold buttons
            selectedGenres = [...document.querySelectorAll('#genre-grid button')]
                .filter(b => b.style.fontWeight === 'bold')
                .map(b => b.textContent);
        };
        genreGrid.appendChild(btn);
    });

    const moodGrid = document.getElementById('mood-grid');
    MOODS.forEach(mood => {
        const btn = document.createElement('button');

        btn.textContent = mood;
        btn.onclick = () => {
            // only one mood can be selected at a time
            document.querySelectorAll('#mood-grid button').forEach(b => {
                b.style.fontWeight = ''
                b.style.backgroundColor = '';
                b.style.color = '';
            });

            btn.style.fontWeight = 'bold';
            btn.style.backgroundColor = '#d0f0c0'; 
            
            selectedMoods = [mood];
        };
        moodGrid.appendChild(btn);
            
    });
})();

function handleConsent(agreed) {
    userConsent = agreed;
    document.getElementById('consent-banner').style.display = 'none';
    continueAfterConsent();
}

function continueToPlayer() {
    document.getElementById('welcome-screen').style.display = 'none';
    document.getElementById('player-screen').style.display  = 'block';
    loadYouTubeAPI();
    startEEGPollLoop();
    renderQueue();
}

// Draws a simple line chart of valence over time on the welcome screen
function drawHistoryChart(history) {
    const ctx = document.getElementById('history-chart').getContext('2d');
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: history.map((_, i) => `Reading ${i + 1}`),
            datasets: [{
                label:           'Mood Score',
                data:            history.map(h => (h.valence * 100).toFixed(0)),
                borderColor:     'green',
                backgroundColor: 'rgba(0,128,0,0.1)',
                fill:            true,
                tension:         0.3
            }]
        },
        options: {
            scales: {
                y: { min: 0, 
                    max: 100, 
                    title: { display: true, text: 'Mood %', color: '#EFF4F0' },
                    ticks: { color: '#EFF4F0'},
                    grid: { color: 'rgba(255,255,255,0.2)' },
                    border: {
                        display: true,
                        color: 'white'
                    }
                },
                x: {
                    border: {
                        display: true,
                        color: 'white'
                    }
                }
            }
        }
    });
}

// START SESSION, called when user clicks "Start Listening"
async function startSession() {
    ytApiKey     = document.getElementById('yt-key').value.trim();
    claudeApiKey = document.getElementById('claude-key').value.trim();
    serialPort = document.getElementById('serial-port').value.trim();
    nickname   = document.getElementById('nickname').value.trim();

    if (!ytApiKey)  { alert('Please enter at least YT API key'); return; } // need to add:  || !claudeApiKey , once Claude is re-enabled 
    if (!selectedGenres.length)      { alert('Pick at least one genre'); return; }
    if (!selectedMoods.length)       { alert('Pick a target mood'); return; }
    if (!serialPort) { alert('Please enter your serial port'); return; }
    if (!nickname) { alert('Please enter a nickname'); return; }

    // show the consent banner before proceeding
    document.getElementById('consent-banner').style.display = 'block';
    document.getElementById('setup-screen').style.display   = 'none';
}

async function continueAfterConsent() {
    const result = await connectToEEG(serialPort, nickname, selectedGenres, selectedMoods);
    if (!result.success) { 
        alert('Could not connect to EEG on that serial port'); 
        return; 
    }

    if (!result.is_real_eeg) {
        document.getElementById('eeg-warning').style.display = 'block';
    }

    if (result.returning) {
        const historyResponse = await fetch (`http://localhost:8000/mood_history?user_id=${result.user_id}`)
        const historyData = await historyResponse.json();
        moodHistory = historyData.map(h => ({ valence: h.mood, ts: new Date(h.timestamp).getTime() }));

        // search YouTube first so queue is ready when they click Continue
        const query  = selectedGenres[0] + ' ' + selectedMoods[0] + ' music';
        const tracks = await searchYouTube(query);
        queue = tracks;

        // populate welcome screen
        document.getElementById('welcome-nickname').textContent = nickname;
        document.getElementById('welcome-stats').textContent = 
            `You have ${historyData.length} mood readings. Average mood: ${(moodHistory.reduce((a,b) => a + b.valence, 0) / moodHistory.length * 100).toFixed(0)}%`;

        // show welcome screen instead of going straight to player
        document.getElementById('setup-screen').style.display  = 'none';
        document.getElementById('welcome-screen').style.display = 'block';
        
        drawHistoryChart(moodHistory);
        return; 
    }
    
    // Search YouTube for tracks matching genre + mood
    // TODO: improve this by asking Claude for a smarter search query based on EEG + feedback, instead of just "genre + mood"
    const query  = selectedGenres[0] + ' ' + selectedMoods[0] + ' music';
    const tracks = await searchYouTube(query);
    if (!tracks.length) { alert('No tracks found — check your YouTube key'); return; }

    queue = tracks;
    
    // Switch screens
    document.getElementById('setup-screen').style.display = 'none';
    document.getElementById('player-screen').style.display = 'block';

    // Boot everything
    loadYouTubeAPI(); // loads the YouTube iframe player
    startEEGPollLoop(); // starts EEG data 
    renderQueue();  // shows the track queue
}


// YOUTUBE SEARCH, calls the YouTube Data API
async function searchYouTube(query, maxResults = 10) {
    const url = `https://www.googleapis.com/youtube/v3/search`
                + `?part=snippet&type=video&videoCategoryId=10`
                + `&maxResults=${maxResults}`
                + `&q=${encodeURIComponent(query)}`
                + `&key=${ytApiKey}`;

    const response = await fetch(url);
    const data = await response.json();

    if (!data.items) { console.error('YouTube error:', data); return []; }

    // Turn the raw API response into a simpler list of track objects
    return data.items.map(item => ({
        id: item.id.videoId,
        title: item.snippet.title,
        channel: item.snippet.channelTitle,
        thumb: item.snippet.thumbnails?.default?.url || '',
        reason: ''   // Claude will fill this in later
    }));
}


// YOUTUBE PLAYER, loads the iframe API and creates the player
function loadYouTubeAPI() {
    // YouTube requires us to load their script, then call our init
    const script = document.createElement('script');
    script.src   = 'https://www.youtube.com/iframe_api';
    document.head.appendChild(script);

    // Before we unload the page (e.g. user closes tab), try to sync any unsaved feedback to the server
    window.addEventListener('beforeunload', () => {
        syncPendingFeedback()
    });

    // YouTube calls this function automatically when it's ready
    window.onYouTubeIframeAPIReady = function() {
        const container = document.getElementById('yt-player-container');
        container.innerHTML = '<div id="yt-player"></div>';

        ytPlayer = new YT.Player('yt-player', {
        height: '360',
        width:  '640',
        videoId: queue[0]?.id || '',
        playerVars: { autoplay: 1, controls: 1 },
        events: {
            onReady:       () => playTrack(0),
            onStateChange: (e) => {
            // When a song finishes, automatically play the next one
                if (e.data === YT.PlayerState.ENDED) {
                        syncPendingFeedback(); // make sure we save any unsaved feedback before moving on
                        nextTrack();
                }
            }
        }
        });
    };
}

function playTrack(idx) {
    if (idx < 0 || idx >= queue.length) return;
    currentIdx = idx;
    const track = queue[idx];

    // Update the UI
    document.getElementById('track-title').textContent   = track.title;
    document.getElementById('track-channel').textContent = track.channel;

    // Tell YouTube to play this video
    if (ytPlayer && ytPlayer.loadVideoById) {
        ytPlayer.loadVideoById(track.id);
    }

    renderQueue();

    // Every 3 tracks, ask Claude for insights + new recommendations
    if (feedbackLog.length > 0 && feedbackLog.length % 3 === 0) {
        askClaude();
    }
}

function nextTrack() {
    if (currentIdx + 1 < queue.length) {
        playTrack(currentIdx + 1);
    } else {
        // Queue ran out — fetch more from Claude + YouTube
        fetchMoreTracks();
    }
}

async function fetchMoreTracks() {
    const query = await getClaudeSearchQuery();
    const tracks = await searchYouTube(query, 8);
    tracks.forEach(t => t.reason = 'Claude rec');
    queue = [...queue, ...tracks];
    renderQueue();
    playTrack(currentIdx + 1);
}

// FEEDBACK, user clicks like or dislike
async function feedback(type) {
    const track = queue[currentIdx];

    // Log the feedback with a snapshot of EEG at this moment
    feedbackLog.push({
        track: track.title,
        id: track.id,
        type:  type,
        eeg:   { ...eegCurrent },   // copy current EEG values
        ts:    Date.now(),
        saved: false  // will be set to true after we successfully send to server
    });

    // save to database
    try {
        await fetch('http://localhost:8000/feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id:    sessionId,
                track_id:      track.id,
                track_title:   track.title,
                feedback_type: type,
                mood_at_time:  eegCurrent.mood
            })
        });
        feedbackLog[feedbackLog.length - 1].saved = true; // mark as saved if no error
    } catch(e) {
        console.error('Error sending feedback to server:', e);
    }

    if (type === 'dislike') {
        // Skip to next track immediately
        setTimeout(nextTrack, 400);
    }

    // Every 2 feedbacks, ask Claude for new insights
    if (feedbackLog.length % 2 === 0) askClaude();
}

async function syncPendingFeedback() {
    const unsaved = feedbackLog.filter(f => !f.saved);
    for (const f of unsaved) {
        try {
            await fetch('http://localhost:8000/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id:    sessionId,
                    track_id:      f.id,
                    track_title:   f.track,
                    feedback_type: f.type,
                    mood_at_time:  f.eeg.mood
                })
            });
            f.saved = true;
        } catch(e) {
            console.error('Error syncing feedback to server:', e);
        }
    }
}


// THIS IS THE KEY FUNCTION 
function startEEGPollLoop() {
    setInterval(async () => {
        try {
            const response = await fetch(`http://localhost:8000/predict?session_id=${sessionId}`);
            const data     = await response.json();

            if (data.status === 'ok' && typeof data.mood === 'number') {
                injectEEGData(data.mood);
            } else {
                console.log('Buffering, EEG status:', data.status, '— samples so far:', data.samples);
            }
        } catch(e) {
            console.error('server.py is unreachable, check to see if running:', e);
        }
    }, 2000);
}


// Call this from Python server's /predict response
// to inject real EEG data into the player.
//
// Example:
//   injectEEGData(0.72)
//
function injectEEGData(mood) {
    eegCurrent.mood = Math.max(0, Math.min(1, mood));
    // eegCurrent.valence = Math.max(0, Math.min(1, valence));
    // eegCurrent.arousal = Math.max(0, Math.min(1, arousal));
    // eegCurrent.stress  = Math.max(0, Math.min(1, stress));

    updateEEGDisplay();
    recordMoodHistory();
}

// Updates the text on screen with current EEG values
function updateEEGDisplay() {
    document.getElementById('mood').textContent = (eegCurrent.mood * 100).toFixed(0) + '%';
    //document.getElementById('val-valence').textContent = (eegCurrent.valence * 100).toFixed(0) + '%';
    //document.getElementById('val-arousal').textContent = (eegCurrent.arousal * 100).toFixed(0) + '%';
    //document.getElementById('val-stress').textContent  = (eegCurrent.stress  * 100).toFixed(0) + '%';
}


// MOOD HISTORY, should track valence over time
function recordMoodHistory() {
    moodHistory.push({ valence: eegCurrent.mood, ts: Date.now() });
    if (moodHistory.length > 30) moodHistory.shift();   // keep last 30 readings
    updateMoodSummary();
}

function updateMoodSummary() {
    if (moodHistory.length < 2) return;

    const recent = moodHistory.slice(-5);
    const avg    = recent.reduce((a, b) => a + b.valence, 0) / recent.length;

    let summary = '';
    if      (avg > 0.65) summary = 'Mood is elevated ✓';
    else if (avg < 0.40) summary = 'Mood is low — adjusting recommendations';
    else                 summary = `Mood is neutral (~${(avg * 100).toFixed(0)}%)`;

    document.getElementById('mood-summary').textContent = summary;
}


// QUEUE DISPLAY, shows upcoming tracks
function renderQueue() {
    const el = document.getElementById('queue-list');
    el.innerHTML = '';

    const slice = queue.slice(currentIdx, currentIdx + 5);
    slice.forEach((track, i) => {
        const div       = document.createElement('div');
        div.textContent = (i === 0 ? '▶ ' : `${i + 1}. `) + track.title + (track.reason ? ` [${track.reason}]` : '');
        if (i > 0) div.onclick = () => playTrack(currentIdx + i);
        el.appendChild(div);
    });
}

// CLAUDE INTEGRATION, get insights + smart search queries
/* async function askClaude() {
    if (isLoadingRecs) return;
    isLoadingRecs = true;

    document.getElementById('insight-text').textContent = 'Claude is thinking...';

    // Build a summary of recent feedback to send to Claude
    const recentFeedback = feedbackLog.slice(-8).map(f =>
        `${f.type.toUpperCase()}: "${f.track}" ` +
        `mood: ${(f.eeg.mood * 100).toFixed(0)}%)`
        //`(valence: ${(f.eeg.valence * 100).toFixed(0)}%, ` +
        //`arousal: ${(f.eeg.arousal * 100).toFixed(0)}%, ` +
        //`stress: ${(f.eeg.stress * 100).toFixed(0)}%)`
    ).join('\n');

    const avgValence = moodHistory.length
        ? (moodHistory.reduce((a, b) => a + b.valence, 0) / moodHistory.length).toFixed(2)
        : 'unknown';


    // later add this 
    // - Valence (positive mood): ${(eegCurrent.valence * 100).toFixed(0)}%
    // - Arousal (energy): ${(eegCurrent.arousal * 100).toFixed(0)}%
    // - Stress: ${(eegCurrent.stress * 100).toFixed(0)}%
    const prompt = `You are an AI music therapist with access to EEG biometric data.

    Current EEG:
    - Valence (positive mood): ${(eegCurrent.mood * 100).toFixed(0)}%
    - Average valence trend: ${avgValence}

    Target mood: ${selectedMoods[0]}
    Currently playing: "${queue[currentIdx]?.title || 'unknown'}"
    Genres: ${selectedGenres.join(', ')}

    Recent feedback:
    ${recentFeedback || 'None yet'}

    In 2-3 sentences: assess if the music is working, and recommend what kind of track to play next.`;

    try {
        const response = await fetch('https://api.anthropic.com/v1/messages', {
        method:  'POST',
        headers: {
            'Content-Type':      'application/json',
            'x-api-key':         claudeApiKey,
            'anthropic-version': '2023-06-01',
            'anthropic-dangerous-direct-browser-access': 'true'
        },
        body: JSON.stringify({
            model:      'claude-sonnet-4-20250514',
            max_tokens: 200,
            messages:   [{ role: 'user', content: prompt }]
        })
        });

        const data = await response.json();
        const text = data.content?.[0]?.text || 'No response';
        document.getElementById('insight-text').textContent = text;

        // Use Claude's insight to pre-fetch better tracks
        await preloadNextBatch();

    } catch(e) {
        document.getElementById('insight-text').textContent = 'Could not reach Claude.';
        console.error(e);
    }

    isLoadingRecs = false;
} /*

// Ask Claude for a YouTube search query based on current EEG state
/*
async function getClaudeSearchQuery() {
    const prompt =
        `Based on these EEG signals, give me ONE YouTube search query (6 words max).\n` +
        `Mood: ${(eegCurrent.mood * 100).toFixed(0)}%, ` +
        //`Valence: ${(eegCurrent.valence * 100).toFixed(0)}%, ` +
        //`Arousal: ${(eegCurrent.arousal * 100).toFixed(0)}%, ` +
        //`Stress: ${(eegCurrent.stress * 100).toFixed(0)}%\n` +
        `Target mood: ${selectedMoods[0]}\n` +
        `Genres: ${selectedGenres.join(', ')}\n` +
        `Reply with ONLY the search query, nothing else.`;

    try {
        const response = await fetch('https://api.anthropic.com/v1/messages', {
        method:  'POST',
        headers: {
            'Content-Type': 'application/json',
            'x-api-key': claudeApiKey,
            'anthropic-version': '2023-06-01',
            'anthropic-dangerous-direct-browser-access': 'true'
        },
        body: JSON.stringify({
            model: 'claude-sonnet-4-20250514',
            max_tokens: 20,
            messages: [{ role: 'user', content: prompt }]
        })
        });

        const data = await response.json();
        return data.content?.[0]?.text?.trim() || (selectedGenres[0] + ' ' + selectedMoods[0]);

    } catch {
        return selectedGenres[0] + ' ' + selectedMoods[0] + ' music';
    }
}
    */


// will start simplely return the same query for testing the pipeline, then improve later with Claude's help once the pipeline is working
async function askClaude() {
    document.getElementById('insight-text').textContent = 
        'Claude disabled for testing — pipeline check mode';
}

// will start with a simple heuristic query and then improve later with Claude's help once the pipeline is working
async function getClaudeSearchQuery() {
    // hardcoded for testing — swap back to Claude once pipeline is confirmed working
    return selectedGenres[0] + ' ' + selectedMoods[0] + ' music';
}

// Fetch new tracks if queue is running low
async function preloadNextBatch() {
if (queue.length - currentIdx > 5) return;   // still enough queued

const query  = await getClaudeSearchQuery();
const tracks = await searchYouTube(query, 6);
tracks.forEach(t => t.reason = 'Claude rec');
queue = [...queue, ...tracks];
renderQueue();
}
