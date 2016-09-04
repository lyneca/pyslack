from fake_team import channel_info, user_info


def make_keys():
    file = open('api_keys.db')
    pairs = [line.split(': ') for line in file]
    return {k: v.strip() for k, v in pairs}


def get_url(key):
    return 'https://google.com'


class RestrictedActionException(Exception):
    def __init__(self):
        super(Exception, self).__init__(self)


class Channel:
    def __init__(self, kwargs):
        self.__dict__.update(kwargs)


class User:
    def __init__(self, kwargs):
        self.__dict__.update(kwargs)


class API:
    def __init__(self, token):
        self.token = token
        self.team_name, self.team_id, self.team_domain = self._get_team_info()
        self.channels = self._get_channels()
        self.users = self._get_users()
        self.keys = {}

    def _get_team_info(self):
        return 'ECORGB TEAM', 0, None

    def _get_channels(self):
        return {x['name']: Channel(x) for x in channel_info}

    def _get_users(self):
        return {x['name']: User(x) for x in user_info}

    def _send(self, method, **params):
        params['token'] = self.token
        r = requests.post(
            'https://slack.com/api/' + method,
            params=params
        )
        if not r.json()['ok']:
            if r.json()['error'] == 'restricted_action':
                raise RestrictedActionException
            else:
                raise Exception(r.json()['error'])
        return r.json()

    def get_channel_name(self, id):
        for channel in self.channels:
            if self.channels[channel].id == id:
                return self.channels[channel].name

    def get_user_name(self, id):
        for user in self.users:
            if self.users[user].id == id:
                return self.users[user].name

    def get_permalink(self, ts, channel):
        return 'https://' + \
               self.team_domain + \
               '.slack.com/archives/' + \
               self.get_channel_name(channel) + \
               '/p' + \
               ts.replace('.', '')

    def post_as_bot(self, channel, message, username='bot', emoji=''):
        print("#{channel_name}: <{username}> {message}".format(channel_name=self.get_channel_name(channel), username=username, message=message))

    def post_as_user(self, **kwargs):
        self.post_as_bot(username='as_user', **kwargs)

    def pin_message(self, channel, ts):
        print("Pinning message...")
        return self._send(
            'pins.add',
            channel=self.channels[channel].id,
            timestamp=ts
        )

    def invite_to_channel(self, user, channel):
        return self._send(
            'channels.invite',
            channel=channel,
            user=user
        )

    def post_to_all(self, message):
        for channel in self.channels:
            print("Posting to #" + channel + "...")
            self.post_as_bot(channel, message)

    def get_message_counts(self, channel=''):
        message_counts = []
        print("Counting messages...")
        for user in self.users:
            messages_by_user = requests.get(
                'https://slack.com/api/search.messages',
                params={
                    'token': self.token,
                    'query': 'from:' + user + (' in:' + channel if channel else ''),
                    'count': 1
                }
            ).json()['messages']['paging']['total']
            if not self.users[user].deleted:
                message_counts.append((user, messages_by_user))
        message_counts.sort(key=lambda x: x[1], reverse=True)
        return message_counts

    def post_loop(self):
        username = input('username: ')
        emoji = input('emoji: ')
        channel = input('channel: ')
        while True:
            self.post_as_bot(channel, input('> '), username, emoji)
