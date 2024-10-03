from rest_framework import exceptions, serializers, status, generics


from .models import *

class CoatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coating
        fields = '__all__'

class FinenessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fineness
        fields = '__all__'
class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    sizes = SizeSerializer(many=True,required=False,read_only=True)
    coating = CoatingSerializer(many=False,required=False,read_only=True)
    fineness = FinenessSerializer(many=False,required=False,read_only=True)
    cat_slug = serializers.SerializerMethodField()
    cat_name = serializers.SerializerMethodField()
    subcat_slug = serializers.SerializerMethodField()
    subcat_name = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = '__all__'
    def get_cat_slug(self,obj):
        return obj.subcategory.category.slug
    def get_cat_name(self,obj):
        return obj.subcategory.category.name
    def get_subcat_slug(self,obj):
        return obj.subcategory.slug

    def get_subcat_name(self,obj):
        return obj.subcategory.name

class ProductShortSerializer(serializers.ModelSerializer):
    cat_slug = serializers.SerializerMethodField()
    subcat_slug = serializers.SerializerMethodField()
    subcat_name = serializers.SerializerMethodField()
    subcat_text = serializers.SerializerMethodField()
    coating = CoatingSerializer(many=False, required=False, read_only=True)
    fineness = FinenessSerializer(many=False, required=False, read_only=True)
    class Meta:
        model = Product
        fields = ['name',
                  'slug',
                  'image',
                  'cat_slug',
                  'subcat_name',
                  'subcat_slug',
                  'subcat_text',
                  'is_new',
                  'article',
                  'is_popular',
                  'is_active',
                  'is_in_stock',
                  'coating',
                  'fineness'
                  ]
    def get_cat_slug(self,obj):
        return obj.subcategory.category.slug
    def get_subcat_slug(self,obj):
        return obj.subcategory.slug
    def get_subcat_name(self,obj):
        return obj.subcategory.name
    def get_subcat_text(self,obj):
        return obj.subcategory.short_description


class SubCategorySerializer(serializers.ModelSerializer):
    #products = ProductSerializer(many=True, required=False, read_only=True)
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
        fields = ['id','size']

class CategorySerializer(serializers.ModelSerializer):
    size_filters = SizeFilterSerializer(many=True, required=False, read_only=True)
    sub_categories = SubCategorySerializer(many=True, required=False, read_only=True)
    class Meta:
        model = Category
        fields = '__all__'

class CategoryShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name','slug','image']

class SubCategoryShortSerializer(serializers.ModelSerializer):
    #products = ProductShortSerializer(many=True, required=False, read_only=True)
    products = serializers.SerializerMethodField()
    class Meta:
        model = SubCategory
        fields = '__all__'
    def get_products(self, obj):
        active_products = obj.products.filter(is_active=True)
        return ProductSerializer(active_products, many=True).data








