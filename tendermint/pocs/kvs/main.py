#! env python3

from vanilla import VanillaApp, Transaction, Result
from vanilla.utils import home_dir, int_to_big_endian, big_endian_to_int
from redis_protocol import parse_stream
from abci.types_pb2 import InternalError, EncodingError, BadNonce, UnknownRequest
import rlp
from rlp.sedes import binary

class SetParam(rlp.Serializable):
    fields = [
        ('key', binary),
        ('value', binary)
    ]

    def __init__(self, key=b'', value=b''):
        super().__init__(key, value)


NONCE_LENGTH = 12

def nonce_key(key):
    return "/nonce/%s" % key

SUPPORTED_CALL = [b'set']

# Setup the application. Pointing it to the same root dir used by Tendermint
# in this example, we are using ~/.vanilla, which means we set a different
# root_dir when running 'init':  'tendermint init --root ~/.vanilla'
app = VanillaApp('.tendermint')
app.debug = True


# Called only once on the first initialization of the application
# this is a good place to put stuff in state like default accounts, storage, etc...
@app.on_initialize()
def on_initialize(storage):
    pass

# Called per incoming tx (used in abci.check_tx).
# Put your transaction validation logic here.  Transaction passing this test
# are placed in the mempool.  If you don't specify this callback, all Tx pass
# by default
@app.validate_transaction()
def validate_transaction(tx, storage):
    """
    check the transaction contain a valid nonce and has a valid call
    """
    if tx.call not in SUPPORTED_CALL:
        return Result.error(code=UnknownRequest, log="call %s not supported" % tx.call)

    nonce = tx.nonce
    # check nonce
    exists = storage.unconfirmed.get_data(nonce_key(nonce))
    if exists:
        return Result.error(code=BadNonce, log="Nonce %X already exists" % nonce)

    # set nonce
    storage.unconfirmed.put_data(nonce_key(nonce), "found".encode('utf-8'))

    return Result.ok()


# Add more or more of these.  This is your apps business logic.
@app.on_transaction('set')
def kvs_set(tx, storage):
    param = tx.decode_params(SetParam)
    storage.confirmed.put_data(param.key, param.value)
    storage.commit()
    return Result.ok()



if __name__ == "__main__":
    app.run()