import re
from datetime import datetime

#import requests
api = __import__('fake_api')
websocket = __import__('fake_websocket')

import ecorgb

eco_key = api.make_keys()['ecorgb']
slack = api.API(eco_key)

players = {}
player_names = {}
game = ecorgb.EcoEnv(ecorgb.make_forest(num_trees=20))


def pb_send(channel, message):
    slack.post_as_bot(
        channel,
        message,
        'Pybot',
        ':godmode:'
    )


do_functions = {}


def do_commands(message):
    string = message['text']
    words = string.split()[1:]
    channel = message['channel']
    user = message['user']
    now = datetime.fromtimestamp(float(message['ts']))
    if user not in players:
        pb_send(channel, "You are not an active player; register with `ACC register`")
    elif players[user].stun > now:
        pb_send(channel, "You are still busy")
    else: return do_functions[words[0]](message['channel'], user, words[1:], now);


def do_chop(channel, user, words, time_when):
    players[user].do(game, ecorgb.Action.chop, players[user].nearby(game, type='tree'), time_when)


do_functions = {
    'chop': do_chop
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
            player_names[words[1]] = players[user] = ecorgb.Player(game, now)


event_output = {
    'transform': "[{location[0]} - {location[1]}] A {from_type} became a {to_type}! (@{location[2]})"
}


def set_output(message):
    global main_channel
    main_channel = message['channel']


responses = {}
functions = {
    #r'pb .+': pb_commands
    r'DO .+': do_commands,
    r'ACC .+': acc_commands,
    r'SET OUTPUT': set_output
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
    for event in game.flush_events():
        pb_send(main_channel, event_output[event['nature']].format(**event))
