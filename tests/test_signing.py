from archiver.util import signing

from tests.utils.clients import rnd_str


def random_json(length=5):
    return {
        rnd_str(): rnd_str()
        for _ in xrange(length)
    }


def get_signed(time_stamp=False):
    json = random_json()
    key = rnd_str()
    signed = signing.sign_json_package(key, json, time_stamp=time_stamp)
    return key, json, signed


def test_can_sign():
    _, json, signed = get_signed()

    for key in json.keys():
        assert json[key] == signed[key]
    assert signed['signature']
    assert not signed.get('timeStamp')


def test_timestamp():
    _, json, signed = get_signed(time_stamp=True)

    for key in json.keys():
        assert json[key] == signed[key]
    assert signed['signature']
    assert signed['timeStamp']


def test_verify():
    for _ in xrange(10):
        key, _, signed = get_signed()
        assert signing.verify_signed(key, signed)


def test_constant():
    key = rnd_str()
    original = random_json()
    last_signed = signing.sign_json_package(key, original)
    for _ in xrange(10):
        signed = signing.sign_json_package(key, original)
        assert signed == last_signed
        last_signed = signed
