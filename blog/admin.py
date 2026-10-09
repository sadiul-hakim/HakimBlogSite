from django.contrib import admin
from .models import (
    BlogCategory,
    BlogComment,
    BlogPage,
    BlogIndexPage,
    BlogPageDocumentAttachment,
    BlogPageGalleryImage,
    BlogPageTag,
)


class BlogPageDocumentAttachmentInline(admin.TabularInline):
    model = BlogPageDocumentAttachment
    extra = 1
    fields = ("document", "title", "description", "sort_order")


class BlogPageGalleryImageInline(admin.TabularInline):
    model = BlogPageGalleryImage
    extra = 1
    fields = ("image", "caption", "sort_order")


class BlogCommentInline(admin.TabularInline):
    model = BlogComment
    extra = 0
    fields = ("author_name", "author_email", "comment", "is_approved", "created_at")
    readonly_fields = ("created_at",)


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "icon", "color", "article_count")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description", "slug")
    list_filter = ("icon",)

    def article_count(self, obj):
        return obj.blog_posts.count()
    article_count.short_description = "Articles"


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ("author_name", "page", "author_email", "created_at", "is_approved")
    list_filter = ("is_approved", "created_at")
    search_fields = ("author_name", "author_email", "comment", "page__title")
    actions = ["approve_comments", "unapprove_comments"]
    date_hierarchy = "created_at"

    def approve_comments(self, request, queryset):
        count = queryset.update(is_approved=True)
        self.message_user(request, f"Approved {count} comment(s).")
    approve_comments.short_description = "Approve selected comments"

    def unapprove_comments(self, request, queryset):
        count = queryset.update(is_approved=False)
        self.message_user(request, f"Unapproved {count} comment(s).")
    unapprove_comments.short_description = "Unapprove selected comments"


@admin.register(BlogPage)
class BlogPageAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "author", "date", "live", "reading_time_display", "first_published_at")
    list_filter = ("category", "live", "date", "author")
    search_fields = ("title", "intro", "author__username", "author__first_name", "author__last_name")
    date_hierarchy = "date"
    autocomplete_fields = ["category"]
    inlines = [
        BlogPageDocumentAttachmentInline,
        BlogPageGalleryImageInline,
        BlogCommentInline,
    ]
    readonly_fields = ("first_published_at", "last_published_at", "latest_revision_created_at")

    def reading_time_display(self, obj):
        return f"{obj.reading_time} min"
    reading_time_display.short_description = "Read Time"


@admin.register(BlogIndexPage)
class BlogIndexPageAdmin(admin.ModelAdmin):
    list_display = ("title", "live", "first_published_at", "last_published_at")
    search_fields = ("title",)
    list_filter = ("live",)
    readonly_fields = ("first_published_at", "last_published_at", "latest_revision_created_at")


@admin.register(BlogPageDocumentAttachment)
class BlogPageDocumentAttachmentAdmin(admin.ModelAdmin):
    list_display = ("title", "page", "document", "sort_order")
    search_fields = ("title", "description", "page__title")
    list_filter = ("page__category",)


@admin.register(BlogPageGalleryImage)
class BlogPageGalleryImageAdmin(admin.ModelAdmin):
    list_display = ("caption", "page", "image", "sort_order")
    search_fields = ("caption", "page__title")
    list_filter = ("page__category",)


@admin.register(BlogPageTag)
class BlogPageTagAdmin(admin.ModelAdmin):
    list_display = ("tag", "content_object")
    search_fields = ("tag__name", "content_object__title")
