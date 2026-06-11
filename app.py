from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from models import db, User, Message

from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


app.config['SECRET_KEY'] = 'secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode= 'threading'
)

online_users = {}

with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        user = User(
            username=username,
            password=password
        )
        
        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            return "Username already exists"

        db.session.add(user)
        db.session.commit()

        return redirect('/login')

    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(
            username=username,
            password=password
        ).first()

        if user:
            login_user(user)
            return redirect('/dashboard')

    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():

    return render_template(
        'dashboard.html',
        username=current_user.username
    )
    
@app.route('/logout')
@login_required
def logout():

    logout_user()

    return redirect('/login')

@app.route('/chat')
@login_required
def chat():

    messages = Message.query.all()

    return render_template(
        'chatroom.html',
        username=current_user.username,
        messages=messages
    )

@socketio.on('send_message')
def handle_send_message(data):

    new_message = Message(
        username=data['username'],
        message=data['message']
    )

    db.session.add(new_message)
    db.session.commit()

    emit(
        'receive_message',
        data,
        to=data['room']
    )

@socketio.on('user_connected')
def handle_user_connected(data):

    username = data['username']

    online_users[username] = request.sid

    emit(
        'online_users',
        list(online_users.keys()),
        broadcast=True
    )

    emit(
        'user_joined',
        {
            'message': f'{username} joined the chat'
        },
        broadcast=True
    )

@socketio.on('disconnect')
def handle_disconnect():

    username_to_remove = None

    for username, sid in online_users.items():

        if sid == request.sid:
            username_to_remove = username
            break

    if username_to_remove:

        del online_users[username_to_remove]

        emit(
            'online_users',
            list(online_users.keys()),
            broadcast=True
        )

        emit(
            'user_left',
            {
                'message':
                f'{username_to_remove} left the chat'
            },
            broadcast=True
        )

@socketio.on('typing')
def handle_typing(data):

    emit(
        'show_typing',
        {
            'username': data['username']
        },
        broadcast=True,
        include_self=False
    )
    
@socketio.on('stop_typing')
def handle_stop_typing():

    emit(
        'hide_typing',
        broadcast=True
    )

@socketio.on('join_room')
def handle_join_room(data):

    room = data['room']

    join_room(room)

    emit(
        'room_notification',
        {
            'message': f'{data["username"]} joined {room}'
        },
        to=room
    )            

if __name__ == "__main__":
    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=True
    )