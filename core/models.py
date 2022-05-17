from django.conf import settings 
from django.db import models
from django.urls import reverse
from django_countries.fields import CountryField


# ярлыки для категории товара, которые будут отображаться в админке (справа), слева просто теги
# 1-й элемент создан для отображения в бд, а 2 для пользователя 


ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='Категории')
    slug = models.SlugField(max_length=255, unique=True, verbose_name='URL', db_index=True)

    class Meta:
        verbose_name = 'Категории'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category', kwargs={'cat_id': self.pk}) 


# will be in items list
class Item(models.Model):

    title = models.CharField(max_length=100)
    price = models.FloatField()
    slug = models.SlugField()
    description = models.TextField(max_length=1000)
    image = models.ImageField(verbose_name='Изображение', blank=True, upload_to='photos/&Y/&m/&d')
    time_create = models.DateField(auto_now_add =True)
    time_update = models.DateField(auto_now=True)
    cat = models.ForeignKey('Category', verbose_name='Категории', on_delete=models.PROTECT)
                                        
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.title    # возвращение title

    def get_absolute_url(self):
        return reverse('item-page', kwargs={'item_slug': self.slug})

    def get_add_to_cart(self):
        return reverse('add-to-cart', kwargs={'item_slug': self.slug})

    def remove_from_cart(self):
        return reverse('remove-from-cart', kwargs={'item_slug': self.slug})


# like intermediate between item and order, считай товар, который в переспективе должен быть в корзине
class OrderItem(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)            # сам пользователь, который делает заказ
    item = models.ForeignKey(Item, on_delete=models.CASCADE)                                # сам товар     
    quantity = models.IntegerField(default=1)                                               # количество
    ordered = models.BooleanField(default=False)                                            # галочка, где ставится закано или нет

    class Meta:
        verbose_name = 'Товары для заказа'
        verbose_name_plural = 'Товары для заказа'

    def __str__(self):  
        return f"{self.quantity} of {self.item.title}"                                      # вывод в админке названия товара и его количества, которое было добавлено в корзину

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_amount_saved(self):
        return self.get_total_item_price()

    def get_final_price(self):
        return self.get_total_item_price()

#shopping cart, store all items
class Order(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)        # ассоциация юзера с заказом 
    items = models.ManyToManyField(OrderItem)                                           # сам товар 
    start_date = models.DateTimeField(auto_now_add=True)                                # момент, когда заказ был создан
    ordered_date = models.DateTimeField()                                               # момент, когда заказ был оформлен
    ordered = models.BooleanField(default=False)                                        # галочка, где ставится закано или нет
    time_create = models.DateField(auto_now_add =True)
    time_update = models.DateField(auto_now=True)
    billing_address = models.ForeignKey('Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)    # связка с адресом
                                        
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return self.user.username

    def get_total(self):

        total = 0
        
        for order_item in self.items.all():
            total += order_item.get_final_price()
        
        return total


class Address(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)      
    last_name = models.CharField(max_length=100)
    street_address = models.CharField(max_length=100)
    street_address_optional = models.CharField(max_length=100)
    country = CountryField(multiple=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Адреса'


class Contact(models.Model):

    email = models.CharField(max_length=50)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.email