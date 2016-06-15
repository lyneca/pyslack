import re
from datetime import datetime

import requests
import websocket

import api

track_changes = False
memory = {}
api.read_keys()
slack = api.API(api.keys['pirates'])
letters = [
    '.-',
    '-...',
    '-.-.',
    '-..',
    '.',
    '..-.',
    '--.',
    '....',
    '..',
    '.---',
    '-.-',
    '.-..',
    '--',
    '-.',
    '---',
    '.--.',
    '--.-',
    '.-.',
    '...',
    '-',
    '..-',
    '...-',
    '.--',
    '-..-',
    '-.--',
    '--..',
]
numbers = [
    '.----',
    '..---',
    '...--',
    '....-',
    '.....',
    '-....',
    '--...',
    '---..',
    '----.',
    '-----'
]

symbols = {
    '"': '.-..-.',
    '$': '...-..-',
    '\'': '.----.',
    '(': '-.--.',
    ')': '-.--.-',
    '[': '-.--.',
    ']': '-.--.-',
    '+': '.-.-.',
    ',': '--..--',
    '-': '-....-',
    '.': '.-.-.-',
    '/': '-..-.',
    ':': '---...',
    ';': '-.-.-.',
    '=': '-...-',
    '?': '..--..',
    '@': '.--.-.',
    '_': '..--.-',
    '¶': '.-.-..',
    '!': '-.-.--',
}
letters = {chr(x + 97): letters[x] for x in range(25)}
numbers = {str(x): numbers[x] for x in range(10)}
text_to_morse = letters
text_to_morse.update(numbers)
text_to_morse.update(symbols)
morse_to_text = {text_to_morse[x]: x for x in text_to_morse}


def send(channel, message):
    slack.post_as_bot(
        channel,
        message,
        'Morsebot',
        ':coal:',
    )


def morse(message):
    string = message['text']
    channel = message['channel']
    out = []
    morse = False
    for word in string.split():
        if word in morse_to_text:
            morse = True
            out.append(morse_to_text[word])
        else:
            out.append(word)
    print(out)
    for char in string:
        if char not in [' ', '.', '-', '/']:
            morse = False
    if morse:
        send(
            channel,
            "Translation: `" + ''.join(out).replace('/', ' ') + '`'
        )


def to_morse(message):
    string = message['text']
    channel = message['channel']
    out = []
    content = ':'.join(string.split(':')[1:]).strip().lower()
    for char in content:
        if char in text_to_morse:
            out.append(text_to_morse[char])
        elif char is ' ':
            out.append('/')
        else:
            out.append(char)
    send(
        channel,
        "Morse: `" + ' '.join(out) + '`'
    )


responses = {}
functions = {
    r'': morse,
    r'morse:': to_morse
}

initial_metadata = requests.get('https://slack.com/api/rtm.start', params={'token': api.keys['pirates']}).json()
wss_url = initial_metadata['url']
timestamp = datetime.now().timestamp()

w = websocket.WebSocket()
w.connect(wss_url)

while True:
    n = w.next().replace('true', 'True').replace('false', 'False').replace('null', 'Null')
    print(n)
    n = eval(n)
    if all([n['type'] == 'message', n['hidden'] if 'hidden' in n else True, 'bot_id' not in n,
            float(n['ts']) > timestamp if 'ts' in n else False]):
        print(n)
        if 'text' not in n:
            continue
        for function in functions:
            if re.match(function, n['text']):
                functions[function](n)
                continue
        for response in responses:
            if re.match(response, n['text']):
                send(n['channel'], responses[response])
                continue
