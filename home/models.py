from django.db import models
from PIL import Image
import os
from django.utils.text import slugify
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField
from ckeditor.fields import RichTextField


def team_member_photo_path(instance, filename):
    """Generate file path for new team member image"""
    ext = 'png'  # Force PNG format
    filename = f"{instance.name.replace(' ', '_').lower()}.{ext}"
    return os.path.join('team_photos/', filename)

class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to=team_member_photo_path, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    portfolio = models.URLField(blank=True, null=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Override save method to compress and convert image to PNG"""
        super().save(*args, **kwargs)  # Save the model first

        if self.photo:
            img_path = self.photo.path
            img = Image.open(img_path)

            # Convert to PNG and compress
            img = img.convert('RGB')
            img.save(img_path, format="PNG", optimize=True, quality=70)  # 70% quality for compression

def pricing_plan_icon_upload(instance, filename):
    """Save the pricing plan icon with a unique name."""
    filename, ext = os.path.splitext(filename)
    return f"pricing_icons/{slugify(instance.name)}{ext}"

class PricingPlan(models.Model):
    PLAN_STATUS = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    name = models.CharField(max_length=100, unique=True, help_text="Enter the plan name (e.g., Basic, Pro, Enterprise)")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Enter the price (e.g., 19.99)")
    description = models.TextField(blank=True, help_text="Short description of the plan")
    features = models.TextField(help_text="List of features (separated by commas)")
    icon = models.ImageField(upload_to=pricing_plan_icon_upload, blank=True, null=True, help_text="Upload an icon for this plan")
    status = models.CharField(max_length=10, choices=PLAN_STATUS, default='active', help_text="Active plans will be displayed on the website")
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']  # Sort plans by price (ascending)
        verbose_name = "Pricing Plan"
        verbose_name_plural = "Pricing Plans"

    def __str__(self):
        return f"{self.name} - ${self.price}"

    def get_feature_list(self):
        """Returns features as a list"""
        return [feature.strip() for feature in self.features.split('\n')]

class Service(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, help_text="Unique identifier for URL")
    
    def __str__(self):
        return self.name

class FAQ(models.Model):
    DEFAULT_SERVICE = "default"
    options = [
        ('Panding','Panding'),
        ('Solved','Solved'),
        ('Archive','Archive'),
    ]
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="faqs",null=True, blank=True, help_text="Leave blank for default FAQs")
    question = models.CharField(max_length=100)
    answer = models.TextField(blank=True)
    status = models.CharField(max_length=10,choices=options,default='Panding')
    email = models.EmailField(max_length=50,default='',blank=True)
    notified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=False,blank=True,null=True)

    def __str__(self):
        return f"{self.service.name if self.service else 'Default'} - {self.question[:50]}"

    class Meta:
        ordering = ["-created_at"]

    def is_answered(self):
        return self.status == "Solved" and len(self.answer) > 0


class Contact(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]

    fullname = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)  # Optional field
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)  # Auto set on creation
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')  # Track inquiry status
    ip_address = models.GenericIPAddressField(blank=True, null=True)  # Store sender's IP

    def __str__(self):
        return f"{self.fullname} - {self.subject}"

    class Meta:
        ordering = ['-created_date']  # Newest inquiries first

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Blog(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    tags = models.ManyToManyField('Tag', blank=True)
    content = RichTextUploadingField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="blogs")
    views = models.PositiveIntegerField(default=0)
    reading_time = models.PositiveIntegerField(default=1)  # In minutes
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
