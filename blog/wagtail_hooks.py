from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup
from .models import BlogCategory, BlogComment


class BlogCategoryViewSet(SnippetViewSet):
    model = BlogCategory
    menu_label = "Categories"
    icon = "folder-open-inverse"
    menu_order = 100
    add_to_admin_menu = False
    list_display = ["name", "slug", "icon", "color"]
    search_fields = ["name", "description", "slug"]


class BlogCommentViewSet(SnippetViewSet):
    model = BlogComment
    menu_label = "Comments"
    icon = "comment"
    menu_order = 200
    add_to_admin_menu = False
    list_display = ["author_name", "page", "author_email", "created_at", "is_approved"]
    list_filter = ["is_approved", "created_at"]
    search_fields = ["author_name", "author_email", "comment", "page__title"]


class BlogAdminGroup(SnippetViewSetGroup):
    menu_label = "Blog Taxonomies & Discussions"
    menu_icon = "tag"
    menu_order = 300
    items = (BlogCategoryViewSet, BlogCommentViewSet)


register_snippet(BlogAdminGroup)
