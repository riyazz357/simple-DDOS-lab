from flask import Flask, request, jsonify, abort
import time
import math
from collections import defaultdict

app = Flask(__name__)
request_count = 0

# --- DEFENSE SYSTEM: RATE LIMITER ---
# Track requests: IP_ADDRESS -> [TIMESTAMP, TIMESTAMP, ...]
request_history = defaultdict(list)

LIMIT_WINDOW = 5 # seconds
MAX_REQUESTS = 50 # Max requests allowed per window

def is_rate_limited(ip):
    current_time = time.time()
    # Get the list of request times for this IP
    timestamps = request_history[ip]
    
    # Filter out timestamps older than the window
    # (Remove requests from > 5 seconds ago)
    request_history[ip] = [t for t in timestamps if current_time - t < LIMIT_WINDOW]
    
    # Check if the remaining count exceeds the limit
    if len(request_history[ip]) >= MAX_REQUESTS:
        return True # BLOCK THEM
    
    # Otherwise, add this new request timestamp
    request_history[ip].append(current_time)
    return False

@app.route('/')
def home():
    return "Server is Online."

@app.route('/heavy_task', methods=['GET'])
def heavy_task():
    global request_count
    
    # 1. APPLY THE SHIELD
    client_ip = request.remote_addr
    if is_rate_limited(client_ip):
        # 429 is the HTTP code for "Too Many Requests"
        return jsonify({"error": "Rate limit exceeded. Cool down."}), 429

    # 2. If allowed, do the work
    request_count += 1
    x = math.factorial(5000) 
    
    return jsonify({
        "status": "Task Complete", 
        "request_id": request_count
    })

if __name__ == '__main__':
    print("🛡️ Protected Server running on port 8000...")
    app.run(host='0.0.0.0', port=8000, debug=False, threaded=True)