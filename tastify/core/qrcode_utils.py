import qrcode
from PIL import Image


def make_qrcode(data: str) -> Image:
    return qrcode.make(data)