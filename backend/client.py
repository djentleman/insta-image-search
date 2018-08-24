from model import (
    do_feature_extraction,
    get_similarity
)

# client for handling requests/jobs for the instagram image search
class IISClient():

    def __init__(self):
        # load saved images into memory here
        self.images = []

    def search_with_image(self, image):
        vector = do_feature_extraction(image)
        print(vector)
        return sorted(self.images, key=lambda x: -get_similarity(x['vector'], vector))[:10]


