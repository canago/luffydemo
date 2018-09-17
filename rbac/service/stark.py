import functools
from types import FunctionType
from django.utils.safestring import mark_safe
from django.shortcuts import HttpResponse, render, redirect
from django.conf.urls import url
from django.db.models import Q
from django.urls import reverse
from django import forms
from django.http import QueryDict
from rbac.utils.pagination import Pagination


class ChangeList(object):
    def __init__(self, config, request, search_list, conn, q, page, queryset):
        self.search_list = search_list
        self.conn = conn
        self.q = q
        self.page = page
        self.config = config
        self.request = request
        self.add_btn = config.display_add_btn()
        self.list_display = config.get_list_display()
        self.action_list = [{'name': func.__name__, 'text': func.text} for func in config.get_action_list()]
        self.queryset = queryset


class StarkConfig(object):
    """
    可被覆盖的类，用来做基类，被继承使用
    """

    def display_checkbox(self, row=None, header=False):
        if header:
            return "选择"
        return mark_safe("<input type='checkbox', name='pk' value='%s' />" % row.pk)

    def get_edit_url(self, row):
        app_label = self.model_class._meta.app_label
        model_name = self.model_class._meta.model_name
        namespace = self.site.app_namespace
        edit_name = '%s:%s_%s_change' % (namespace, app_label, model_name)
        edit_url = reverse(edit_name, kwargs={'pk': row.pk})
        if not self.request.GET:
            return edit_url
        # 获取原搜索的URL值，并保存到URL中，作为reverse使用
        param_str = self.request.GET.urlencode()  # q=嘉瑞&page=2
        new_query_dict = QueryDict(mutable=True)
        new_query_dict[self.back_condition_key] = param_str
        edit_url = "%s?%s" % (edit_url, new_query_dict.urlencode(),)
        return edit_url

    def get_del_url(self, row):
        app_label = self.model_class._meta.app_label
        model_name = self.model_class._meta.model_name
        namespace = self.site.app_namespace
        del_name = '%s:%s_%s_delete' % (namespace, app_label, model_name)
        del_url = reverse(del_name, kwargs={'pk': row.pk})

        return del_url

    def get_add_url(self):
        app_label = self.model_class._meta.app_label
        model_name = self.model_class._meta.model_name
        namespace = self.site.app_namespace
        add_name = '%s:%s_%s_add' % (namespace, app_label, model_name)
        add_url = reverse(add_name)

        return add_url

    def get_list_url(self):
        app_label = self.model_class._meta.app_label
        model_name = self.model_class._meta.model_name
        namespace = self.site.app_namespace
        list_name = '%s:%s_%s_changelist' % (namespace, app_label, model_name)
        list_url = reverse(list_name)

        return list_url

    def display_add_btn(self, row=None, header=False):
        if header:
            return "添加"
        del_url = self.get_add_url()
        tpl = """
        <a href="%s" class="btn btn-success">添加</a>
        """ % del_url

        return mark_safe(tpl)

    def display_edit_btn(self, row=None, header=False):

        if header:
            return "操作"
        edit_url = self.get_edit_url(row)
        del_url = self.get_del_url(row)
        tpl = """
        <a href="%s" >编辑</a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp
        <a href="%s" >删除</a>
        """ % (edit_url, del_url)
        return mark_safe(tpl)

    def display_del_btn(self, row=None, header=False):
        if header:
            return "删除"
        return

    def multi_delete(self):
        print('批量删除')

    multi_delete.text = '批量删除'

    def multi_init(self):
        pass

    multi_init.text = "批量初始化"

    order_by = []
    list_display = [display_checkbox, 'id', 'username', display_edit_btn]
    model_form_class = None  # 跟 get_forms 方法做对应
    action_list = [multi_delete, ]  # 根据select的option 的 val 函数名， select
    search_list = ['id', 'name']

    def __init__(self, model_class, site):
        self.model_class = model_class  # 把注册的表放进来，site.register(models.UserInfo)
        self.site = site
        self.request = None
        self.back_condition_key = "_filter"

    def get_search_list(self):
        val = []
        val.extend(self.search_list)
        return val

    def get_action_list(self):
        val = []
        val.extend(self.action_list)
        return val

    def get_action_dict(self):
        val = {}
        for item in self.action_list:
            val[item.__name__] = item
        return val

    def get_list_display(self):
        return self.list_display

    def get_order_by(self):
        return self.order_by

    def get_search_condition(self, request):
        """
        添加过滤条件, 搜索使用
        :param request:
        :return:
        """
        conn = Q()
        conn.connector = "OR"
        q = request.GET.get('q', "")
        search_list = self.get_search_list()

        if q:
            for field in search_list:
                conn.children.append(('%s__contains' % field, q))

        return search_list, conn, q

    def changelist_view(self, request):
        """
        查的view函数
        :param request:
        :return:
        """
        if request.method == "POST":
            pass
        search_list, conn, q = self.get_search_condition(request)
        total_count = self.model_class.objects.filter(conn).count()

        query_params = request.GET.copy()
        query_params._mutable = True  # 深copy一份数据，并且让值可以修改
        page = Pagination(request.GET.get('page'), total_count, request.path_info, query_params, per_page=2)
        queryset = self.model_class.objects.filter(conn).order_by(*self.get_order_by())[page.start:page.end]
        cl = ChangeList(self, request, search_list, conn, q, page, queryset)



        return render(request, 'rbac/changelist.html', {
                                                        'cl': cl,
                                                        })

    def get_forms(self):

        if self.model_form_class:
            return self.model_form_class

        class AddForms(forms.ModelForm):
            class Meta:
                model = self.model_class
                fields = "__all__"

        return AddForms

    def add_view(self, request):

        AddForms = self.get_forms()
        form = AddForms()
        return render(request, 'rbac/form_change.html', {'form': form})

    def delete_view(self, request, pk):
        return HttpResponse('delete_view')

    def change_view(self, request, pk):

        obj = self.model_class.objects.filter(pk=pk).first()
        if not obj:
            return HttpResponse('404')
        Forms = self.get_forms()
        if request.method == 'GET':
            form = Forms(instance=obj)
            return render(request, 'rbac/form_change.html', {'form': form})
        form = Forms(data=request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect(self.get_list_url())
        return render(request, 'rbac/form_change.html', {'form': form})

    def wrapper(self, func):
        # 为增删改查预留空间
        @functools.wraps(func)
        def inner(request, *args, **kwargs):
            self.request = request
            ret = func(request, *args, **kwargs)
            return ret

        return inner

    def get_urls(self):
        """
        # 制作  增删改查  4个URL
        :return: 列表
        """
        info = self.model_class._meta.app_label, self.model_class._meta.model_name

        urlpatterns = [
            url(r'^list/$', self.wrapper(self.changelist_view), name='%s_%s_changelist' % info),
            url(r'^add/$', self.wrapper(self.add_view), name='%s_%s_add' % info),
            url(r'^(?P<pk>\d+)/change/$', self.wrapper(self.change_view), name='%s_%s_change' % info),
            url(r'^(?P<pk>\d+)/delete/$', self.wrapper(self.delete_view), name='%s_%s_delete' % info),
        ]
        if self.extra_urls():
            urlpatterns.append(self.extra_urls())

        return urlpatterns

    def extra_urls(self):
        # 为URL扩展做准备
        pass

    @property
    def urls(self):
        return self.get_urls()


class AdminSite(object):

    def __init__(self):
        self._registry = {}  # 把注册的表放进来，site.register(models.UserInfo)
        self.app_name = "stark"
        self.app_namespace = "stark"

    def register(self, model_class, stark_config_cls=None, ):
        # 把注册的表放进来，site.register(models.UserInfo)
        if not stark_config_cls:
            stark_config_cls = StarkConfig
        self._registry[model_class] = stark_config_cls(model_class, self)

    def get_urls(self):
        """
        # 把表明变成小写返回给   urls
        _registry 包含了所有注册的类
        :return: 返回一个列表给urls，列表值为
        """
        urlpatterns = []
        for k, v in self._registry.items():
            app_label = k._meta.app_label
            model_name = k._meta.model_name
            urlpatterns.append(url(r'%s/%s/' % (app_label, model_name), (v.urls, None, None)))
        return urlpatterns

    @property
    def urls(self):
        """
        自定义 URL。  根据表明自定义URL
        :return:  元组
                        ([
                            url(r'^admin/', admin.site.urls),
                        ], name=None, namespace=None)
        """
        return self.get_urls(), self.app_name, self.app_namespace


# 使用单例模式，导入一个模块之后，该对象，就在内存加载一片空间，从此不在改变
site = AdminSite()
