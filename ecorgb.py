from datetime import datetime, timedelta

class EcoEnv:
    def __init__(self, region):
        self.spawn = (0,0)
        self.places = {self.spawn: region}
        self.events = []
    
    def new_event(self, **kwargs):
        self.events.append(kwargs)
    
    def flush_events(self):
        ret = self.events
        self.events = []
        return ret

class Region:
    def __init__(self, ents=[]):
        self.entities = {}
        self.entity_number = 0
        for ent in ents:
            self.add(ent)
    
    def add(self, entity):
        self.entities[self.entity_number] = entity
        ret = self.entity_number
        self.entity_number += 1
        return ret

def make_forest(num_trees):
    region = Region([{'type': 'tree'} for x in range(num_trees)])
    return region

class Player:
    def __init__(self, env, stun):
        self.loc = env.spawn
        self.stun = stun
    
    def do(self, env, action, target_index, dt_when):
        self.stun = dt_when + action(env, env.places[self.loc], (self.loc, 0, target_index))
        
    def nearby(self, env, **kwargs):
        for loc, each in env.places[self.loc].entities.items():
            good = True
            for k, v in each.items():
                if k in kwargs and kwargs[k] is not v:
                    good = False
            if good:
                return loc

class Action:
    def chop(env, region, location):
        if location[2] in region.entities and region.entities[location[2]]['type'] == 'tree':
            region.entities[location[2]]['type'] = 'log'
            env.new_event(nature='transform', location=location, from_type='tree', to_type='log')
            return timedelta(seconds=10)
        return timedelta()

