# app.py

from flask import Flask, request, jsonify, render_template
from models import Base, Game, Team, TeamMember, Cylinder
from game import GameManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)
# with app.app_context():
#     db.create_all()

manager = GameManager()#db.session)

# Serve static files from the 'web' directory
app.static_folder = 'web'
app.static_url_path= '/static'
 
# # Route for the index page
# @app.route('/')
# def index():
#     return render_template('web/index.html')

# Create a new game
@app.route('/game', methods=['POST'])
def create_game():
    data = request.get_json()

    if 'name' not in data or 'cylinders' not in data:
        return jsonify({'error': 'Invalid payload'}), 400

    name = data['name']
    cylinders_data = data['cylinders']

    # Convert JSON data to Cylinder objects
    cylinders = [Cylinder(c['latitude'], c['longitude'], c['radius']) for c in cylinders_data]

    # Create a new game
    new_game = manager.create_game(name, cylinders)
    print (new_game)

    # Add the new game to the list of games
    #games.append(new_game)

    return jsonify({'game': new_game.to_json() , 'message': 'Game created successfully'}), 201
    # data = request.json
    # name = data.get('name')
    # altitude_threshold = data.get('altitude_threshold')
    # game = manager.create_game(db.session, name, altitude_threshold)
    # return jsonify({'message': f'Game "{game.name}" created successfully!'}), 201

# Update game
@app.route('/game/<int:game_id>', methods=['PATCH'])
def update_game(game_id):

    data = request.get_json()

    game = manager.update_game(game_id, data) #data['cylinders'])

    return jsonify({'game': game.to_json(), 'message': 'Game updated successfully'}), 200

# single game
@app.route('/game/<int:game_id>', methods=['GET'])
def get_single_game(game_id):
    g = manager.find_game_by_id(game_id)
    if g:
        return jsonify({'game': g.to_json()}), 200
    else:
        return jsonify({'message': 'error'}), 400
    
    
# List games
@app.route('/game', methods=['GET'])
def get_games():
    games = manager.list_games()
    return (games)

# List games
@app.route('/game/<int:game_id>', methods=['DELETE'])
def delete_game(game_id):
    if manager.delete_game(game_id):
        return jsonify({'message': "ok"}), 200
    else:
        return jsonify({'message': "error"}), 500


# Create game instance
@app.route('/igame/<int:game_id>', methods=['POST'])
def create_igame(game_id):
    data = request.json
    if 'name' in data:
        gi = manager.create_igame(data['name'], game_id)
        if gi:
            return jsonify({'igame': gi.to_json(), 'message': 'ok'}), 200

    return jsonify({'message': 'nok'}), 500

# get all igames
@app.route("/igame", methods=['GET'])
def get_igames():
    igames = manager.get_all_igames()
    if igames:
        return jsonify({"igames": [ g.to_json() for g in igames ], 'message': 'ok' })
    else:
        return jsonify({'message': 'nok'}), 500

@app.route('/igame/<int:igame_id>', methods=['GET'])
def get_igame(igame_id):
    igame = manager.find_igame_by_id(igame_id)
    if igame:
        return jsonify({'igame': igame.to_json(), 'score': manager.score_igame(igame.id), 'message': 'ok'}), 200
    else:
        return jsonify({'message': 'nok'}), 404

@app.route('/igame/<int:igame_id>', methods=['DELETE'])
def delete_igame(igame_id):
    if manager.delete_igame(igame_id):
        return jsonify({'message': 'ok'}), 200
    else:
        return jsonify({'message': 'nok'}), 500
    
# Create a new team
@app.route('/igame/<int:igame_id>/team', methods=['POST'])
def create_team(igame_id):
    data = request.json
    game_id = data.get('igame_id')
    name = data.get('name')
    if name and name != "":
        team = manager.create_team(igame_id, name)
        return jsonify({'message': f'Team "{team.name}" created successfully!'}), 201
    else:
        return jsonify({'message': 'nok'}), 404

# Delete Team
@app.route('/igame/<int:igame_id>/team/<int:team_id>', methods=['DELETE'])
def delete_team(igame_id, team_id):
    igame = manager.delete_team(igame_id, team_id)
    if igame:
        return jsonify({'igame': igame.to_json(), 'message':'ok'}), 201
    else:
        return jsonify({'message': 'nok'}), 500

# Join a Team
@app.route('/igame/<int:igame_id>/team/<int:team_id>', methods=['POST'])
def join_team(igame_id, team_id):
    data = request.json
    if data and 'player_name' in data and data['player_name'] != "":
        player = manager.join_igame(igame_id, team_id, data['player_name'])
        if player:
            return jsonify({'player': player.to_json(True), 'message': 'ok' })

    return jsonify({'message': 'nok'}), 500

# update color
@app.route('/team/<int:team_id>/color', methods=['PATCH'])
def udpate_color_team(team_id):
    team = manager.update_team_color(team_id)
    return jsonify({'message': 'ok'}), 200

# Add a team member
@app.route('/team/member/add', methods=['POST'])
def add_team_member():
    data = request.json
    team_id = data.get('team_id')
    name = data.get('name')
    member = manager.add_team_member(team_id, name)
    return jsonify({'message': f'Member "{member.name}" added successfully to the team!'}), 201

# Update team member location
@app.route('/player/<int:player_id>', methods=['PATCH'])
def update_team_member_location(player_id):
    data = request.json
    member_pass = data.get('member_password')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    altitude = data.get('altitude')
    manager.update_team_member_location(player_id, member_pass, latitude, longitude, altitude)
    return jsonify({'message': f'Team member location updated successfully!'}), 200

# Create a new cylinder
@app.route('/cylinder/create', methods=['POST'])
def create_cylinder():
    data = request.json
    game_id = data.get('game_id')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    radius = data.get('radius')
    cylinder = manager.create_cylinder(game_id, latitude, longitude, radius)
    return jsonify({'message': 'Cylinder created successfully!'}), 201


if __name__ == '__main__':
    app.run(debug=True)
