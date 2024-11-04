from flask import Flask, render_template,request, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room
import os

app = Flask(__name__)
socketio = SocketIO(app)

connected_users = 0

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/chat')
def chat():
    username = request.args.get('username')
    room = request.args.get('room')
    if username and room:
        return render_template('chat.html', username=username, room=room)
    else:
        return redirect(url_for('home'))


@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info("{} has sent message to the room {}: {}".format(data['username'],
                                                                    data['room'],
                                                                    data['message']))
    socketio.emit('receive_message', data, room=data['room'])


@socketio.on('join_room')
def handle_join_room_event(data):
    app.logger.info("hadnle room")
    app.logger.info("{} has joined the room {}".format(data['username'], data['room']))
    global connected_users  
    connected_users += 1  
    join_room(data['room'])  
    socketio.emit('join_room_announcement', {**data, "onlineUser": connected_users}, room=data['room'])  


@socketio.on('leave_room')
def handle_leave_room_event(data):
    app.logger.info("{} has left the room {}".format(data['username'], data['room']))
    leave_room(data['room'])
    global connected_users  
    connected_users -= 1
    socketio.emit('leave_room_announcement', data, room=data['room'])


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use PORT environment variable or fallback to 5000  
    socketio.run(app, debug=True, host='0.0.0.0', port=port)  # Bind to 0.0.0.0 and use the port variable  