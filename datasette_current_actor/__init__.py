from datasette import hookimpl
from datasette.database import Database
import asyncio
import threading

# Adds a current_actor() function to SQLite that shows the current actor's
# ID.

tls = threading.local()

original_execute_fn = Database.execute_fn
async def patched_execute_fn(self, fn):
    task = asyncio.current_task()

    request = None if not hasattr(task, '_dux_request') else task._dux_request

    def wrapped_fn(conn):
        tls.request = request
        rv = fn(conn)
        tls.request = None
        return rv

    return await original_execute_fn(self, wrapped_fn)

original_execute_write_fn = Database.execute_write_fn
async def patched_execute_write_fn(self, fn, block=True):
    task = asyncio.current_task()

    request = None if not hasattr(task, '_dux_request') else task._dux_request

    def wrapped_fn(conn):
        tls.request = request
        rv = fn(conn)
        tls.request = None
        return rv

    return await original_execute_write_fn(self, wrapped_fn, block)

def get_actor_from_request(request, args):
    scope = None if not request else request.scope

    path = ['actor']

    if args:
        for arg in args:
            path.append(arg)
    else:
        path.append('id')

    for p in path:
        if scope and p in scope:
            scope = scope[p]
        else:
            scope = None

    if isinstance(scope, str) or isinstance(scope, int):
        return scope

Database.execute_fn = patched_execute_fn
Database.execute_write_fn = patched_execute_write_fn
@hookimpl
def prepare_connection(conn):
    try:
        if getattr(conn, 'engine') == 'duckdb':
            return
    except AttributeError:
        pass

    def current_actor(*args):
        return get_actor_from_request(tls.request, args)

    def current_actor_ip():
        req = tls.request
        if not req:
            return None


        xff = req.headers.get('x-forwarded-for', '')
        first_ip = xff.split(',')[0].strip()

        if first_ip:
            return first_ip

        return req.scope['client'][0]

    def current_actor_user_agent():
        req = tls.request
        if not req:
            return None

        ua = req.headers.get('user-agent', '')

        if not ua:
            return None

        return ua

    conn.create_function("current_actor", -1, current_actor)
    conn.create_function("current_actor_ip", 0, current_actor_ip)
    conn.create_function("current_actor_user_agent", 0, current_actor_user_agent)

# We always register an actor_from_request hook so that our
# actor_from_request hookwrapper is guaranteed to fire
# on every request.
@hookimpl
def actor_from_request(datasette, request):
    return None

@hookimpl(specname='actor_from_request', hookwrapper=True)
def sniff_actor_from_request(datasette, request):
    asyncio.current_task()._dux_request = request

    # all corresponding hookimpls are invoked here
    outcome = yield
