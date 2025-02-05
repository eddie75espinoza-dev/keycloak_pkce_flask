import urllib.parse
import requests
from flask import Blueprint, redirect, url_for, request, session, jsonify
from core.config import APP_CONFIG
from core.keycloak_client import keycloak_openid
from routers import helpers
from logs import logs_config


bp = Blueprint('auth', __name__, url_prefix='/auth')


# Standard flow
# @bp.route("/login")
# def login():
#     try:
#         auth_url = keycloak_openid.auth_url(redirect_uri=url_for("auth.callback", _external=True))
        
#         return redirect(auth_url)
#     except Exception as e:
#         logs_config.logger.error(f"Error generating auth URL: {str(e)}")
#         return "Failed to initiate login", 500


# @bp.route("/callback")
# def callback():
#     code = request.args.get("code")
#     if not code:
#         return "Error: Missing authorization code", 400

#     redirect_uri = url_for("auth.callback", _external=True)

#     try:
#         token = keycloak_openid.token(
#             grant_type="authorization_code",
#             code=code,
#             redirect_uri=redirect_uri,
#         )

#         session["access_token"] = token["access_token"]
#         session["refresh_token"] = token["refresh_token"]
        
#         return f"Login successful! Token saved in session.\ntoken: \n{token["access_token"]}"
#     except Exception as e:
#         return f"Error during token exchange: {str(e)}", 500


# @bp.route("/logout")
# def logout():
#     try:
#         refresh_token = session.get("refresh_token")

#         if refresh_token:
#             keycloak_openid.logout(refresh_token)

#         session.clear()

#         return redirect(url_for("auth.login"))
#     except Exception as e:
#         logs_config.logger.error(f"Error during logout: {str(e)}")
#         return "Failed to logout", 500
    

# Standard flow + PKCE
@bp.route("/login")
def login():
    try:
        # Generar PKCE
        code_verifier, code_challenge = helpers.generate_pkce_pair()

        session["code_verifier"] = code_verifier

        # Construcción manual de la URL de autenticación
        auth_url = (
            f"{APP_CONFIG.KC_SERVER_URL}/realms/{APP_CONFIG.KC_REALM}/protocol/openid-connect/auth?"
            f"client_id={APP_CONFIG.KC_CLIENT_ID}&"
            f"redirect_uri={urllib.parse.quote(APP_CONFIG.KC_REDIRECT_URI)}&"
            f"response_type=code&"
            f"scope=openid&"
            f"code_challenge={code_challenge}&"
            f"code_challenge_method=S256"
        )
        
        return redirect(auth_url)

    except Exception as e:
        logs_config.logger.error(f"Error during login: {str(e)}")
        return f"Error during login: {str(e)}", 500


@bp.route("/callback")
def callback():
    code = request.args.get("code")

    if not code:
        logs_config.logger.error(f"code: {code}")
        return "Error: Missing authorization code", 400

    code_verifier = session.get("code_verifier")
    if not code_verifier:
        logs_config.logger.error(f"code_verifier: {code_verifier}")
        return "Error: Missing code_verifier", 400

    token_url = f"http://host.docker.internal:8080/realms/{APP_CONFIG.KC_REALM}/protocol/openid-connect/token"
    
    try:
        # Intercambio del código por un token
        response = requests.post(token_url, data={
            "grant_type": "authorization_code",
            "client_id": APP_CONFIG.KC_CLIENT_ID,
            "redirect_uri":APP_CONFIG.KC_REDIRECT_URI,
            "code": code,
            "code_verifier": code_verifier
        }, headers={"Content-Type": "application/x-www-form-urlencoded"})
        
        token_data = response.json()
        
        if "access_token" not in token_data:
            return f"Error: {token_data}", 400
        
        session["access_token"] = token_data["access_token"]
        session["refresh_token"] = token_data["refresh_token"]

        return jsonify({"message": "Login successful!", "token": token_data})
    
    except Exception as e:
        logs_config.logger.error(f"Error during token exchange: {str(e)}")
        return f"Error during token exchange: {str(e)}", 500


@bp.route("/logout")
def logout():
    try:
        refresh_token = session.get("refresh_token")

        if not refresh_token:
            logs_config.logger.error("No access token found in session.")
            return "Error: No refresh token found.", 400

        keycloak_openid.logout(refresh_token)
        
        session.clear()
        
        return redirect(url_for("auth.login"))
    
    except Exception as e:
        logs_config.logger.error(f"Error during logout: {str(e)}")
        return f"Error during logout: {str(e)}", 500