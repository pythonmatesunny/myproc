from django.contrib import admin
from .models import  ImageFrames,FLag
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import MyUser
from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import MyUser


admin.site.register(FLag)


class ImageFramesAdmin(admin.ModelAdmin):
    list_display = ['id','user', 'time_stamp' , 'flagged_types' , 'frame_captype','is_red_flagged', ]
    def flagged_types(self,obj):
        return [ flag for flag in obj.flagged_as.all() ]
admin.site.register(ImageFrames,ImageFramesAdmin)


#MyUser FORMS 
class UserCreationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    class Meta:
        model = MyUser
        fields = ('access_key', 'name','email')
    def clean_password(self):
        password = self.cleaned_data.get("password")
        return password
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["access_key"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()
    class Meta:
        model = MyUser
        fields = ('access_key','email', 'password', 'name', 'is_active', 'is_admin')


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('access_key','email', 'name', 'is_admin')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('access_key','email', 'password')}),
        ('Personal info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_admin',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('access_key','email', 'name', 'password'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()
admin.site.register(MyUser, UserAdmin)
admin.site.unregister(Group)

