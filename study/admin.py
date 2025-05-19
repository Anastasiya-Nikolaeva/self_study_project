from django.contrib import admin

from .models import Material, Test, Theme

admin.site.register(Theme)
admin.site.register(Material)
admin.site.register(Test)
