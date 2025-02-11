from django.db.models import Q
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Thread, Message

User = get_user_model()


class ThreadSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True
    )

    class Meta:
        model = Thread
        fields = ['id', 'participants', 'created', 'updated']

    def validate_participants(self, value):
        """Ensure only two users are in a thread."""
        request = self.context.get('request')

        if len(value) != 2:
            raise serializers.ValidationError("A thread must have exactly 2 participants.")

        if request.user not in value:
            raise serializers.ValidationError("You cannot create a thread with yourself.")

        return value

    def save(self, **kwargs):
        existing_thread = Thread.objects.filter(participants=self.validated_data['participants'][0]) \
            .filter(participants=self.validated_data['participants'][1]).first()

        if existing_thread:
            return existing_thread

        thread = Thread.objects.create()
        thread.participants.set(self.validated_data['participants'])
        thread.save()
        return thread


class ThreadMessagesSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=False)
    thread = serializers.PrimaryKeyRelatedField(queryset=Thread.objects.all(), many=False)

    class Meta:
        model = Message
        fields = ['id', 'thread', 'sender', 'text', 'created', 'is_read']
        read_only_fields = ['id', 'thread', 'sender', 'text', 'created', 'is_read']


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.HiddenField(default=serializers.CurrentUserDefault())
    thread = serializers.PrimaryKeyRelatedField(queryset=Thread.objects.all(), many=False)

    class Meta:
        model = Message
        fields = ['id', 'thread', 'sender', 'text']

    def validate_sender(self, value):
        """Ensure sender is part of the thread."""
        thread_id = self.initial_data.get('thread')
        thread = Thread.objects.get(id=thread_id)

        if not thread or value not in thread.participants.all():
            raise serializers.ValidationError("Sender must be a participant in the thread.")
        return value