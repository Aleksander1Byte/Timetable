def generate_hash():
    import random
    hash = random.getrandbits(64)
    return "%016x" % hash
