from flask import render_template
from flask_login import login_required, current_user
from app.chats import chat_bp
from app.models import Chat
from sqlalchemy import and_, or_
from app.models import User, Chat
from datetime import timedelta
from app import db
@chat_bp.route("/")
@login_required
def inbox():

    chats = (
        Chat.query.filter(
            (Chat.sender_id == current_user.id) |
            (Chat.receiver_id == current_user.id)
        )
        .order_by(Chat.sent_at.desc())
        .all()
    )

    conversations = {}
    users = {}

    for chat in chats:

        other_id = (
            chat.receiver_id
            if chat.sender_id == current_user.id
            else chat.sender_id
        )

        if other_id not in conversations:
            conversations[other_id] = chat
            users[other_id] = (
                chat.receiver
                if chat.sender_id == current_user.id
                else chat.sender
            )

    print("\n===== FINAL CONVERSATIONS =====")
    for uid, chat in conversations.items():
        print(
            f"Other={uid}, "
            f"User={users[uid].full_name}, "
            f"Sender={chat.sender_id}, "
            f"Receiver={chat.receiver_id}, "
            f"Message={chat.message}"
        )
    print("===============================\n")

    return render_template(
        "chats/inbox.html",
        conversations=conversations,
        users=users
    )

@chat_bp.route("/<int:user_id>")
@login_required
def conversation(user_id):

    other = User.query.get_or_404(user_id)

    messages = (
        Chat.query.filter(
            or_(
                and_(
                    Chat.sender_id == current_user.id,
                    Chat.receiver_id == other.id
                ),
                and_(
                    Chat.sender_id == other.id,
                    Chat.receiver_id == current_user.id
                )
            )
        )
        .order_by(Chat.sent_at.asc())
        .all()
    )
    Chat.query.filter(
        Chat.sender_id == other.id,
        Chat.receiver_id == current_user.id,
        Chat.is_read == False
    ).update(
        {"is_read": True}
    )

    db.session.commit()
    return render_template(
        "chats/conversation.html",
        messages=messages,
        other=other,
        timedelta=timedelta
    )