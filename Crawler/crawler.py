from __future__ import print_function
import os
import Crawler.WikiaAPI as api
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


if __name__ == '__main__':
    for i in range(100):
        wikias = api.get_wikia_info(ids=range(1000 * i + 1, 1000 * (i + 1)))
        if wikias is None:
            print('Request\'s results are empty!')
        else:
            for wikia in wikias:
                if wikia["lang"] == 'en' and wikia['hub'] == 'Movies':
                    if not os.path.exists('./hubs/' + wikia['hub']):
                        os.makedirs('./hubs/' + wikia['hub'])
                    api.set_domain(wikia['domain'])
                    print(wikia['title'])
                    characters = get_articles_from_category('Characters', {'Characters', })
                    if characters:
                        os.makedirs('./hubs/{0}/{1}'.format(wikia['hub'], wikia['id']), exist_ok=True)
                        for character in characters:
                            text, images = api.get_article_content(id=character)
                            with open('./hubs/{0}/{1}/{2}.txt'.format(wikia['hub'], wikia['id'], character), 'w') as f:
                                f.write(text)
                            count = 0
                            if images:
                                os.makedirs('./hubs/{0}/{1}/{2}'.format(wikia['hub'], wikia['id'], character),
                                            exist_ok=True)
                                for image in images:
                                    localpath = './hubs/{0}/{1}/{2}/{3}.png'.format(wikia['hub'], wikia['id'],
                                                                                    character, count)
                                    urllib.request.urlretrieve(image["src"], localpath)
                                    count += 1
