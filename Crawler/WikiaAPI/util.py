import requests


def wikia_request(url, params):
    params['format'] = 'json'
    headers = {
        'User-Agent' : 'WikiaSurfer'
    }

    response = requests.get(url, params=params, headers=headers)
    try:
        response = response.json()
    except ValueError:
        return None
    if 'exception' in response:
        print('Something is going wrong: {details}'.format(**response['exception']))
        return None

    return response
