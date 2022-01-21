from django.shortcuts import render,redirect
from rest_framework.views import APIView
import json
from django.views.generic import View
from django.http.response import JsonResponse, StreamingHttpResponse,HttpResponse
from .Camera import image_verify
import cv2
import numpy as np
from django.views.decorators.csrf import csrf_exempt
import base64
from.models import ImageFrames
from django.views import View
from django.utils.decorators import method_decorator
from .helpers import push_frame
import face_recognition
from .models import compare_faces,eyes_moment_detect,PPE_detaction_test,mobile_detaction,MyUser
from rest_framework.generics import ListAPIView,GenericAPIView,RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .serializer import FlaggedImagesSerializer
from rest_framework.renderers import TemplateHTMLRenderer,JSONRenderer
from rest_framework.decorators import authentication_classes,permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from .helpers import get_tokens_for_user
from django.contrib.auth import authenticate,login,logout
from .helpers import getcurrent_user
from .serializer import MyUserSerializer




def test_compare():
    first_img = ImageFrames.objects.all().first().image_frame.open('rb').read()
    last_img = ImageFrames.objects.all().last().image_frame.open('rb').read()

    encoded_first_img = face_recognition.face_encodings(first_img)[0]
    
    encoded_2nd_img = face_recognition.face_encodings(last_img)[0]

    encoded_2nd_img = face_recognition.face_encodings(last_img)[0]
    res = face_recognition.compare_faces([encoded_first_img], encoded_2nd_img, tolerance=0.5)



