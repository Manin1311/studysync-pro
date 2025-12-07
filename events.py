from flask import request
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from extensions import socketio, db
from models import StudyRoom, User
from datetime import datetime

users_in_room = {}

@socketio.on('join')
def on_join(data):
    username = data.get('username')
    room_id = data.get('room_id')
    
    if not username or not room_id:
        return
        
    room = str(room_id)
    join_room(room)
    
    if room not in users_in_room:
        users_in_room[room] = []
        
    if username not in users_in_room[room]:
        users_in_room[room].append(username)
    
    emit('status', {
        'msg': f'{username} has entered the room.',
        'users': users_in_room[room]
    }, room=room)

@socketio.on('leave')
def on_leave(data):
    username = data.get('username')
    room_id = data.get('room_id')
    
    room = str(room_id)
    leave_room(room)
    
    if room in users_in_room and username in users_in_room[room]:
        users_in_room[room].remove(username)
        
    emit('status', {
        'msg': f'{username} has left the room.',
        'users': users_in_room.get(room, [])
    }, room=room)

@socketio.on('message')
def on_message(data):
    """Handle chat messages"""
    room = str(data.get('room_id'))
    emit('message', {
        'username': data.get('username'),
        'msg': data.get('msg'),
        'timestamp': datetime.utcnow().strftime('%H:%M')
    }, room=room)

@socketio.on('draw')
def on_draw(data):
    """Handle whiteboard drawing events"""
    room = str(data.get('room_id'))
    emit('draw', data, room=room, include_self=False)

@socketio.on('clear_board')
def on_clear(data):
    room = str(data.get('room_id'))
    emit('clear_board', {}, room=room)
