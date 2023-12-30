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



# Create a new team
@app.route('/team/create', methods=['POST'])
def create_team():
    data = request.json
    game_id = data.get('game_id')
    name = data.get('name')
    team = manager.create_team(game_id, name)
    return jsonify({'message': f'Team "{team.name}" created successfully!'}), 201

# Add a team member
@app.route('/team/member/add', methods=['POST'])
def add_team_member():
    data = request.json
    team_id = data.get('team_id')
    name = data.get('name')
    member = manager.add_team_member(team_id, name)
    return jsonify({'message': f'Member "{member.name}" added successfully to the team!'}), 201

# Update team member location
@app.route('/team/member/update_location', methods=['POST'])
def update_team_member_location():
    data = request.json
    member_id = data.get('member_id')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    altitude = data.get('altitude')
    manager.update_team_member_location(member_id, latitude, longitude, altitude)
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
