from datetime import datetime, timedelta

from flask_login import current_user
from flask_socketio import emit, join_room

from app import db, socketio
from app.models import Chat


print("CHAT EVENTS LOADED")


@socketio.on("connect")
def connect():

    if current_user.is_authenticated:

        # Personal room for notifications/inbox updates
        join_room(f"user_{current_user.id}")

        print(
            f"{current_user.full_name} connected"
        )


@socketio.on("disconnect")
def disconnect():

    if current_user.is_authenticated:

        print(
            f"{current_user.full_name} disconnected"
        )


@socketio.on("join_chat")
def join_chat(data):
    """
    data = {
        "other_user": 5
    }
    """

    if not current_user.is_authenticated:
        return


    room = "_".join(
        map(
            str,
            sorted(
                [
                    current_user.id,
                    data["other_user"]
                ]
            )
        )
    )


    join_room(room)


    emit(
        "joined_room",
        {
            "room": room
        }
    )


@socketio.on("send_message")
def send_message(data):

    """
    data = {
        receiver_id: 2,
        property_id: 10 or None,
        message: "Hello"
    }
    """

    if not current_user.is_authenticated:
        return


    receiver_id = data["receiver_id"]


    # Room for the actual conversation
    conversation_room = "_".join(
        map(
            str,
            sorted(
                [
                    current_user.id,
                    receiver_id
                ]
            )
        )
    )


    chat = Chat(
        sender_id=current_user.id,
        receiver_id=receiver_id,
        property_id=data.get("property_id"),
        message=data["message"],
        sent_at=datetime.utcnow()
    )


    db.session.add(chat)
    db.session.commit()

    # Update active conversation window
    emit(
        "new_message",
        {
            "id": chat.id,
            "sender_id": chat.sender_id,
            "receiver_id": chat.receiver_id,
            "property_id": chat.property_id,
            "message": chat.message,
            "sent_at": (
                chat.sent_at + timedelta(hours=5, minutes=45)
            ).strftime("%I:%M %p")
        },
        room=conversation_room
    )



    # Update inbox/messages list
    emit(
        "conversation_updated",
        {
            "sender_id": chat.sender_id,
            "receiver_id": chat.receiver_id,
            "message": chat.message,
            "sent_at": (
                chat.sent_at + timedelta(hours=5, minutes=45)
            ).strftime("%b %d"),
            "is_read": chat.is_read
        },
        room=f"user_{receiver_id}"
    )