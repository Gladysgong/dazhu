from django.contrib import admin
import models
from django.utils import timezone

class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'timestamp')
    readonly_fields = ('last_update',)
    def save_model(self, request, obj, form, change):
        obj.body = request.POST["body"]
        obj.last_update = timezone.now()
        return super(BlogPostAdmin,self).save_model(request, obj, form,change)

admin.site.register(models.BlogPost,BlogPostAdmin)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'body' ,'target_blog',)
    def target_blog(self,obj):
        return "<a href='%s'>%s</a>" % ("/blog/details/"+obj.blog.guid,obj.blog.title)
    target_blog.allow_tags = True

admin.site.register(models.Comment,CommentAdmin)

class CateAdmin(admin.ModelAdmin):
    list_display = ('title', )
admin.site.register(models.Category,CateAdmin)