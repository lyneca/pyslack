from datetime import datetime
from time import mktime, sleep

JSON_FORMAT = "{{'type': 'message', 'ts': {timestamp}, 'text': {text!r}, 'user': {user_id}, 'channel': {channel_id}}}"

msg_list_format = ('channel_id', 'user_id', 'text')
msg_list = [
    (0, 0, "SET OUTPUT"), 1,
    (0, 0, "ACC register player"), 1,
    (0, 0, "DO plant"), 1,
    (0, 0, "DO eat"), 1,
    (0, 0, "DO chop"), 1,
    (0, 0, "DO pick"), 15,
]

class WebSocket:
    def __init__(self):
        self.last_timestamp = mktime(datetime.now().timetuple())
        self.index = 0
    
    def connect(self, url):
        pass
    
    def next(self):
        while len(msg_list) == 2 * self.index:
            pass
        
        msg = dict(zip(msg_list_format, msg_list[2 * self.index]))
        delay = msg_list[2 * self.index + 1]
        self.last_timestamp += delay
        self.index += 1
        
        output = JSON_FORMAT.format(
            timestamp=self.last_timestamp,
            **msg
        )
        
        sleep(delay)
        
        return output

