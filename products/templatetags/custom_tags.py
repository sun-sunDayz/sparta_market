from django import template

register = template.Library()

@register.filter
def custom_range(value):
    return range(1, value + 1)


@register.filter()
def filter_by_product_id(queryset, product_id):
    return queryset.filter(product_id=product_id).first()

@register.filter()
def average_rating(querytset):
    li = []
    for product in querytset:
        li.append(product.rating)
    return sum(li)/len(li)