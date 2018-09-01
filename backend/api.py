import hug
from client import IISClient
from io import BytesIO

iis_client = IISClient()

api = hug.API(__name__)
api.http.add_middleware(hug.middleware.CORSMiddleware(api, max_age=10))

@hug.post('/upload')
def upload_file(body):
    """accepts file uploads"""
    filename = 'file'
    content = body[filename]
    print(content)
    if type(content) == str:
        content = content.encode()
    response = iis_client.search_with_image(BytesIO(content))
    return response
