#! env python3

import time
import os
from vanilla.client import RpcClient
from vanilla import Transaction
from redis_protocol import encode
from main import NONCE_LENGTH, SetParam

def generate_nonce():
    return int.from_bytes(os.urandom(NONCE_LENGTH), "big")

class NotFound(Exception):
    pass

class Client():

    def __init__(self, host="127.0.0.1", port=46657):
        self.rpc = RpcClient(host=host, port=port)

    def set(self, key, value):
        tx = Transaction()
        tx.call = 'set'
        tx.nonce = generate_nonce()
        tx.params = SetParam(key, value)

        response = self.rpc.send_tx_commit(tx.encode())
        if response['deliver_tx']['code'] != 0:
            raise Exception("bad response code: %s" % str(response))

    def get(self, key):
        resp = self.rpc.query('/data', key, False)
        value = resp['response']['value']
        if not value:
            raise NotFound("key %s not found" % key)

        return bytes.fromhex(value)

if __name__ == '__main__':
    cl = Client()
    from IPython import embed;embed()