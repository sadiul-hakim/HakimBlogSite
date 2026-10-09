import math
from django.db import models
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.utils import timezone
from django.utils.text import slugify

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from wagtail import blocks
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    TitleFieldPanel,
)
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Orderable, Page
from wagtail.search import index
from wagtail.snippets.models import register_snippet


# ==========================================
# Snippets & Taxonomies
# ==========================================

class BlogCategory(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=80, unique=True, help_text="URL slug for category filtering")
    description = models.CharField(max_length=250, blank=True)
    icon = models.CharField(
        max_length=50,
        default="code",
        help_text="Icon identifier e.g. python, cpu, server, bot, database, cloud, terminal",
    )
    color = models.CharField(
        max_length=20,
        default="#4f46e5",
        help_text="Hex color code for badge styling (e.g. #4f46e5, #059669, #0284c7)",
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("description"),
        FieldPanel("icon"),
        FieldPanel("color"),
    ]

    class Meta:
        verbose_name = "Blog Category"
        verbose_name_plural = "Blog Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        "BlogPage",
        related_name="tagged_items",
        on_delete=models.CASCADE,
    )


# ==========================================
# StreamField Custom Blocks
# ==========================================

class CodeSnippetBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False, help_text="File name or code title (e.g. models.py, main.go)")
    language = blocks.ChoiceBlock(
        choices=[
            ("python", "Python"),
            ("javascript", "JavaScript"),
            ("typescript", "TypeScript"),
            ("html", "HTML"),
            ("css", "CSS"),
            ("sql", "SQL"),
            ("bash", "Bash / Shell"),
            ("json", "JSON"),
            ("yaml", "YAML"),
            ("dockerfile", "Dockerfile"),
            ("rust", "Rust"),
            ("go", "Go"),
            ("csharp", "C#"),
            ("cpp", "C++"),
            ("plaintext", "Plain Text"),
        ],
        default="python",
    )
    code = blocks.TextBlock(help_text="Paste your code here")

    class Meta:
        template = "blog/blocks/code_block.html"
        icon = "code"
        label = "Code Snippet"


class CalloutBlock(blocks.StructBlock):
    callout_type = blocks.ChoiceBlock(
        choices=[
            ("info", "Info (Blue)"),
            ("tip", "Pro Tip (Green)"),
            ("warning", "Warning (Amber)"),
            ("important", "Important (Purple)"),
        ],
        default="info",
    )
    title = blocks.CharBlock(required=False, help_text="Optional title for the callout box")
    text = blocks.RichTextBlock(features=["bold", "italic", "link", "code", "ul", "ol"])

    class Meta:
        template = "blog/blocks/callout_block.html"
        icon = "info-circle"
        label = "Callout / Notice"


class QuoteBlock(blocks.StructBlock):
    quote = blocks.TextBlock()
    author = blocks.CharBlock(required=False, help_text="Author or source")
    source_title = blocks.CharBlock(required=False, help_text="Source title / book / talk")

    class Meta:
        template = "blog/blocks/quote_block.html"
        icon = "openquote"
        label = "Blockquote"


class ImageWithCaptionBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    caption = blocks.CharBlock(required=False, help_text="Image caption")
    alt_text = blocks.CharBlock(required=False, help_text="Alt text for accessibility")

    class Meta:
        template = "blog/blocks/image_block.html"
        icon = "image"
        label = "Image with Caption"


class DownloadableDocBlock(blocks.StructBlock):
    document = DocumentChooserBlock()
    title = blocks.CharBlock(required=False, help_text="Custom display title for the file")
    description = blocks.CharBlock(required=False, help_text="Short description of this file")

    class Meta:
        template = "blog/blocks/document_block.html"
        icon = "doc-full"
        label = "Downloadable Document"


