from __future__ import print_function
from aiohttp import ClientSession, TCPConnector

import asyncio
import os
import WikiaAPI as api
import urllib.request
import re

is_category = re.compile('Category:([\w]*)')


def get_articles_from_category(category, visited):
    result = []
    articles = api.get_wikia_articles(category=category, limit=100000)
    if articles is None:
        return []
    else:
        for article in articles:
            sub_category = is_category.search(article['url'])
            if sub_category is not None:
                sub_category = sub_category.group(1)
                if sub_category not in visited:
                    visited.add(sub_category)
                    result += get_articles_from_category(sub_category, visited)
            else:
                result.append(article['id'])
    return result


def crawl():
    for i in range(100):
        wikias = api.get_wikia_info(ids=range(1000 * i + 1, 1000 * (i + 1)))
        if wikias is None:
            print('Request\'s results are empty!')
        else:
            for wikia in wikias:
                if wikia["lang"] == 'en' and wikia['hub'] == 'Movies' and not os.path.exists(
                        './hubs/{0}/{1}'.format(wikia['hub'], wikia['id'])):
                    # os.makedirs('./hubs/' + wikia['hub'], exist_ok=True)
                    # if not os.path.exists('./hubs/' + wikia['hub']):
                    api.set_domain(wikia['domain'])
                    print(str(wikia['id']) + wikia['title'])
                    characters = get_articles_from_category('Characters', {'Characters', })
                    if characters:
                        os.makedirs('./hubs/{0}/{1}'.format(wikia['hub'], wikia['id']), exist_ok=True)
                        for character in characters:
                            try:
                                text, images = api.get_article_content(id=character)
                                with open('./hubs/{0}/{1}/{2}.txt'.format(wikia['hub'], wikia['id'], character),
                                          'w') as f:
                                    f.write(text)
                                count = 0
                                if images:
                                    os.makedirs('./hubs/{0}/{1}/{2}'.format(wikia['hub'], wikia['id'], character),
                                                exist_ok=True)
                                    images = set(map(lambda d: d['src'], images))
                                    for image in images:
                                        localpath = './hubs/{0}/{1}/{2}/{3}'.format(wikia['hub'], wikia['id'],
                                                                                    character, count)
                                        urllib.request.urlretrieve(image, localpath)
                                        count += 1
                            except BaseException as e:
                                print(e)


async def crawl_async():
    os.makedirs('./hubs', exist_ok=True)
    connector = None
    # tasks = [asyncio.ensure_future(crawl_wikias(list(range(1000 * i + 1, 1000 * (i + 1))), connector)) for i in
    #          range(100)]
    # await asyncio.gather(*tasks)
    for i in range(0, 10000):
        await crawl_wikias(range(10*i+1, 10*(i+1)))


async def crawl_wikias(id_range, connector: TCPConnector=None):
    wikias = await api.get_wikia_info_async(ids=id_range)
    if not wikias:
        print('Request\'s results are empty!')
        return None

    wikias = filter(lambda wikia: wikia["lang"] == 'en' and wikia['hub'] == 'Books' and not os.path.exists(
        './hubs/{0}/{1}'.format(wikia['hub'], wikia['id'])), wikias)
    with ClientSession(connector=connector) as session:
        tasks = [asyncio.ensure_future(crawl_wikia(wikia, session))
                 for wikia in wikias]
        await asyncio.gather(*tasks)


async def crawl_wikia(wikia: dict, session):
    print('Gathering from: {0}'.format(wikia['title']))
    characters = await get_articles_from_category_async('Characters', set(), wikia['domain'], session)
    if characters:
        os.makedirs('./hubs/{0}/{1}'.format(wikia['hub'], wikia['id']), exist_ok=True)

    tasks = [asyncio.ensure_future(crawl_character(character, wikia, session)) for character in characters]
    await asyncio.gather(*tasks)


async def crawl_character(character, wikia: dict, session):
    try:
        filename = './hubs/{0}/{1}/{2}.txt'.format(wikia['hub'], wikia['id'], character)
        if os.path.isfile(filename):
            return

        text, images = await api.get_article_content_async(wikia['domain'], session, id=character)
        with open(filename, 'w') as f:
            f.write(text)
        count = 0
        if images:
            os.makedirs('./hubs/{0}/{1}/{2}'.format(wikia['hub'], wikia['id'], character),
                        exist_ok=True)
            images = set(map(lambda d: d['src'], images))
            for image in images:
                localpath = './hubs/{0}/{1}/{2}/{3}'.format(wikia['hub'], wikia['id'],
                                                            character, count)
                urllib.request.urlretrieve(image, localpath)
                count += 1
    except BaseException as e:
        print('Error during processing {0} from {1}: {2}'.format(character, wikia['title'], e))


async def get_articles_from_category_async(category, visited, domain, session):
    visited.add(category)

    result, tasks = [], []
    articles = await api.get_wikia_articles_async(domain, session, category=category, limit=100000)
    if articles is None:
        return []
    else:
        for article in articles:
            sub_category = is_category.search(article['url'])
            if sub_category is not None:
                sub_category = sub_category.group(1)
                if sub_category not in visited:
                    tasks.append(asyncio.ensure_future(get_articles_from_category_async(sub_category, visited,
                                                                                        domain, session)))
            else:
                result.append(article['id'])
    task_results = await asyncio.gather(*tasks)
    for sub_category in task_results:
        result += sub_category

    return result


if __name__ == '__main__':
    # crawl()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.ensure_future(crawl_async()))
    loop.close()