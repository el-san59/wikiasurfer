from keras.models import model_from_json
from os import listdir
from os.path import isdir, join
import cv2
import numpy as np

# size = 64, 64
# path = 'Samples'
# folders = [f for f in listdir(path) if isdir(join(path, f))]
#
# data = []
# for folder in folders:
#     for image_path in listdir(join(path, folder)):
#         image = cv2.imread(join(path, folder, image_path), cv2.IMREAD_GRAYSCALE)
#         if image is not None:
#             image = cv2.resize(image, size, interpolation=cv2.INTER_CUBIC)
#             data.append(image)
# print('{0} images loaded'.format(len(data)))
#
# data = np.array(data).astype('float32')/255
# data = np.reshape(data, (-1, 64, 64, 1))
#
# with open('model.json') as f:
#     loaded_json = f.read()
# model = model_from_json(loaded_json)
# model.load_weights('model.h5')
# pew = model.predict(data).reshape(len(data), -1)
# print(pew.shape)

model = None
size = (64, 64)


def load_model(path_to_model, path_to_weights):
    global model
    with open(path_to_model) as f:
        loaded_json = f.read()
    model = model_from_json(loaded_json)
    model.load_weights(path_to_weights)


def get_image(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    return cv2.resize(image, size).reshape(64, 64, 1)/255


def calculate_distance(image_path_1, image_path_2):
    images = [get_image(image_path_1), get_image(image_path_2)]
    center_1, center_2 = model.predict(images).reshape(2, -1)
    return np.sum((center_1 - center_2) ** 2)
