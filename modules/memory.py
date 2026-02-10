import struct


def unpack_uint32(value: bytes) -> int:
    return struct.unpack("<I", value)[0]



