import wikipedia
import WikiaAPI as api
import os
import json

main_directory = 'hubs/'
hubs = ['Movies']
def load_wiki():
    for hub in hubs:
        not_found = []
        wikias = os.listdir(main_directory + hub)
        # wikias = wikias[:3]
        # print(wikias)

        wikias_info = api.get_wikia_info(ids=wikias)

        for wikia in wikias_info:
            # if str(wikia['id'])+'.json' not in os.listdir('{0}{1}/{2}/'.format(main_directory, hub, wikia['id'])):
            with open('{0}{1}/{2}/{2}.json'.format(main_directory, hub, wikia['id']), 'w') as f:
                json.dump(wikia, f, indent=4)
            name = wikia['name'].lower().replace('wiki', '').replace('fanon', '').strip() + ' film'
            print(hub, name)
            wikis = wikipedia.search(name)
            print(wikis)
            if wikis:
                try:
                    page = wikipedia.page(wikis[0])
                except Exception as e:
                    print('/////////////////////////////////////')
                    print(e)
                    print('/////////////////////////////////////')
                with open('{0}{1}/{2}/{2}.wiki'.format(main_directory, hub, wikia['id']), 'w') as f:
                    print(page.content, file=f)

            # else:
            #     print('Exist/////////////////////////////////////////////////////////')



wikias_info = api.get_wikia_info(ids=[54105])
for wikia in wikias_info:
    print(wikia)
    name = wikia['name']
    print(wikia['url'])
    print(name)
    wikis = wikipedia.search(name)
    print(wikis)
    page = wikipedia.page(wikis[0])
    with open('{0}.wiki'.format(wikia['id']), 'w') as f:
        print(page.content, file=f)