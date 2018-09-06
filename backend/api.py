import hug
from client import IISClient
from io import BytesIO

iis_client = IISClient()

api = hug.API(__name__)
api.http.add_middleware(hug.middleware.CORSMiddleware(api, max_age=10))

@hug.post('/upload')
def upload_file(body):
    return      ['https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Tunnel_View_2%2C_Yosemite_Valley%2C_Yosemite_NP_-_Diliff.jpg/800px-Tunnel_View_2%2C_Yosemite_Valley%2C_Yosemite_NP_-_Diliff.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/Tunnel_View_5%2C_Yosemite_Valley%2C_Yosemite_NP_-_Diliff.jpg/2880px-Tunnel_View_5%2C_Yosemite_Valley%2C_Yosemite_NP_-_Diliff.jpg']

    """accepts file uploads"""
    filename = 'file'
    content = body[filename]
    if type(content) == str:
        content = content.encode()
    response = iis_client.search_with_image(BytesIO(content))
    return response
