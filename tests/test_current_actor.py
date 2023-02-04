from datasette.app import Datasette
import json
import sqlite3
import pytest


@pytest.mark.asyncio
async def test_plugin_is_installed():
    datasette = Datasette(memory=True)
    response = await datasette.client.get("/-/plugins.json")
    assert response.status_code == 200
    installed_plugins = {p["name"] for p in response.json()}
    assert "datasette-current-actor" in installed_plugins

@pytest.mark.asyncio
async def test_current_actor_none():
    datasette = Datasette(memory=True)
    response = await datasette.client.get("/_memory.json?sql=select+current_actor()+as+actor&_shape=array")
    assert response.status_code == 200
    assert response.json() == [{'actor': None}]

@pytest.mark.asyncio
async def test_current_actor_some():
    datasette = Datasette(memory=True, plugins_dir='./tests/plugins/')
    response = await datasette.client.get("/_memory.json?sql=select+current_actor()+as+actor&_shape=array")
    assert response.status_code == 200
    assert response.json() == [{'actor': 'root'}]

@pytest.mark.asyncio
async def test_insert_defaults(tmp_path):
    db_name = tmp_path / "db.sqlite"
    conn = sqlite3.connect(db_name)
    conn.close()
    datasette = Datasette(
        memory=True,
        plugins_dir='./tests/plugins/',
        files=[db_name]
    )

    db = datasette.get_database('db')
    #rv = await mem.execute_write("CREATE TABLE logs(user text default (current_actor()), value text)")
    await db.execute_write("CREATE TABLE logs(user text default (current_actor()), value text)")

    #print(list(rv))
    #response = await datasette.client.get("/_memory.json?sql=select+%2A+from+logs&_shape=array")
    response = await datasette.client.get("/db.json?sql=select+user+from+logs&_shape=array")
    assert response.status_code == 200
    assert response.json() == []

    print(datasette.client.post)
    response = await datasette.client.post(
        "/db/logs/-/insert",
        headers={
            'content-type': 'application/json',
        },
        content=json.dumps({
            "row": {
                "value": "value1",
            }
        })
    )
    assert response.status_code == 201
    response = await datasette.client.get("/db.json?sql=select+user,value+from+logs&_shape=array")
    assert response.status_code == 200
    assert response.json() == [{ 'user': 'root', 'value': 'value1'}]

