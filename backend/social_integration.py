"""
Social Shopping Integration Module for Aetherstore Engine
Implements social features, community shopping, and virtual styling
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import uuid
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Friendship, SocialEvent as DBSocialEvent, GroupSession

class SocialEventType(Enum):
    FRIEND_ADDED = "friend_added"
    CHAT_MESSAGE = "chat_message"
    SHARED_ITEM = "shared_item"
    GROUP_INVITE = "group_invite"
    LIVE_SHOPPING_START = "live_shopping_start"
    LIVE_SHOPPING_END = "live_shopping_end"
    STYLE_RATING = "style_rating"
    OUTFIT_SHARE = "outfit_share"

class GroupShoppingStatus(Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class SocialEvent:
    """Represents a social event"""
    event_id: str
    event_type: SocialEventType
    user_id: str
    timestamp: str
    data: Dict
    target_user_id: Optional[str] = None

@dataclass
class GroupShoppingSession:
    """Represents a group shopping session"""
    session_id: str
    name: str
    creator_id: str
    members: List[str]
    created_at: str
    status: GroupShoppingStatus
    store_id: str
    start_time: str
    end_time: Optional[str]
    active_users: List[str]

@dataclass
class StyleRecommendation:
    """Represents a style recommendation from community"""
    recommendation_id: str
    by_user_id: str
    for_user_id: str
    product_id: str
    reason: str
    rating: float  # 1.0 to 5.0
    timestamp: str
    accepted: bool = False

class SocialManager:
    """Manages social features for Aetherstore"""
    
    def __init__(self):
        # In-memory caches for fast retrieval (synced from DB on startup)
        self.friends_list = {}
        self.group_sessions = {}
        self.social_events = []
        self.active_chats = {}
        self.room_messages = {}  # room_id -> [messages]
        self.style_recommendations = {}  # user_id -> [recommendations]
        self.live_shopping_rooms = {}  # room_id -> room_data
        self.user_presence = {}  # user_id -> {"status": "...", "last_seen": "..."}
        
        print("Social Manager initialized")
    
    def add_friend(self, user_id: str, friend_id: str) -> bool:
        """Add a friend to user's friend list and persist to DB"""
        db = SessionLocal()
        try:
            # Check if friendship already exists
            existing = db.query(Friendship).filter(
                Friendship.user_id == user_id,
                Friendship.friend_id == friend_id
            ).first()
            
            if not existing:
                new_friendship = Friendship(user_id=user_id, friend_id=friend_id)
                db.add(new_friendship)

                # Log event
                new_event = DBSocialEvent(
                    user_id=user_id,
                    target_user_id=friend_id,
                    event_type=SocialEventType.FRIEND_ADDED.value,
                    data={"initiator": user_id}
                )
                db.add(new_event)
                db.commit()

                # Update cache
                if user_id not in self.friends_list: self.friends_list[user_id] = []
                self.friends_list[user_id].append(friend_id)
                return True
        except Exception as e:
            print(f"Error adding friend: {e}")
            db.rollback()
        finally:
            db.close()
        return False
    
    def get_friends(self, user_id: str) -> List[str]:
        """Get user's friend list"""
        return self.friends_list.get(user_id, [])
    
    def create_group_shopping_session(self, name: str, creator_id: str, 
                                    members: List[str], store_id: str) -> GroupShoppingSession:
        """Create a new group shopping session and persist to DB"""
        db = SessionLocal()
        try:
            new_session = GroupSession(
                name=name,
                creator_id=creator_id,
                store_id=store_id,
                status=GroupShoppingStatus.PLANNED.value,
                settings={"members": members}
            )
            db.add(new_session)

            # Log event
            new_event = DBSocialEvent(
                user_id=creator_id,
                event_type=SocialEventType.GROUP_INVITE.value,
                data={"session_id": str(new_session.id), "members": members}
            )
            db.add(new_event)
            db.commit()

            # Create session object for return (bridging models)
            session = GroupShoppingSession(
                session_id=str(new_session.id),
                name=name,
                creator_id=creator_id,
                members=members,
                created_at=datetime.now().isoformat(),
                status=GroupShoppingStatus.PLANNED,
                store_id=store_id,
                start_time=datetime.now().isoformat(),
                end_time=None,
                active_users=[]
            )
            self.group_sessions[session.session_id] = session
            return session
        except Exception as e:
            print(f"Error creating session: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    def start_group_session(self, session_id: str) -> bool:
        """Start a group shopping session"""
        if session_id in self.group_sessions:
            session = self.group_sessions[session_id]
            session.status = GroupShoppingStatus.ACTIVE
            session.active_users = session.members.copy()
            print(f"Started group session: {session_id}")
            
            # Create social event
            event = SocialEvent(
                event_id=f"event_{uuid.uuid4().hex[:12]}",
                event_type=SocialEventType.LIVE_SHOPPING_START,
                user_id=session.creator_id,
                timestamp=datetime.now().isoformat(),
                data={"session_id": session_id, "store_id": session.store_id}
            )
            self.social_events.append(event)
            
            return True
        return False
    
    def add_style_recommendation(self, by_user_id: str, for_user_id: str, 
                               product_id: str, reason: str, rating: float) -> StyleRecommendation:
        """Add a style recommendation from one user to another"""
        recommendation_id = f"rec_{uuid.uuid4().hex[:12]}"
        
        recommendation = StyleRecommendation(
            recommendation_id=recommendation_id,
            by_user_id=by_user_id,
            for_user_id=for_user_id,
            product_id=product_id,
            reason=reason,
            rating=rating,
            timestamp=datetime.now().isoformat()
        )
        
        if for_user_id not in self.style_recommendations:
            self.style_recommendations[for_user_id] = []
        
        self.style_recommendations[for_user_id].append(recommendation)
        print(f"Added style recommendation from {by_user_id} to {for_user_id}")
        
        # Create social event
        event = SocialEvent(
            event_id=f"event_{uuid.uuid4().hex[:12]}",
            event_type=SocialEventType.STYLE_RATING,
            user_id=by_user_id,
            target_user_id=for_user_id,
            timestamp=recommendation.timestamp,
            data={
                "recommendation_id": recommendation_id,
                "product_id": product_id,
                "rating": rating
            }
        )
        self.social_events.append(event)
        
        return recommendation
    
    def share_item(self, user_id: str, item_id: str, recipients: List[str]) -> bool:
        """Share an item with friends"""
        print(f"User {user_id} shared item {item_id} with {len(recipients)} users")
        
        # Create social events for each recipient
        for recipient in recipients:
            event = SocialEvent(
                event_id=f"event_{uuid.uuid4().hex[:12]}",
                event_type=SocialEventType.SHARED_ITEM,
                user_id=user_id,
                target_user_id=recipient,
                timestamp=datetime.now().isoformat(),
                data={"item_id": item_id}
            )
            self.social_events.append(event)
        
        return True
    
    def get_user_social_events(self, user_id: str) -> List[Dict]:
        """Get social events for a user"""
        user_events = []
        
        for event in self.social_events:
            if event.user_id == user_id or (event.target_user_id and event.target_user_id == user_id):
                user_events.append({
                    "event_id": event.event_id,
                    "event_type": event.event_type.value,
                    "user_id": event.user_id,
                    "target_user_id": event.target_user_id,
                    "timestamp": event.timestamp,
                    "data": event.data
                })
        
        return user_events
    
    def join_live_shopping_room(self, room_id: str, user_id: str) -> bool:
        """Join a live shopping room"""
        if room_id not in self.live_shopping_rooms:
            self.live_shopping_rooms[room_id] = {
                "participants": [],
                "created_at": datetime.now().isoformat(),
                "active": True
            }
        
        if user_id not in self.live_shopping_rooms[room_id]["participants"]:
            self.live_shopping_rooms[room_id]["participants"].append(user_id)
            print(f"User {user_id} joined live shopping room {room_id}")
            
            # Update user presence
            self.user_presence[user_id] = {
                "status": "live_shopping",
                "room_id": room_id,
                "last_seen": datetime.now().isoformat()
            }
            
            return True
        
        return False
    
    def send_group_message(self, room_id: str, user_id: str, message: str) -> Dict:
        """Send a message in a group shopping session"""
        msg_data = {
            "id": f"msg_{uuid.uuid4().hex[:12]}",
            "room_id": room_id,
            "user_id": user_id,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        if room_id not in self.room_messages:
            self.room_messages[room_id] = []
        
        self.room_messages[room_id].append(msg_data)
        print(f"Message sent by {user_id} in room {room_id}")
        
        return msg_data
    
    def get_room_messages(self, room_id: str, limit: int = 50) -> List[Dict]:
        """Get recent messages from a room"""
        if room_id in self.room_messages:
            return self.room_messages[room_id][-limit:]
        return []

class SocialShoppingService:
    """Main service for social shopping features"""
    
    def __init__(self):
        self.social_manager = SocialManager()
        print("Social Shopping Service initialized")
    
    async def add_friend(self, user_id: str, friend_id: str) -> Dict:
        """Add a friend to user's network"""
        success = self.social_manager.add_friend(user_id, friend_id)
        
        if success:
            return {
                "success": True,
                "user_id": user_id,
                "friend_id": friend_id,
                "message": f"Successfully added {friend_id} as friend"
            }
        else:
            return {
                "success": False,
                "message": f"{friend_id} is already in your friend list"
            }
    
    async def get_friends_list(self, user_id: str) -> Dict:
        """Get user's friend list"""
        friends = self.social_manager.get_friends(user_id)
        
        return {
            "user_id": user_id,
            "friends_count": len(friends),
            "friends": friends
        }
    
    async def create_group_shopping_session(self, name: str, creator_id: str, 
                                          members: List[str], store_id: str) -> Dict:
        """Create a new group shopping session"""
        session = self.social_manager.create_group_shopping_session(
            name, creator_id, members, store_id
        )
        
        return {
            "session_id": session.session_id,
            "name": session.name,
            "creator_id": session.creator_id,
            "members": session.members,
            "store_id": session.store_id,
            "status": session.status.value,
            "message": "Group shopping session created successfully"
        }
    
    async def start_group_session(self, session_id: str) -> Dict:
        """Start a group shopping session"""
        success = self.social_manager.start_group_session(session_id)
        
        if success:
            return {
                "session_id": session_id,
                "success": True,
                "message": "Group shopping session started"
            }
        else:
            return {
                "session_id": session_id,
                "success": False,
                "message": "Session not found or could not be started"
            }
    
    async def add_style_recommendation(self, by_user_id: str, for_user_id: str, 
                                     product_id: str, reason: str, rating: float) -> Dict:
        """Add a style recommendation"""
        try:
            recommendation = self.social_manager.add_style_recommendation(
                by_user_id, for_user_id, product_id, reason, rating
            )
            
            return {
                "success": True,
                "recommendation_id": recommendation.recommendation_id,
                "by_user_id": recommendation.by_user_id,
                "for_user_id": recommendation.for_user_id,
                "product_id": recommendation.product_id,
                "rating": recommendation.rating,
                "message": "Style recommendation added successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to add style recommendation"
            }
    
    async def share_item_with_friends(self, user_id: str, item_id: str, recipients: List[str]) -> Dict:
        """Share an item with friends"""
        success = self.social_manager.share_item(user_id, item_id, recipients)
        
        return {
            "success": success,
            "user_id": user_id,
            "item_id": item_id,
            "recipients_count": len(recipients),
            "message": f"Item shared with {len(recipients)} friends" if success else "Failed to share item"
        }
    
    async def get_user_social_activity(self, user_id: str) -> Dict:
        """Get user's social activity"""
        events = self.social_manager.get_user_social_events(user_id)
        friends = self.social_manager.get_friends(user_id)
        
        return {
            "user_id": user_id,
            "friends_count": len(friends),
            "recent_events_count": len(events),
            "recent_events": events[-10:],  # Last 10 events
            "friends": friends[:20]  # First 20 friends
        }
    
    async def join_live_shopping_session(self, room_id: str, user_id: str) -> Dict:
        """Join a live shopping session"""
        success = self.social_manager.join_live_shopping_room(room_id, user_id)
        
        if success:
            return {
                "success": True,
                "room_id": room_id,
                "user_id": user_id,
                "message": "Joined live shopping session successfully"
            }
        else:
            return {
                "success": False,
                "message": "Failed to join live shopping session"
            }
    
    async def send_group_message(self, room_id: str, user_id: str, message: str) -> Dict:
        """Send a message in a group session"""
        msg_data = self.social_manager.send_group_message(room_id, user_id, message)
        
        return {
            "success": True,
            "message_id": msg_data["id"],
            "room_id": room_id,
            "user_id": user_id,
            "message": message,
            "timestamp": msg_data["timestamp"]
        }
    
    async def get_group_messages(self, room_id: str, limit: int = 10) -> Dict:
        """Get messages from a group session"""
        messages = self.social_manager.get_room_messages(room_id, limit)
        
        return {
            "room_id": room_id,
            "message_count": len(messages),
            "messages": messages,
            "limit": limit
        }

# Example usage
async def main():
    social_service = SocialShoppingService()
    
    # Add friends
    friend_result = await social_service.add_friend("user_123", "user_456")
    print("Friend Add Result:")
    print(json.dumps(friend_result, indent=2))
    
    # Create group shopping session
    session_result = await social_service.create_group_shopping_session(
        "Fashion Friday", 
        "user_123", 
        ["user_456", "user_789"], 
        "store_abc"
    )
    print("\nGroup Session Creation Result:")
    print(json.dumps(session_result, indent=2))
    
    # Add style recommendation
    style_result = await social_service.add_style_recommendation(
        "user_456", "user_123", "item_xyz", "This matches your style!", 4.5
    )
    print("\nStyle Recommendation Result:")
    print(json.dumps(style_result, indent=2))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())