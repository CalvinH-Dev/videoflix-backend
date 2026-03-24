import django_rq


def get_queue(name: str = "default"):
    """
    Retrieve a Redis queue by name.

    Args:
        name: Name of the Redis queue.

    Returns:
        The Redis queue instance.
    """
    return django_rq.get_queue(name)


def get_connection(name: str = "default"):
    """
    Retrieve a Redis connection by name.

    Args:
        name: Name of the Redis connection.

    Returns:
        The Redis connection instance.
    """
    return django_rq.get_connection(name)
