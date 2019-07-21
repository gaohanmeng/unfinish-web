from django.contrib import admin

from .models import Comment
from MyBlog.custom_site import custom_site
from MyBlog.base_admin import BaseOwnerAdmin


@admin.register(Comment, site=custom_site)
class CommentAdmin(BaseOwnerAdmin):
    list_display = ('target', 'nickname', 'content', 'website', 'created_time')
