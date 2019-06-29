from django.db import models

# Create your models here.

class Story(models.Model):
  volumeNo=models.IntegerField()
  title=models.CharField(max_length=2048,blank=True,null=True)
  content=models.TextField(null=True,blank=True)
  footnote=models.TextField(null=True,blank=True)
  def __str__(self):
    return f"{self.volumeNo} - {self.title}"


