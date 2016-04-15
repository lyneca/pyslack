import requests
print("Go here:")
print(
    requests.get(
        'https://slack.com/oauth/authorize',
        params={
            'client_id': '13152575825.33382774226',
            'scope': 'read post client'
        }
    ).request.url
)
print("\nWhen that's done, copy the code parameter from the URL and paste it here.")
code = input('> ')
print('Your access token:')
print(requests.get(
    'https://slack.com/api/oauth.access',
    params={
        'client_id': '13152575825.33382774226',
        'client_secret': '64bdbd9374df1eac191786ccc81b4103',
        'code': code,
    }
).json())
input()