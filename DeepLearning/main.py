from os import listdir
from os.path import isdir, join
from DeepLearning.AutoEncoder import create_autoencoder
from sklearn.model_selection import train_test_split
import cv2
import numpy as np

size = 64, 64
path = 'Samples'
folders = [f for f in listdir(path) if isdir(join(path, f))]

data = []
for folder in folders:
    for image_path in listdir(join(path, folder)):
        image = cv2.imread(join(path, folder, image_path), cv2.IMREAD_GRAYSCALE)
        if image is not None:
            image = cv2.resize(image, size, interpolation=cv2.INTER_CUBIC)
            data.append(image)
print('{0} images loaded'.format(len(data)))

data = np.array(data).astype('float32')/255
data = np.reshape(data, (-1, 64, 64, 1))

train, test = train_test_split(data)
autoencoder, encoder = create_autoencoder(64, 64)
autoencoder.fit(train, train, nb_epoch=300, batch_size=16, shuffle=True, validation_data=(test, test))


model_json = encoder.to_json()
with open('model.json', 'w') as f:
    f.write(model_json)
encoder.save_weights('model.h5')
print('Model saved to disk')
