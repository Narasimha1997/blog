def encode(version_string):
    version = version_string.split(".")
    v = 0
    for idx, split in enumerate(version):
        if int(split) > 255:
            return 0
        v = v | (int(split) << (24 - (idx + 1) * 8))
    return v

# test
print(encode('1.2.3'))
print(encode('255.255.2'))

def decode(version):
    c1 = (version >> 16) & 0xff
    c2 = (version >> 8) & 0xff
    c3 = version & 0xff

    return "{}.{}.{}".format(c1, c2, c3)

print(decode(66051))
print(decode(16776962))