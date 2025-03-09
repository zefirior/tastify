import os
import string

ROOM_CODE_LENGTH = 4
ROOM_CODE_ALLOWED_CHARS = string.ascii_uppercase + string.digits
ROUND_DURATION_SEC = int(os.getenv('ROUND_DURATION_SEC', 150))

ALLOW_ORIGINS = [
    'http://tastify.zefirior.com',
    'http://localhost:3000',
    'http://0.0.0.0:3000',
]
