from django.urls import URLPattern, path
from core.views import *

urlpatterns = [
    path('', HomePage.as_view(), name='home-page'),
    path('item-page/<slug:item_slug>/', item_page, name='item-page'),
    path('add-to-cart/<slug:item_slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug:item_slug>/', remove_from_cart, name='remove-from-cart'),
    path('summary-page/', OrderSummaryView.as_view(), name='summary-page'),
    path('remove-single-item-from-cart/<slug:item_slug>/', remove_single_item_from_cart, name='remove-single-item-from-cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout-page'),
    #path('search/', Search.as_view(), name='search')
    path('category/<int:cat_id>/', show_category, name='category'),
    path('items/', get_items, name='items-page'),
    path("search/", Search.as_view(), name='search'),
    path('contact/', ContactView.as_view(), name='contact')
]