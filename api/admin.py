from django.utils.html import mark_safe
from django.contrib import admin
from .models import Item, ItemImage


class ItemImageInline(admin.TabularInline):  # or StackedInline
    model = ItemImage
    extra = 1
    fields = ("image", "preview")
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj.image and hasattr(obj.image, "url"):
            return mark_safe(f'<img src="{obj.image.url}" style="max-height: 100px;"/>')
        return "No Image"
    preview.short_description = "Preview"


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description")
    search_fields = ("title", "description")
    inlines = [ItemImageInline]


@admin.register(ItemImage)
class ItemImageAdmin(admin.ModelAdmin):
    list_display = ("item", "image")
