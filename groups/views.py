from collections import defaultdict

from groups.models import Group, GroupMembership
from products.models import Product
from users.models import User


# Create your views here.

def reorganize_groups(product_id: int) -> None:
    students = GroupMembership.objects.filter(group__product_id=product_id)
    product = Product.objects.get(id=product_id)
    max_group_size, min_group_size = product.maximum_group_size, product.minimum_group_size
    students_set = {i.user_id for i in students}
    new_groups = defaultdict(set)  # group_id to students ids

    new_number_of_groups = 1
    while len(students_set) > new_number_of_groups * max_group_size:
        new_number_of_groups += 1

    # fulling groups to minimum size
    cur_group = 1
    for student in students:
        if len(new_groups[cur_group]) >= max_group_size:
            if cur_group < new_number_of_groups:
                cur_group += 1
            else:
                break
        new_groups[cur_group].add(student.user_id)
        students_set.remove(student.user_id)

    # adding equal amount of students to each group
    student_to_one_group = len(students_set) // new_number_of_groups
    for i in range(1, new_number_of_groups + 1):
        for j in range(student_to_one_group):
            new_groups[i].add(students_set.pop())

    # adding remaining students to groups
    remaining_students = len(students_set) % new_number_of_groups
    for i in range(1, remaining_students + 1):
        new_groups[i + 1].add(students_set.pop())

    GroupMembership.objects.filter(group__product_id=product_id).delete()
    groups_users = Group.objects.filter(product_id=product_id)

    if len(groups_users) < len(new_groups):
        Group.objects.create(name=f'Group {len(groups_users) + 1}', product_id=product_id)
    elif len(groups_users) > len(new_groups):
        for group in groups_users[len(new_groups):]:
            group.delete()

    # adding students to groups using true group ids
    groups = Group.objects.filter(product_id=product_id)
    ind = 0
    for students_ids in new_groups.values():
        group = Group.objects.get(id=groups[ind].id)
        for user_id in students_ids:
            user = User.objects.get(id=user_id)
            GroupMembership.objects.create(user=user, group=group)
        ind += 1


def add_user_to_group(user_id: int, group_id: int) -> None:
    group = Group.objects.get(id=group_id)
    user = User.objects.get(id=user_id)
    GroupMembership.objects.create(user=user, group=group)
