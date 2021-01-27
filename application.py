from gevent import monkey

monkey.patch_all()
import os

from app import create_app, socketio

app = create_app()

## For Local debugging without docker for main app

if __name__ == "__main__":
    if app.debug and bool(os.getenv("LOCAL_DOCKER", None)):
        app.run(host="0.0.0.0", port=7970, debug=True)  # if socketio is not implemented
        # socketio.run(app, host="0.0.0.0", port=7970, debug=True)
    elif app.debug:
        app.run(host="0.0.0.0", port=7970, debug=True)  # if socketio is not implemented
        # socketio.run(app, host="0.0.0.0", port=7970, debug=True)
    else:
        app.run()  # for gunicorn
