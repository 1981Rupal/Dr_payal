# wsgi.py - WSGI entry point for production deployment

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app_enhanced import create_app

# Create application instance
app = create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
