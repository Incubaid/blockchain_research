SipHash
-------

###### The Story

- **Hash functions**
    - Generates random output from certain input, in a very fast manner
    - Easy to get collisions with
        > Assume , I designed a hash function called DumpHash()
        > That takes any number `0 <= x <= 100` and returns the remainder
        > modulus 3.

        > `DumpHash(100) = 1`

        > `DumpHash(99) = 0`

        > `DumpHash(98) = 2`

        > `DumpHash(97) = 1`

        > Some inputs will certainly results in same output. This is called **`collision`**

        > Since our `DumpHash()` uses (modulus 3) the out put must be < 3
        > or in math terms, output is in set `[0, 2]` or we say thato output space is of length of 3

        > **If you're generating random inputs and apply the DumpHash() to them it akes
        > on average 3/2 or 1.5 attempt before you could get a collision**

- **Cryptographic Hash functions**
    - Example: `SHA` algorithms Family
    - Slow
    - Designed to make it hard to get collisions or predict them in a computationally feasible way

        > It means in order to get a collision, you may want to try huge number of inputs on average
        which may take very long time like decades or hunders of years with the current computation power

        > it is difficult for an attacker to find two messages X and Y such that SHA(X) = SHA(Y), even though anyone may
          compute SHA(X).

- **Problems with collisions**
    - Hash functions are used in Hash Tables, or dictionaries.If you frequently getting
    collisions, it means your Hash Table is going from `O(0)` performance into
    `O(n)` for retrieval of items.

    - Both Hash functions & Cryptographic Hash functions are vulnerable to collisions if you took the out
    put and reduced its size to certain size

        > In one of the attacks on hash tables called `Hash flodding Attack`,

        > If hash function is used to map request coming from webserver to a DB table index of say (2 millions)
        records, based on headers, using a dictionary. Then an attacker can send bad headers in thousands of requests which have same
        hash, and thus hurting the performance of the dictionary lookups and even may cause Denial of service

###### Meet Siphash

- A Psudo Random function that is designed to produce (Keyd) hashes
    > It takes a key, and an input and producs a hash
- Unlike cryptographic hash functions such as SHA
    > SipHash instead guarantees that, having seen Xi and SipHash(Xi, k), an attacker who does not know the key k cannot find (any information about) k or SipHash(Y, k) for any message Y ∉ {Xi} which they have not seen before.

    > being a keyd hashing, means Siphash prevents `Hash flooding attacks`

- Siphash is meant to be a (MAC) `message authentication code` like (HMAC) function
- It uses symmetric key encryption (same key) for hashing and verification

###### Difference betwwen MAC & Digital signature


| Goal                          | Description                                                                                                          | MAC                         | Digital signature |
| ------------------------------|----------------------------------------------------------------------------------------------------------------------|---------------------------- |-------------------|
| Integrity                     |  Is Data tampered with                                                                                               |      yes                    |     yes           |
| Authentication                |  Data coming from certain sender                                                                                     |      yes                    |     yes           |
| Non-repudiation               |  Any user who can verify a signature **can not** also produce new signatures                                         |      No      (non-secure)   |     yes (secure)  |
| Secure against Replay Attacks |  Can Attacker re-send same encrypted message again and fool system to think sender sent this message again           |      No   (non-secure)      |  No   (non-secure)|


###### Using Siphash in signing messages

- Yes you can, but take it with a grain of salt, Digital signature is more secure in this case

>Using digital signature is much more secure because Siphsh uses symmetric key encryption scheme and uses same key for hashing aand verification
if key is leaked, an attacker could even sign other messages fooling system to think
he's authorized to do so. because it uses symmetric key encryption unless
- you used one time secret key per message and found a way to exchange a secret key between 2 machines
secretly using some mechanism like [Deffi helman key exchange](https://en.wikipedia.org/wiki/Diffie%E2%80%93Hellman_key_exchange)
- or you prevent verifiers from having the key, except only on a a hardware module with the key printed inside
so verifiers of messages can not produce signed messages

- In digital signature, you sign with private key and verify with public

**Important**
- If you use siphash or digital signature, you may want to prevent Replay attacks by timestamping your messages so that
an attacker, can not copy a message and send it back fooling system into thinking it's legal message


