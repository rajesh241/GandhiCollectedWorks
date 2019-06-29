from django.contrib import admin
from .models import Story
# Register your models here.

class StoryModelAdmin(admin.ModelAdmin):
  list_display=["volumeNo","title"]
  list_filter=["volumeNo"]
  search_fields=["title"]
  class Meta:
    model=Story
admin.site.register(Story,StoryModelAdmin)

