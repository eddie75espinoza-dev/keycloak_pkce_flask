from flask import Blueprint, session, jsonify, render_template
from core.keycloak_client import keycloak_openid
from logs import logs_config


bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@bp.route("/")
def user_info():
    access_token = session.get("access_token")
    
    if not access_token:
        # return jsonify({"error": "User not authenticated"}), 401
        rendered_html = render_template('index.html')
        return rendered_html
    
    try:     
        user_data = keycloak_openid.userinfo(access_token)

        context = {"name" : user_data.get('name')}     
        
        rendered_html = render_template('index.html', **context)

        return rendered_html
   
    except Exception as e:
        import traceback
        logs_config.logger.error("Error fetching user info:", traceback.format_exc())
        return jsonify({"error": f"Failed to fetch user info: {str(e)}"}), 500
