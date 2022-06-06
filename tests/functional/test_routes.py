import pytest
from SV import create_app


def test_home_page():
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """

    flask_app = create_app('flask.cfg')

    print(flask_app.__dict__)

    with flask_app.test_client() as test_client:
        response = test_client.get('/')

        assert response.status_code == 200



if __name__ == '__main__':
    test_home_page()