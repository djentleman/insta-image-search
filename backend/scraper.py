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
    'car', 'supercar', 'driving', 'roadtrip', 'scenery', 'nature', 'park', 'wildlife',
    'clothes', 'fashion', 'couple', 'selfie', 'friends', 'fun', 'food', 'foodporn',
    'lunch', 'dinner', 'burger', 'hotdog', 'sushi', 'coffee', 'pasta', 'pizza',
    'ramen', 'borscht', 'soup', 'tasty', 'beer', 'wine', 'whiskey', 'sake', 'alcohol', 'pub',
    'safari', 'elephant', 'zebra', 'horse', 'rhino', 'giraffe', 'africa', 'desert',
    'truck', 'boat', 'ship', 'plane', 'airport', 'aeroplane', 'submarine', 'museum',
    'mexican', 'italian', 'japanese', 'chinese', 'korean', 'jamaican', 'record', 'vinyl',
    'love', 'instagood', 'me', 'tbt', 'cute', 'girl', 'boy', 'bored', 'music', 'instacool'
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
                small_url = image['thumbnail_resources'][1]['src']
                full_url = image['display_url']
                print(full_url)
                hashtags = [tag for tag in image['edge_media_to_caption']['edges'][0]['node']['text'].replace('\n', '').split(' ') if '#' in tag]
                account_id = image['owner']['id']
                image_data = BytesIO(requests.get(small_url).content)
                image_vector = model.do_feature_extraction(image_data)
                shortcode = image['shortcode']
                instagram_url = 'https://www.instagram.com/p/%s/' % (shortcode,)
                data.append({
                    'searchterm': hashtag,
                    'hashtags': hashtags,
                    'full_url': full_url,
                    'small_url': small_url,
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


