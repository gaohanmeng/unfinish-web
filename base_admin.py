from django.contrib import admin


class BaseOwnerAdmin(admin.ModelAdmin):
    """
    1.用来自动补充文章，分类，标签，侧边栏，友链这些Ｍｏｄｅｌ的ｏｗｎｅｒ字段
    ２．用来针对ｑｕｅｒｙｓｅｔ过滤当前用户的数据
    """
    def get_queryset(self, request):
        qs = super(BaseOwnerAdmin, self).get_queryset(request)
        return qs.filter(owner=request.user)

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(BaseOwnerAdmin, self).save_model(request, obj, form, change)
