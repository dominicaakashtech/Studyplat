from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class StudyGroup(models.Model):
    name = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    members = models.ManyToManyField(User, related_name='joined_groups', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    max_members = models.IntegerField(default=50)
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']

class Resource(models.Model):
    RESOURCE_TYPES = [
        ('document', 'Document'),
        ('link', 'Link'),
        ('note', 'Note'),
    ]
    
    study_group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='resources/', blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-uploaded_at']

class Message(models.Model):
    study_group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"

    class Meta:
        ordering = ['sent_at']

class StudySession(models.Model):
    study_group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='sessions')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    scheduled_time = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['scheduled_time']