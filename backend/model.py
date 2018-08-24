from keras.applications.vgg16 import VGG16
from keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input
from scipy import spatial
from PIL import Image
import numpy as np


model = VGG16(weights='imagenet', include_top=False)

def do_feature_extraction(img_bytes):
    img = Image.open(img_bytes)
    img = img.resize((224, 224))
    #img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)

    features = model.predict(x)
    feature_vector = features.reshape(7*7*512)
    return feature_vector

def get_similarity(vec1, vec2):
    return 1 - spatial.distance.cosine(vec1, vec2)

