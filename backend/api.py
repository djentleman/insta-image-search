import hug
from client import IISClient
from io import BytesIO

iis_client = IISClient()


@hug.post('/upload')
def upload_file(body):
    """accepts file uploads"""
    filename = list(body.keys()).pop()
    content = body[filename]
    response = iis_client.search_with_image(BytesIO(content))
    return response

