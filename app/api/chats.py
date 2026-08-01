from flask import Blueprint, request
from sqlalchemy import or_, and_
from app import db
from app.models import Chat, User
from app.api.helpers import api_response, token_required

api_chats = Blueprint('chats', __name__)

@api_chats.route('/conversations', methods=['GET'])
@token_required
def get_conversations(current_user):
    """
    Returns a list of unique conversations (Inbox).
    Equivalent to the 'inbox' route in chats/routes.py
    """
    # Fetch all messages involving the current user
    chats = (
        Chat.query.filter(
            or_(
                Chat.sender_id == current_user.id,
                Chat.receiver_id == current_user.id
            )
        )
        .order_by(Chat.sent_at.desc())
        .all()
    )

    conversations_map = {}
    for chat in chats:
        other_id = chat.receiver_id if chat.sender_id == current_user.id else chat.sender_id
        
        # We only keep the most recent message for each unique user
        if other_id not in conversations_map:
            other_user = User.query.get(other_id)
            conversations_map[other_id] = {
                "user_id": other_id,
                "full_name": other_user.full_name if other_user else "Unknown",
                "profile_image": other_user.profile_image if other_user else None,
                "last_message": chat.message,
                "sent_at": chat.sent_at.isoformat(),
                "is_read": chat.is_read if chat.receiver_id == current_user.id else True,
                "sender_id": chat.sender_id
            }

    return api_response("success", data=list(conversations_map.values()))

@api_chats.route('/messages/<int:user_id>', methods=['GET'])
@token_required
def get_messages(current_user, user_id):
    """
    Returns chat history between current user and another user.
    Equivalent to the 'conversation' route in chats/routes.py
    """
    other = User.query.get_or_404(user_id)

    messages = (
        Chat.query.filter(
            or_(
                and_(Chat.sender_id == current_user.id, Chat.receiver_id == other.id),
                and_(Chat.sender_id == other.id, Chat.receiver_id == current_user.id)
            )
        )
        .order_by(Chat.sent_at.asc())
        .all()
    )

    # Mark messages as read (Reuse logic from routes.py)
    Chat.query.filter(
        Chat.sender_id == other.id,
        Chat.receiver_id == current_user.id,
        Chat.is_read == False
    ).update({"is_read": True})
    db.session.commit()

    return api_response("success", data=[{
        "id": m.id,
        "sender_id": m.sender_id,
        "message": m.message,
        "sent_at": m.sent_at.isoformat(),
        "is_read": m.is_read,
        "property_id": m.property_id
    } for m in messages])

@api_chats.route('/messages/read/<int:user_id>', methods=['POST'])
@token_required
def mark_as_read(current_user, user_id):
    """API to manually mark a conversation as read"""
    Chat.query.filter(
        Chat.sender_id == user_id,
        Chat.receiver_id == current_user.id,
        Chat.is_read == False
    ).update({"is_read": True})
    db.session.commit()
    return api_response("success", "Messages marked as read")