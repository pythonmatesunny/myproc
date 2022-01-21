from django.db import models
from django.conf import settings
from django.core import validators
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat, slice_filter
import secrets
import boto3
import os
from datetime import datetime as dt
from django.contrib.auth.models import User
import datetime
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser,AbstractUser
)
from django.contrib.auth.hashers import make_password



def upload_to(instance, filename):
    return f"aws_mage_comp_{secrets.token_hex()}.{filename.split('.')[-1]}"

def profile_size(value):
    if value.size > 1024 * 1024 * 0.5:
        raise ValidationError(f"Image size is {filesizeformat(value.size)} required size {filesizeformat(1024 * 1024 * 0.5)}")


client=boto3.client('rekognition', region_name="ap-south-1", aws_access_key_id = settings.AWS_ACCESS_KEY_ID, aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY)


def compare_faces(sourceFile, targetFile):
    try:
        sourceFile = sourceFile.open('rb').read()
        targetFile = targetFile.open('rb').read()
        response=client.compare_faces(SimilarityThreshold=10,
                                    SourceImage={'Bytes': sourceFile},
                                    TargetImage={'Bytes': targetFile})
    except:
        response=client.compare_faces(SimilarityThreshold=10,
                            SourceImage={'Bytes': sourceFile},
                            TargetImage={'Bytes': targetFile})
    return response


def eyes_moment_detect(targetFile):
    try:
        targetFile = targetFile.open('rb').read()
        
        response = client.detect_faces(Image={'Bytes':targetFile},Attributes=['ALL'])
    except:
         response = client.detect_faces(Image={'Bytes':targetFile},Attributes=['ALL'])
    return response


def mobile_detaction(targetFile):
    try:
        targetFile = targetFile.open('rb').read()
        
        response = client.detect_labels(Image={'Bytes':targetFile},MaxLabels=4)
    except:
         response = client.detect_labels(Image={'Bytes':targetFile}, MaxLabels=4)
    return response


def PPE_detaction_test(targetFile):
    try:
        targetFile = targetFile.open('rb').read()
        
        response = client.detect_protective_equipment(
                Image={'Bytes':targetFile},
                SummarizationAttributes={
                    'MinConfidence': 90,
                    'RequiredEquipmentTypes': [
                        'FACE_COVER',
                        'HEAD_COVER',
                        'HAND_COVER',
                    ]
                }
            )
    except:
        response = client.detect_protective_equipment(
                Image={'Bytes': targetFile},
                SummarizationAttributes={
                    'MinConfidence': 90,
                    'RequiredEquipmentTypes': [
                        'FACE_COVER',
                        'HEAD_COVER',
                        'HAND_COVER',
                    ]
                }
            )
    return response


def upload_frame_loc():
    dtString =  dt.now().strftime('%d-%m-%Y')
    path = f'media\camera_frames\camera_{dtString}'

    if not os.path.exists(path):
        os.makedirs(path)

    return path


class FLag(models.Model):
    FLAG_NAMES = (
    ('quality_issue', 'quality_issue'),
    ('more_faces', 'more_faces'),
    ('noface_for_2_sec', 'noface_for_2_sec'),
    ('face_not_centered', 'face_not_centered'),
    ('face_covered', 'face_covered'),
    ('mobile_detection', 'mobile_detection'),
    ('sun_glasses', 'sun_glasses'),
    ('head_covered', 'head_covered'),
    )

    flag_name = models.CharField(max_length=30,choices=FLAG_NAMES)
    flagged_time=models.DateTimeField(auto_now_add=True ,null=True,blank=True)
    

    class Meta:
        verbose_name_plural = 'Flag'

    def __str__(self):
        return self.flag_name


class ImageFrames(models.Model):

    CAPTURE_TYPE = (
    ('register', 'REGISTER'),
    ('mentoring', 'MENTORING'),
    )
    
    time_stamp = models.DateTimeField(auto_now_add=True)
    image_frame = models.FileField(upload_to = 'camera_frames',null=True,blank=True,max_length=500,validators=[
        validators.FileExtensionValidator(
                                   allowed_extensions=validators.get_available_image_extensions(),
                                   message="'%(extension)s' not valid Image."
                               ), profile_size],)
    flagged_as = models.ManyToManyField('FLag',blank=True)
    frame_captype = models.CharField(max_length=30,choices=CAPTURE_TYPE)
    is_red_flagged=models.BooleanField(default=False)
    attempt_id=models.IntegerField(default=0)
    test_id=models.IntegerField(default=0)
    client_id=models.IntegerField(default=0)
    profile_id=models.IntegerField(default=0)

    user=models.ForeignKey('MyUser',on_delete=models.CASCADE,null=True,blank=True)



class MyUserManager(BaseUserManager):

    def create_user(self, access_key,  password=None):
        if not access_key:
            raise ValueError('access_key is required')
        user = self.model(
            access_key=access_key
        )
        user.set_password(access_key)
        user.save(using=self._db)
        return user

    def create_superuser(self, access_key,  password=None):
  
        user = self.create_user(
            access_key=access_key,
            password=access_key,
    
        )
        user.is_admin = True
        user.is_staff=True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):

    name=models.CharField(max_length=100,null=True,blank=True)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        null=True,
        blank=True
    )
    access_key=models.CharField(max_length=255,unique=True)


    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff=models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'access_key'
    REQUIRED_FIELDS = []


    def get_full_name(self):
        return self.email   


    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    def __str__(self):
        return  str(self.access_key)


    


    
