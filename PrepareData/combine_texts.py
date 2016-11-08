import os
import json

main_directory = 'FrontEnd/static/hubs/'
hubs = ['Movies', 'Games', 'Books']

def combine_texts():
    for hub in hubs:
        wikias = os.listdir(main_directory+hub)
        for wikia in wikias:
            path = '{0}{1}/{2}/'.format(main_directory, hub, wikia)
            docs = os.listdir(path)
            with open(path+list(filter(lambda x: '.json' in x, docs))[0], 'r') as f:
                info = json.load(f)
            texts = []
            docs_for_combine = list(filter(lambda x: ('.p' or '.pwiki') in x, docs))
            for doc in docs_for_combine:
                with open(path+doc, 'r') as f:
                    for line in f:
                        texts.append(line.strip())
            info['text'] = ' '.join(texts)
            info['tag'] = 'combined'
            print(info['id'], hub)
            with open(path+str(info['id'])+'.wiki.json', 'w') as f:
                json.dump(info, f, indent=4)


for hub in hubs:
    print(hub)
    wikias = os.listdir(main_directory + hub)
    for wikia in wikias:
        path = '{0}{1}/{2}/'.format(main_directory, hub, wikia)
        docs = os.listdir(path)
        with open(path + list(filter(lambda x: '.wiki.json' in x, docs))[0], 'r') as f:
            info = json.load(f)
            # print(info)
        characters = list(filter(lambda x: x.endswith('.p'), docs))
        for char in characters:
            char_id = int(char.replace('.p', ''))
            d = {}
            text = ''
            with open(path+char, 'r') as f:
                for line in f:
                    text+=line.strip()
            with open(path+char.replace('.p', '.txt'), 'r') as f:
                for line in f:
                    d['title'] = line.strip()
                    break
            d['text'] = text
            d['id_wiki'] = wikia
            d['id_char'] = char_id
            d['id'] = int(str(wikia)+str(char_id))
            d['tag'] = 'character'
            d['url'] = info['url']
            d['hub'] = info['hub']
            d['name_wiki'] = info['title']
            # print(d)
            with open(path+str(char_id)+'.char.json', 'w') as f:
                json.dump(d, f)




