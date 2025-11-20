from django.conf import settings
from pylibrelinkup import PyLibreLinkUp


def get_libre_client() -> PyLibreLinkUp:
    email = settings.LIBRELINKUP_EMAIL
    password = settings.LIBRELINKUP_PASSWORD

    if not email or not password:
        raise RuntimeError("LIBRE_EMAIL ou LIBRE_PASSWORD não configurados no .env")

    client = PyLibreLinkUp(email=email, password=password, region='LA')
    client.authenticate()
    return client