import django_rq


def get_queue():
    return django_rq.get_queue("default")


def get_connection():
    return django_rq.get_connection("default")
