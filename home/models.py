from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from blog.models import BlogPage, BlogCategory


class HomePage(Page):
    hero_badge = models.CharField(
        max_length=60,
        default="Engineering & Technology",
        help_text="Small badge above main hero heading",
    )
    hero_title = models.CharField(
        max_length=150,
        default="Exploring Modern Technology, Systems & AI",
        help_text="Main hero heading",
    )
    hero_subtitle = models.CharField(
        max_length=350,
        default="In-depth technical guides, engineering thoughts, and hands-on explorations across Python, Backend Architecture, Artificial Intelligence, and Modern Cloud Systems.",
        help_text="Hero description",
    )
    about_snippet = RichTextField(
        blank=True,
        help_text="Optional brief author/site intro on the homepage",
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("hero_badge"),
                FieldPanel("hero_title"),
                FieldPanel("hero_subtitle"),
            ],
            heading="Hero Section",
        ),
        FieldPanel("about_snippet"),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        
        # Latest articles
        latest_posts = (
            BlogPage.objects.live()
            .order_by("-date", "-first_published_at")
            .select_related("category", "header_image", "author")
            .prefetch_related("tags")
        )
        
        # Featured post (the newest post)
        featured_post = latest_posts.first()
        recent_posts = latest_posts[1:7] if featured_post else []
        
        # All categories with their live posts
        categories = list(BlogCategory.objects.all())
        category_sections = []
        for cat in categories:
            cat_posts = latest_posts.filter(category=cat)[:4]
            if cat_posts:
                category_sections.append({
                    "category": cat,
                    "featured": cat_posts[0],
                    "articles": cat_posts[1:4],
                })
        
        # Tags
        from taggit.models import Tag
        tags = Tag.objects.all()[:25]
        
        context.update(
            {
                "latest_posts": latest_posts[:12],
                "featured_post": featured_post,
                "recent_posts": recent_posts,
                "category_sections": category_sections,
                "total_articles": latest_posts.count(),
                "categories": categories,
                "tags": tags,
            }
        )
        return context