def data_uri_to_cv2_img(uri):
    encoded_data = uri.split(',')[1]
    decodestring  = base64.b64decode(encoded_data)
    nparr = np.fromstring(decodestring, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


def light_check(image, threshold):
    is_light = np.mean(image) > threshold
    # (127 - 255) denotes light image
    # (0 - 127) denotes dark image
    return is_light



@csrf_exempt
def test_image(request):
    
    actual_image = data_uri_to_cv2_img(request.body.decode('utf-8'))
    img_attr = image_verify(actual_image)

    #AWS DETACTION-------
    try:
        success, encoded_image = cv2.imencode('.png', actual_image)
    except:
        success, encoded_image = cv2.imencode('.jpg', actual_image)
    
    byte_image = encoded_image.tobytes()
    
    try:
        ppe_res=PPE_detaction_test(byte_image)
        for part in ppe_res['Persons'][0]['BodyParts']:
            if part['Name']=='FACE':
                if part['EquipmentDetections'][0]['CoversBodyPart']['Value']==True:
                    img_attr[f"{part['Name']}_covered"]=True
        
    except:
        img_attr[f"FACE_covered"]=False
    try:
        mobile_res=mobile_detaction(byte_image)
        for label in mobile_res['Labels']:
            if label['Name']=='Phone' or label['Name']=='Mobile Phone' :
                img_attr['MobilePhone']=True
            else:
                img_attr['MobilePhone']=False

    except:
         img_attr['MobilePhone']=False

    try:
        eyes_resp = eyes_moment_detect(byte_image)
        if eyes_resp['FaceDetails'][0]['Sunglasses']['Value']==True:
            img_attr['Sunglasses']=True
        else:
            img_attr['Sunglasses']=False

    except:
         img_attr['MobilePhone']=False

    return JsonResponse({'status':'done',
                          'image':img_attr},safe=False)



class RedirectView(View):

    def get(self,request):
        return redirect("aws_app:index")

class Mentoring(APIView):
    permission_classes = [AllowAny]
    authentication_classes=[SessionAuthentication]
    renderer_classes = [ TemplateHTMLRenderer ]
    
    def get(self,request):
        return Response({"Mentoring":False},template_name='aws_app/index.html',)




@method_decorator(csrf_exempt, name='dispatch')
class SaveFrame(APIView):
    permission_classes = [AllowAny]
    authentication_classes=[SessionAuthentication]
    

    # Get all Saved Images
    def get(self,request):
        images = ImageFrames.objects.all().order_by('-time_stamp')
        response =  render(request, 'aws_app/result2.html',{
            'images_frames':images,
            
        })

        return response

    def post(self,request):
        try:
            # Frame in bytes and format it
            frame_data = request.data
            actual_image = data_uri_to_cv2_img(frame_data['img_frame'])
            #Image Check attributes
            img_attr = image_verify(actual_image)


            #SUNNY CHANGES FOR AWS DETACTION-----------
            try:
                success, encoded_image = cv2.imencode('.png', actual_image)
            except:
                success, encoded_image = cv2.imencode('.jpg', actual_image)
            
            byte_image = encoded_image.tobytes()
        


            #Push Frame in DB only if mentoring phase or take button clicked
            buttonclick = frame_data['buttonclick']
            phase = (frame_data['mode'] == 'mentoring')
            
            if any([buttonclick,phase]):
                #we will make calls to client server for question number

                try:
                    ppe_res=PPE_detaction_test(byte_image)
                    for part in ppe_res['Persons'][0]['BodyParts']:
                        if part['Name']=='FACE':
                            if part['EquipmentDetections'][0]['CoversBodyPart']['Value']==True:
                                img_attr[f"{part['Name']}_covered"]=True
                  
                except:
                    pass


                try:
                    mobile_res=mobile_detaction(byte_image)
                    for label in mobile_res['Labels']:
                        if label['Name']=='Phone' or label['Name']=='Mobile Phone':
                            img_attr['MobilePhone']=True
                except:
                    pass


                try:
                    eyes_resp = eyes_moment_detect(byte_image)
                    if eyes_resp['FaceDetails'][0]['Sunglasses']['Value']==True:
                        img_attr['Sunglasses']=True
                except:
                    pass


                
                push_frame(actual_image,frame_data['mode'],img_attr)
        
            last_img = ImageFrames.objects.filter(frame_captype = frame_data['mode'],).last().image_frame


            
            res = compare_faces(last_img,last_img)
            eyes_resp = eyes_moment_detect(last_img)

            if res['FaceMatches'][0]['Similarity'] > 90 and eyes_resp['FaceDetails'][0]['EyesOpen']['Value']:
                compare_status = True
            else:
                compare_status = False
            
            
            response =  JsonResponse({'compare_status':compare_status,'image_attr':img_attr},safe=False)
        
        except Exception as e:
            print(' Exception----> ',e)
            response =  JsonResponse({'status':'error in mentoring {}'.format(str(e)),'compare_status':False},safe=False)

        return response
        


    


class ExamMentoring(APIView):
    permission_classes = [AllowAny]
    authentication_classes=[SessionAuthentication]
    renderer_classes = [ TemplateHTMLRenderer ]
    
    def get(self,request):
        return Response({"Mentoring":True},template_name='aws_app/index.html',)




class ImageView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = ImageFrames.objects.all()
    serializer_class = FlaggedImagesSerializer
    lookup_field = 'id'





class FlaggedImagesView(ListAPIView,RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = ImageFrames.objects.all()

    def list(self, request, *args, **kwargs):
        try:
            flag1 = request.query_params.get('flag1','')
            flag2 = request.query_params.get('flag2','')
            flag3 = request.query_params.get('flag3','')
            flag4 = request.query_params.get('flag4','')
            user_id = request.query_params.get('user_id',None)
            
            if not all([flag1,flag2,flag3,flag4]):
                imageframes = self.get_queryset()
            else:
                imageframes = self.get_queryset().filter(Q(flagged_as__flag_name = flag1) | Q(flagged_as__flag_name = flag2) |  Q(flagged_as__flag_name = flag3) |  Q(flagged_as__flag_name = flag4 ))
            
            # if user_id:
            #     imageframes.filter(user_id)
            flagged_images = FlaggedImagesSerializer(imageframes,many=True).data
            response =  Response(flagged_images,200)
            return response
        except Exception as e:
            response =  Response('err: {}'.format(str(e)),400)
        
        return response






@method_decorator(csrf_exempt, name='dispatch')
class registration(APIView):
    permission_classes=[AllowAny]
    
    def post(self,request):
        try:
            
            query=request.data

            serialized_data = MyUserSerializer(data = request.data)
            if serialized_data.is_valid(raise_exception=True):
                user=MyUser.objects.create_user(access_key=query['access_key'],password=query['access_key'])
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                tokens=get_tokens_for_user(user)
                return Response(tokens)

        except Exception as e:
            return Response({"error":"bad req {}".format(str(e))},status=400)




class GetLoginToken(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        user=MyUser.objects.filter(access_key=request.data.get("access_key")).first()
        password=request.data.get("access_key")


        if user is not None :

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            tokens=get_tokens_for_user(user)
            return Response(tokens)
        return Response({"detail":"No active account found with the given credentials"},status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        


        
        




    

















