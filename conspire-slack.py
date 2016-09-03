import re
import random
from datetime import datetime

import requests
api = __import__('api')
websocket = __import__('websocket')

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

def inform_players():
    for target_id, kappa_id in kappa.items():
        pb_send(target_id, "{kappa_name} can cap you.".format(kappa_name=slack.get_user_name(kappa_id)))

def sign_up(message):
    signup.add(message['user'])

def sign_down(message):
    signup.remove(message['user'])

def admin(command):
    def decorated(message):
        if 'user' in message and slack.get_user_name(message['user']) in admins:
            command(message)
    return decorated

def player(command):
    def decorated(message):
        if 'user' in message:
            if message['user'] in kappa:
                command(message)
            else:
                pb_send(message['channel'], "You must be playing to use that command.")
    return decorated

@admin
def start_game(message):
    global signup, kappa, swapreq, functions, main_channel, eliminated
    if len(signup) < 2:
        return
    main_channel = message['channel']
    eliminated = []
    chain = list(signup)
    random.shuffle(chain)
    kappa = {chain[i-1]: chain[i] for i in range(len(chain))}
    del signup
    swapreq = set()
    functions = game_functions
    pb_send(main_channel, "The game has started! There are {} players".format(len(kappa)))
    inform_players()


def end_routine():
    global kappa, swapreq, signup, functions, main_channel, eliminated
    del kappa
    del swapreq
    del main_channel
    del eliminated
    signup = set()
    functions = prep_functions

@admin
def end_game(message):
    end_routine()
    pb_send(message['channel'], "Game ended.")

def save_routine():
    out = open('kappa.dat', 'w')
    out.write('\n'.join("{}: {}".format(k, v) for k, v in kappa.items()))
    out.close()
    out = open('swapreq.dat', 'w')
    out.write('\n'.join("{}: {}".format(k, v) for k, v in swapreq))
    out.close()

@admin
def save_game(message):
    save_routine()
    pb_send(message['channel'], "Game successfully saved.")

@admin
def load_game(message):
    global signup, kappa, swapreq, functions, main_channel, eliminated
    functions = game_functions
    main_channel = message['channel']
    eliminated = []
    del signup
    kappaf = open('kappa.dat')
    kappa = dict(line.rstrip().split(': ') for line in kappaf)
    kappaf.close()
    swapf = open('swapreq.dat')
    swapreq = set(line.rstrip().split(': ') for line in swapf)
    swapf.close()
    pb_send(message['channel'], "Game successfully loaded.")
    inform_players()
    
@admin
def punish_lyneca(message):
    global admins
    admins = [x for x in admins if x != 'lyneca']

def show_kappa(sharer, target, format="{default_message}", back_format="{default_message}"):
    if sharer not in kappa:
        pb_send(sharer, "You cannot share anything in response as you are eliminated.")
    sharer_kappa = kappa[sharer]
    sharer_name = slack.get_user_name(sharer)
    sharer_kappa_name = slack.get_user_name(sharer_kappa)
    target_name = slack.get_user_name(target)
    fargs = {
        'sharer': sharer_name, 
        'sharer_kappa': sharer_kappa_name, 
        'target': target_name,
    }
    default_forward = "{sharer} has shared with you that {sharer_kappa} can cap them.".format(**fargs)
    default_backward = "{target} has been informed of your kappa.".format(**fargs)
    pb_send(target, format.format(default_message=default_forward, **fargs))
    if back_format: pb_send(sharer, format.format(default_message=default_backward, **fargs))

@player
def kswap(message):
    string = message['text']
    words = string.split()[1:]
    channel = message['channel']
    caller = message['user']
    flag = words.pop(-1)
    if flag not in ['direct', 'cancel', 'delay']:
        words.append(flag)
        flag = 'delay'
    target_name = '_'.join(words)
    if target_name not in slack.users:
        pb_send(channel, "Player \"{}\" not found.".format(target_name))
        return
    target = slack.users[target_name].id
    if flag == 'cancel':
        pb_send(channel, "Share request cancelled." if (caller, target) in swapreq else "Share request not found.")
        swapreq.discard((caller, target))
    else:
        if (target, caller) in swapreq:  # happens whether flag is 'direct' or 'delay'
            swapreq.remove((target, caller))
            show_kappa(sharer=caller, target=target)
            show_kappa(sharer=target, target=caller, format="In response, {default_message}", back_format="In response, {default_message}")
        elif flag == 'delay':
            swapreq.add((caller, target))
        elif flag == 'direct':
            show_kappa(sharer=caller, target=target)

@player
def cap(message):
    target_name = '_'.join(message['text'].split()[1:])
    caller = message['user']
    caller_name = slack.get_user_name(caller)
    if target_name in slack.users:
        target = slack.users[target_name].id
        if target not in kappa:
            pb_send(message['channel'], target_name + (" has already been eliminated!" if target in eliminated else " is not playing this game."))
        elif kappa[target]==caller:
            eliminate(target,'capped')
        else:
            eliminate(caller,'failed')
    else:
        pb_send(message['channel'], "Player \"{}\" not found.".format(target_name))


@player
def resign(message):
    eliminate(message['user'], 'resigned')

@admin
def terminate(message):
    global running
    running = False
    pb_send(message['channel'], "Program terminated")

functions = prep_functions = {
    r'SIGN ?UP': sign_up,
    r'SIGN ?DOWN': sign_down,
    r'START': start_game,
    r'LOAD': load_game,
    r'SCREW LYNECA': punish_lyneca,
    r'TERMINATE': terminate,
}.items()

game_functions = {
    r'KSWAP .+': kswap,
    r'CAP .+': cap,
    r'RESIGN .+': resign,
    r'END': end_game,
    r'SAVE': save_game,
    r'SCREW LYNECA': punish_lyneca,
}.items()

elim_msg = {
    'capped': '{elim} has been capped by {capped_by} and has been eliminated!',
    'resigned': '{elim} has resigned from the game.',
    'failed': '{elim} capped the wrong player, ({wrong_target}) and has been eliminated!',
}

def eliminate(id, reason, wrong_target_name = ''):
    has_new_target = kappa.pop(id)
    name = slack.get_user_name(id)
    eliminated.append(name)
    has_new_target_name = slack.get_user_name(has_new_target)
    has_new_kappa = [k for k in kappa if kappa[k] == id][0]
    pb_send(main_channel, elim_msg[reason].format(elim=name, capped_by=has_new_target_name, wrong_target=wrong_target_name))
    if has_new_target == has_new_kappa:
        eliminated.append(has_new_target_name)
        eliminated.reverse()
        pb_send(main_channel, "The game is over! The results are as follows: \n```" + '\n'.join(str(num+1).rjust(2) + ': ' + place for num, place in enumerate(eliminated)) + '```')
        end_routine()
    else:
        kappa[has_new_kappa] = has_new_target
        pb_send(has_new_kappa, "{new_kappa} can now cap you.".format(new_kappa=has_new_target_name))
        save_routine()

w = websocket.WebSocket()

wss_url = api.get_url(conspire_key)
init_time = datetime.now()
w.connect(wss_url)

running = True
while running:
    n = w.next().replace('true', 'True').replace('false', 'False').replace('none', 'None').replace('null', 'None')
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

