import mistune

from django.db import models
from django.core.cache import cache
from django.contrib.auth.models import User
from django.utils.functional import cached_property


class Category(models.Model):
    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_ITEMS = (
        (STATUS_NORMAL, '正常'),
        (STATUS_DELETE, '删除'),
    )
    name = models.CharField(max_length=50, verbose_name='名称')
    status = models.PositiveIntegerField(default=STATUS_NORMAL, choices=STATUS_ITEMS,
                                         verbose_name='状态')
    is_nav = models.BooleanField(default=False, verbose_name='是否为导航')
    owner = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE)
    # django2.0之后，定义外键和一对一关系时,　只有在定义一对一时才需要，多对多，一对多时都不需要
    # 需要加on_delete参数, 默认是ＣＡＳＣＡＤＥ，详情查看ｄｊａｎｇｏ文档
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = verbose_name_plural = '分类'

    # @classmethod
    # def get_navs(cls):
    #     categories = cls.objects.filter(status=cls.STATUS_NORMAL)
    #     nav_categories = []
    #     normal_categories = []
    #
    #     for cate in categories:
    #         if cate.is_nav:
    #             nav_categories.append(cate)
    #         else:
    #             normal_categories.append(cate)
    #
    #     return {
    #         'navs': nav_categories,
    #         'categories': normal_categories,
    #     }

    def __str__(self):
        return self.name


class Tag(models.Model):
    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_ITEMS = (
        (STATUS_NORMAL, '正常'),
        (STATUS_DELETE, '删除'),
    )
    name = models.CharField(max_length=10, verbose_name='名称')
    status = models.PositiveIntegerField(default=STATUS_NORMAL, choices=STATUS_ITEMS,
                                         verbose_name='状态')
    owner = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = verbose_name_plural = '标签'

    def __str__(self):
        return self.name


class Post(models.Model):
    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_DRAFT = 2
    STATUS_ITEMS = (
        (STATUS_NORMAL, '正常'),
        (STATUS_DELETE, '删除'),
        (STATUS_DRAFT, '草稿'),
    )
    title = models.CharField(max_length=20, verbose_name='标题')
    desc = models.CharField(max_length=25, blank=True, verbose_name='摘要')
    is_title = models.BooleanField(default=False, verbose_name='是否置顶文章')
    content = models.TextField(verbose_name='正文', help_text='正文内容必须为MarkDown格式')
    status = models.PositiveIntegerField(default=STATUS_NORMAL, choices=STATUS_ITEMS,
                                         verbose_name='状态')
    category = models.ForeignKey(Category, verbose_name='分类', on_delete=models.CASCADE)
    tag = models.ManyToManyField(Tag, verbose_name='标签')
    owner = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    pv = models.PositiveIntegerField(default=1)
    uv = models.PositiveIntegerField(default=1)

    content_html = models.TextField(verbose_name='正文html代码', blank=True, editable=False)

    is_md = models.BooleanField(default=False, verbose_name='markdown语法')

    class Meta:
        verbose_name = verbose_name_plural = '文章'
        ordering = ['-id']  # 根据ｉｄ进行降序排序

    # @cached_property
    # def tags(self):
    #     return ','.join(self.tag.values_list('name', flat=True))

    @staticmethod
    def get_by_tag(tag_id):
        try:
            tag = Tag.objects.get(id=tag_id)
        except Exception:
            tag = None
            post_list = []
        else:
            post_list = tag.post_set.filter(status=Post.STATUS_NORMAL).select_related('owner', 'category')

        return post_list, tag

    @staticmethod
    def get_by_category(category_id):
        try:
            category = Category.objects.get(id=category_id)
        except Exception:
            category = None
            post_list = []
        else:
            post_list = category.post_set.filter(status=Post.STATUS_NORMAL).select_related('owner', 'category')

        return post_list, category

    # @classmethod
    # def latest_posts(cls, with_related=True):
    #     queryset = cls.objects.filter(status=cls.STATUS_NORMAL)
    #     if with_related:
    #         queryset = queryset.select_related('owner', 'category')
    #     return queryset

    @classmethod
    def latest_posts(cls):
        return cls.objects.filter(status=cls.STATUS_NORMAL)

    # @classmethod
    # def hot_post(cls):
    #     return cls.objects.filter(status=cls.STATUS_NORMAL).order_by('-pv').only('title')
    @classmethod
    def hot_posts(cls):
        result = cache.get('hot_posts')
        if not result:
            result = cls.objects.filter(status=cls.STATUS_NORMAL).order_by('-pv')
            cache.set('hot_posts', result, 10 * 60)
        return result

    # def save(self, force_insert=False, force_update=False, using=None,
    #          update_fields=None, *args, **kwargs):
    #     self.content_html = mistune.markdown(self.content)
    #     super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.is_md:
            self.content_html = mistune.markdown(self.content)
        else:
            self.content_html = self.content
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
