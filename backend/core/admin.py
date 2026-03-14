from django.contrib import admin


class NormalisedLookupAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "label", "order_index")
    search_fields = ("code", "label", "description")
    ordering = ("order_index", "label")
