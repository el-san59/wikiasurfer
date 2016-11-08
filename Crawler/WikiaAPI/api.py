from .util import wikia_request, wikia_request_async
from aiohttp import ClientSession

API_URL = 'http://{domain}/api/v1/{action}'
WIKIA_URL = 'http://www.wikia.com/api/v1/{action}'
DOMAIN = 'www.wikia.com'


def set_domain(domain):
    global DOMAIN
    DOMAIN = domain


def get_wikia_info(**kwargs):
    """

    :rtype: json
    :param kwargs:
        ids - wikia's ids list(int)

    :return: info about specified wikia
    """
    kwargs.setdefault('ids', 0)
    try:
        kwargs['ids'] = ','.join(map(lambda id: str(id), kwargs['ids']))
    finally:
        response = wikia_request(WIKIA_URL.format(action='Wikis/Details'), kwargs)
        if response is not None:
            return response['items'].values()
        return None


def get_wikia_articles(**kwargs):
    """

    :rtype: json
    :param kwargs:
        category: Return only articles belonging to the provided valid category title (string)
        namespaces: Comma-separated namespace ids (string)
        limit: Limit the number of results (int)
        offset: Lexicographically minimal article title (string)
    :return: 
    """
    kwargs.setdefault('limit', 25)
    response = wikia_request(API_URL.format(domain=DOMAIN, action='Articles/List'), kwargs)
    if response is not None:
        return response['items']


def get_article_content(**kwargs):
    """

    :param kwargs:
        id: A single article ID
    :return:
    """
    kwargs.setdefault(id, 0)
    response = wikia_request(API_URL.format(domain=DOMAIN, action='Articles/AsSimpleJson'), kwargs)
    if response is not None:
        result = ''
        pictures = []
        for section in response['sections']:
            result += '{title}\n'.format(title=section['title'])
            for content in section['content']:
                if content['type'] == 'paragraph':
                    result += '{text}\n'.format(text=content['text'])
                else:
                    result += '{text}\n'.format(text=__article_elements_rec__(content['elements']))
                pictures += section['images']
        return result, pictures


def get_article_info(**kwargs):
    kwargs.setdefault('abstract', 100)
    kwargs.setdefault('width', 200)
    kwargs.setdefault('height', 200)
    response = wikia_request(API_URL.format(domain=DOMAIN, action='Articles/Details'), params=kwargs)
    return response


def __article_elements_rec__(elements):
    result = ''
    for elem in elements:
        result += '{text}\n{elements}'.format(text=elem['text'], elements=__article_elements_rec__(elem['elements']))
    return result


async def get_wikia_info_async(**kwargs):
    """

    :rtype: json
    :param kwargs:
        ids - wikia's ids list(int)

    :return: info about specified wikia
    """
    kwargs.setdefault('ids', 0)
    try:
        kwargs['ids'] = ','.join(map(lambda id: str(id), kwargs['ids']))
    finally:
        with ClientSession() as session:
            response = await wikia_request_async(WIKIA_URL.format(action='Wikis/Details'), kwargs, session)
        if response is not None:
            return response['items'].values()
        return None


async def get_wikia_articles_async(domain, session, **kwargs):
    kwargs.setdefault('limit', 25)
    response = await wikia_request_async(API_URL.format(domain=domain, action='Articles/List'), kwargs, session)
    if response is not None:
        return response['items']


async def get_article_content_async(domain, session, **kwargs):
    kwargs.setdefault(id, 0)
    response = await wikia_request_async(API_URL.format(domain=domain, action='Articles/AsSimpleJson'), kwargs, session)
    if response is not None:
        result = ''
        pictures = []
        for section in response['sections']:
            result += '{title}\n'.format(title=section['title'])
            for content in section['content']:
                if content['type'] == 'paragraph':
                    result += '{text}\n'.format(text=content['text'])
                else:
                    result += '{text}\n'.format(text=__article_elements_rec__(content['elements']))
                pictures += section['images']
        return result, pictures