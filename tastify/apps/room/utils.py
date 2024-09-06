import random
import string


ROOM_CODE_LENGTH = 4
ROOM_CODE_ALLOWED_CHARS = string.ascii_uppercase + string.digits


def generate_room_code():
    return ''.join(random.choices(ROOM_CODE_ALLOWED_CHARS, k=ROOM_CODE_LENGTH))
