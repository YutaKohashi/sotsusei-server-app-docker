from django.contrib import admin
from .models import *

# Register your models here.
#@admin.register(UploadImage)
class UserAdmin(admin.ModelAdmin):
    pass

@admin.register(StoreTable)
@admin.register(EmployeeTable)
@admin.register(GroupStoreTable)
@admin.register(ImageTable)
@admin.register(HumanTable)
@admin.register(ThreadsTable)
@admin.register(CarTable)
@admin.register(NewsTable)
@admin.register(TokenTable)
class UserAdmin(admin.ModelAdmin):
    pass


