import sys
import os

# Add root project directory to sys.path so app and db modules are found
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app


class VercelPathFixMiddleware:
    """
    Middleware to ensure incoming Vercel Serverless Function rewrites
    correctly preserve the requested URL path (/login, /signup, /, etc.)
    and prevent infinite redirect loops.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        # Extract the real requested URI from proxy headers or environment
        request_uri = (
            environ.get("HTTP_X_MATCHED_PATH")
            or environ.get("HTTP_X_FORWARDED_URI")
            or environ.get("REQUEST_URI")
            or environ.get("PATH_INFO", "/")
        )

        # Strip query strings if present
        if "?" in request_uri:
            request_uri = request_uri.split("?", 1)[0]

        # Strip any Vercel internal function path prefix (/api/index or /api/index.py)
        if request_uri.startswith("/api/index.py"):
            request_uri = request_uri[len("/api/index.py"):] or "/"
        elif request_uri.startswith("/api/index"):
            request_uri = request_uri[len("/api/index"):] or "/"
        elif request_uri in ("/api", "/api/"):
            request_uri = "/"

        environ["PATH_INFO"] = request_uri
        return self.wsgi_app(environ, start_response)


# Wrap Flask wsgi_app with the path fix middleware
app.wsgi_app = VercelPathFixMiddleware(app.wsgi_app)
