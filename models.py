# models.py

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import time
import string
import random

Base = declarative_base()

class Game(Base):
    __tablename__ = 'games'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    #altitude_threshold = Column(Float)
    #teams = relationship('Team', back_populates='game')
    cylinders = relationship('Cylinder', back_populates='game')

    def __init__(self, name, cylinders):
        self.name = name
        self.cylinders = cylinders

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'cylinders': [ c.to_json() for c in self.cylinders ]
        }

class GameInstance(Base):
    __tablename__ = 'gameinstances'
    id = Column(Integer, primary_key=True)
    name     = Column(String)
    password = Column(String)
    game_id = Column(Integer, ForeignKey('games.id'))
    start_date = Column(Integer)
    end_date   = Column(Integer)
    teams = relationship('Team', back_populates='igame')
    game  = relationship('Game')

    def __init__(self, name, game_id):
        self.name = name
        self.teams = []
        self.password = None
        self.game_id = game_id
        self.start_date = time.time()

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'game_id': self.game_id,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'teams': [ t.to_json() for t in self.teams ],
            'cylinders': [ c.to_json() for c in self.game.cylinders ]
        }
    
class Team(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    igame_id = Column(Integer, ForeignKey('gameinstances.id'))
    igame = relationship('GameInstance', back_populates='teams')
    members = relationship('TeamMember', back_populates='team')

    def to_json(self):
        return {
            'name': self.name,
            'id':   self.id,
            'members': [ m.to_json() for m in self.members ]
        }

class TeamMember(Base):
    __tablename__ = 'teammembers'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    password = Column(String)
    team_id = Column(Integer, ForeignKey('teams.id'))
    team = relationship('Team', back_populates='members')
    location_history = relationship('LocationHistory', back_populates='member')

    def __init__(self, name, team_id):
        self.name = name
        self.team_id = team_id
        self.password = self.randomword(64);

    def randomword(self, length):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))
        
    def to_json(self, with_pass=False):
        return {
            'id': self.id,
            'name': self.name,
            'password': self.password if with_pass else None
        }

class LocationHistory(Base):
    __tablename__ = 'locationhistory'
    id = Column(Integer, primary_key=True)
    team_member_id = Column(Integer, ForeignKey('teammembers.id'))
    member = relationship('TeamMember', back_populates='location_history')
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class Cylinder(Base):
    __tablename__ = 'cylinders'
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'))
    game = relationship('Game', back_populates='cylinders')
    latitude = Column(Float)
    longitude = Column(Float)
    radius = Column(Float)

    def __init__(self, latitude, longitude, radius):
        self.latitude = latitude
        self.longitude = longitude
        self.radius = radius

    def to_json(self):
        return { "id": self.id,
                 "game": self.game_id,
                 "latitude": self.latitude,
                 "longitude": self.longitude,
                 "radius" : self.radius
                }
    
