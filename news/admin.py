from django.contrib import admin
from nested_inline.admin import NestedStackedInline, NestedModelAdmin
from django.utils.safestring import mark_safe
from .models import *

class ContentBlockInline(NestedStackedInline):
    model = ContentBlock
    extra = 0

class NewsItemAdmin(NestedModelAdmin):
    model = NewsItem
    inlines = [ContentBlockInline]


admin.site.register(Tag)
admin.site.register(ContentBlockType)
admin.site.register(NewsItem, NewsItemAdmin)