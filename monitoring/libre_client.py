from pylibrelinkup import LibreLinkUpClient, APIUrl
from pylibrelinkup.exceptions import RedirectError
import os

def get_libre_client():
    email = os.getenv("LIBRE_EMAIL")
    password = os.getenv("LIBRE_PASSWORD")
    region_env = os.getenv("LIBRE_REGION", "LA")  # já assume LA por padrão

    api_url = APIUrl.from_string(region_env.upper())

    client = LibreLinkUpClient(email=email, password=password, api=api_url)
    try:
        client.authenticate()
    except RedirectError as e:
        # Em último caso, se ainda der redirect, usa o valor sugerido pela API
        new_api_url = e.args[0]
        client = LibreLinkUpClient(email=email, password=password, api=new_api_url)
        client.authenticate()

    return client