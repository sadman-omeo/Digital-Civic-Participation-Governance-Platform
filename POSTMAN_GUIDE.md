# Lab 04 – API Development and Postman (Flask)
## Student ID: 23301111 | Port: 1111

---

## How to Run the Application

```
cd c:\Users\ASUS\Downloads\sami
pip install flask
python app.py
```
Browser → http://127.0.0.1:1111

---

# ═══════════════════════════════════════════════════════
# FEATURE 1 – AI CHATBOT APIs
# ═══════════════════════════════════════════════════════

---

## API 1 — Send a Message to the Chatbot

| | |
|---|---|
| **Method** | POST |
| **URL** | `http://127.0.0.1:1111/api/chat` |

### Headers
| Key | Value |
|---|---|
| Content-Type | application/json |

### Request Body (raw → JSON)
```json
{
  "session_id": "session_23301111",
  "message": "Hello! What can you do?"
}
```

### Expected Response (200 OK)
```json
{
  "session_id": "session_23301111",
  "user_message": "Hello! What can you do?",
  "bot_reply": "I can: \n• Answer general queries 💬\n• Explain why voting matters 🗳️\n...",
  "timestamp": "2026-03-10 10:30:00"
}
```

### Other Test Messages to Try
```json
{ "session_id": "session_23301111", "message": "Why should I vote?" }
{ "session_id": "session_23301111", "message": "How do I register to vote?" }
{ "session_id": "session_23301111", "message": "What is democracy?" }
{ "session_id": "session_23301111", "message": "Tell me about the I Voted sticker" }
{ "session_id": "session_23301111", "message": "What is Python?" }
```

### Error Case — Missing message field
```json
{}
```
Expected: **400 Bad Request** → `{"error": "Missing 'message' in request body."}`

---

## API 2 — Get Chat History

| | |
|---|---|
| **Method** | GET |
| **URL** | `http://127.0.0.1:1111/api/chat/history?session_id=session_23301111` |

### Headers
*(none required)*

### Request Body
*(none — GET request)*

### Expected Response (200 OK)
```json
{
  "session_id": "session_23301111",
  "message_count": 4,
  "history": [
    { "role": "user", "text": "Hello! What can you do?", "timestamp": "2026-03-10 10:30:00" },
    { "role": "bot",  "text": "I can: ...",              "timestamp": "2026-03-10 10:30:00" },
    { "role": "user", "text": "Why should I vote?",      "timestamp": "2026-03-10 10:31:00" },
    { "role": "bot",  "text": "Voting is your fundamental right...", "timestamp": "2026-03-10 10:31:00" }
  ]
}
```

### Error Case — Missing session_id
`http://127.0.0.1:1111/api/chat/history`  
Expected: **400 Bad Request** → `{"error": "Provide 'session_id' as a query parameter."}`

---

## API 3 — List All Chat Sessions

| | |
|---|---|
| **Method** | GET |
| **URL** | `http://127.0.0.1:1111/api/chat/sessions` |

### Request Body
*(none)*

### Expected Response (200 OK)
```json
{
  "total_sessions": 1,
  "sessions": [
    { "session_id": "session_23301111", "message_count": 4 }
  ]
}
```

---

## API 4 — Clear Chat History

| | |
|---|---|
| **Method** | DELETE |
| **URL** | `http://127.0.0.1:1111/api/chat/clear` |

### Headers
| Key | Value |
|---|---|
| Content-Type | application/json |

### Request Body (raw → JSON)
```json
{
  "session_id": "session_23301111"
}
```

### Expected Response (200 OK)
```json
{
  "message": "Chat history for 'session_23301111' cleared."
}
```

### Error Case — Session not found
```json
{ "session_id": "nonexistent_session" }
```
Expected: **404 Not Found** → `{"error": "Session not found."}`

---

# ═══════════════════════════════════════════════════════
# FEATURE 2 – VOTING + "I VOTED" VIRTUAL STICKER APIs
# ═══════════════════════════════════════════════════════

---

## API 5 — Get List of Candidates

| | |
|---|---|
| **Method** | GET |
| **URL** | `http://127.0.0.1:1111/api/candidates` |

### Request Body
*(none)*

### Expected Response (200 OK)
```json
{
  "candidates": ["Candidate A", "Candidate B", "Candidate C"]
}
```

---

## API 6 — Cast a Vote

| | |
|---|---|
| **Method** | POST |
| **URL** | `http://127.0.0.1:1111/api/vote` |

### Headers
| Key | Value |
|---|---|
| Content-Type | application/json |

### Request Body (raw → JSON)
```json
{
  "voter_id": "voter_23301111",
  "candidate": "Candidate A"
}
```

### Expected Response (201 Created)
```json
{
  "message": "Vote cast successfully! 🎉",
  "voter_id": "voter_23301111",
  "candidate": "Candidate A",
  "sticker_url": "http://127.0.0.1:1111/api/sticker?voter_id=voter_23301111",
  "share_message": "🗳️ I just voted for Candidate A! Exercise your right — every vote shapes our future! #IVoted #Democracy #YouthVotes",
  "timestamp": "2026-03-10 10:35:00"
}
```

### Error Case 1 — Voting twice (same voter_id)
```json
{
  "voter_id": "voter_23301111",
  "candidate": "Candidate B"
}
```
Expected: **409 Conflict** →
```json
{
  "error": "You have already voted!",
  "voter_id": "voter_23301111",
  "voted_for": "Candidate A"
}
```

### Error Case 2 — Invalid candidate
```json
{
  "voter_id": "voter_002",
  "candidate": "Candidate Z"
}
```
Expected: **400 Bad Request** →
```json
{
  "error": "Invalid candidate. Choose from: ['Candidate A', 'Candidate B', 'Candidate C']"
}
```

