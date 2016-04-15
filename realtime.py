import re
from datetime import datetime

import requests
import websocket

import api

track_changes = False
memory = {}

slack = api.API(api.the_pirates)


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


responses = {}
functions = {
    r'pb .+': pb_commands
}

initial_metadata = requests.get('https://slack.com/api/rtm.start', params={'token': api.the_pirates}).json()
wss_url = initial_metadata['url']
timestamp = datetime.now().timestamp()

w = websocket.WebSocket()
w.connect(wss_url)

while True:
    n = w.next().replace('true', 'True').replace('false', 'False')
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
        for function in functions:
            if re.match(function, n['text']):
                functions[function](n)
                continue
        for response in responses:
            if re.match(response, n['text']):
                pb_send(n['channel'], responses[response])
                continue
