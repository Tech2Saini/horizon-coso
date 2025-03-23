from django.contrib import admin
from .models import TeamMember,PricingPlan,Service, FAQ,Contact,Blog, Category, Tag


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'email', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('name', 'role', 'email')
    list_editable = ['email','is_active','order']

@admin.register(PricingPlan)
class PricingPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'status','order', 'created_at')
    list_filter = ('status',)
    search_fields = ('name', 'features')
    list_editable  = ['price','status','order']
    # prepopulated_fields = {"slug": ("name",)}


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name",)

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question","is_answered","notified","email", "service", "is_active", "status")
    list_filter = ("service", "is_active",'status')
    search_fields = ("question", "answer")
    list_editable = ['is_active','status',]

    ordering = ("-updated_at",'-created_at')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'email', 'subject', 'status', 'created_date')
    list_filter = ('status', 'created_date')
    search_fields = ('fullname', 'email', 'subject', 'message')
    list_editable  = ['status']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'created_at', 'published')
    list_filter = ('category', 'status', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    filter_horizontal = ('tags',)
