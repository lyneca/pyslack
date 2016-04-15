import re
from datetime import datetime

import requests
import websocket

import api

track_changes = False
memory = {}

accusations = {}
accusations_order = []
votes = {
    'live': [],
    'die': [],
}
slack = api.API(api.read_keys('mafia_game_4_bot'))


def pb_send(channel, message):
    try:
        slack.post_as_user(
            channel,
            message
        )
    except api.RestrictedActionException:
        print("Luke, I tried to post to #annoucements again...")


def print_readable(n):
    if n['type'] == 'message' and 'previous_message' not in n:
        print("@%s sent a message to #%s: %s" % (
            slack.get_user_name(n['user']),
            slack.get_channel_name(n['channel']),
            n['text'])
              )
    else:
        if not n['type'] == 'reconnect_url':
            print("Event of type %s" % n['type'])


def show_votes(channel):
    pb_send(channel, "Results of today's trial:")
    pb_send(
        channel,
        '```' +
        'live: %s\n' % len(votes['live']) +
        '\n'.join(['  <@' + user + '>' for user in votes['live']]) +
        '```'
    )
    pb_send(
        channel,
        '```' +
        'die: %s\n' % len(votes['die']) +
        '\n'.join(['  <@' + user + '>' for user in votes['die']]) +
        '```'
    )


def show_accusations(channel):
    string = '```' + (('\n'.join(
        [
            '<@' + accused + '>' +
            ': %s\n' % (len(accusations[accused])) +
            '\n'.join(
                ['  <@' + name + '>' for name in accusations[accused]]
            ) for accused in accusations
            ]
    )) if len(accusations) > 1 else 'There are no accusations.') + '```'
    pb_send(channel, "Results of today's accusation:")
    pb_send(channel, string)


def pb_commands(message):
    string = message['text']
    channel = message['channel']
    words = string.split()[1:]
    command = words[0]
    if command == 'reply':
        if len(' '.join(words[1:]).split(' :|: ')) == 2:
            responses[eval('r\'' + ' '.join(words[1:]).split(' :|: ')[0] + '\'')] = ' '.join(words[1:]).split(' :|: ')[
                1]
            pb_send(channel, "Saved.")
        else:
            pb_send(channel, "Incorrect syntax; must be `pb reply [phrase] :|: [reply]`.")
    elif command == 'track_edits':
        global track_changes
        track_changes = not track_changes
        pb_send(channel, "Tracking of changes is now set to %s" % track_changes)


def mafia_commands(message):
    text = message['text']
    channel = message['channel']
    user = message['user']
    command = text.split()[1]
    params = text.split()[2:]
    if command == 'accuse':
        if len(params) > 0:
            if params[0][:2] == '<@':
                name = params[0][2:-1]
                for person in accusations:
                    if user in accusations[person]:
                        accusations[person].remove(user)
                        if len(accusations[person]) == 0:
                            accusations_order.remove(person)
                if name in accusations:
                    accusations[name].append(user)
                else:
                    accusations_order.append(name)
                    accusations[name] = [user]
                pb_send(channel, "<@%s> accused <@%s>" % (user, name))
        else:
            pb_send(channel, "You gotta specify who you want to accuse!")
    elif command == 'vote':
        if len(params) > 0:
            if params[0] not in votes:
                pb_send(channel, "Wait, live or die? You can't just `vote`, you gotta go `vote live` or `vote die`.")
            else:
                for state in votes:
                    if user in votes[state]:
                        votes[state].remove(user)
                votes[params[0]].append(user)
                pb_send(channel, "<@%s> voted for the accused to %s." % (user, params[0]))
    elif command == 'show' and slack.get_user_name(user) == 'god':
        if len(params) > 0:
            if params[0] == 'accusations':
                show_accusations(channel)
            elif params[0] == 'votes':
                show_votes(channel)
        else:
            pb_send(channel, "What do you want me to show? `show votes` or `show accsusations`")
    elif command == 'say':
        pb_send(channel, ' '.join(params))


def changed_message(message):
    if track_changes:
        pb_send(
            message['channel'],
            '<@%s> edited "%s" to "%s": %s' % (
                message['message']['user'],
                message['previous_message']['text'],
                message['message']['text'],
                slack.get_permalink(message['previous_message']['ts'], message['channel'])
            )
        )


responses = {}
functions = {
    r'^pb .+': pb_commands,
    r'[Ll]ynx: ': mafia_commands,
}

initial_metadata = requests.get('https://slack.com/api/rtm.start',
                                params={'token': api.read_keys('mafia_game_4_bot')}).json()
wss_url = initial_metadata['url']
timestamp = datetime.now().timestamp()

w = websocket.WebSocket()
w.connect(wss_url)
done_trial_announcement = False
person_on_trial = ''

while True:
    n = w.next().replace('true', 'True').replace('false', 'False').replace('null', 'None')
    try:
        n = eval(n)
    except NameError:
        pass
    try:
        print_readable(n)
    except KeyError:
        pass
    if all([n['type'] == 'message', n['hidden'] if 'hidden' in n else True, 'bot_id' not in n,
            float(n['ts']) > timestamp if 'ts' in n else False]):
        if 'subtype' in n:
            if n['subtype'] == 'message_changed':
                changed_message(n)
            continue
        if n['user'] in ['USLACKBOT', slack.users['god'].id]:
            if n['text'] in ["Reminder: It's trial time! Use `lynx: vote [live/die]` to vote live or die.",
                             'lynx: end accuse']:
                show_accusations(n['channel'])
                if len(accusations) > 0:
                    accused = sorted(
                        [(user, len(accusations[user])) for user in accusations],
                        key=lambda x: x[1],
                        reverse=True
                    )
                    top = []
                    for accusation in accused:
                        if accusation[1] == accused[0][1]:
                            top.append(accusation)
                    flag = False
                    for a in accusations_order:
                        for b in top:
                            if a == b[0]:
                                person_on_trial = b[0]
                                flag = True
                    if not flag:
                        pb_send(slack.channels['accusations'].id, "Something's not right... Luke, help!")
                    pb_send(slack.channels['accusations'].id,
                            "<@%s> is on trial!" % person_on_trial)
                    accusations = {}
                else:
                    pb_send(slack.channels['accusations'].id, "Welp, looks like noboody got accused...")
            elif n['text'] in [
                "Reminder: It's night! Use `lynx: target [name]` in a PM to me if you have a night role.",
                "lynx: end trial"
            ]:
                show_votes(n['channel'])
                if len(votes['live']) >= len(votes['die']):
                    pb_send(slack.channels['accusations'].id, "<@%s>, you survived!" % person_on_trial)
                else:
                    pb_send(slack.channels['accusations'].id, "<@%s>, you are dead..." % person_on_trial)
                    slack.invite_to_channel(person_on_trial, slack.channels['collateral'].id)
        for function in functions:
            if re.match(function, n['text']):
                functions[function](n)
                continue
        for response in responses:
            if re.match(response, n['text']):
                pb_send(n['channel'], responses[response])
                continue
