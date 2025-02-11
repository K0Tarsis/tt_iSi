from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import Thread, Message
from .serializers import ThreadSerializer, MessageSerializer, ThreadMessagesSerializer


class ThreadListCreateView(generics.ListCreateAPIView):
    """
    GET: List all threads of the authenticated user.
    POST: Create a new thread (or return existing one).
    """
    serializer_class = ThreadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Thread.objects.filter(participants=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ThreadDeleteView(generics.DestroyAPIView):
    """Delete a thread if the user is a participant or a superuser."""
    queryset = Thread.objects.all()
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        thread = self.get_object()

        if request.user not in thread.participants.all() and not request.user.is_superuser:
            return Response({"error": "You are not a participant in this thread."}, status=status.HTTP_403_FORBIDDEN)

        thread.delete()
        return Response({"message": "Thread deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class MessageListView(generics.ListAPIView):
    """Retrieve messages for a thread."""
    serializer_class = ThreadMessagesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        thread_id = self.kwargs['thread_id']
        if self.request.user.is_superuser:
            return Message.objects.filter(thread_id=thread_id).order_by('created')
        else:
            return Message.objects.filter(thread_id=thread_id, thread__participants=self.request.user).order_by('created')

class MessageCreateView(generics.CreateAPIView):
    """Create message."""
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data={"text": request.data['text'], "thread": request.data['thread'], "sender": request.user}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MarkMessageAsReadView(APIView):
    """Mark a message as read."""
    permission_classes = [IsAuthenticated]

    def post(self, request, message_id):
        message = Message.objects.filter(id=message_id, thread__participants=request.user).first()

        if not message:
            return Response({"error": "Message not found or access denied."}, status=status.HTTP_403_FORBIDDEN)

        message.is_read = True
        message.save()

        return Response({"message": "Message marked as read."}, status=status.HTTP_200_OK)


class UnreadMessagesCountView(APIView):
    """Retrieve the count of unread messages for the authenticated user."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        unread_count = Message.objects.filter(thread__participants=request.user, is_read=False).exclude(sender=request.user).count()
        return Response({"unread_messages": unread_count}, status=status.HTTP_200_OK)

