import pytest

from vial.app import Vial


@pytest.fixture
def app():
    return Vial()

@pytest.fixture
def test_client(app):
    return app.test_session()
