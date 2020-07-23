from django.contrib import admin
from  RSofBX.apps.bxdb.models import book_ratings,bx_info,book_tags,user_info,admin_info,tags

# Register your models here.


from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered
'''
app_models = apps.get_app_config("bxdb").get_models()  # 获取app:bxdb下所有的model,得到一个生成器
# 遍历注册model
for model in app_models:
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass
'''
admin.site.register([book_ratings,book_tags,admin_info])


class bookInfoAdmin(admin.ModelAdmin):
    list_display = ('book_id','book_title','book_author','average_rating')
    search_fields = ('book_id','original_title','book_title',)

class userInfoAdmin(admin.ModelAdmin):
    list_display = ('user_id','user_name','age')
    search_fields = ('user_name','user_id',)

class tagsAdmin(admin.ModelAdmin):
    list_display = ('tag_id','tag_name')
    search_fields = ('tag_name',)

admin.site.register(tags,tagsAdmin)
admin.site.register(bx_info,bookInfoAdmin)
admin.site.register(user_info,userInfoAdmin)