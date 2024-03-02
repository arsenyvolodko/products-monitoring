import datetime

from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import pytz

import products_monitoring.settings
from products.models import *
from groups.views import *


# Create your views here.
def add_user_to_product_util(user_id: int, product_id: int):
    ProductMembership.objects.create(user_id=user_id, product_id=product_id)

    product_groups = Group.objects.filter(product_id=product_id).annotate(students_count=Count('students')).order_by(
        'students_count')

    if product_groups:
        group_with_least_students = product_groups.first()
    else:
        group = Group.objects.create(name='Group 1', product_id=product_id)
        add_user_to_group(user_id, group.id)
        return

    if group_with_least_students.students_count == group_with_least_students.product.maximum_group_size:
        group = Group.objects.create(name=f'Group {product_groups.count() + 1}', product_id=product_id)
        add_user_to_group(user_id, group.id)
        reorganize_groups(product_id)
        return

    add_user_to_group(user_id, group_with_least_students.id)


@api_view(['POST'])
def add_user_to_product(request, user_id: int, product_id: int):
    get_object_or_404(User, pk=user_id)
    product = get_object_or_404(Product, pk=product_id)
    if product.start_time < datetime.datetime.now().astimezone(
            tz=pytz.timezone(products_monitoring.settings.TIME_ZONE)):
        return Response(status=status.HTTP_403_FORBIDDEN, data={'error': 'This product is already started'})

    if ProductMembership.objects.filter(user_id=user_id, product_id=product_id).exists():
        return Response(status=status.HTTP_403_FORBIDDEN, data={'error': 'This user is already in this product'})

    add_user_to_product_util(user_id, product_id)
    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def get_available_products(request):
    products = Product.objects.filter(start_time__gt=datetime.datetime.now())
    product_data = {}
    for product in products:
        product_data[product.name] = {
            'name': product.name,
            'author': product.author,
            'start_time': product.start_time,
            'price': product.price,
            'lessons_number': product.lessons.count()
        }
    return Response(product_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_product_lessons(request, user_id: int, product_id: int):
    if not ProductMembership.objects.filter(user_id=user_id, product_id=product_id).exists():
        return Response(status=status.HTTP_403_FORBIDDEN)
    product = get_object_or_404(Product, pk=product_id)
    lessons = product.lessons.all()
    lessons_data = {}
    for lesson in lessons:
        lessons_data[lesson.name] = {
            'link': lesson.link
        }
    return Response(lessons_data, status=status.HTTP_200_OK)


def calculate_group_occupation_percentage(product_id: int) -> float:
    groups = Group.objects.filter(product_id=product_id)
    max_group_size = Product.objects.get(id=product_id).maximum_group_size
    groups_per = []
    for group in groups:
        groups_per.append(group.students.count() / max_group_size)
    if len(groups_per) == 0:
        return 0
    return sum(groups_per) / len(groups_per) * 100


def calculate_products_selling_percentage(product_id: int) -> float:
    users = User.objects.all()
    product_students = ProductMembership.objects.filter(product_id=product_id)
    if users.count() == 0:
        return 0
    return product_students.count() / users.count() * 100


@api_view(['GET'])
def get_products_statistics(request):
    products = Product.objects.all()
    products_data = {}
    for product in products:
        products_data[product.name] = {
            'students_number': product.clients.count(),
            'average_group_occupation': calculate_group_occupation_percentage(product.id),
            'product_selling': calculate_products_selling_percentage(product.id)
        }
    return Response(products_data, status=status.HTTP_200_OK)
