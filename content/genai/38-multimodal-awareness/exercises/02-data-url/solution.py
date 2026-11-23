import base64


def data_url(mime, data):
    if not data:
        raise ValueError("no data")
    return "data:" + mime + ";base64," + base64.b64encode(data).decode()
