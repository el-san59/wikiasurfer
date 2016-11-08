from keras.layers import Input, Convolution2D, MaxPooling2D, UpSampling2D
from keras.models import Model


def create_autoencoder(input_x, input_y):
    input_img = Input(shape=(input_x, input_y, 1))

    x = Convolution2D(32, 5, 5, activation='relu', border_mode='same')(input_img)
    x = MaxPooling2D((2, 2), border_mode='same')(x)
    x = Convolution2D(16, 5, 5, activation='relu', border_mode='same')(x)
    x = MaxPooling2D((2, 2), border_mode='same')(x)
    x = Convolution2D(16, 5, 5, activation='relu', border_mode='same')(x)
    encoded = MaxPooling2D((2, 2), border_mode='same')(x)

    x = Convolution2D(16, 5, 5, activation='relu', border_mode='same')(encoded)
    x = UpSampling2D((2, 2))(x)
    x = Convolution2D(16, 5, 5, activation='relu', border_mode='same')(x)
    x = UpSampling2D((2, 2))(x)
    x = Convolution2D(32, 5, 5, activation='relu', border_mode='same')(x)
    x = UpSampling2D((2, 2))(x)
    decoded = Convolution2D(1, 5, 5, activation='sigmoid', border_mode='same')(x)

    autoencoder = Model(input_img, decoded)
    autoencoder.compile(optimizer='adagrad', loss='binary_crossentropy')

    encoder = Model(input_img, encoded)
    return autoencoder, encoder



