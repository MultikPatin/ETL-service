from dotenv.main import find_dotenv, load_dotenv

load_dotenv(find_dotenv(".env"))

from .postgres import settings as postgres_settings  # noqa
from .sqlite import settings as sqlite_settings  # noqa
from .django import settings as django_settings  # noqa
from .elastic import settings as elastic_settings  # noqa
