# -*- coding: utf-8 -*-
from functools import wraps
import hashlib
from flask import request, make_response, jsonify, url_for, \
        Response, g, render_template, current_app, abort
from .rate_limit import RateLimit


def returns_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        r = f(*args, **kwargs)
        return Response(r, content_type='application/json; charset=utf-8')
    return decorated_function


def replace_func_with(func, version_specs, patch=False):
    '''
    @param func: the function to replace the original function.
    @param version_specs: a list of version_spec.
    if any of the version_specs matched, the original func will be replaced.
    example of version_spec:
    {'client': 'ios', 'gte': (2, 10)} or
    {'client': 'android', 'gt': (1, 12), 'lte': (2, 10)} '''

    def outer(orig_func):
        @wraps(orig_func)
        def decorated_function(*args, **kwargs):
            version = (g.get('version_major'), g.get('version_minor'))
            client = g.get('client')
            if not any(match_spec(client, version, spec)
                       for spec in version_specs):
                return orig_func(*args, **kwargs)

            if isinstance(func, basestring):
                new_func = get_func_from_str(func, args)
                new_args = args[1:]
            else:
                new_func = func
                new_args = args
            if not new_func:
                return orig_func(*args, **kwargs)
            if patch:
                return new_func(orig_func(*args, **kwargs))
            return new_func(*new_args, **kwargs)
        return decorated_function
    return outer


def get_func_from_str(func, args):
    if not args:
        return
    first_arg = args[0]
    try:
        return getattr(first_arg, func)
    except AttributeError:
        return


def patch_func_with(func, version_specs):
    '''
    @param func: the function to patch the original function.
        Called after the original function is called.
    @param version_specs: a list of version_spec.
        if any of the version_specs matched, the original func will be patch.
    '''

    def outer(orig_func):
        @wraps(orig_func)
        def decorated_function(*args, **kwargs):
            version = (g.get('version_major'), g.get('version_minor'))
            client = g.get('client')
            if any(match_spec(client, version, spec)
                   for spec in version_specs):
                return func(orig_func(*args, **kwargs))
            else:
                return orig_func(*args, **kwargs)
        return decorated_function
    return outer


def match_spec(client, version, version_spec):
    if client != version_spec.get('client', ''):
        return False
    return all(match_version(k, v, version)
               for k, v in version_spec.items() if k != 'client')


def match_version(k, v, version):
    return any((
        (k == 'gt' and version > v),
        (k == 'lt' and version < v),
        (k == 'eq' and version == v),
        (k == 'gte' and version >= v),
        (k == 'lte' and version <= v),
    ))


def render_api_template(filename, *args, **kwargs):
    filename = (g.get('client') or 'android') + '/' + filename
    return render_template(filename, *args, **kwargs)


def cache_control(*directives):
    """Insert a Cache-Control header with the given directives."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # invoke the wrapped function
            rv = f(*args, **kwargs)
            # convert the returned value to a response object
            rv = make_response(rv)
            # insert the Cache-Control header and return response
            rv.headers['Cache-Control'] = ', '.join(directives)
            return rv
        return wrapped
    return decorator


def no_cache(f):
    """Insert a no-cache directive in the response. This decorator just
    invokes the cache-control decorator with the specific directives."""
    return cache_control('private', 'no-cache', 'no-store', 'max-age=0')(f)


def open_json(f):
    """Generate a JSON response from a database model or a Python
    dictionary."""
    @wraps(f)
    def wrapped(*args, **kwargs):
        # invoke the wrapped function
        rv = f(*args, **kwargs)

        # the wrapped function can return the dictionary alone,
        # or can also include a status code and/or headers.
        # here we separate all these items
        status = None
        headers = None
        if isinstance(rv, tuple):
            rv, status, headers = rv + (None,) * (3 - len(rv))
        if isinstance(status, (dict, list)):
            headers, status = status, None

        if rv is None:
            rv = jsonify(
                {'status': 416, 'error': 'not match',
                 'message': 'Object does not exist'})
            rv.status_code = 416
            return rv

        # if the response was a database model, then convert it to a
        # dictionary
        if not isinstance(rv, dict):
            rv = rv.to_open_json()

        # generate the JSON response
        rv = jsonify(rv)
        if status is not None:
            rv.status_code = status
        if headers is not None:
            rv.headers.extend(headers)
        return rv
    return wrapped


def paginate(collection, max_per_page=25):
    """Generate a paginated response for a resource collection.

    Routes that use this decorator must return a MongoEngine query as a
    response.

    The output of this decorator is a Python dictionary with the paginated
    results. The application must ensure that this result is converted to a
    response object, either by chaining another decorator or by using a
    custom response object that accepts dictionaries."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # invoke the wrapped function
            query = f(*args, **kwargs)

            # obtain pagination arguments from the URL's query string
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', max_per_page,
                                            type=int), max_per_page)

            # run the query with Flask-MongoEngine's pagination
            p = query.paginate(page, per_page)

            # build the pagination metadata to include in the response
            pages = {'page': page, 'per_page': per_page,
                     'total': p.total, 'pages': p.pages}
            # generate the paginated collection as a dictionary
            results = [item.to_open_json() for item in p.items]

            # return a dictionary as a response
            return {collection: results, 'meta': pages}
        return wrapped
    return decorator


def rate_limit(limit, per, scope_func=lambda: request.remote_addr):
    """Limits the rate at which clients can send requests to 'limit' requests
    per 'period' seconds. Once a client goes over the limit all requests are
    answered with a status code 429 Too Many Requests for the remaining of
    that period."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_app.config['USE_RATE_LIMITS']:
                key = 'rate-limit/%s/%s/' % (f.__name__, scope_func())
                limiter = RateLimit(key, limit, per)
                if not limiter.over_limit:
                    rv = f(*args, **kwargs)
                else:
                    rv = jsonify(
                        {'status': 429, 'error': 'too many requests',
                         'message': 'You have exceeded your request rate'})
                    rv.status_code = 429
                    return rv
                #rv = make_response(rv)
                g.headers = {
                    'X-RateLimit-Remaining': str(limiter.remaining),
                    'X-RateLimit-Limit': str(limiter.limit),
                    'X-RateLimit-Reset': str(limiter.reset)
                }
                return rv
            else:
                return f(*args, **kwargs)
        return wrapped
    return decorator


def permission(f):
    """Need permission to involke current function"""
    @wraps(f)
    def wrapped(*args, **kwargs):
        api_granted = f.__name__ in g.user.permissions
        if not api_granted:
            abort(405)

        params = filter(lambda p: p.api == f.__name__, g.user.permissions)[0].allowed_params
        if params:
            if not request.args.keys():
                abort(403)
            for k in request.args.keys():
                param = params.get(k)
                if param and request.args.get(k) not in param:
                    abort(403)

        if set(request.args.keys()).intersection(['page', 'pages']) and \
                not set(request.args.keys()).intersection(params.keys()):
            abort(403)

        rv = f(*args, **kwargs)
        return rv
    return wrapped
