# ⚔️ XP Leveling & Battle System — Integration Guide

## Overview

This document covers the new **XP/Level system** and **real-time Level-Up Battle Arena** added to the Education Portal.

---

## 🆕 New Dependencies

Add to `requirements.txt`:
```
Flask-SocketIO==5.3.6
python-socketio==5.10.0
python-engineio==4.8.0
```

Install:
```bash
pip install -r requirements.txt
```

Run server:
```bash
python app.py
```
> Note: The server now uses `socketio.run()` instead of `app.run()` to enable WebSocket support.

---

## ⚡ XP Rewards Table

| Action                  | EXP Gained |
|-------------------------|-----------|
| Successful code solve   | +30       |
| Code attempt (any)      | +5        |
| Per correct quiz answer | +10       |
| Completing a quiz       | +20       |
| Winning a battle        | +75       |
| Losing a battle         | +25       |

---

## 📊 Level Thresholds

| Level | Total EXP Required |
|-------|--------------------|
| 1     | 0                  |
| 2     | 100                |
| 3     | 250                |
| 4     | 450                |
| 5     | 700                |
| 6     | 1,000              |
| 7     | 1,350              |
| 8     | 1,750              |
| 9     | 2,200              |
| 10    | 2,700              |

---

## 🔌 Updated API Responses

### `/api/auth/login` and `/api/auth/register`
Now includes `exp` and `level` in the user object:
```json
{
  "user": {
    "id": 1,
    "name": "Jane",
    "exp": 150,
    "level": 2,
    ...
  }
}
```

### `/api/judge` (Code submission)
Now includes `exp_result`:
```json
{
  "runOutput": "55\n",
  "aiAnalysis": "✓ Success...",
  "success": true,
  "exp_result": {
    "exp_gained": 30,
    "total_exp": 180,
    "old_level": 2,
    "new_level": 2,
    "leveled_up": false,
    "progress": 32,
    "reason": "Code submission"
  }
}
```
> When `leveled_up: true`, trigger the Level-Up Battle prompt in your UI!

### `/api/quiz/submit`
Also includes `exp_result` in the same format.

---

## 🆕 New Endpoints

### `GET /api/user/xp`
**Auth required**

Returns current XP and level info:
```json
{
  "exp": 180,
  "level": 2,
  "progress": 32,
  "exp_for_next": 250,
  "current_threshold": 100
}
```

### `GET /api/leaderboard`
**No auth required**

Returns top 20 users by EXP:
```json
[
  { "rank": 1, "name": "Alice", "student_id": "S001", "level": 5, "exp": 823 },
  { "rank": 2, "name": "Bob",   "student_id": "S002", "level": 4, "exp": 601 }
]
```

---

## ⚔️ Battle System Endpoints

### `POST /api/battle/queue`
**Auth required**

Join the matchmaking queue. Matches players at the **same level**.

**Response — matched immediately:**
```json
{
  "status": "matched",
  "battle_id": 12,
  "problem": {
    "title": "FizzBuzz",
    "description": "Write a function fizzbuzz(n)...",
    "time_limit": 150
  },
  "opponent": { "name": "Bob", "level": 2 }
}
```

**Response — waiting for opponent:**
```json
{
  "status": "waiting",
  "battle_id": 11,
  "message": "Waiting for an opponent at your level..."
}
```
→ Poll `GET /api/battle/poll/<battle_id>` every few seconds while waiting.

---

### `GET /api/battle/poll/<battle_id>`
**Auth required**

Polling fallback for clients without WebSocket.

```json
{
  "battle_id": 11,
  "status": "active",
  "level": 2,
  "winner_id": null,
  "opponent": { "name": "Bob", "level": 2 },
  "problem": {
    "title": "FizzBuzz",
    "description": "...",
    "time_limit": 150
  },
  "started_at": "2026-02-17T10:30:00"
}
```

---

### `POST /api/battle/<battle_id>/submit`
**Auth required**

Submit your code solution. Runs against automated test cases.

**Request:**
```json
{ "code": "def fizzbuzz(n):\n    if n%15==0: return 'FizzBuzz'\n    ..." }
```

**Response — tests pass, battle over:**
```json
{
  "test_results": [
    { "passed": true,  "expected": "Fizz", "actual": "Fizz" },
    { "passed": true,  "expected": "Buzz", "actual": "Buzz" }
  ],
  "all_passed": true,
  "battle_over": true,
  "you_won": true,
  "winner_name": "Jane",
  "exp_result": {
    "exp_gained": 75,
    "total_exp": 325,
    "old_level": 2,
    "new_level": 3,
    "leveled_up": true,
    ...
  }
}
```

