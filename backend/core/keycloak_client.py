from keycloak import KeycloakOpenID

from core.config import APP_CONFIG


keycloak_openid = KeycloakOpenID(
    server_url="http://host.docker.internal:8080",
    client_id=APP_CONFIG.KC_CLIENT_ID,
    realm_name=APP_CONFIG.KC_REALM
)
