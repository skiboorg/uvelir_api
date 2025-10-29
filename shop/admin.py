from django.contrib import admin
from nested_inline.admin import NestedStackedInline, NestedModelAdmin
from django.utils.safestring import mark_safe
from .models import *
from django.utils.html import format_html
from django.db.models import Sum

class SizeInline(NestedStackedInline):
    model = Size
    extra = 0


class ImageInline(NestedStackedInline):
    model = ProductImage
    extra = 0


class FinenessGemInline(NestedStackedInline):
    model = FinenessGem
    extra = 0


class ProductAdmin(NestedModelAdmin):
    list_display = ('image_preview','article','name','total_quantity','has_garniture','product_url','subcategory','filter','is_new','is_popular','is_active',)
    model = Product
    inlines = [SizeInline,ImageInline]
    readonly_fields = ['image_preview']
    list_filter = ['is_popular','is_active','null_opt_price','hidden_category','has_garniture']
    search_fields = ('name','subcategory__name','uid')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(total_quantity_sum=Sum('sizes__quantity'))

    def total_quantity(self, obj):
        return obj.total_quantity_sum or 0  # Показываем 0, если None

    total_quantity.admin_order_field = 'total_quantity_sum'

    total_quantity.short_description = 'Остаток'

    def product_url(self, obj):
        # Генерация URL и добавление кнопки для копирования
        url = obj.get_product_url()
        html = f'''
                    <input type="text" value="{url}" readonly style="width: 300px;">
                    <button onclick="copyToClipboard('{url}'); return false;">Копировать</button>
                    <script>
                        function copyToClipboard(text) {{
                            navigator.clipboard.writeText(text).then(function() {{
                                alert('URL скопирован в буфер обмена!');
                            }}, function(err) {{
                                console.error('Ошибка при копировании URL: ', err);
                            }});
                        }}
                    </script>
                '''
        return mark_safe(html)
    def image_preview(self, obj):

        if obj.images.filter(is_main=True).first():
            return mark_safe(
                '<img src="{0}" width="150" height="150" style="object-fit:contain" />'.format(obj.images.filter(is_main=True).first().file.url))
        else:
            return 'Нет изображения'

    image_preview.short_description = 'Текущее изображение'

class SizeFilterInline(NestedStackedInline):
    model = SizeFilter
    extra = 0

class SubcategorySizeFilterInline(NestedStackedInline):
    model = SubcategorySizeFilter
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
    inlines = [SubcategorySizeFilterInline]


class PromoItemInline(NestedStackedInline):
    model = PromoItem
    extra = 0


class PromoAdmin(NestedModelAdmin):
    list_display = ('name', )
    model = Promo
    inlines = [PromoItemInline]

class SelectionItemInline(NestedStackedInline):
    model = SelectionItem
    extra = 0

class SelectionAdmin(NestedModelAdmin):
    list_display = ('name', )
    model = Selection
    inlines = [SelectionItemInline]


class FinenessAdmin(NestedModelAdmin):
    list_display = ('label', )
    model = Fineness
    inlines = [FinenessGemInline]

class GemInline(NestedStackedInline):
    model = Gem
    extra = 0

class GemGroupAdmin(NestedModelAdmin):
    list_display = ('label', )
    model = GemGroup
    inlines = [GemInline]

class GemAdmin(NestedModelAdmin):
    list_display = ('label', )
    search_fields = ('uid',)
    model = Gem

admin.site.register(Category, CategoryAdmin)
admin.site.register(Fineness,FinenessAdmin)
admin.site.register(Coating)
admin.site.register(Gem,GemAdmin)
admin.site.register(GemGroup)
admin.site.register(SubCategory,SubCategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(SubCategoryFilter)
admin.site.register(Material)
admin.site.register(Popular)
admin.site.register(Banner)
admin.site.register(Promo, PromoAdmin)
admin.site.register(Selection, SelectionAdmin)
admin.site.register(SEOPage)
