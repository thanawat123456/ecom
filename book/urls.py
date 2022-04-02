from django.contrib import admin
from django.urls import path, re_path
from django.contrib.auth.decorators import login_required
from . import views


urlpatterns = [
    #path('', views.index, name='index'),
    path('', login_required(views.BookListView.as_view(), login_url='/login'), name='index'),
    # path('detail/<slug:slug>/', views.detail, name='detail'),
    path('detail/<slug:slug>/', views.BookDetailView.as_view(), name='detail'),
    re_path(r'add/$', views.book_add, name='book_add'),
    path('about/', views.About, name='about'),
    path('checkout/', views.checkout, name='checkout'),
    re_path(r'cart/add/(?P<slug>[\w-]+)/$', views.cart_add, name='cart_add'),
    path('contact/', views.Contact, name='contact'),
    path('service/', views.Service, name='service'),
    re_path(r'cart/delete/(?P<slug>[\w-]+)/$', views.cart_delete, name='cart_delete'),
    re_path(r'cart/list/$', views.cart_list, name='cart_list'),
    re_path(r'cart/checkout/$', views.cart_checkout, name='cart_checkout'),
]
