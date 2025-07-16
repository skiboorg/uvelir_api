from rest_framework import exceptions, serializers, status, generics
from django.db.models import Min, Avg, Sum

from .models import *
class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'

class CoatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coating
        fields = '__all__'

class FinenessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fineness
        fields = '__all__'

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'
class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = '__all__'



class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'

class ProductShortSerializer(serializers.ModelSerializer):
    cat_slug = serializers.SerializerMethodField()
    subcat_slug = serializers.SerializerMethodField()
    subcat_name = serializers.SerializerMethodField()
    subcat_text = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    min_price_opt = serializers.SerializerMethodField()
    avg_weight = serializers.SerializerMethodField()
    items_count = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    coating = CoatingSerializer(many=False, required=False, read_only=True)
    fineness = FinenessSerializer(many=False, required=False, read_only=True)
    material = MaterialSerializer(many=False, required=False, read_only=True)
    images = ProductImageSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'image',
            'cat_slug', 'subcat_name', 'subcat_slug', 'subcat_text',
            'is_new', 'article', 'is_popular', 'is_active', 'is_in_stock',
            'coating', 'fineness', 'material',
            'min_price', 'min_price_opt', 'avg_weight',
            'items_count', 'has_garniture', 'images'
        ]

    def get_image(self, obj):
        main_image = obj.images.filter(is_main=True).first()
        return main_image.file.url if main_image else None

    def get_items_count(self, obj):
        return obj.sizes.aggregate(total=Sum('quantity'))['total']

    def get_min_price(self, obj):
        return obj.sizes.aggregate(min_price=Min('price'))['min_price']

    def get_min_price_opt(self, obj):
        return obj.sizes.aggregate(min_price=Min('price_opt'))['min_price']

    def get_avg_weight(self, obj):
        return obj.sizes.aggregate(avg_weight=Avg('avg_weight'))['avg_weight']

    def get_cat_slug(self, obj):
        if obj.subcategory and obj.subcategory.category:
            return obj.subcategory.category.slug
        return None

    def get_subcat_slug(self, obj):
        if obj.subcategory:
            return obj.subcategory.slug
        return None

    def get_subcat_name(self, obj):
        if obj.subcategory:
            return obj.subcategory.name
        return None

    def get_subcat_text(self, obj):
        if obj.subcategory:
            return obj.subcategory.short_description
        return None


class ProductSerializer(serializers.ModelSerializer):
    sizes = SizeSerializer(many=True,required=False,read_only=True)
    coating = CoatingSerializer(many=False,required=False,read_only=True)
    fineness = FinenessSerializer(many=False,required=False,read_only=True)
    material = MaterialSerializer(many=False,required=False,read_only=True)
    cat_slug = serializers.SerializerMethodField()
    cat_name = serializers.SerializerMethodField()
    subcat_slug = serializers.SerializerMethodField()
    subcat_name = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    min_price_opt = serializers.SerializerMethodField()
    avg_weight = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True,required=False,read_only=True)

    garniture_products = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'
    def get_image(self, obj):
        if obj.images.filter(is_main=True):
            return obj.images.filter(is_main=True).first().file.url
        else:
            return None
    def get_cat_slug(self,obj):
        return obj.subcategory.category.slug
    def get_cat_name(self,obj):
        return obj.subcategory.category.name
    def get_subcat_slug(self,obj):
        return obj.subcategory.slug

    def get_subcat_name(self,obj):
        return obj.subcategory.name

    def get_min_price(self, obj):
        # Получаем минимальное значение price из связанных объектов Size
        return obj.sizes.aggregate(min_price=Min('price'))['min_price']
    def get_min_price_opt(self, obj):
        # Получаем минимальное значение price из связанных объектов Size
        return obj.sizes.aggregate(min_price=Min('price_opt'))['min_price']

    def get_avg_weight(self, obj):
        # Получаем среднее значение avg_weight из связанных объектов Size
        return obj.sizes.aggregate(avg_weight=Avg('avg_weight'))['avg_weight']

    def get_garniture_products(self, obj):
        """ Получает список товаров, указанных в garniture_set_uuids """
        if not obj.garniture_set_uuids:
            return []

        # Разбиваем строку на список UID
        product_uids = [uid.strip() for uid in obj.garniture_set_uuids.split(",") if uid.strip()]

        # Находим товары по UID
        products = Product.objects.filter(uid__in=product_uids)

        # Сериализуем найденные товары
        return ProductShortSerializer(products, many=True, context=self.context).data

class SubCategoryFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategoryFilter
        fields = '__all__'

class SubcategorySizeFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubcategorySizeFilter
        fields = '__all__'

class SubCategorySerializer(serializers.ModelSerializer):
    #products = ProductSerializer(many=True, required=False, read_only=True)
    size_filters = SubCategoryFilterSerializer(many=True, required=False, read_only=True)
    products = serializers.SerializerMethodField()
    class Meta:
        model = SubCategory
        fields = '__all__'

    def get_products(self, obj):
        active_products = obj.products.filter(is_active=True)
        return ProductShortSerializer(active_products, many=True).data

class SizeFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = SizeFilter
        fields = ['id','size','is_active']

class CategorySerializer(serializers.ModelSerializer):
    size_filters = SizeFilterSerializer(many=True, required=False, read_only=True)
    #sub_categories = SubCategorySerializer(many=True, required=False, read_only=True)
    sub_categories = serializers.SerializerMethodField()
    coatings = CoatingSerializer(many=True, required=False, read_only=True)
    materials = MaterialSerializer(many=True, required=False, read_only=True)
    def get_sub_categories(self,obj):
        qs = SubCategory.objects.filter(category=obj, is_active=True)
        return SubCategoryNoProductsSerializer(qs, many=True).data
    class Meta:
        model = Category
        fields = '__all__'

class SubCategoryNoProductsSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubCategory
        fields = ['id','name','slug']


class CategoryShortSerializer(serializers.ModelSerializer):
    #sub_categories = SubCategoryNoProductsSerializer(many=True, required=False, read_only=True)
    sub_categories = serializers.SerializerMethodField()

    def get_sub_categories(self,obj):
        qs = SubCategory.objects.filter(category=obj, is_active=True)
        return SubCategoryNoProductsSerializer(qs, many=True).data
    class Meta:
        model = Category
        fields = ['sub_categories','id','name','slug','image','icon','items_count']



class SubCategoryShortSerializer(serializers.ModelSerializer):
    #products = ProductShortSerializer(many=True, required=False, read_only=True)
    products = serializers.SerializerMethodField()
    class Meta:
        model = SubCategory
        fields = '__all__'
    def get_products(self, obj):
        active_products = obj.products.filter(is_active=True)
        return ProductSerializer(active_products, many=True).data




class FavoriteSerializer(serializers.ModelSerializer):
    product = ProductShortSerializer(many=False, read_only=True)
    class Meta:
        model = Favorite
        fields = '__all__'

