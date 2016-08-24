import re
from datetime import datetime

#import requests
api = __import__('fake_api')
websocket = __import__('fake_websocket')

conspire_key = api.make_keys()['conspiracy']
slack = api.API(conspire_key)

def pb_send(channel, message):
    slack.post_as_bot(
        channel,
        message,
        'Pybot',
        ':godmode:'
    )

signup = set()

def sign_up(message):
    signup.add(message['user'])

def sign_down(message):
    signup.remove(message['user'])

def start_game(message):
    global signup, kappa, swapreq, functions
    chain = list(signup)
    random.shuffle(chain)
    def get_line_graph(l):
        for i in range(len(chain)):
            yield (chain[i], chain[i+1])
        yield (chain[-1], chain[0])
    del signup
    kappa = dict(get_line_graph(chain))
    swapreq = set()
    functions = game_functions

def end_game(message):
    global kappa, swapreq, signup, functions
    del kappa
    del swapreq
    signup = set()
    functions = prep_functions




def kswap(message):
    string = message['text']
    words = string.split()[1:]
    channel = message['channel']
    user = message['user']
    now = datetime.fromtimestamp(float(message['ts']))
    if user not in players:
        pb_send(channel, "You are not an active player; register with `ACC register`")
    elif players[user].stun > now:
        pb_send(channel, "You are still busy")
    else:
        todo = do_functions[words[0]]
        return todo[0](message['channel'], user, words[1:], now, todo[1:]);


def do_targeted(channel, user, words, time_when, args):
    action, target_type = args
    targets = players[user].find_all(game, type=target_type)
    target = targets[0] if targets else None
    players[user].do(game, time_when, action, target_location=(players[user].loc, 0, target))

do_functions = {
    'chop': (do_targeted, 'chop', 'tree'),
    'eat': (do_targeted, 'eat', 'bean'),
    'plant': (do_targeted, 'plant', 'bean'),
    'pick': (do_targeted, 'pick', 'bean stalk'),
}


def acc_commands(message):
    syntax = "ACC"
    string = message['text']
    words = string.split()[1:]
    channel = message['channel']
    user = message['user']
    now = datetime.fromtimestamp(float(message['ts']))
    if words == []:
        pass
    elif words[0] == 'register':
        syntax += " register <alias>"
        if len(words) > 2:
            pb_send(channel, "`{syntax}` alias must not contain spaces".format(syntax=syntax))
        elif len(words) < 2:
            pb_send(channel, "`{syntax}`".format(syntax=syntax))
        elif words[1] in player_names:
            pb_send(channel, "that name is taken")
        else:
            player_names[words[1]] = players[user] = playerrgb.Player(game, now)


responses = {}
functions = prep_functions = {
    r'SIGN UP': sign_in,
    r'SIGN DOWN': sign_out,
    r'START': start_game,
}.items()

game_functions = {
    r'KSWAP .+': kswap,
    r'CAP .+': cap,
    r'RESIGN .+': resign,
    r'END': end_game,
}.items()

w = websocket.WebSocket()

wss_url = api.get_url(eco_key)
init_time = datetime.now()
w.connect(wss_url)

while True:
    n = w.next().replace('true', 'True').replace('false', 'False').replace('none', 'None')
    print(n)
    n = eval(n)
    if all([
        n['type'] == 'message',
        n['hidden'] if 'hidden' in n else True,  # why is this here
        'bot_id' not in n,
        datetime.fromtimestamp(float(n['ts'])) > init_time if 'ts' in n else False
    ]):
        for key, func in functions:
            if re.match(key, n['text']):
                func(n)
                continue
       # for response in responses:
       #     if re.match(response, n['text']):
       #         pb_send(n['channel'], responses[response])
       #         continue

