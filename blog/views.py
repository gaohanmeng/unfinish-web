from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView
from django.db.models import Q, F

from .models import Post, Tag, Category
from config.models import SideBar
from comment.forms import CommentForm
from comment.models import Comment


class CommonViewMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'sidebars': SideBar.get_all(),
        })
        context.update(Category.get_navs())
        return context


class IndexView(CommonViewMixin, ListView):
    queryset = Post.latest_posts()
    paginate_by = 3
    context_object_name = 'post_list'
    template_name = 'blog/list.html'


class PostListView(ListView):
    queryset = Post.latest_posts()
    paginate_by = 1
    context_object_name = 'post_list'
    template_name = 'blog/list.html'
# def post_list(request, category_id=None, tag_id=None):
#     tag = None
#     category = None
#
#     if tag_id:
#         post_list, tag = Post.get_by_tag(tag_id)
#
#     elif category_id:
#         post_list, category = Post.get_by_category(category_id)
#
#     else:
#         post_list = Post.latest_posts()
#
#     context = {
#         'category': category,
#         'tag': tag,
#         'post_list': post_list,
#         'sidebar': SideBar.get_all()
#     }
#     context.update(Category.get_navs())
#
#     return render(request, 'blog/list.html', context=context)


class PostDetailView(CommonViewMixin, DetailView):
    queryset = Post.latest_posts()
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'comment_form': CommentForm,
            'comment_list': Comment.get_by_target(self.request.path),
        })
        return context


# def post_detail(request, post_id=None):
#     try:
#         post = Post.objects.get(id=post_id)
#     except Exception:
#         post = None
#     context = {
#         'post': post,
#         'sidebar': SideBar.get_all()
#     }
#     context.update(Category.get_navs())
#     return render(request, 'blog/detail.html', context={'post': post})

class CategoryView(IndexView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.kwargs.get('category_id')
        category = get_object_or_404(Category, pk=category_id)
        context.update({
            'category': category,
            # 'category_id': category_id
        })
        return context

    def get_queryset(self):
        """重写queryset，根据分类过滤"""
        queryset = super().get_queryset()
        category_id = self.kwargs.get('category_id')
        return queryset.filter(category_id=category_id)


class TagView(IndexView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag_id = self.kwargs.get('tag_id')
        tag = get_object_or_404(Tag, pk=tag_id)
        context.update({
            'tag': tag,
        })
        return context

    def get_queryset(self):
        """重写queryset,根据标签过滤"""
        queryset = super().get_queryset()
        tag_id = self.kwargs.get('tag_id')
        return queryset.filter(tag__id=tag_id)


class SearchView(IndexView):
    """增加啊搜索页面"""
    def get_context_data(self):
        context = super().get_context_data()
        context.update({
            'keyword': self.request.GET.get('keyword', '')
        })
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        keyword = self.request.GET.get('keyword')
        if not keyword:
            return queryset
        return queryset.filter(Q(title=keyword) | Q(desc=keyword))


class AuthorView(IndexView):
    """增加作者页面"""
    # """调整展示逻辑"""
    # def get_context_data(self):
    #     context = super().get_context_data()
    #     context.update({
    #         'author': self.request.GET.get('owner_id')
    #     })

    def get_queryset(self):
        queryset = super().get_queryset()
        author_id = self.kwargs.get('owner_id')
        return queryset.filter(owner_id=author_id)