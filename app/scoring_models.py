from math import radians, sin, cos, sqrt, atan2
from datetime import datetime

# Abstract super class with some common helpers
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
                "valid_team": None,
                "altitude": 0
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

    def get_zero_counters(self, igame):
        counters={ team.id: 0 for team in igame.teams }
        return counters
    
    def get_all_lh_dict_sorted(self, igame):
        all_locations = []
        for t in igame.teams:
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

        return sorted(all_locations, key=lambda x: x['timestamp'])

class ScoringTraditional(Scoring):
    def __init__(self):
        super().__init__()
        
    def score_igame(self, igame):
        counters = self.get_zero_counters(igame)
        all_locations = self.get_all_lh_dict_sorted(igame)
        validations = self.get_game_cylinders(igame)

        for lh in all_locations:
            if lh['timestamp'] > igame.end_date.timestamp():
                break
            for v in validations:
                if not lh['altitude']:
                    # sorry mate, need alti
                    continue
                if ('valid_alt' not in v or lh['altitude'] > v['valid_alt']) and self.is_location_in_cylinder(lh, v):
                    if 'valid_team' in v and v['valid_team'] and 'valid_time' in v:
                        to_add = lh['timestamp'] - v['valid_time']
                        counters[v['valid_team']] += to_add
                    v['valid_time']      = lh['timestamp']
                    v['valid_team']      = lh['team_id']
                    v['valid_team_name'] = lh['team_name']
                    v['valid_alt']       = lh['altitude']

        # Add the rest of the score compared to now()
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
                        if (self.is_location_in_cylinder(lh, v)
                            and ('valid_alt' not in v or lh.altitude > v['valid_alt'])
                            and ('valid_time' not in v or lh.timestamp.timestamp() > v['valid_time'])):
                            v['valid_time'] = lh.timestamp.timestamp()
                            v['valid_team'] = t.id
                            v['valid_color'] = t.get_color_hex()
                            v['valid_alt'] = lh.altitude

        return (validations)

# TBD
class DegressiveScoring(Scoring):
    def __init__(self, degress_factor=1):
        self.degress_factor = degress_factor
        super().__init__()

    def score_igame(self, igame):
        counters = self.get_zero_counters(igame)
        all_locations = self.get_all_lh_dict_sorted(igame)
        validations = self.get_game_cylinders(igame)

        # Add the rest of the score compared to now()
        compare_date = datetime.utcnow()
        if compare_date > igame.end_date:
            compare_date = igame.end_date
        compare_date = compare_date.timestamp()
        
        for lh in all_locations:
            if lh['timestamp'] > igame.end_date.timestamp():
                break
            for v in validations:
                if not lh['altitude']:
                    continue
                if (self.is_location_in_cylinder(lh, v)
                    and ('valid_alt'  not in v or lh['altitude'] > (v['valid_alt']  - self.degress_factor * (compare_date-v['valid_time'])))
                    and ('valid_time' not in v or lh['timestamp'] > v['valid_time'])):
                    if 'valid_team' in v and v['valid_team'] and 'valid_time' in v:
                        to_add = lh['timestamp'] - v['valid_time']
                        counters[v['valid_team']] += to_add
                    v['valid_time']      = lh['timestamp']
                    v['valid_team']      = lh['team_id']
                    v['valid_team_name'] = lh['team_name']
                    v['valid_alt']       = lh['altitude']

        for v in validations:
            if v['valid_team']:
                to_add = compare_date - v['valid_time']
                counters[v['valid_team']] += to_add
            
        return counters


    def score_latest_update(self, igame):
        validations = self.get_game_cylinders(igame)
        compare_date = datetime.utcnow().timestamp()
        
        for t in igame.teams:
            for m in t.members:
                for lh in m.location_history: 
                    for v in validations:
                        if (self.is_location_in_cylinder(lh, v)
                            and ('valid_alt' not in v or lh.altitude > (v['valid_alt']  - self.degress_factor * (compare_date-v['valid_time'])))
                            and ('valid_time' not in v or lh.timestamp.timestamp() > v['valid_time'])):
                            v['valid_time'] = lh.timestamp.timestamp()
                            v['valid_team'] = t.id
                            v['valid_color'] = t.get_color_hex()
                            v['valid_alt'] = lh.altitude

        for v in validations:
            if 'valid_alt' in v:
                v['valid_alt'] = max(0,v['valid_alt']  - self.degress_factor * (compare_date-v['valid_time']))
        return (validations)
        
        return
                                    


class ScoringFactory():
    def __init__(self):
        return
    
    def get_scoring_system(self, system):
        # Py3.10 only
        #match system:
        #    case 'trad':
        if system == 'trad':
            return ScoringTraditional()

        if system == 'degress':
            return DegressiveScoring(1)

        # default
        return ScoringTraditional()
        
