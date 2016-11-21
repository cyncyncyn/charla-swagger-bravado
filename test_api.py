import random
import string

import pytest
from bravado.client import SwaggerClient
from bravado.swagger_model import load_file
from bravado.exception import HTTPBadRequest


def random_word(length):
    return ''.join(random.choice(string.lowercase) for i in range(length))


@pytest.fixture(scope='module')
def client():
    client = SwaggerClient.from_spec(load_file("swagger.yaml"))
    client.characters.list().result()
    return client


def test_create_character(client):
    character_name = random_word(10)

    Character = client.get_model('Character')
    new_character = Character(name=character_name, species='Human')

    assert not new_character.id

    created_character = client.characters.create(character=new_character).result()

    assert created_character.id
    assert created_character.name == character_name


def test_try_create_character_with_malformed_photo_url_fails(client):
    character_name = random_word(10)

    Character = client.get_model('Character')
    new_character = Character(
        name=character_name, species='Human', photo_url="malformed_url")

    with pytest.raises(HTTPBadRequest) as exc_info:
        client.characters.create(character=new_character).result()

    assert exc_info.value.response.json().get('photo_url')
    assert 'Enter a valid URL.' in exc_info.value.response.json()['photo_url']