class BlogStreamBlock(blocks.StreamBlock):
    heading = blocks.CharBlock(
        form_classname="title",
        icon="title",
        label="Heading",
        help_text="Section sub-heading",
    )
    paragraph = blocks.RichTextBlock(
        features=[
            "h3",
            "h4",
            "bold",
            "italic",
            "link",
            "ol",
            "ul",
            "hr",
            "code",
            "blockquote",
        ],
        icon="pilcrow",
    )
    code = CodeSnippetBlock()
    callout = CalloutBlock()
    quote = QuoteBlock()
    image = ImageWithCaptionBlock()
    document = DownloadableDocBlock()
    embed = EmbedBlock(icon="media", label="Embed (YouTube, Vimeo, etc.)")


# ==========================================
# Post Attachments & Gallery
# ==========================================

class BlogPageDocumentAttachment(Orderable):
    page = ParentalKey("BlogPage", related_name="attachments", on_delete=models.CASCADE)
    document = models.ForeignKey(
        "wagtaildocs.Document",
        on_delete=models.CASCADE,
        related_name="+",
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Custom title for this document (e.g. Source Code Archive, PDF Cheat Sheet)",
    )
    description = models.CharField(max_length=300, blank=True)

    panels = [
        FieldPanel("document"),
        FieldPanel("title"),
        FieldPanel("description"),
    ]


class BlogPageGalleryImage(Orderable):
    page = ParentalKey("BlogPage", related_name="gallery_images", on_delete=models.CASCADE)
    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.CASCADE,
        related_name="+",
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
    ]


# ==========================================
# Reader Comments Model
# ==========================================

class BlogComment(Orderable):
    page = ParentalKey("BlogPage", related_name="reader_comments", on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="blog_comments",
    )
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField(blank=True)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(
        default=True,
        help_text="Approved comments are visible to all readers",
    )

    panels = [
        FieldPanel("author_name"),
        FieldPanel("author_email"),
        FieldPanel("comment"),
        FieldPanel("is_approved"),
    ]

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Blog Comment"
        verbose_name_plural = "Blog Comments"

    def __str__(self):
        return f"Comment by {self.author_name} on {self.page.title}"

    @property
    def author_initials(self):
        parts = self.author_name.strip().split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        elif parts:
            return parts[0][:2].upper()
        return "U"


# ==========================================
# Blog Index & Blog Post Pages
# ==========================================

class BlogIndexPage(Page):
    intro = RichTextField(blank=True)
    posts_per_page = models.PositiveIntegerField(
        default=6,
        help_text="Number of articles to display per page",
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("posts_per_page"),
    ]

    subpage_types = ["blog.BlogPage"]

    def get_posts(self):
        return (
            BlogPage.objects.child_of(self)
            .live()
            .order_by("-date", "-first_published_at")
            .select_related("category", "header_image", "author")
            .prefetch_related("tags")
        )

    def get_context(self, request):
        context = super().get_context(request)
        posts = self.get_posts()

        # Category Filter
        category_slug = request.GET.get("category")
        selected_category = None
        if category_slug:
            try:
                selected_category = BlogCategory.objects.get(slug=category_slug)
                posts = posts.filter(category=selected_category)
            except BlogCategory.DoesNotExist:
                pass

        # Tag Filter
        tag_slug = request.GET.get("tag")
        selected_tag = None
        if tag_slug:
            posts = posts.filter(tags__slug=tag_slug)
            selected_tag = tag_slug

        # Search query within blog
        search_query = request.GET.get("q")
        if search_query:
            posts = posts.search(search_query)

        # Pagination
        paginator = Paginator(posts, self.posts_per_page)
        page_number = request.GET.get("page")

        try:
            paginated_posts = paginator.page(page_number)
        except PageNotAnInteger:
            paginated_posts = paginator.page(1)
        except EmptyPage:
            paginated_posts = paginator.page(paginator.num_pages)

        # All categories for sidebar/filters
        all_categories = BlogCategory.objects.all()
        from taggit.models import Tag
        all_tags = Tag.objects.all()[:20]
        recent_posts = (
            BlogPage.objects.live()
            .order_by("-date", "-first_published_at")
            .select_related("category", "header_image")[:5]
        )

        context.update(
            {
                "posts": paginated_posts,
                "paginator": paginator,
                "categories": all_categories,
                "recent_posts": recent_posts,
                "tags": all_tags,
                "selected_category": selected_category,
                "selected_tag": selected_tag,
                "search_query": search_query or "",
            }
        )
        return context


