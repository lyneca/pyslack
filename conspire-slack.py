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

admins = ['spivee','lyneca']
signup = set()

def sign_up(message):
    signup.add(message['user'])

def sign_down(message):
    signup.remove(message['user'])

def admin(command):
    def decorated(message):
        if 'user' in message and slack.get_user_name(message['user']) in admins:
            command(message)
    return decorated

@admin
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

@admin
def end_game(message):
    global kappa, swapreq, signup, functions
    del kappa
    del swapreq
    signup = set()
    functions = prep_functions

@admin
def save_game(message):
    out = open('kappa.dat', 'w')
    out.writelines("{}: {}".format(k, v) for k, v in kappa.items())
    out.close()
    out = open('swapreq.dat', 'w')
    out.writelines("{}: {}".format(k, v) for k, v in swapreq.items())
    out.close()
    pb_send(message['channel'], "Game successfully saved.")

@admin
def load_game(message):
    global signup, kappa, swapreq, functions
    functions = game_functions
    del signup
    kappaf = open('kappa.dat')
    kappa = dict(line.split(': ') for line in kappaf)
    kappaf.close()
    swapf = open('swapreq.dat')
    swapreq = dict(line.split(': ') for line in swapf)
    swapf.close()
    pb_send(message['channel'], "Game successfully loaded.")
    
@admin
def punish_lyneca(message):
    global admins
    admins = [x for x in admins if x != 'lyneca']

def show_kappa(sharer, target, format="{default_message}", back_format="{default_message}"):
    sharer_kappa = kappa[sharer]
    sharer_name = slack.get_user_name(sharer)
    sharer_kappa_name = slack.get_user_name(sharer_kappa)
    fargs = {
        'sharer': sharer_name, 
        'sharer_kappa': sharer_kappa_name, 
        'target': 
    }
    default_forward = "{sharer} has shared with you that {sharer_kappa} can cap them.".format(**fargs)
    default_backward = "{target} has been informed of your kappa.".format(**fargs)
    pb_send(target, format.format(default_message=default_forward, **fargs))
    if back_format: pb_send(sharer, format.format(default_message=default_backward, **fargs))

def kswap(message):
    string = message['text']
    words = string.split()[1:]
    channel = message['channel']
    caller = message['user']
    flag = words.pop(-1)
    if flag not in ['direct', 'cancel', 'delay']:
        words.append(flag)
        flag = delay
    target_name = '_'.join(words)
    try:
        target = slack.users[target_name].id
    except(KeyError):
        pb_send(channel, "Player \"{}\" not found.".format(target_name))
        return
    if flag == 'cancel':
        pb_send(channel, "Share request cancelled." if caller, target in kswap else "Share request not found.")
        kswap.discard((caller, target))
    else 
        if target, caller in kswap:  # happens whether flag is 'direct' or 'delay'
            kswap.remove((target, caller))
            show_kappa(sharer=caller, target=target)
            show_kappa(sharer=target, target=caller, format="In response, {default_message}", back_format="In response, {default_message}")
        else if flag = 'delay':
            kswap.add((caller, target))
        else if flag = 'direct':
            show_kappa(sharer=caller, tarhet=target)


def cap(message):
    target_name = '_'.join(message['text'][1:])
    caller = message['user']
    caller_name = slack.get_user_name(caller)
    try:
        target = slack.users[target_name].id
    except(KeyError):
        pb_send(message['channel'], "Player \"{}\" not found.".format(target_name))
    if kappa[target]=caller:
        eliminate(target,'capped')
    else:
        eliminate(caller,'failed')


def resign(message):
    eliminate(message['user'], 'resigned')

functions = prep_functions = {
    r'SIGN UP': sign_in,
    r'SIGN DOWN': sign_out,
    r'START': start_game,
    r'LOAD': load_game,
    r'SCREW LYNECA': punish_lyneca,
}.items()

game_functions = {
    r'KSWAP .+': kswap,
    r'CAP .+': cap,
    r'RESIGN .+': resign,
    r'END': end_game,
    r'SAVE': save_game,
    r'SCREW LYNECA': punish_lyneca,
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

