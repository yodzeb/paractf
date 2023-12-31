# game.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base, Game, Team, TeamMember, Cylinder, GameInstance, LocationHistory
from sqlalchemy.orm import Session

class GameManager:
    def __init__(self, db_url='sqlite:///game.db'):
        #self.session = session
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.s = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.s)
        return

    def create_game(self, name, cylinders):
        game = Game(name=name, cylinders=cylinders)
        self.Session.add(game) #session.add(game)
        self.Session.commit() #session.commit()
        return game

    def list_games(self):
        games = self.Session.query(Game).all()
        return [ g.to_json() for g in games ]

    def create_team(self, igame_id, name):
        team = Team(name=name, igame_id=igame_id)
        self.Session.add(team)
        self.Session.commit()
        return team

    def delete_team(self, igame_id, team_id):
        igame = self.Session.query(GameInstance).get(igame_id)
        if igame:
            for t in igame.teams:
                if t.id == team_id:
                    self.Session.delete(t)
                    igame.teams.remove(t)
                    self.Session.add(igame)
                    self.Session.commit()
                    return igame
        return False
                    
    
    def add_team_member(self, team_id, name):
        member = TeamMember(name=name, team_id=team_id)
        self.Session.add(member)
        self.Session.commit()
        return member

    def update_team_member_location(self, member_id, member_pass, latitude, longitude, altitude):
        member = self.Session.query(TeamMember).get(member_id)
        if member:
            if member.password == member_pass:
                # Store historical location
                location = LocationHistory(
                    team_member_id=member.id,
                    latitude=latitude,
                    longitude=longitude,
                    altitude=altitude,
                )
                print (location.id)
                self.Session.add(location)
                #self.Session.add(member)
                self.Session.commit()

    def create_cylinder(self, game_id, latitude, longitude, radius):
        cylinder = Cylinder(game_id=game_id, latitude=latitude, longitude=longitude, radius=radius)
        self.Session.add(cylinder)
        self.Session.commit()
        return cylinder

    def find_game_by_id(self, game_id):
        return self.Session.query(Game).get(game_id)

    def update_game(self, game_id, data):
        game = self.find_game_by_id(game_id)
        print (game.id)
        if game is None:
            return jsonify({'error': 'Game not found'}), 404

        if 'cylinders' in data:
            for c in game.cylinders:
                self.Session.delete(c)
            # Convert JSON data to Cylinder objects
            new_cylinders = [Cylinder(c['latitude'], c['longitude'], c['radius']) for c in data['cylinders']]

            # Update the game's cylinders
            game.cylinders = new_cylinders
        if 'name' in data:
            game.name = data['name']
            
        self.Session.add(game)
        self.Session.commit()
        return game

    def delete_game(self, game_id):
        game = self.find_game_by_id(game_id)
        if game is None:
            return jsonify({'error': 'Game not found'}), 404

        for c in game.cylinders:
            self.Session.delete(c)
            
        self.Session.delete(game)
        self.Session.commit()
        return True

    def find_igame_by_id(self, igame_id):
        return self.Session.query(GameInstance).get(igame_id)


    def join_igame(self, igame_id, team_id, player_name):
        igame = self.find_igame_by_id(igame_id)
        if igame:
            print (igame)
            for t in igame.teams:
                if t.id == team_id:
                    print ("found team")
                    player = TeamMember(name=player_name, team_id=team_id)
                    self.Session.add(player)
                    self.Session.commit()
                    return player
        print ("error")
        return False

    def get_all_igames(self):
        return self.Session.query(GameInstance).all()
    
    def create_igame(self, name, game_id):
        game = self.find_game_by_id(game_id)
        if game:
            gi = GameInstance(name, game.id)
            self.Session.add(gi)
            self.Session.commit()
            return gi
        return None
    
        
# Usage example:
# manager = GameManager()
# game = manager.create_game('CTF Game', altitude_threshold=100)
# team = manager.create_team(game.id, 'Red Team')
# member = manager.add_team_member(team.id, 'Player 1')
# manager.update_team_member_location(member.id, 34.0522, -118.2437, 50.0)
# cylinder = manager.create_cylinder(game.id, 34.0522, -118.2437, 10.0)
