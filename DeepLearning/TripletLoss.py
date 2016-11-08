import lasagne
import theano.tensor as T
import theano
import numpy as np
import pickle


def build_network(input_variable=None):
    network = lasagne.layers.InputLayer(shape=(1, 1, 64, 64), input_var=input_variable)
    network = lasagne.layers.Conv2DLayer(network, num_filters=32, filter_size=(5, 5),
                                         nonlinearity=lasagne.nonlinearities.rectify,
                                         W=lasagne.init.GlorotUniform())
    network = lasagne.layers.MaxPool2DLayer(network, pool_size=(2, 2))
    network = lasagne.layers.Conv2DLayer(network, num_filters=32, filter_size=(5, 5),
                                         nonlinearity=lasagne.nonlinearities.rectify)
    network = lasagne.layers.MaxPool2DLayer(network, pool_size=(2, 2))
    # network = lasagne.layers.DropoutLayer(network, p=.5)
    network = lasagne.layers.DenseLayer(network, num_units=256)

    return network


def create_model():
    sample = T.tensor4('sample')
    match = T.tensor4('match')

    network = build_network()
    output_1 = lasagne.layers.get_output(network, sample)
    output_2 = lasagne.layers.get_output(network, match)

    distance = (T.sum(output_1 * output_2)/(output_1.norm(2) * output_2.norm(2))).norm(1)
    # T.sum(T.sub(output_1, output_2) ** 2)

    loss_positive = 1 - distance
    loss_negative = distance

    all_params = lasagne.layers.get_all_params(network)
    updates_positive = lasagne.updates.adagrad(loss_positive, all_params)
    updates_negative = lasagne.updates.adagrad(loss_negative, all_params)

    train_positive = theano.function(inputs=[sample, match], outputs=loss_positive, updates=updates_positive)
    train_negative = theano.function(inputs=[sample, match], outputs=loss_negative, updates=updates_negative)
    predict = theano.function(inputs=[sample, match], outputs=distance)

    return predict, train_positive, train_negative


def test_save():
    model, t, _ = create_model()
    print('Model created!')
    sample_1 = np.ones((1, 1, 64, 64))
    sample_2 = np.zeros((1, 1, 64, 64))
    for i in range(5):
        t(sample_1, sample_2)
    print(model(sample_1, sample_2))

    with open('model.dat', 'wb') as f:
        pickle.dump(model, f)


def test_load():
    sample_1 = np.ones((1, 1, 64, 64))
    sample_2 = np.zeros((1, 1, 64, 64))
    with open('model.dat', 'rb') as f:
        model = pickle.load(f)
    print(model(sample_1, sample_2))

if __name__ == '__main__':
    test_load()
