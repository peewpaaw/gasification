import binascii
import os
import random


def generate_token():
    """ generates a pseudo random code using os.urandom and binascii.hexlify """
    # determine the length based on min_length and max_length
    #length = random.randint(self.min_length, self.max_length)
    length = random.randint(10, 10)
    # generate the token using os.urandom and hexlify
    return binascii.hexlify(
        os.urandom(10)
    ).decode()[0:length]
