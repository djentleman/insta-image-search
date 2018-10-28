import os
import json
from model import (
    do_feature_extraction,
    get_similarity
)
import numpy as np
from loader import load_image_data

def calculate_hashtag_popularity(hashtags):
    scores = {}
    for hashtag_set in hashtags:
        for hashtag in hashtag_set:
            if hashtag in scores.keys():
                scores[hashtag] += 1
            else:
                scores[hashtag] = 1
    return scores

# client for handling requests/jobs for the instagram image search
class IISClient():

    def __init__(self):
        # load saved images into memory here
        self.images = load_image_data()
        self.result_count = 15

    def search_with_image(self, image):
        vector = do_feature_extraction(image)
        print(vector)
        results = sorted(self.images, key=lambda x: -get_similarity(x['image_vector'], vector))[:self.result_count]
        stripped_results = [{
            'instagram_url': res['instagram_url'],
            'img_src': res['full_url'],
            'account_id': res['account_id'],
            'hashtags': res['hashtags'],
        } for res in results]
        return {
            'images': stripped_results,
            'hashtags': calculate_hashtag_popularity([res['hashtags'] for res in stripped_results])
        }
