from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_socketio import SocketIO, emit
from datetime import datetime
import os
import sqlite3
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app)

# Fixed users
USERS = {
    'Abhi': '415341',
    'Sanya': '841401'
}

# Track online users and their last seen
online_users = {}
user_last_seen = {}

# Initialize database
def init_db():
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  sender TEXT NOT NULL,
                  receiver TEXT NOT NULL,
                  content TEXT NOT NULL,
                  timestamp TEXT NOT NULL,
                  is_read INTEGER DEFAULT 0)''')
    
    # Add user_status table
    c.execute('''CREATE TABLE IF NOT EXISTS user_status
                 (username TEXT PRIMARY KEY,
                  last_seen TEXT NOT NULL,
                  is_online INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in USERS and USERS[username] == password:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/get_unread_messages')
def get_unread_messages():
    if 'username' not in session:
        return jsonify([])
    
    username = session['username']
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    
    # Get unread messages
    c.execute('''SELECT sender, content, timestamp 
                 FROM messages 
                 WHERE receiver = ? AND is_read = 0
                 ORDER BY timestamp''', (username,))
    messages = []
    for row in c.fetchall():
        messages.append({
            'username': row[0],
            'msg': row[1],
            'timestamp': row[2]
        })
    
    # Mark messages as read
    c.execute('''UPDATE messages 
                 SET is_read = 1 
                 WHERE receiver = ? AND is_read = 0''', (username,))
    conn.commit()
    conn.close()
    
    return jsonify(messages)

@app.route('/get_chat_history')
def get_chat_history():
    if 'username' not in session:
        return jsonify([])
    
    username = session['username']
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    
    # Get all messages where user is sender or receiver
    c.execute('''SELECT sender, content, timestamp 
                 FROM messages 
                 WHERE sender = ? OR receiver = ?
                 ORDER BY timestamp''', (username, username))
    
    messages = []
    for row in c.fetchall():
        messages.append({
            'username': row[0],
            'msg': row[1],
            'timestamp': row[2]
        })
    
    conn.close()
    return jsonify(messages)

@app.route('/get_user_status/<username>')
def get_user_status(username):
    if username not in USERS:
        return jsonify({'error': 'User not found'}), 404
    
    is_online = username in online_users
    last_seen = user_last_seen.get(username, 'Never')
    
    return jsonify({
        'is_online': is_online,
        'last_seen': last_seen
    })

@socketio.on('connect')
def handle_connect():
    if 'username' in session:
        username = session['username']
        online_users[username] = request.sid
        user_last_seen[username] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Broadcast user online status to all clients
        emit('user_status', {
            'username': username,
            'status': 'online',
            'last_seen': user_last_seen[username]
        }, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    if 'username' in session:
        username = session['username']
        if username in online_users:
            del online_users[username]
        user_last_seen[username] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Broadcast user offline status to all clients
        emit('user_status', {
            'username': username,
            'status': 'offline',
            'last_seen': user_last_seen[username]
        }, broadcast=True)

@socketio.on('message')
def handle_message(data):
    if 'username' in session:
        sender = session['username']
        receiver = 'Sanya' if sender == 'Abhi' else 'Abhi'
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Save message to database
        conn = sqlite3.connect('chat.db')
        c = conn.cursor()
        c.execute('''INSERT INTO messages (sender, receiver, content, timestamp)
                     VALUES (?, ?, ?, ?)''', 
                  (sender, receiver, data['msg'], timestamp))
        conn.commit()
        conn.close()
        
        # Prepare message data
        message_data = {
            'msg': data['msg'],
            'username': sender,
            'timestamp': datetime.now().strftime('%H:%M'),
            'id': data.get('id', str(int(datetime.now().timestamp() * 1000)))  # Use provided ID or generate one
        }
        
        # Add reply information if present
        if 'replyTo' in data and data['replyTo']:
            message_data['replyTo'] = data['replyTo']
        
        # Broadcast message
        emit('message', message_data, broadcast=True)

@socketio.on('typing')
def handle_typing(data):
    emit('typing', {
        'username': session.get('username')
    }, broadcast=True, include_self=False)

@socketio.on('stop_typing')
def handle_stop_typing():
    emit('stop_typing', broadcast=True, include_self=False)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, 
                host='0.0.0.0',
                port=port,
                debug=False,
                allow_unsafe_werkzeug=True)
