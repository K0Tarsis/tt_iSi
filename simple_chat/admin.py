from django.contrib import admin
from rest_framework.exceptions import ValidationError
from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import Thread, Message


class ThreadAdminForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = "__all__"

    def clean(self):
        """
        Ensures the thread has exactly 2 participants.
        """
        cleaned_data = super().clean()
        participants = cleaned_data.get("participants")

        if not participants:
            raise ValidationError("A thread must have exactly 2 participants.")

        if participants.count() != 2:
            raise ValidationError("A thread must have exactly 2 participants.")

        if Thread.objects \
                .filter(participants=participants[0]) \
                .filter(participants=participants[1]) \
                .first():
            raise ValidationError("A thread with the same participants already exists.")

        return cleaned_data


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    form = ThreadAdminForm

    list_display = ('id', 'get_participants', 'created', 'updated')
    filter_horizontal = ('participants',)
    ordering = ('-created',)

    def get_participants(self, obj):
        """
        Return a comma-separated participant list for the admin display.
        """
        return ", ".join(user.username for user in obj.participants.all())

    get_participants.short_description = "Participants"

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'thread', 'text', 'created', 'is_read')
    list_filter = ('is_read', 'created')
    search_fields = ('text', 'sender__username')


