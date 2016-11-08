import requests
from aiohttp import ClientSession
import aiohttp

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
    except aiohttp.TimeoutError:
        print('Timeout error!')
        return None
    if 'exception' in response:
        print('Something is going wrong: {details}'.format(**response['exception']))
        return None

    return response

async def wikia_request_async(url, params, session: ClientSession):
    async with session.get(url, params=params, timeout=600) as response:
        try:
            response = await response.json()
        except ValueError:
            print('Can\'t parser JSON response!')
            print(response.text())
            return None
        except aiohttp.TimeoutError:
            print('Timeout error!')
            return None
        if 'exception' in response:
            # print('Something is going wrong: {details}'.format(**response['exception']))
            return None
        return response