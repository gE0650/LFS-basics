def decode1(bytestring: bytes):
    return "".join([bytes([b]).decode("utf-8") for b in bytestring])