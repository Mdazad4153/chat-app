# Real-Time Chat Application

A modern, WhatsApp-style chat application built with Flask and Socket.IO that enables real-time messaging between two users.

## Features

- 💬 Real-time messaging with WebSocket support
- 👤 Two-user system (Abhi and Sanya)
- 📱 Mobile-responsive WhatsApp-style UI
- 💾 Message history with SQLite database
- 🔔 Unread message notifications
- ⌨️ Typing indicators
- ↩️ Message reply functionality
- 🎨 Modern UI with animations

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd chat-app
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open http://localhost:5000 in your browser

## Login Credentials

- User 1:
  - Username: Abhi
  - Password: 415341

- User 2:
  - Username: Sanya
  - Password: 841401

## Technologies Used

- Backend:
  - Flask
  - Flask-SocketIO
  - SQLite
  - Python

- Frontend:
  - HTML5
  - CSS3
  - JavaScript
  - Socket.IO Client
  - Font Awesome Icons

## Features in Detail

1. **Real-Time Messaging**
   - Instant message delivery
   - Typing indicators
   - Online status

2. **Message History**
   - Persistent storage in SQLite
   - Load previous messages
   - Unread message tracking

3. **Reply System**
   - Reply to specific messages
   - Click to view original message
   - Highlighted replies

4. **Modern UI**
   - WhatsApp-inspired design
   - Responsive layout
   - Smooth animations
   - Emoji support

## License

MIT License
