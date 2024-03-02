from django.db import models

from users.models import User


# Create your models here.
class Group(models.Model):
    name = models.CharField(max_length=100)
    students = models.ManyToManyField(User, through='GroupMembership')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE,
                                related_name='groups')

    def __str__(self):
        return self.name


class GroupMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user} - {self.group}'
