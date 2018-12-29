from client import IISClient
import numpy as np
from keras.callbacks import LambdaCallback
from keras.optimizers import RMSprop
from keras.layers import (
    Dense,
    Input,
)
from keras.models import (
    Model,
    model_from_json
)
from functools import reduce
from random import (
    choice as rndchoice,
    randint,
    random
)
import json

def clean_hashtags(hashtags):
    hashtags =  [h.replace(' ', '') for h in hashtags if h[0] == '#']
    if len(hashtags) == 0:
        return []
    split_hashtags = [ht.split('#') for ht in hashtags]
    # rejoin
    hashtags = list(reduce(lambda x, y: x + y, split_hashtags))
    hashtags = [ht if ht[0] == '#' else '#' + ht for ht in hashtags if ht != '']
    hashtags = list(set(hashtags))
    return hashtags

# this will probably need to me moved somwhere else...
def load_model(path):
    # load json and create model
    json_file = open('%s.json' % path, 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights("%s.h5" % path)
    print("Loaded model from disk")
    return loaded_model

client = IISClient()
data = [{'iv': i['image_vector'], 'ht': clean_hashtags(i['hashtags'])} for i in client.images]
data = [d for d in data if len(d['ht']) > 1]

mapping = json.loads(open('mapping.json', 'r+').read())
reverse_mapping = json.loads(open('reverse_mapping.json', 'r+').read())
embedding_model = load_model('word_embedder')

img_vectors = [x['iv'] for x in data]
# should be closest to mean for ewach vevtpr
word_vectors = [[embedding_model.predict([mapping[ht]])[0] for ht in y['ht']] for y in data]

inputs = [[x, y.reshape(300,)] for i, x in enumerate(img_vectors) for y in word_vectors[i]]
inputs = sorted(inputs, key=lambda x: random())

X = []
Y = []
for i in inputs:
    X.append(i[0])
    Y.append(i[1])

# network hyperparameters

validation_size = 0.2

validation_count = int(len(X)*validation_size)

Xv = np.array(X[:validation_count])
Yv = np.array(Y[:validation_count])
Xt = np.array(X[validation_count:])
Yt = np.array(Y[validation_count:])

# RNN hyperparameters
learning_rate = 0.015
#lambda_loss_amount = 0.0015
batch_size = 128
epochs = 200

n_input = len(X[0])
n_hidden = 1000
n_output = len(Y[0])

input_layer = Input(shape=(n_input,), dtype='float32', name='input_layer')
hidden_layer = Dense(2500, activation='sigmoid')(input_layer)
output_layer = Dense(n_output, activation='linear', name='output_layer')(hidden_layer)

optimizer = RMSprop(lr=learning_rate)
model = Model(inputs=[input_layer], output=[output_layer])
model.compile(loss='mean_squared_error', optimizer=optimizer)

def save_model(model, path):
    # serialize model to JSON
    print("Saving Model...")
    model_json = model.to_json()
    with open("%s.json" % path, "w") as json_file:
        json_file.write(model_json)
    # serialize weights to HDF5
    model.save_weights("%s.h5" % path)
    print("Saved model to disk")

best_error = 999999
best_model = model

def on_epoch_end(epoch, logs):
    global best_model
    global best_error
    print()
    print('----- Epoch: %s' % (int(epoch)+1,))
    print('Running Validation...')
    pred = model.predict(Xv)
    diff = np.absolute(pred - Yv)
    test_error = diff.sum() / len(Yv)
    if test_error < best_error:
        print('New Best!')
        best_error = test_error
        best_model = model
        save_model(best_model, 'hashtag_classifier')
    print(pred.shape)
    print(Yv.shape)
    #print("Train Error: %s" % str(train_error))
    print("Test Error: %s" % str(test_error))
    print("Best Error: %s" % str(best_error))


print_callback = LambdaCallback(on_epoch_end=on_epoch_end)
on_epoch_end(-1, None)
model.fit(Xt, Yt, batch_size=batch_size,
                  epochs=epochs,
                  callbacks=[print_callback])

