from django.db import models
from django.contrib.auth.models import User


class AIRequest(models.Model):
    TASK_CHOICES = [
        ('sentiment', 'Sentiment Analysis'),
        ('summary', 'Summarization'),
        ('image', 'Image Generation'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task_type = models.CharField(max_length=20, choices=TASK_CHOICES)
    input_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.task_type}'


class AIResponse(models.Model):
    request = models.OneToOneField(
        AIRequest,
        on_delete=models.CASCADE,
        related_name='response'
    )
    output_text = models.TextField(blank=True, null=True)
    image_base64 = models.TextField(blank=True, null=True)
    raw_response = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Response for request {self.request.id}'
