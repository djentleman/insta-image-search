import requests
import time
import json
import model
from io import BytesIO

# just some junk for now
hashtags = [
    'italy', 'america', 'england', 'france', 'japan', 'korea', 'russia', 'france', 'germany',
    'london', 'milano', 'moscow', 'kyoto', 'tokyo', 'rome', 'castle', 'church', 'temple',
    'pet', 'exoticpet', 'animal', 'dog', 'cat', 'rabbit', 'hamster', 'guineapig', 'snake',
    'car', 'supercar', 'driving', 'roadtrip', 'scenery', 'nature', 'park', 'wildwife',
    'clothes', 'fashion', 'couple', 'selfie', 'friends', 'fun'
]

output_file = '%s_image_data.json'
base_url = 'https://www.instagram.com/explore/tags/%s/?__a=1'
wait = 2 # seconds
data = []

for hashtag in hashtags:
    print(hashtag)
    url = base_url % (hashtag,)
    images = json.loads(requests.get(url).text)
    for image in images['graphql']['hashtag']['edge_hashtag_to_media']['edges']:
        try:
            image = image['node']
            if not image['is_video']:
                # want the 250x250 thumbnail
                image_url = image['thumbnail_resources'][1]['src']
                print(image_url)
                account_id = image['owner']['id']
                image_data = BytesIO(requests.get(image_url).content)
                image_vector = model.do_feature_extraction(image_data)
                shortcode = image['shortcode']
                instagram_url = 'https://www.instagram.com/p/%s/' % (shortcode,)
                data.append({
                    'hashtag': hashtag,
                    'image_url': image_url,
                    'instagram_url': instagram_url,
                    'image_vector': image_vector.tolist(),
                    'account_id': account_id
                })
            time.sleep(wait)
        except Exception as e:
            print(e)
    open(output_file % (hashtag,), 'w+').write(json.dumps(data))
    data = []
    time.sleep(wait)


