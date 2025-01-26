import string

ROOM_CODE_LENGTH = 4
ROOM_CODE_ALLOWED_CHARS = string.ascii_uppercase + string.digits

ALLOW_ORIGINS = [
    "http://tastify.zefirior.com",
    "http://localhost:3000",
    "http://0.0.0.0:3000",
]
