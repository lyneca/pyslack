import api
mafia = api.API(api.read_keys('mafia_game_4'))
string = "Message count:\n```" + '\n'.join(
    [
        (
            mafia.users[count[0]].real_name + ' ' if mafia.users[count[0]].real_name.strip() else ''
        ) + '(@' + count[0] + '): ' + str(count[1]) for count in mafia.get_message_counts('town_square')
        ]
) + '```'
mafia.pin_message('town_square',
                  mafia.post_as_bot(mafia.channels['town_square'].id, string, 'Message Count Bot', ':100:')['ts'])