### Error Case 3 — Missing fields
```json
{
  "voter_id": "voter_003"
}
```
Expected: **400 Bad Request** → `{"error": "Missing 'candidate'."}`

---

## API 7 — Get the "I Voted" Virtual Sticker

| | |
|---|---|
| **Method** | GET |
| **URL** | `http://127.0.0.1:1111/api/sticker?voter_id=voter_23301111` |

### Request Body
*(none — GET request)*

### Expected Response (200 OK)
```json
{
  "voter_id": "voter_23301111",
  "candidate": "Candidate A",
  "voted_at": "2026-03-10 10:35:00",
  "sticker_title": "I Voted! 🗳️",
  "sticker_svg": "<svg xmlns='http://www.w3.org/2000/svg' ...>...</svg>",
  "share_caption": "🗳️ I just VOTED and I'm proud of it! Your vote is your voice — use it! 💪 #IVoted #YouthVotes #Democracy #MakeYourVoiceHeard",
  "social_links": {
    "twitter": "https://twitter.com/intent/tweet?text=I+just+VOTED+%23IVoted+%23YouthVotes",
    "facebook": "https://www.facebook.com/sharer/sharer.php?u=&quote=I+just+VOTED+%23IVoted"
  }
}
```

### Error Case — Voter hasn't voted yet
`http://127.0.0.1:1111/api/sticker?voter_id=nobody`  
Expected: **404 Not Found** → `{"error": "Voter ID not found. Please vote first."}`

---

## API 8 — Check Voting Status

| | |
|---|---|
| **Method** | GET |
| **URL** | `http://127.0.0.1:1111/api/vote/status?voter_id=voter_23301111` |

### Request Body
*(none)*

### Expected Response — Already Voted (200 OK)
```json
{
  "voter_id": "voter_23301111",
  "has_voted": true,
  "voted_for": "Candidate A",
  "voted_at": "2026-03-10 10:35:00"
}
```

### Expected Response — Has NOT Voted (200 OK)
```json
{
  "voter_id": "new_voter",
  "has_voted": false
}
```

---

## API 9 — Get Voting Statistics

| | |
|---|---|
| **Method** | GET |
| **URL** | `http://127.0.0.1:1111/api/vote/stats` |

### Request Body
*(none)*

### Expected Response (200 OK)
```json
{
  "total_votes": 3,
  "candidates": [
    { "candidate": "Candidate A", "votes": 2, "percentage": 66.67 },
    { "candidate": "Candidate B", "votes": 1, "percentage": 33.33 },
    { "candidate": "Candidate C", "votes": 0, "percentage": 0 }
  ],
  "last_updated": "2026-03-10 10:40:00"
}
```

---

# ═══════════════════════════════════════════════════════
# FULL POSTMAN TESTING FLOW (Step-by-Step)
# ═══════════════════════════════════════════════════════

Follow this order to test all APIs sequentially:

### Step 1 — Start Flask server
```
python app.py
```
Server runs at http://127.0.0.1:1111

---

### Step 2 — Chatbot: Send a greeting
- Method: POST | URL: /api/chat
- Body: `{ "session_id": "test_session", "message": "Hello" }`
- ✅ Expect 200 with bot reply

### Step 3 — Chatbot: Ask about voting
- Body: `{ "session_id": "test_session", "message": "Why should I vote?" }`
- ✅ Expect 200 with detailed voting response

### Step 4 — Chatbot: View history
- Method: GET | URL: /api/chat/history?session_id=test_session
- ✅ Expect 200 with 4 messages (2 user + 2 bot)

### Step 5 — Chatbot: List sessions
- Method: GET | URL: /api/chat/sessions
- ✅ Expect list with test_session

### Step 6 — Vote: Get candidates
- Method: GET | URL: /api/candidates
- ✅ Expect 3 candidates

### Step 7 — Vote: Cast vote
- Method: POST | URL: /api/vote
- Body: `{ "voter_id": "voter_23301111", "candidate": "Candidate A" }`
- ✅ Expect 201 with sticker_url and share_message

### Step 8 — Vote: Try voting again (duplicate)
- Same body as Step 7
- ✅ Expect 409 Conflict

### Step 9 — Sticker: Get "I Voted" sticker
- Method: GET | URL: /api/sticker?voter_id=voter_23301111
- ✅ Expect 200 with SVG sticker content

### Step 10 — Vote: Check status
- Method: GET | URL: /api/vote/status?voter_id=voter_23301111
- ✅ Expect has_voted: true

### Step 11 — Vote: Get stats
- Method: GET | URL: /api/vote/stats
- ✅ Expect candidate A with 1 vote

### Step 12 — Chatbot: Clear session
- Method: DELETE | URL: /api/chat/clear
- Body: `{ "session_id": "test_session" }`
- ✅ Expect 200 cleared message

---

# Summary Table

| # | Feature | Method | Endpoint | Purpose |
|---|---------|--------|----------|---------|
| 1 | Chatbot | POST | /api/chat | Send message, get AI reply |
| 2 | Chatbot | GET | /api/chat/history | View conversation history |
| 3 | Chatbot | GET | /api/chat/sessions | List all active sessions |
| 4 | Chatbot | DELETE | /api/chat/clear | Delete session history |
| 5 | Voting | GET | /api/candidates | List candidates |
| 6 | Voting | POST | /api/vote | Cast a vote |
| 7 | Sticker | GET | /api/sticker | Get "I Voted" SVG sticker |
| 8 | Voting | GET | /api/vote/status | Check if voter has voted |
| 9 | Voting | GET | /api/vote/stats | Live voting statistics |

**Student ID:** 23301111  |  **Port:** 1111  |  **Framework:** Flask (Python)
