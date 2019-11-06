import os

from angery_cms_server.app import app

angery_cms_server = app

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
