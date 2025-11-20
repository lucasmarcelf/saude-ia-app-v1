from django.conf import settings
from pylibrelinkup import PyLibreLinkUp, APIUrl


def get_libre_client() -> PyLibreLinkUp:
    email = settings.LIBRELINKUP_EMAIL
    password = settings.LIBRELINKUP_PASSWORD
    region_env = settings.LIBRELINKUP_API_URL

    api = APIUrl.from_string(region_env.upper())

    if not email or not password:
        raise RuntimeError("LIBRE_EMAIL ou LIBRE_PASSWORD não configurados no .env")

    client = PyLibreLinkUp(email=email, password=password, api_url=api)
    client.authenticate()
    return client