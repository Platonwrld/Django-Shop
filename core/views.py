from django.shortcuts import get_object_or_404, render, redirect
from requests import request

from core.tasks import send_spam_email
from .models import *
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, ListView, CreateView
from django.core.exceptions import ObjectDoesNotExist
from .forms import *
from django.db.models import Q
from django.http import Http404
from django.http import HttpResponse
from django.core.paginator import Paginator
from .service import *
# from .tasks import send_spam_email


menu = [{'title': 'It-Ground', 'url_name': 'home_page'},
        {'title1': 'Товары', 'url_name': 'about_view'},
        {'title2': 'Категории', 'url_name': 'check_products'}]
        

class HomePage(ListView):
    model = Item      
    template_name = 'home_page.html'
    paginate_by = 6
    context_object_name = 'items'       
    extra_context = {'title': 'Главная страница'} 

     # функция формирует статический и динамический контекст, который далее передается в шаблон
    def get_context_data(self, *args, **kwargs):

        context = super().get_context_data(**kwargs)       

        # добавление новой переменной в контекст
        context['menu'] = menu 
        context['cat_selected'] = 0

        return context


class Search(ListView):

    model = Item

    template_name = 'items_page.html'
    paginate_by = 6
    context_object_name = 'items' 

    def get_queryset(self):
        return Item.objects.filter(title__icontains=self.request.GET.get("q"))

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["q"] = f'q={self.request.GET.get("q")}&'
        return context




def item_page(request, item_slug):

    item = get_object_or_404(Item, slug=item_slug)
    
    context = {
        'item': item,
        'title': item.title,
        'cat_selected': 0,
    }

    return render(request, 'item_page.html', context=context)


def add_to_cart(request, item_slug):
    
    item = get_object_or_404(Item, slug=item_slug)

    order_item, created = OrderItem.objects.get_or_create(item=item, user=request.user, ordered=False)

    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, 'Your item was updated!')
        else:
            messages.info(request, 'Your item was added to your cart!') 
            order.items.add(order_item)
            return redirect('summary-page')
    else:
        ordered_date = timezone.now()                                                       
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)          
        order.items.add(order_item)
        messages.info(request, 'Your item was added to your cart!')                                                         
    return redirect('summary-page') 


def remove_from_cart(request, item_slug):

    item = get_object_or_404(Item, slug=item_slug)

    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]

        if order.items.filter(item__slug=item.slug).exists():                                  
            
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            order.items.remove(order_item)
            
            messages.info(request, 'Your item was successfully removed from your cart!')
            return redirect('summary-page')
        
        else:
            messages.info(request, 'Your item was not in your cart')
            return redirect('summary-page')                                                                   
    
    else:   
        messages.info(request, 'Your do not have an active order')                                                                                
        return redirect('summary-page') 


class OrderSummaryView(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):

        try:
            order = Order.objects.get(user=self.request.user, ordered=False)

            context = {
                'object': order,
                'menu': menu,               
            }

            return render(self.request, 'summary_page.html', context)

        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


def remove_single_item_from_cart(request, item_slug):

    item = get_object_or_404(Item, slug=item_slug)
    
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order

        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect('summary-page') 
        
        else:
            messages.info(request, "This item was not in your cart")
            return redirect('summary-page', item_slug) 
    
    else:
        messages.info(request, "You do not have an active order")
        return redirect('summary-page', item_slug) 


class CheckoutView(View):

    # метод get
    def get(self, *args, **kwargs):
        
        form = CheckoutForms()  # получение формы 
        order = Order.objects.get(user=self.request.user, ordered=False)

        context = {
            'forms': form,
            'order': order,
        }

        return render(self.request, 'checkout_page.html', context=context)

    # метод post
    def post(self, *args, **kwargs):

        form = CheckoutForms(self.request.POST or None)  # получение формы (либо запрос Post, лиюо никакого)
    
        # попытка получить заказ определенного юзера
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)        # получяения заказа

            if form.is_valid():     # проверка полученных данных на валидность
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                email = form.cleaned_data.get('email')
                street_address = form.cleaned_data.get('street_address')
                street_address_optional = form.cleaned_data.get('street_address_optional')
                country = form.cleaned_data.get('country')
                # same_billing_address = form.cleaned_data.get('same_billing_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_options = form.cleaned_data.get('payment_options')

                billing_address = Address(
                    user = self.request.user,
                    street_address = street_address,
                    street_address_optional = street_address_optional,
                    country = country,
                )

                billing_address.save()

                order.billing_address = billing_address
                order.save()

                return redirect('checkout-page')

        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("summary-page")

        context = {
            'forms': form,
        }

        return render(self.request, 'checkout_page.html', context=context)


def show_category(request, cat_id):

    items = Item.objects.filter(cat_id=cat_id)
    categories = Category.objects.all()
 
    if len(items) == 0:
        raise Http404


    context = {
        'items': items,
        'menu': menu,
        'title': 'Отображение по категориям',
        'cats': categories,
        'cat_selected': cat_id,
    }

    return render(request, 'items_page.html', context=context)


def get_items(request):
    
    items = Item.objects.all()
    cats = Category.objects.all()
 
    context = {
        'items': items,
        'menu': menu,
        'title': 'Товары',
        'cats': cats,
        'title': 'Категории',
        'cat_selected': 0,
    }
 
    return render(request, 'items_page.html', context=context)


class ContactView(CreateView):

    model = Contact
    form_class = ContactForm
    template_name = 'emailsp.html'
    success_url = '/'

    def form_valid(self, form):

        form.save()
        # send(form.instance.email)
        send_spam_email.delay(form.instance.email)      # delay сообщает, что надо запустить таск и идти далее по программе, не дожидаясь результата

        return super().form_valid(form)