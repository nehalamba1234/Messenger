from flask import Flask, render_template,request, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room
import os
from flask_login import current_user,LoginManager,login_user, logout_user, login_required
from db import get_user,save_room,add_room_members,save_user


app = Flask(__name__)
app.secret_key = "my_secret_key"
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

connected_users = 0

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return render_template("room.html")

    message = '' 
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = get_user(username)
        if user and user.check_password(password):
            login_user(user)
            return render_template('room.html')
        else:
            message = "failed to login"
    return render_template('login.html', message = message)
        
  
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/signup', methods = ['GET','POST'])
def signUp():
    if request.method=='POST':
        username = request.form.get('username')
        password = request.form.get('password')
        save_user(username,password)
        return redirect(url_for('login'))
    else:
        return render_template('signup.html')
        

@app.route('/chat')
def chat():
    username = request.args.get('username')
    room = request.args.get('room')
    if username and room:
        return render_template('chat.html', username=username, room=room)
    else:
        return redirect(url_for('home'))

@app.route('/create_room',methods =['GET','POST'])
@login_required
def createRoom():
    
    if request.method == 'POST':
        room_name = request.form.get('room_name')
        usernames = [username.strip() for username in request.form.get('members').split(',')]
    if len(room_name) and len(usernames):
        room_id  = save_room(room_name,current_user.username)
        if current_user.username in usernames:
            usernames.remove(current_user.username)
        add_room_members(room_id,room_name,usernames,current_user.usernames)
        return redirect(url_for('view_room'))
    else:
        message = "failed to create room"  
    return render_template('create_room.html')


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

@login_manager.user_loader
def load_user(username):
    return 
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5004))  # Use PORT environment variable or fallback to 5000  
    socketio.run(app, debug=True, host='0.0.0.0', port=port)  # Bind to 0.0.0.0 and use the port variable  