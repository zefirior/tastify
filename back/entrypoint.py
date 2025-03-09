import logging

from back.db.base import DBSettings
from back.server.app import get_app

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logger.addHandler(logging.StreamHandler())

settings = DBSettings()
settings.setup()

app = get_app()
