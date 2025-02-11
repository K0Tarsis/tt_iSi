from django.urls import path
from .views import (
    ThreadListCreateView, ThreadDeleteView,
    MarkMessageAsReadView,
    UnreadMessagesCountView,
    MessageView
)

urlpatterns = [
    path('threads/', ThreadListCreateView.as_view(), name='thread-list-create'),
    path('threads/<int:pk>/', ThreadDeleteView.as_view(), name='thread-delete'),
    path('messages/<int:message_id>/read/', MarkMessageAsReadView.as_view(), name='mark-message-as-read'),
    path('messages/unread-count/', UnreadMessagesCountView.as_view(), name='unread-messages-count'),
    path("threads/<int:thread_id>/messages/", MessageView.as_view(), name="message-list-create"),

]
