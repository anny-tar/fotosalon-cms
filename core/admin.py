from django.contrib import admin
from .models import (
    SiteSettings, ContactItem, SmtpSettings,
    EmailTemplate, SectionTemplate, PageSection
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name',)


@admin.register(ContactItem)
class ContactItemAdmin(admin.ModelAdmin):
    list_display = ('type', 'label', 'value', 'order', 'is_active')
    list_filter = ('type', 'is_active')
    ordering = ['order', 'type']


@admin.register(SmtpSettings)
class SmtpSettingsAdmin(admin.ModelAdmin):
    list_display = ('host', 'port', 'from_email', 'use_tls')


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('key', 'subject')


@admin.register(SectionTemplate)
class SectionTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'template_name')


@admin.register(PageSection)
class PageSectionAdmin(admin.ModelAdmin):
    list_display = ('page', 'template', 'order', 'is_active')
    list_filter = ('page', 'is_active')