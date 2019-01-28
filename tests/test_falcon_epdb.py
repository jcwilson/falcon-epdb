import json
from falcon.testing import SimpleTestResource


try:
    from cryptography.fernet import Fernet

    def test_fernet_client(fernet, fernet_client, mock_epdb_serve):
        doc = {'message': 'Hello world!'}
        resource = SimpleTestResource(json=doc)
        fernet_client.app.add_route('/', resource)

        header_value = fernet.encrypt(json.dumps({'epdb': {}}).encode())
        result = fernet_client.simulate_get(headers={
            'X-EPDB': 'Fernet {}'.format(header_value.decode())
        })

        assert mock_epdb_serve.called
        assert mock_epdb_serve.called_once_with(port=9000)

except ImportError:
    pass


try:
    import jwt

    def test_jwt_client(jwt_key, jwt_client, mock_epdb_serve):
        doc = {'message': 'Hello world!'}
        resource = SimpleTestResource(json=doc)
        jwt_client.app.add_route('/', resource)

        header_value = jwt.encode({'epdb': {}}, jwt_key)
        result = jwt_client.simulate_get(headers={
            'X-EPDB': 'JWT {}'.format(header_value.decode())
        })

        assert mock_epdb_serve.called
        assert mock_epdb_serve.called_once_with(port=9000)

except ImportError:
    pass
