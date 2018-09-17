from django.template import Library
from types import FunctionType

register = Library()

@register.inclusion_tag('rbac/table.html')
def table(cl):
    header_list = []  # 定义表头
    if cl.list_display:
        for item in cl.list_display:
            if isinstance(item, FunctionType):
                verbose_name = item(cl.config, header=True)
            else:
                verbose_name = cl.config.model_class._meta.get_field(item).verbose_name
            header_list.append(verbose_name)
    else:
        header_list.append(cl.config.model_class._meta.model_name)

    body_list = []  # 定义表内容
    for field in cl.queryset:
        row_list = []
        if not cl.list_display:
            # list_display 空的时候 需要显示一个字段。   直接就是 类
            row_list.append(field)
            body_list.append(row_list)
            continue
        for item in cl.list_display:
            if isinstance(item, FunctionType):
                val = item(cl.config, row=field)
            else:
                val = getattr(field, item)  # 根据自定义的字段，反射出改字段的值
            row_list.append(val)
        body_list.append(row_list)
    return {'header_list': header_list, 'body_list': body_list}