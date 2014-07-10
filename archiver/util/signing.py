import copy
import hmac
import time
import hashlib
import calendar

from archiver.settings import HMAC_KEY


def sign(payload):
    return sign_json_package(HMAC_KEY, payload, time_stamp=True, sign_with=['id'])


def verify_submition(package):
    try:
        return verify_signed_json(package['signature'], HMAC_KEY, package, signed_with=['timeStamp'])
    except KeyError:
        return False


def verify_callback(package):
    try:
        return verify_signed_json(package['signature'], HMAC_KEY, package, signed_with=['timeStamp', 'id'])
    except KeyError:
        return False


def verify_signed(key, package, signed_with=()):
    try:
        return verify_signed_json(package['signature'], key, package, signed_with=signed_with)
    except KeyError:
        return False


def hmac_signature(key, sign_with):
    return hmac.new(
        key=key,
        msg=sign_with,
        digestmod=hashlib.sha256,
    ).hexdigest()


def sign_json_package(key, to_sign, time_stamp=False, sign_with=()):
    package = copy.deepcopy(to_sign)

    signables = ''.join([str(to_sign[index]) for index in sign_with])

    if time_stamp:
        stamp = calendar.timegm(time.gmtime())
        package['timeStamp'] = stamp
        signables = str(package['timeStamp']) + signables

    signature = hmac_signature(key, signables)

    package['signature'] = signature

    return package


def verify_signed_json(signature, key, package, signed_with=()):
    comp_sig = sign_json_package(key, package, sign_with=signed_with)['signature']
    return comp_sig == signature
