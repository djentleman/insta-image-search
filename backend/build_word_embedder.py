from client import IISClient
import numpy as np
from keras.layers import (
    Input,
    Embedding,
    Reshape,
    Dense,
    dot
)
from keras.callbacks import LambdaCallback
from keras.models import Model
from functools import reduce
from random import (
    choice as rndchoice,
    randint
)
# train model

def clean_hashtags(hashtags):
    hashtags =  [h.replace(' ', '') for h in hashtags if h[0] == '#']
    if len(hashtags) == 0:
        return []
    split_hashtags = [ht.split('#') for ht in hashtags]
    # rejoin
    hashtags = list(reduce(lambda x, y: x + y, split_hashtags))
    hashtags = [ht if ht[0] == '#' else '#' + ht for ht in hashtags if ht != '']
    return hashtags

client = IISClient()
data = [{'iv': i['image_vector'], 'ht': clean_hashtags(i['hashtags'])} for i in client.images]
data = [d for d in data if len(d['ht']) > 1]

# word vector set - hard, we need to train a word embedding
hashtags = [d['ht'] for d in data]
all_hashtags = np.array(list({w for y in hashtags for w in y}))

vocab_size = len(all_hashtags)

mapping = {h: i for i, h in enumerate(all_hashtags)}
reverse_mapping = {str(i): h for i, h in enumerate(all_hashtags)}

# now build context pairs
# iterate over every individual hashtag, get a positive and a negative example

n_labels = 5

pairs = []
labels = []

for i, hts in enumerate(hashtags):
    print(i)
    for j, hashtag in enumerate(hts):
        ht_whitelist = list(set(hts).difference(hashtag))
        # positive
        for i in range(n_labels):
            pairs.append(
                [
                    mapping[hashtag],
                    mapping[rndchoice(ht_whitelist)]
                ]
            )
            labels.append(1)
        # negative
        for i in range(n_labels):
            while True:
                # pick a random hashtag
                random_hashtag = rndchoice(all_hashtags)
                # check if in whitelist
                if random_hashtag not in hts:
                    negative_hashtag = random_hashtag
                    break
            pairs.append(
                [
                    mapping[hashtag],
                    mapping[negative_hashtag]
                ]
            )
            labels.append(0)

pairs = np.array(pairs)
labels = np.array(labels)

# OK! we have our dataset to build the word embedding

# network hyperparameters
vector_dim = 300
epochs = 100
batch_size = 100000



input_target = Input((1,))
input_context = Input((1,))

embedding = Embedding(vocab_size, vector_dim, input_length=1, name='embedding')

target = embedding(input_target)
target = Reshape((vector_dim, 1))(target)
context = embedding(input_context)
context = Reshape((vector_dim, 1))(context)

# get cosine similarity
similarity = dot(axes=0, inputs=[target, context], normalize=True)
# get dot product
dot_product = dot(axes=1, inputs=[target, context], normalize=False)
dot_product = Reshape((1,))(dot_product)

output = Dense(1, activation='sigmoid')(dot_product)

model = Model(input=[input_target, input_context], output=output)
model.compile(loss='binary_crossentropy', optimizer='rmsprop')

similarity_model = Model(input=[input_target, input_context], output=similarity)

vector_model = Model(input=input_target, output=target)

def save_model(model, path):
    # serialize model to JSON
    print("Saving Model...")
    model_json = model.to_json()
    with open("%s.json" % path, "w") as json_file:
        json_file.write(model_json)
    # serialize weights to HDF5
    model.save_weights("%s.h5" % path)
    print("Saved model to disk")

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

# build similarity lambda, and fitting function :)
def on_epoch_end(epoch, logs):
    print('Epoch: %d' % (epoch+1))
    if epoch % 10 != 9:
        print('skipping vaidation...')
        return
    words = [randint(0, vocab_size-1) for i in range(5)]
    for word in words:
        similarities = [(i, similarity_model.predict([np.array([word]), np.array([i])])[0][0][0]) for i in range(vocab_size)]
        similarities = sorted(similarities, key=lambda x: x[1])
        most_similar = similarities[-20:-1]
        least_similar = similarities[:19]
        print('------------------------------')
        print('Word: %s' % reverse_mapping[str(word)])
        print('Similar Words: %s' % ', '.join([reverse_mapping[str(x[0])] for x in most_similar]))
        print('Disimilar Words: %s' % ', '.join([reverse_mapping[str(x[0])] for x in least_similar]))
        print('------------------------------')




print_callback = LambdaCallback(on_epoch_end=on_epoch_end)
on_epoch_end(-1, None)
model.fit([pairs[:, 0], pairs[:, 1]], labels, batch_size=batch_size,
                    epochs=epochs,
                    callbacks=[print_callback])

save_model(vector_model, 'word_embedder')'