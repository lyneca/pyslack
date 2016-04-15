import api
slack = api.API(api.read_keys('mafia_game_4'))
slack.post_loop()
