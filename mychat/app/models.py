from django.db import models

# Create your models here.
class ScrapedData(models.Model):
    url = models.URLField()
    content = models.TextField()