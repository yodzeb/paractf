from math import radians, sin, cos, sqrt, atan2
from datetime import datetime

# Abstract super class
class Scoring():
    def __init__(self):
        return

    def haversine(self, lat1, lon1, lat2, lon2):
        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = 6371000 * c  # Radius of the Earth in meters

        return distance

    def is_coordinate_within_circle(self, coord, center, radius):
        # coord and center should be tuples (latitude, longitude)
        distance = self.haversine(coord[0], coord[1], center[0], center[1])
        return distance <= radius

    def get_game_cylinders(slf, igame):
        validations = []
        for c in igame.game.cylinders:
            valid = {
                "cylinder_id": c.id,
                "lat": c.latitude,
                "lon": c.longitude,
                "radius": c.radius,
                "valid_time": 0,
                "valid_color": None,
                "valid_team": None
            }
            validations.append(valid)
        return validations

    def is_location_in_cylinder(self, lh, v):
        if isinstance(lh, dict):
            return self.is_coordinate_within_circle((lh['latitude'], lh['longitude']),(v['lat'], v['lon']),v['radius']) and v['valid_time'] < int(lh['timestamp'])
        else:
            return self.is_coordinate_within_circle((lh.latitude, lh.longitude),(v['lat'], v['lon']),v['radius']) and v['valid_time'] < int(lh.timestamp.timestamp())
    
    def score_igame(self, igame):
        return False

    def score_latest_update(self, igame):
        return []

class ScoringTraditional(Scoring):
    def __init__(self):
        super().__init__()
        
    def score_igame(self, igame):
        counters = {}
        all_locations = []
        validations = self.get_game_cylinders(igame)
        
        for t in igame.teams:
            counters[t.id] = 0
            for m in t.members:
                for lh in m.location_history:
                    all_locations.append( {
                        'team_name': t.name,
                        'team_id':   t.id,
                        'timestamp': lh.timestamp.timestamp(),
                        'latitude':  lh.latitude,
                        'longitude': lh.longitude,
                        'altitude':  lh.altitude
                    })

        for lh in sorted(all_locations, key=lambda x: x['timestamp']):
            if lh['timestamp'] > igame.end_date.timestamp():
                break
            for v in validations:
                if self.is_location_in_cylinder(lh, v):
                    if 'valid_team' in v and v['valid_team'] and 'valid_time' in v:
                        to_add = lh['timestamp'] - v['valid_time']
                        counters[v['valid_team']] += to_add
                    v['valid_time']      = lh['timestamp']
                    v['valid_team']      = lh['team_id']
                    v['valid_team_name'] = lh['team_name']

        compare_date = datetime.utcnow()
        if compare_date > igame.end_date:
            compare_date = igame.end_date
        for v in validations:
            if v['valid_team']:
                to_add = compare_date.timestamp() - v['valid_time']
                counters[v['valid_team']] += to_add
            
        return counters

    def score_latest_update(self, igame):
        validations = self.get_game_cylinders(igame)
        
        for t in igame.teams:
            for m in t.members:
                for lh in m.location_history:
                    for v in validations:
                        if self.is_location_in_cylinder(lh, v):
                            v['valid_time'] = lh.timestamp.timestamp()
                            v['valid_team'] = t.id
                            v['valid_color'] = t.get_color_hex()
        return (validations)


class ScoringFactory():
    def __init__(self):
        return
    
    def get_scoring_system(self, system):
        match system:
            case 'trad':
                return ScoringTraditional()

        return ScoringTraditional()
        
