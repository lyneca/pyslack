from datetime import datetime, timedelta
from ecorgb import Event

class Targeted:
    def chop(player, env, time, region, area, target, **kwargs):
        target_id, target = target
        if not target or target['type'] != 'tree': return 'TARGET_TYPE'
        target['type'] = 'log'
        env.new_record(actor=player, nature='transform', location=(region[0], area[0], target_id), from_type='tree', to_type='log')
        player.stun = time + timedelta(seconds=10)
    
    def eat(player, env, time, region, area, target, **kwargs):
        target_id, target = target
        if not target or target['type'] != 'bean': return 'TARGET_TYPE'
        del region[1].entities[target_id]
        env.new_record(actor=player, nature='disappear', location=(region[0], area[0], target_id), from_type='bean')
    
    def plant(player, env, time, region, area, target, **kwargs):
        target_id, target = target
        if not target or target['type'] != 'bean': return 'TARGET_TYPE'
        target['type'] = 'young bean stalk'
        env.new_record(actor=player, nature='transform', location=(region[0], area[0], target_id), from_type='bean', to_type='young bean stalk')
        env.queue_event(time + timedelta(seconds=10), Event.Transform((region[0], area[0], target_id), {'type':'bean stalk'}))
    
    def pick(player, env, time, region, area, target, **kwargs):
        target_id, target = target
        if not target or target['type'] != 'bean stalk': return 'TARGET_TYPE'
        del region[1].entities[target_id]
        env.new_record(actor=player, nature='disappear', location=(region[0], area[0], target_id), from_type='bean stalk')
        for i in range(3):
            x = region[1].add({'type': 'bean'})
            env.new_record(actor=player, nature='appear', location=(region[0], area[0], x), to_type='bean')
        player.stun = time + timedelta(seconds=10)
    
    actions = {  # maybe do this automatically using function names somehow?
        'chop': chop,
        'eat': eat,
        'plant': plant,
        'pick': pick,
    }


class Player:
    def __init__(self, env, stun):
        self.loc = env.spawn
        self.stun = stun
    
    def find_all(self, env, **kwargs):
        return [
            this_location 
            for this_location, this in env.places[self.loc].entities.items()  # all nearby entities
            if all([                          # if all
                k in this and this[k] == v  #  conditions are met
                for k, v in kwargs.items()    #  as specified by kwargs
            ])  # could be implemented by casting sets and testing subsets
        ]
    
    def do(self, env, time, action, **kwargs):
        if action in Targeted.actions:
            if time < self.stun: return 'BUSY'
            if 'target_location' not in kwargs: return 'TARGET_NONE'
            t_l = kwargs.pop('target_location')
            target_things = zip(t_l, env.get(t_l))
            kwargs.update(zip(('region', 'area', 'target'), target_things))
            return Targeted.actions[action](self, env, time, **kwargs)
        else: return 'ACTION_BAD'
    
