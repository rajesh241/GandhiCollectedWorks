from django.db import models

# Create your models here.


class Article(models.Model):
    """This is the basic class for Article"""
    title = models.CharField(max_length=2048)
    content = models.TextField(blank=True, null=True)
    footnote = models.TextField(blank=True, null=True)
    volume_number = models.IntegerField(blank=True, null=True)
    chapter_number = models.IntegerField(blank=True, null=True)
    posted = models.DateField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        """To define meta data attributes"""
        db_table = 'article'
    def __str__(self):
        """Default str method for the class"""
        return f"{self.title}"


