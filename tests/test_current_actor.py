from datasette.app import Datasette
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
async def test_current_actor_none():
    datasette = Datasette(memory=True, plugins_dir='./tests/plugins/')
    response = await datasette.client.get("/_memory.json?sql=select+current_actor()+as+actor&_shape=array")
    assert response.status_code == 200
    assert response.json() == [{'actor': 'someuser'}]
