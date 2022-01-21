from django.db.models import fields
from rest_framework.serializers import ModelSerializer
from .models import ImageFrames,FLag, MyUser


class FLagSerializer(ModelSerializer):
    class Meta:
        model = FLag
        fields = '__all__'


class FlaggedImagesSerializer(ModelSerializer):
    flagged_as = FLagSerializer(read_only = True,many = True)
    class Meta:
        model = ImageFrames
        fields = '__all__'




class MyUserSerializer(ModelSerializer):
    class Meta:
        model = MyUser
        fields = '__all__'