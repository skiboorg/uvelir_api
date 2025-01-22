from django.contrib import admin
from nested_inline.admin import NestedStackedInline, NestedModelAdmin
from django.utils.safestring import mark_safe
from .models import *

class SizeInline(NestedStackedInline):
    model = Size
    extra = 0

class ProductAdmin(NestedModelAdmin):
    list_display = ('image_preview','article','name','subcategory','filter','is_new','is_popular','is_active',)
    model = Product
    inlines = [SizeInline]
    readonly_fields = ['image_preview']
    list_filter = ['is_popular','is_active','null_opt_price','hidden_category']
    search_fields = ('name','subcategory__name',)

    def image_preview(self, obj):

        if obj.image:
            return mark_safe(
                '<img src="{0}" width="150" height="150" style="object-fit:contain" />'.format(obj.image.url))
        else:
            return 'Нет изображения'

    image_preview.short_description = 'Текущее изображение'

class SizeFilterInline(NestedStackedInline):
    model = SizeFilter
    extra = 0


class CategoryAdmin(NestedModelAdmin):
    list_display = ('image_preview', 'name',)
    model = SubCategory
    inlines = [SizeFilterInline]
    readonly_fields = ['image_preview']

    def image_preview(self, obj):

        if obj.image:
            return mark_safe(
                '<img src="{0}" width="150" height="150" style="object-fit:contain" />'.format(obj.image.url))
        else:
            return 'Нет изображения'

    image_preview.short_description = 'Текущее изображение'


class SubCategoryAdmin(NestedModelAdmin):
    list_display = ('name', 'category',)
    model = SubCategory



admin.site.register(Category, CategoryAdmin)
admin.site.register(Fineness)
admin.site.register(Coating)
admin.site.register(SubCategory,SubCategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(SubCategoryFilter)
admin.site.register(Material)
admin.site.register(Popular)
