from django.urls import reverse
from django.core.files.base import ContentFile
import cv2
from .models import ImageFrames
from .models import ImageFrames,FLag
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken






#save frames in DB
def push_frame(img_frame,mode,img_attr,user=None):
    is_success, im_buf_arr = cv2.imencode(".jpg", img_frame)
    byte_im = im_buf_arr.tobytes()
    con_image = ContentFile(byte_im)
    image_frame = ImageFrames()
    image_frame.image_frame.save(name = 'test.jpg',content = con_image ,save=False)
    image_frame.save()

    for key in img_attr.keys():
  
        if (key=="centered_face" and img_attr[key]==False):
            flag,created=FLag.objects.get_or_create(flag_name="face_not_centered")
            image_frame.flagged_as.add(flag)
            image_frame.is_red_flagged=True
        elif (key=="centered_face" and img_attr[key]==True):
            continue


        elif key == 'MobilePhone' and img_attr[key] == True:
            flag,created=FLag.objects.get_or_create(flag_name=key)
            image_frame.flagged_as.add(flag)
            image_frame.is_red_flagged=True

        elif key == 'Sunglasses' and img_attr[key] == True:
            flag,created=FLag.objects.get_or_create(flag_name=key)
            image_frame.flagged_as.add(flag)
            image_frame.is_red_flagged=True
        elif img_attr[key] == True:
            flag,created=FLag.objects.get_or_create(flag_name=key)
            image_frame.flagged_as.add(flag)
            image_frame.is_red_flagged=True


    

    if mode != 'register':
        image_frame.frame_captype = 'mentoring'
    else:
        image_frame.frame_captype = 'register'
    # image_frame.user=user
    image_frame.save()



def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'url':reverse("aws_app:redirect")

    }

def getcurrent_user (token):
    jwt_object = JWTAuthentication()
    validated_token = jwt_object.get_validated_token(token)
    user = jwt_object.get_user(validated_token)
    return user