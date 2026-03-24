import django_rq


def get_queue(name="default"):
    return django_rq.get_queue(name)


def get_connection(name="default"):
    return django_rq.get_connection(name)
