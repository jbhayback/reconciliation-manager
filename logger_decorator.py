from datetime import datetime
import inspect


def log_time(msg=None):
    def decorator(f):
        nonlocal msg
        if msg is None:
            msg = '{} time spent: '.format(f.__name__)

        def inner(*args, **kwargs):
            # check if the object has a logger
            global logger
            if args and hasattr(args[0], 'logger'):
                logger = args[0].logger
            start = datetime.now()
            result = f(*args, **kwargs)
            logger.info(
                msg + ' {} seconds'.format((datetime.now() - start).total_seconds())
            )
            return result

        return inner

    return decorator


def log_params(f):
    arg_spec = inspect.getargspec(f).args
    has_self = arg_spec and arg_spec[0] == 'self'

    def decorator(*args, **kwargs):
        logger.info(
            'calling {} with args: {}, and kwargs: {}'.format(
                f.__name__, args if not has_self else args[1:], kwargs
            )
        )
        return f(*args, **kwargs)

    return decorator
