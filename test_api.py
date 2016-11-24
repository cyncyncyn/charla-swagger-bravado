# -*- coding: utf-8 -*-
import random
import string
import requests

import pytest
from bravado.client import SwaggerClient
from bravado.swagger_model import load_file
from bravado.exception import HTTPBadRequest


def random_word(length):
    return ''.join(random.choice(string.lowercase) for i in range(length))


@pytest.fixture(scope='module')
def client():
    client = SwaggerClient.from_spec(load_file("swagger.yaml"))
    return client


def test_create_character(client):
    character_name = random_word(10)

    Character = client.get_model('Character')
    new_character = Character(name=character_name, species='Human')

    created_character = client.characters.create(character=new_character
                                                 ).result()

    character = client.characters.retrieve(character_id=created_character.id
                                           ).result()
    assert character.name == character_name


def test_create_character_with_requests():
    character_name = random_word(10)

    url = 'http://localhost:8000/api/characters/'
    data = {'name': character_name, 'species': 'Human'}

    response = requests.post(url, data=data)
    created_character = response.json()

    get_url = "{}{}".format(url, created_character['id'])

    character = requests.get(get_url).json()

    assert character['name'] == character_name


def test_try_create_character_with_malformed_photo_url_fails(client):
    character_name = random_word(10)

    Character = client.get_model('Character')
    new_character = Character(
        name=character_name, species='Human', photo_url="malformed_url")

    with pytest.raises(HTTPBadRequest) as exc_info:
        client.characters.create(character=new_character).result()

    assert exc_info.value.response.json().get('photo_url')
    assert 'Enter a valid URL.' in exc_info.value.response.json()['photo_url']
