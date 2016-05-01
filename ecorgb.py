import heapq

class EcoEnv:
    def __init__(self, region):
        self.spawn = (0,0)
        self.places = {self.spawn: region}
        self.records = []
        self.queue_num = 0
        self.queue = []
    
    def new_record(self, **kwargs):
        self.records.append(kwargs)
    
    def flush_records(self):
        ret = self.records
        self.records = []
        return ret
    
    def queue_event(self, time, event):
        heapq.heappush(self.queue, (time, self.queue_num, event))
        self.queue_num += 1
    
    def call_events(self, time):
        while len(self.queue) > 0 and time >= self.queue[0][0]:
            sim_time, nul, event = heapq.heappop(self.queue)
            event.call(self, sim_time)
    
    def get(self, location):
        r_l, a_l, e_l = (location + (None, None, None))[0:3]
        r = self.places.get(r_l)
        a = None
        e = r.entities.get(e_l) if r else None
        return (r, a, e)
    

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


def make_region(**ent_nums):
    entities = [
        [{'type': type} for x in range(quantity)] 
        for type, quantity in ent_nums.items()
    ]
    region = Region(sum(entities, []))
    return region
    

class Event:
    class Transform:
        def __init__(self, location, changes):
            self.target = location
            self.changes = changes
        
        def call(self, env, time):
            target = env.get(self.target)[2]
            if target:
                from_type = target['type']
                target.update(self.changes)
                to_type = target['type']
                env.new_record(nature='transform', location=self.target, from_type=from_type, to_type=to_type)
    
