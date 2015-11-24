import string
import random


def random_id(length):
    return ''.join(random.choice(string.ascii_letters + string.digits)
                   for _ in xrange(length))
