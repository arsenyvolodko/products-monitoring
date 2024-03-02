from django.urls import path

from products import views

app_name = 'products'

urlpatterns = [
    path('api/get_available_products', views.get_available_products, name='get_available_products'),
    path('api/get_product_lessons/<int:user_id>/<int:product_id>', views.get_product_lessons,
         name='get_product_lessons'),
    path('api/get_products_statistics', views.get_products_statistics, name='get_products_statistics'),
    path('api/add_user_to_product/<int:user_id>/<int:product_id>', views.add_user_to_product, name='add_user_to_product'),
]
