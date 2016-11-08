import os
import shutil
main_directory = 'hubs/'
hubs = ['Books']


def remove_empty_wikias(wikia, hub):
    path = '{0}{1}/{2}'.format(main_directory, hub, wikia)
    if not os.listdir(path):
        os.rmdir(path)


def remove_character(path, character):
    os.remove(path + character)
    # os.remove(path + character.replace('txt', 'p'))
    if os.path.exists(path + character.replace('.txt', '')):
        shutil.rmtree(path + character.replace('.txt', ''))


def clean_characters():
    for hub in hubs:
        wikias = os.listdir(main_directory+hub)
        print(len(wikias))
        for wikia in wikias:
            remove_empty_wikias(wikia, hub)
        wikias = os.listdir(main_directory + hub)
        print(len(wikias))
        for wikia in wikias:
            path = '{0}{1}/{2}/'.format(main_directory, hub, wikia)
            characters = list(filter(lambda x: '.txt' in x, os.listdir(path)))
            for character in characters:
                if os.path.getsize(path+character) < 1800:
                    remove_character(path, character)

        wikias = os.listdir(main_directory + hub)
        print(len(wikias))
        for wikia in wikias:
            remove_empty_wikias(wikia, hub)

        wikias = os.listdir(main_directory + hub)
        print(len(wikias))

if __name__ == '__main__':
    clean_characters()


