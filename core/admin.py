from django.contrib import admin
from .models import *


class ItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'image']
    list_display_links = ['id', 'title']
    search_fields = ['title', 'description']
    prepopulated_fields = {"slug": ("title", )}
   

admin.site.register(Item, ItemAdmin)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Category)
admin.site.register(Contact)