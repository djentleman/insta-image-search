from client import IISClient
import numpy as np
from keras.layers import (
    Input,
    Embedding,
    Reshape,
    Dense,
    dot
)
from keras.models import Model
from functools import reduce
from random import (
    choice as rndchoice
)
# train model

def clean_hashtags(hashtags):
    hashtags =  [h.replace(' ', '') for h in hashtags if h[0] == '#']
    return hashtags

client = IISClient()
data = [{'iv': i['image_vector'], 'ht': clean_hashtags(i['hashtags'])} for i in client.images]
data = [d for d in data if len(d['ht']) > 1]

# image vector set - easy
X = np.array([d['iv'] for d in data])


# word vector set - hard, we need to train a word embedding
hashtags = [d['ht'] for d in data]
all_hashtags = np.array(list({w for y in hashtags for w in y}))

vocab_size = len(all_hashtags)

mapping = {h: i for i, h in enumerate(all_hashtags)}
reverse_mapping = {str(i): h for i, h in enumerate(all_hashtags)}

# now build context pairs
# iterate over every individual hashtag, get a positive and a negative example

pairs = []
labels = []

for i, hts in enumerate(hashtags):
    print(i)
    for j, hashtag in enumerate(hts):
        ht_whitelist = list(set(hts).difference(hashtag))
        # positive
        pairs.append(
            [
                mapping[hashtag],
                mapping[rndchoice(ht_whitelist)]
            ]
        )
        labels.append(1)
        # negative
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

# build similarity lambda, and fitting function :)
