import re
from datetime import datetime

import requests
import websocket

import api

track_changes = False
memory = {}

slack = api.API(api.the_pirates)

players = {}
player_names = {}
game = EcoEnv(make_forest(num_trees=20))

def pb_send(channel, message):
    slack.post_as_bot(
        channel,
        message,
        'Pybot',
        ':godmode:'
    )


def pb_commands(message):
    string = message['text']
    channel = message['channel']
    words = string.split()[1:]
    command = words[0]
    if command == 'set':
        memory[words[1]] = ' '.join(words[2:])
        pb_send(channel, 'Set "%s" to "%s".' % (words[1], ' '.join(words[2:])), )
    elif command == 'get':
        if words[1] in memory:
            pb_send(channel, memory[words[1]])
    elif command == 'reply':
        if len(' '.join(words[1:]).split(' :|: ')) == 2:
            responses[eval('r\'' + ' '.join(words[1:]).split(' :|: ')[0] + '\'')] = ' '.join(words[1:]).split(' :|: ')[1]
            pb_send(channel, "Saved.")
        else:
            pb_send(channel, "Incorrect syntax; must be `pb reply [phrase] :|: [reply]`.")
    elif command == 'track_edits':
        global track_changes
        track_changes = not track_changes

do_functions = {}

def do_commands(message):
    string = message['text']
    words = string.split()[1:]
    channel = message['channel']
    user = message['user']
    if user not in players:
        pb_send(channel, "You are not an active player; register with `ACC register`")
    elif players[user].stun > datetime.now().timestamp():
        pb_send(channel, "You are still busy")
    else return do_functions[words[0]](message['channel'], user, words[1:]);

def do_chop(channel, user, words):
    players[user].do(game, Action.chop, players[user].nearby(type='tree'), datetime.now().timestamp())

do_functions = {
    'chop': do_chop
}

def acc_commands(message):
    syntax = "ACC"
    string = message['text']
    words = string.split()[1:]
    channel = message['channel']
    user = message['user']
    if words == []:
        pass
    elif words[0] == 'register':
        syntax += " register <alias>"
        if len(words) > 2:
            pb_send(channel, "`{syntax}` alias must not contain spaces".format(syntax=syntax))
        elif len(words) < 2:
            pb_send(channel, "`{syntax}`".format(syntax=syntax))
        elif words[1] in player_names
            pb_send(channel, "that name is taken")
        else
            player_names[words[1]] = players[user] = Player(game)
            
def changed_message(message):
    if track_changes:
        pb_send(
            message['channel'],
            '@%s edited "%s" to "%s": %s' % (
                slack.get_user_name(message['message']['user']),
                message['previous_message']['text'],
                message['message']['text'],
                slack.get_permalink(message['previous_message']['ts'], message['channel'])
            )
        )

event_output = {
    'transform': "[{location[0]} - {location[1]}] A {from_type} became a {to_type}! (@{location[2]})"
}

responses = {}
functions = {
    #r'pb .+': pb_commands
    r'DO .+': do_commands
    r'ACC .+': acc_commands
}.items()

initial_metadata = requests.get('https://slack.com/api/rtm.start', params={'token': api.the_pirates}).json()
wss_url = initial_metadata['url']
timestamp = datetime.now().timestamp()

w = websocket.WebSocket()
w.connect(wss_url)

while True:
    n = w.next().replace('true', 'True').replace('false', 'False').replace('none', 'None')
    print(n)
    n = eval(n)
    if all([
                n['type'] == 'message',
        n['hidden'] if 'hidden' in n else True,
                'bot_id' not in n,
                float(n['ts']) > timestamp if 'ts' in n else False
    ]):
        if 'subtype' in n:
            if n['subtype'] == 'message_changed':
                changed_message(n)
            continue
        print(n)
        for key, func in functions:
            if re.match(key, n['text']):
                func(n)
                continue
       # for response in responses:
       #     if re.match(response, n['text']):
       #         pb_send(n['channel'], responses[response])
       #         continue
        for event in game.flush_events()
            pb_send(main_channel, event_output[event['nature']].format(**event))
