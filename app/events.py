from app import socketio


def push_event(
    event_name=None, message="Push Event Triggered", data=None, broadcast=False
):
    if event_name:
        socketio.emit(event_name, data if data else message, broadcast=broadcast)


def push_data(message="Push Data Event Triggered", data=None, broadcast=False):
    socketio.emit("push_data", data if data else message, broadcast=broadcast)
