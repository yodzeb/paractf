# game.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Game, Team, TeamMember, Cylinder
from sqlalchemy.orm import Session

class GameManager:
    def __init__(self, db_url='sqlite:///game.db'):
        #self.session = session
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)()
        return

    def create_game(self, name, cylinders):
        game = Game(name=name, cylinders=cylinders)
        self.Session.add(game) #session.add(game)
        self.Session.commit() #session.commit()
        return game

    def list_games(self):
        games = self.Session.query(Game).all()
        return [ { 'id': g.id, "name": g.name } for g in games ]

    def create_team(self, game_id, name):
        team = Team(name=name, game_id=game_id)
        self.Session.add(team)
        self.Session.commit()
        return team

    def add_team_member(self, team_id, name):
        member = TeamMember(name=name, team_id=team_id)
        self.Session.add(member)
        self.Session.commit()
        return member

    def update_team_member_location(self, member_id, latitude, longitude, altitude):
        member = self.Session.query(TeamMember).get(member_id)
        if member:
            # Store historical location
            location = LocationHistory(
                team_member_id=member.id,
                latitude=latitude,
                longitude=longitude,
                altitude=altitude,
            )
            self.Session.add(location)

            # Update current location
            member.latitude = latitude
            member.longitude = longitude
            member.altitude = altitude

            self.Session.commit()

    def create_cylinder(self, game_id, latitude, longitude, radius):
        cylinder = Cylinder(game_id=game_id, latitude=latitude, longitude=longitude, radius=radius)
        self.Session.add(cylinder)
        self.Session.commit()
        return cylinder

    def find_game_by_id(self, game_id):
        return self.Session.query(Game).get(game_id)

    def update_game(self, game_id, cylinders):
        game = self.find_game_by_id(game_id)
        print (game.id)
        if game is None:
            return jsonify({'error': 'Game not found'}), 404

        for c in game.cylinders:
            self.Session.delete(c)
        # Convert JSON data to Cylinder objects
        new_cylinders = [Cylinder(c['latitude'], c['longitude'], c['radius']) for c in cylinders]

        # Update the game's cylinders
        game.cylinders = new_cylinders
        self.Session.add(game)
        self.Session.commit()
        return game


# Usage example:
# manager = GameManager()
# game = manager.create_game('CTF Game', altitude_threshold=100)
# team = manager.create_team(game.id, 'Red Team')
# member = manager.add_team_member(team.id, 'Player 1')
# manager.update_team_member_location(member.id, 34.0522, -118.2437, 50.0)
# cylinder = manager.create_cylinder(game.id, 34.0522, -118.2437, 10.0)