**Response — partial pass:**
```json
{
  "test_results": [
    { "passed": true,  "expected": "Fizz",     "actual": "Fizz" },
    { "passed": false, "expected": "FizzBuzz",  "actual": "Fizz" }
  ],
  "all_passed": false,
  "battle_over": false
}
```

---

### `POST /api/battle/<battle_id>/leave`
**Auth required**

Forfeit the battle. The opponent wins automatically.

```json
{ "message": "Left battle" }
```

---

### `GET /api/battle/history`
**Auth required**

Last 10 battles for the current user:
```json
[
  {
    "battle_id": 12,
    "level": 2,
    "opponent": "Bob",
    "you_won": true,
    "date": "2026-02-17T10:35:00"
  }
]
```

---

## 🔌 WebSocket Events (Real-Time)

After login, connect to the WebSocket server and authenticate:

```javascript
const socket = io('http://localhost:5000');

socket.on('connect', () => {
  socket.emit('authenticate', { token: yourJwtToken });
});
```

### Events you receive:

| Event              | When triggered                                | Payload |
|--------------------|-----------------------------------------------|---------|
| `battle_start`     | An opponent is found and battle begins        | `{ battle_id, problem, opponent }` |
| `battle_result`    | Battle ends (win/loss/forfeit)                | `{ battle_id, winner_id, you_won, exp_result }` |
| `opponent_solved`  | Your opponent just solved the problem         | `{ battle_id, message }` |

---

## 🎮 Battle Problem Pool (Level-Scaled)

Problems cycle every 5 levels:

| Level | Problem           | Time Limit |
|-------|-------------------|------------|
| 1     | Sum of Two Numbers | 2 min     |
| 2     | FizzBuzz          | 2.5 min    |
| 3     | Palindrome Check  | 2.5 min    |
| 4     | Fibonacci         | 3 min      |
| 5     | Count Vowels      | 3 min      |
| 6     | Sum of Two Numbers (again) | 2 min |
| ...   | Cycles             | ...        |

---

## 🗂 New Database Tables

### `battle`
| Column            | Type     | Description                          |
|-------------------|----------|--------------------------------------|
| id                | int      | Primary key                          |
| player1_id        | int      | FK → user                            |
| player2_id        | int      | FK → user (null while waiting)       |
| level             | int      | Battle level                         |
| problem_key       | int      | Key into BATTLE_PROBLEMS dict        |
| status            | string   | waiting / active / finished          |
| winner_id         | int      | FK → user (null until battle ends)   |
| player1_solved_at | datetime | Timestamp when P1 solved             |
| player2_solved_at | datetime | Timestamp when P2 solved             |
| started_at        | datetime | When battle became active            |
| finished_at       | datetime | When battle ended                    |

### New `user` columns
| Column | Type | Default |
|--------|------|---------|
| exp    | int  | 0       |
| level  | int  | 1       |

---

## 🖥 Frontend Integration

Place `battle_arena.html` in your `static/` folder:
```
static/
  battle_arena.html   ← The complete battle UI
  new6.html
  new3.html
```

Access at: `http://localhost:5000/battle_arena.html`

### Adding XP bar to your existing dashboard

After any code submission or quiz, use the `exp_result` in the response:
```javascript
function handleExpResult(expResult) {
  if (!expResult) return;

  // 1. Update XP bar
  updateXpBar(expResult.progress, expResult.exp_for_next, expResult.total_exp);

  // 2. Show floating +XP notification
  showXpPopup(`+${expResult.exp_gained} XP`);

  // 3. Level-up!
  if (expResult.leveled_up) {
    showLevelUpModal(expResult.new_level);
    // Prompt user to enter battle queue
  }
}
```

---

## 🔄 Flow Summary

```
User solves code or quiz
         ↓
   EXP awarded via API
         ↓
   Check exp_result.leveled_up
         ↓
   [If leveled up] → Show Level-Up popup
         ↓
   User clicks "Enter Battle" → POST /api/battle/queue
         ↓
   [Status: waiting] → Poll /api/battle/poll/:id every 3s
   [Status: matched] → Show Arena UI immediately
         ↓
   WebSocket: battle_start event fires on both clients
         ↓
   Both users code their solution against same problem
         ↓
   POST /api/battle/:id/submit — runs test cases server-side
         ↓
   First to pass all tests wins
         ↓
   WebSocket: battle_result fires on both clients
         ↓
   Winner: +75 XP | Loser: +25 XP
         ↓
   Level-up check repeats
```
