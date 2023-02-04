from datasette import hookimpl
from datasette.database import Database
import asyncio
import threading

# Adds a current_actor() function to SQLite that shows the current actor's
# ID.

actor = threading.local()

original_execute_fn = Database.execute_fn
async def patched_execute_fn(self, fn):
    task = asyncio.current_task()

    scope = None if not hasattr(task, '_dux_request') else task._dux_request.scope

    def wrapped_fn(conn):
        if scope and 'actor' in scope and scope['actor'] and 'id' in scope['actor']:
            actor.actor = scope['actor']['id']
        else:
            actor.actor = None
        rv = fn(conn)
        actor.actor = None
        return rv

    return await original_execute_fn(self, wrapped_fn)

original_execute_write_fn = Database.execute_write_fn
async def patched_execute_write_fn(self, fn, block=True):
    task = asyncio.current_task()

    scope = None if not hasattr(task, '_dux_request') else task._dux_request.scope

    def wrapped_fn(conn):
        if scope and 'actor' in scope and scope['actor'] and 'id' in scope['actor']:
            actor.actor = scope['actor']['id']
        else:
            actor.actor = None
        rv = fn(conn)
        actor.actor = None
        return rv

    return await original_execute_write_fn(self, wrapped_fn, block)

Database.execute_fn = patched_execute_fn
Database.execute_write_fn = patched_execute_write_fn
@hookimpl
def prepare_connection(conn):
    try:
        if getattr(conn, 'engine') == 'duckdb':
            return
    except AttributeError:
        pass

    def fn():
        return actor.actor

    conn.create_function(
        "current_actor", 0, fn
    )

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
