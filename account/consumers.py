from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import *
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat_group_name = f'chat_{self.chat_id}'

        # Join the chat group
        await self.channel_layer.group_add(
            self.chat_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the chat group
        await self.channel_layer.group_discard(
            self.chat_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')

        if message_type == 'message':
            # Handle sending a new message
            message = text_data_json['message']
            sender = text_data_json['sender']

            # Save the message to the database
            sender_obj = await sync_to_async(User.objects.get)(username=sender)
            chat = await sync_to_async(Chat.objects.get)(id=self.chat_id)
            message_obj = await sync_to_async(Message.objects.create)(
                chat=chat,
                sender=sender_obj,
                content=message
            )

            # Broadcast the message to the chat group
            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': sender,
                    'message_id': message_obj.id,
                }
            )

        elif message_type == 'read_receipt':
            # Handle read receipts
            message_id = text_data_json['message_id']
            message = await sync_to_async(Message.objects.get)(id=message_id)
            message.read = True
            await sync_to_async(message.save)()

            # Broadcast the read receipt to the chat group
            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    'type': 'read_receipt',
                    'message_id': message_id,
                }
            )


    async def chat_message(self, event):
        # Send the message to the WebSocket
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'sender': event['sender'],
            'message_id': event['message_id'],
        }))

    async def read_receipt(self, event):
        # Send the read receipt to the WebSocket
        await self.send(text_data=json.dumps({
            'type': 'read_receipt',
            'message_id': event['message_id'],
        }))