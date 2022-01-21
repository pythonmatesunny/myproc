import cv2
from django.views.generic.base import View
import dlib
import numpy as np
import face_recognition
import datetime
from django.core.files.base import ContentFile
from .models import ImageFrames
from .helpers import push_frame


def light_check(image, threshold):
    is_fine = np.mean(image) > threshold
    # (127 - 255) denotes light image
    # (0 - 127) denotes dark image
    return is_fine




SECOND_TO_CONSIDER = 2
SIZE_FOR_CENTER = 160

moreFaceTime = None
noFaceTime = None


def image_verify(img_frame):
    global moreFaceTime,noFaceTime

    face_attributes = {
        "more_faces": False,
        "no_face_for_2_sec": False,
        "centered_face":False,
    }

    img = cv2.resize(img_frame, (500, 500))
    imgOriginal = img.copy()

    (center_h, center_w) = img.shape[:2] 

    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if not light_check(imgGray, 100):
        print("QUALITY ISSUE!!!")

    faces = face_recognition.api.face_locations(img, model='hog')

    if len(faces) > 1 and moreFaceTime is None:
        print("MORE THAN ONE FACE IS PRESENT!!!")
        moreFaceTime = datetime.datetime.now()

    elif len(faces) < 1 and noFaceTime is None:
        print("NO FACE VISIBLE!!!")
        noFaceTime = datetime.datetime.now()
  

    if noFaceTime:
        print((datetime.datetime.now() - noFaceTime).seconds)
 

    if moreFaceTime is not None and (datetime.datetime.now() - moreFaceTime).seconds >= SECOND_TO_CONSIDER:
        print(f"MORE FACES FOR {SECOND_TO_CONSIDER} SEC")
        face_attributes['more_faces'] = True

    elif noFaceTime is not None and (datetime.datetime.now() - noFaceTime).seconds >= SECOND_TO_CONSIDER:
        print(f"NO FACES FOR {SECOND_TO_CONSIDER} SEC")
        face_attributes['no_face_for_2_sec'] = True
 




    # face absence for longer duration

    if moreFaceTime is not None and (datetime.datetime.now() - moreFaceTime).seconds >= SECOND_TO_CONSIDER*2:
        print(f"MORE FACES FOR {SECOND_TO_CONSIDER} SEC")
        
    elif noFaceTime is not None and (datetime.datetime.now() - noFaceTime).seconds >= SECOND_TO_CONSIDER*2:
        print(f"NO FACES FOR {SECOND_TO_CONSIDER} SEC")


    print('length faces ->',len(faces))
    
    if len(faces) == 1:
        for face in faces:
            x1, y1 = face[3], face[0] # ADD THIS
            x2, y2 = face[1], face[2] # ADD THIS
            x3, y3 = (x1 + x2) // 2, (y1 + y2) // 2 # ADD THIS

        
            # Uncomment to check only
            if ((center_w // 2 - SIZE_FOR_CENTER) < x3 < (center_w // 2 + SIZE_FOR_CENTER)) and \
                                ((center_h // 2 - SIZE_FOR_CENTER) < y3 < (center_h // 2 + SIZE_FOR_CENTER)):
                                face_attributes['centered_face'] = True
                


            # Will check if it is center or not
        
        
        moreFaceTime = None
        noFaceTime = None

    image_verified = True
    for _, value in face_attributes.items():
        if value:
            image_verified = False
            break
    


    if image_verified:
        print('Image has passed tests')
    else:
        print('test failed')

    return face_attributes
    




