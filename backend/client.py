import os
import json
from model import (
    do_feature_extraction,
    get_similarity
)
import numpy as np

# client for handling requests/jobs for the instagram image search
class IISClient():

    def __init__(self):
        # load saved images into memory here
        self.images = []
        self.load_images()
        self.result_count = 15

    def search_with_image(self, image):
        vector = do_feature_extraction(image)
        print(vector)
        results = sorted(self.images, key=lambda x: -get_similarity(x['image_vector'], vector))[:self.result_count]
        return [{
            'instagram_url': res['instagram_url'],
            'img_src': res['full_url'],
            'account_id': res['account_id'],
            'hashtags': res['hashtags'],
        } for res in results]

    def load_images(self):
        for filename in os.listdir('data/'):
            print('Loading %s...' % (filename,))
            data = json.loads(open('data/' + filename, 'r+').read())
            self.images += data
        for i in range(len(self.images)):
            self.images[i]['image_vector'] = np.asfarray(self.images[i]['image_vector'])

