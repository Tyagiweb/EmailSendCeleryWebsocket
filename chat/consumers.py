# import json
# from channels.generic.websocket import AsyncWebsocketConsumer

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.accept()
#         await self.send(text_data=json.dumps({
#             "message": "WebSocket connection established!"
#         }))

#     async def disconnect(self, close_code):
#         print("Disconnected")

#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         message = data.get("message", "")
#         await self.send(text_data=json.dumps({
#             "response": f"You said: {message}"
#         }))



import json
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from .models import Room

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        query_params = parse_qs(self.scope["query_string"].decode())
        token = query_params.get("token", [None])[0]
        room_id = query_params.get("room_id", [None])[0]

        if not token or not room_id:
            await self.close()
            return

        try:
            access_token = AccessToken(token)
            user_id = access_token["user_id"]

            user = await self.get_user(user_id)
            room = await self.get_room(room_id)
            
            if user is None or room is None:
                await self.close()
                return

            is_user_in_room = await self.is_user_in_room(user, room)

            if not is_user_in_room:
                await self.close()
                return

            self.scope["user"] = user
            self.room_id = room_id
            self.room_group_name = f"chat_{room_id}"

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )


            await self.accept()
            await self.send(text_data=json.dumps({
                "message": f"Connected to chat room {room_id}"
            }))

        except Exception as e:
            print(f"Connection error: {e}")
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        print("Disconnected")



    # async def receive(self, text_data):
    #     data = json.loads(text_data)
    #     message = data.get("message")

    #     if message:
    #         await self.channel_layer.group_send(
    #             self.room_group_name,
    #             {
    #                 "type": "chat_message",
    #                 "message": message,
    #                 "user": self.scope["user"].username,
    #                 "sender_channel": self.channel_name,  # Add sender channel name
    #             }
    #         )




    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message")

        if message:
            user = self.scope["user"]
            room_id = self.room_id

            # Append message to DB
            await self.append_message(room_id, user, message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "user": user.username,
                    "sender_channel": self.channel_name,
                }
            )



    async def chat_message(self, event):
        if self.channel_name == event.get("sender_channel"):
            return
        await self.send(text_data=json.dumps({
            "user": event["user"],
            "message": event["message"]
        }))

    @database_sync_to_async
    def append_message(self, room_id, user, message):
        room = Room.objects.get(id=room_id)
        chat_history = room.chat or []

        # Determine role: 'user' or 'reviewer'
        role = 'user' if user == room.user else 'reviewer'

        chat_history.append({role: message})
        room.chat = chat_history
        room.save()


    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def get_room(self, room_id):
        try:
            return Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return None

    @database_sync_to_async
    def is_user_in_room(self, user, room):
        return room.user == user or room.reviewer == user



# #For video call
# class SignalingConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_name = "test_room"  # fixed room for demo
#         self.room_group_name = f"signaling_{self.room_name}"

#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#         await self.accept()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         # Broadcast to group except sender
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 "type": "signaling.message",
#                 "message": data,
#                 "sender_channel": self.channel_name,
#             }
#         )

#     async def signaling_message(self, event):
#         if self.channel_name != event["sender_channel"]:
#             await self.send(text_data=json.dumps(event["message"]))
