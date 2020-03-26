"""Flask server for SET"""
import eventlet
import logging
import os
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, join_room, leave_room, send, emit

from Users import User
from Game import Game

app = Flask(__name__)
socketio = SocketIO(app)
app.secret_key = os.getenv("SECRET_KEY", "")

ROOMS = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stats')
def stats():
    """display room stats"""
    resp = {
        "total": len(ROOMS.keys())
    }
    if 'rooms' in request.args:
        if ROOMS:
            resp["rooms"] = sorted([ v.to_json() for v in ROOMS.values() ], key=lambda k: k.get('date_modified'), reverse=True)
        else:
            resp["rooms"] = None
    return jsonify(resp)

@socketio.on('create')
def on_create(data):
    user = User(data['username'],data['pwhash'])

    # create a game and add player
    gm = Game(data['name'], data['size'])
    gm.add_player(user)

    # save gamestate
    room = gm.game_id
    ROOMS[room] = gm
    
    # broadcast gamestate over socket
    join_room(room)
    emit('update_rooms', [room.to_json() for room in ROOMS.values()])
    emit('join_room', {'room': room})

@socketio.on('want_update_rooms')
def want_update_rooms(data):
    emit('update_rooms', [room.to_json() for room in ROOMS.values()])

@socketio.on('join')
def on_join(data): 
    user = User(data['username'],data['pwhash'])

    room = data['room']
    
    if room in ROOMS:
        # add player
        rooms[room].add_player(user)

        # rebroadcast game object
        join_room(room)
        send(ROOMS[room].to_json(), room=room)
    else:
        emit('error', {'error': 'Unable to join room. Room does not exist.'})

@socketio.on('leave')
def on_leave(data):
    
    user = User(data['username'],data['pwhash'])
    room = data['room']

    # prevent errors
    if not room in ROOMS.keys():
        emit('error', {'error' : 'Room does not exist.'})
        return
    
    # remove player
    rooms[room].remove_player(user)

    # rebroadcast game object
    leave_room(room)
    send(ROOMS[room].to_json(), room=room)

@socketio.on('set_select')
def set_select(data):

    user = User(data['username'],data['pwhash'])

    room = data['room']
    selection = data['selection']

    # prevent errors
    if not room in ROOMS.keys():
        emit('error', {'error' : 'Room does not exist.'})
        return

    game = ROOMS[room]

    # check if the player selected a valid set
    if game.check_set(selection):

        # update points
        game.reward(user)
        game.unblock_players()

        # update gameboard
        game.remove_set(selection)
        game.draw()

        # rebroadcast game object
        send(game.to_json(), room=room)
    else:
        
        # disable player until next turn
        game.punish(user)

        # rebroadcast game object
        send(game.to_json(), room=room)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)
