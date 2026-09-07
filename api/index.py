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
    (/api/index or /api/index.py) map directly to Flask routes (/, /login, etc.).
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "")
        if path.startswith("/api/index.py"):
            environ["PATH_INFO"] = path[len("/api/index.py"):] or "/"
        elif path.startswith("/api/index"):
            environ["PATH_INFO"] = path[len("/api/index"):] or "/"
        elif path in ("/api", "/api/"):
            environ["PATH_INFO"] = "/"
        return self.wsgi_app(environ, start_response)


# Wrap Flask wsgi_app with the path fix middleware
app.wsgi_app = VercelPathFixMiddleware(app.wsgi_app)
