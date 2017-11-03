# Key-value store as a tendermint app using py-tendermint

The goal of this poc is to create a super simple key-value store on top of tendermint.
It is going to be written in python using the [py-tendermint](https://github.com/davebryson/py-tendermint) library called Vanilla

**Vanilla**:  
A Python microframework for building blockchain applications with Tendermint.  
Vanilla abstract the ABCI API and expose some decorator that your application has to use to implement the business logic. The are 3 decorator you can use:

- **on_initialize**:  Called on the very first run of the application. Can be used to initialize genesis state
- **validate_transaction**: Single validator for the app.  This is based on the idea that the single Transaction can be handled by a single validator.  Used to 'check' transaction to see whether or not they should be included in the mempool or ignored.
- **on_transaction**: A decorator for functions that implement core business logic and can alter application state.  The provided function MUST accept a 2 params 'tx' and 'storage'. The 'rule' must match the value set in Tx.call

## Installation

Install tendermint:
```python
j.tools.prefab.local.apps.tendermint.build()
j.tools.prefab.local.apps.tendermint.install()
```

Install the key-value store app:
```shell
pip install -r requirement.txt
```

## Usage
- Start tendermint using a custom home path so we isolate our blockchain:
```shell
tendermint --home .tendermint_poc node
```
- Start our application:
```shell
python3 app.py
```

Your application is now running and you should see the tendermint node start creating blocks.

To talk to our key-value store application, use the client provided. the client.py implement the client logic and if you execute this file it will instanciate a client and open an ipython shell in which you can play.
```python
python3 client.py
Python 3.6.3 (default, Oct 24 2017, 14:48:20)
Type 'copyright', 'credits' or 'license' for more information
IPython 6.2.1 -- An enhanced Interactive Python. Type '?' for help.

In [1]: cl.set('hello','world')

In [2]: cl.get('hello')
Out[2]: b'world'
```

## Application architecture

### Server side

First we instantiate a Vanilla application and point it to the same directory as the tendermint node.  

```python
app = VanillaApp('.tendermint')
app.debug = True
```

The VanillaApp does all the heavy lifting of the ACBI protocol for you. It implement all the required method to be ACBI compatible and provide the user with a storage implementation of a merkle tree


Then we implement our application logic using the decorator.  
First we implement the `validate_transaction` decorator. In this method we will validate that the transaction contains a valid nonce and that the type of call is indeed supported by our application

```python
NONCE_LENGTH = 12

def nonce_key(key):
    return "/nonce/%s" % key

SUPPORTED_CALL = [b'set']

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
```

Next, we implement the logic when an transaction is accepted.
This is done using the `on_transaction` decorator that takes the type of call it should handle.  
We also create a `SetParam` class, this class is going to be used by the client and server to serialize the argument of the set request into the transaction. Once again py-tendermint provide us with simple interface to achieve this.  
The actual logic of the set method is really simple, we deserialize the parameter of the request, then we save the key value pair into the merkle tree.

```python
class SetParam(rlp.Serializable):
    fields = [
        ('key', binary),
        ('value', binary)
    ]

    def __init__(self, key=b'', value=b''):
        super().__init__(key, value)

@app.on_transaction('set')
def kvs_set(tx, storage):
    param = tx.decode_params(SetParam)
    storage.confirmed.put_data(param.key, param.value)
    storage.commit()
    return Result.ok()
```

Finally, write the entry point of the application and start the server:

```python
if __name__ == "__main__":
    app.run()
```

### client side
The client is also really simple. It a class that expose 2 methods, `set` and `get`. 
The Client class encapsulate an `RPCClient` that is provided by `py-tendermint`.

The `set` method creates a transation objet, generate a nonce, set the type of call then send the transaction and wait for the transaction to be processed and then inspect the result.

The `get` method doesn't use transaction. Instead it sends a query to our server and ask the value that is associated with a key in the storage. The VanillaApp class already implement the logic for the query. Currently there is no exposed decorator to modifiy the behavior or the query request, but the code is simple and should not be a problem to expose it if we need different behavior.

Here the full client class:
```python
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
```