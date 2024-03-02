from django.db import models

from groups.models import Group
from users.models import User

# from groups.models import Group


class Product(models.Model):
    name = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    price = models.FloatField()
    clients = models.ManyToManyField(User, through='ProductMembership')

    _minimum_group_size = 2
    _maximum_group_size = 3

    @property
    def minimum_group_size(self):
        return self._minimum_group_size

    @minimum_group_size.setter
    def minimum_group_size(self, value):
        self._minimum_group_size = value
        self._update_group_size_limits(minimum=value)

    @property
    def maximum_group_size(self):
        return self._maximum_group_size

    @maximum_group_size.setter
    def maximum_group_size(self, value):
        self._maximum_group_size = value
        self._update_group_size_limits(maximum=value)

    def _update_group_size_limits(self, minimum=minimum_group_size, maximum=maximum_group_size):
        self._minimum_group_size = minimum
        self._maximum_group_size = maximum
        from groups.views import reorganize_groups
        reorganize_groups(self.id)

    def __str__(self):
        return self.name


class ProductMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user} - {self.product}'


class Lesson(models.Model):
    name = models.CharField(max_length=100)
    link = models.URLField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='lessons')

    def __str__(self):
        return self.name
