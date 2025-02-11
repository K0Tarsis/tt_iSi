from django.contrib.auth import get_user_model
from django.db import models
from django.core.exceptions import ValidationError

User = get_user_model()


class Thread(models.Model):
    participants = models.ManyToManyField(User)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def clean(self):
        """Ensure a thread does not have more than 2 participants."""
        if self.pk and self.participants.count() != 2:
            raise ValidationError("A thread can have at most 2 participants.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Thread between {', '.join(user.username for user in self.participants.all())}"


class Message(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)


    def clean(self):
        if self.sender and self.thread and self.sender not in self.thread.participants.all():
            raise ValidationError("The sender must be a participant of the selected thread.")


    def __str__(self):
        return f"Message from {self.sender.username}: {self.text[:20]}..."