class BlogPage(Page):
    date = models.DateField("Post date", default=timezone.now)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="authored_posts",
    )
    author_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Custom display author name if different from account username",
    )
    category = models.ForeignKey(
        "BlogCategory",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="blog_posts",
    )
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    intro = models.CharField(
        max_length=350,
        help_text="Summary/excerpt shown on cards and search results",
    )
    header_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    body = StreamField(
        BlogStreamBlock(),
        use_json_field=True,
        blank=True,
    )
    manual_read_time = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Optional reading time in minutes (calculated automatically if left blank)",
    )

    search_fields = Page.search_fields + [
        index.SearchField("intro"),
        index.SearchField("body"),
        index.FilterField("date"),
        index.FilterField("category_id"),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("date"),
                FieldPanel("author"),
                FieldPanel("author_name"),
                FieldPanel("category"),
                FieldPanel("tags"),
                FieldPanel("manual_read_time"),
            ],
            heading="Article Information & Taxonomy",
        ),
        FieldPanel("intro"),
        FieldPanel("header_image"),
        FieldPanel("body"),
        InlinePanel("attachments", label="Downloadable Documents / Files"),
        InlinePanel("gallery_images", label="Additional Images / Gallery"),
        InlinePanel("reader_comments", label="Reader Comments"),
    ]

    parent_page_types = ["blog.BlogIndexPage"]
    subpage_types = []

    @property
    def display_author(self):
        if self.author_name:
            return self.author_name
        if self.author:
            return self.author.get_full_name() or self.author.username
        return "Hakim"

    @property
    def reading_time(self):
        if self.manual_read_time:
            return self.manual_read_time
        # Calculate estimated reading time (~200 words/min)
        total_words = len(self.intro.split()) if self.intro else 0
        for block in self.body:
            if block.block_type in ("paragraph", "heading"):
                total_words += len(str(block.value).split())
            elif block.block_type == "code":
                code_val = block.value.get("code", "") if isinstance(block.value, dict) else ""
                total_words += len(str(code_val).split())
        minutes = max(1, math.ceil(total_words / 200))
        return minutes

    def get_related_posts(self):
        related = BlogPage.objects.live().exclude(id=self.id)
        if self.category:
            related = related.filter(category=self.category)
        return related.order_by("-date")[:3]

    def get_context(self, request):
        context = super().get_context(request)
        context["approved_comments"] = self.reader_comments.filter(is_approved=True)
        context["related_posts"] = self.get_related_posts()
        context["recent_posts"] = (
            BlogPage.objects.live()
            .exclude(id=self.id)
            .order_by("-date")[:5]
        )
        context["categories"] = BlogCategory.objects.all()
        from taggit.models import Tag
        context["tags"] = Tag.objects.all()[:20]
        
        # Previous / Next post navigation
        live_posts = list(
            BlogPage.objects.live().order_by("date", "first_published_at")
        )
        try:
            current_index = live_posts.index(self)
            context["prev_post"] = live_posts[current_index - 1] if current_index > 0 else None
            context["next_post"] = live_posts[current_index + 1] if current_index < len(live_posts) - 1 else None
        except ValueError:
            context["prev_post"] = None
            context["next_post"] = None

        # Prepopulate comment form fields if user is authenticated
        if request.user.is_authenticated:
            context["user_initial_name"] = request.user.get_full_name() or request.user.username
            context["user_initial_email"] = request.user.email
        else:
            context["user_initial_name"] = ""
            context["user_initial_email"] = ""
            
        return context

