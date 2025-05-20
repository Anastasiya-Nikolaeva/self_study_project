from django.contrib import admin

from .models import Answer, Material, Question, Test, Theme

admin.site.register(Theme)
admin.site.register(Material)
admin.site.register(Test)
admin.site.register(Question)
admin.site.register(Answer)
