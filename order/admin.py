from django.contrib import admin
from nested_inline.admin import NestedStackedInline,NestedModelAdmin
from .models import *

class OrderItemInline(NestedStackedInline):
    model = OrderItem
    extra = 0

class OrderAdmin(NestedModelAdmin):
    list_display = ('id','user__fio','user__email', 'is_paid','is_done','is_deliveried','created_at','total_price',)
    model = Order
    inlines = [OrderItemInline]
    list_filter = ('is_paid','is_done','is_deliveried',)




admin.site.register(Order,OrderAdmin)
admin.site.register(Delivery)
admin.site.register(Payment)
admin.site.register(Status)

