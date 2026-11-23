def make_request(request_id, method, params=None):
    ...


def make_notification(method, params=None):
    ...


def make_result(request_id, result):
    ...


def make_error(request_id, code, message):
    ...


def classify(message):
    ...
