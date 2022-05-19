from django.shortcuts import render,reverse,redirect,get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib import messages
import face_recognition
from face_recognition.face_recognition_cli import image_files_in_folder
import cv2
from PIL import Image, ImageDraw
from sklearn import neighbors
import numpy as np
import pickle
import os
import shutil
import math
import datetime
from .models import CustomUser,Attendance,Student
from .utils import check_student
from django.conf import settings

BASE_DIR = settings.BASE_DIR
MODEL_DATA_PATH = os.path.join(BASE_DIR,"media/model_data/")
MODEL = "hog"


def create_dataset_util(id,camera=0):
    if(os.path.exists(MODEL_DATA_PATH + "dataset/")==False):
        os.makedirs(MODEL_DATA_PATH + "dataset/")
    dataset_dir = MODEL_DATA_PATH + "dataset/"

    if(os.path.exists(dataset_dir+str(id))==False):
        os.makedirs(dataset_dir+str(id))
    directory=dataset_dir+str(id)

    video = cv2.VideoCapture(camera)

    # Our dataset naming counter
    sampleNum = 0
    # Capturing the faces one by one and detect the faces and showing it on the window
    while(True):
        # Grab a single frame of video
        ret,frame = video.read()

        if not ret:
            video.release()
            cv2.destroyAllWindows()
            return False

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        face_bounding_boxes = face_recognition.face_locations(rgb_small_frame,model = MODEL)

        # If there are no people (or too many people) in a frame, skip it.
        if len(face_bounding_boxes)!=1:
            continue

        top,right,bottom,left = face_bounding_boxes[0]
        top *= 4
        bottom *= 4
        right *= 4
        left *= 4

        sampleNum = sampleNum+1
        face_image_array = frame[top:bottom, left:right]
        final_image = Image.fromarray(face_image_array)
        final_image.save(directory+'/'+str(sampleNum)+'.jpg')
        cv2.rectangle(frame,(left,top),(right,bottom),(0,255,0),1)
        cv2.waitKey(100)
        cv2.imshow("camera",frame)
        cv2.waitKey(1)
        #To get out of the loop
        if(sampleNum>120):
            break
    #Stoping the videostream
    video.release()
    # destroying all the windows
    cv2.destroyAllWindows()
    return True


def train_model_util():
    X = []
    y = []
    train_dir = MODEL_DATA_PATH + "dataset/"
    if os.path.exists(train_dir) and len(os.listdir(train_dir))==0:
        return False,{"message":"No dataset found to create model"}

    model_trained_for = []
    # Loop through each person in the training set
    for class_dir in os.listdir(train_dir):
        if not os.path.isdir(os.path.join(train_dir, class_dir)):
            continue
        try:
            if Student.objects.get(user_id=class_dir,dataset_created=True):
                # Loop through each training image for the current person
                for img_path in image_files_in_folder(os.path.join(train_dir, class_dir)):
                    image = face_recognition.load_image_file(img_path)
                    face_bounding_boxes = face_recognition.face_locations(image)

                    if len(face_bounding_boxes) != 1:
                        # If there are no people (or too many people) in a training image, skip the image.
                        os.remove(img_path)
                    else:
                        # Add face encoding for current image to the training set
                        X.append(face_recognition.face_encodings(image, known_face_locations=face_bounding_boxes)[0])
                        y.append(class_dir)

                model_trained_for.append(str(class_dir))
        except Exception as e:
            continue

    if len(X)==0:
        return False,{"message":"No dataset found to create model"}

    # Determine how many neighbors to use for weighting in the KNN classifier
    n_neighbors = int(round(math.sqrt(len(X))))

    knn_algo = "ball_tree"

    # Create and train the KNN classifier
    knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algo, weights='distance')
    knn_clf.fit(X, y)

    # Save the trained KNN classifier
    model_save_path = os.path.join(MODEL_DATA_PATH,"trained_knn_model.clf")
    with open(model_save_path, 'wb') as f:
        pickle.dump(knn_clf, f)

    for id in model_trained_for:
        if check_student(id):
            user = CustomUser.objects.get(id=id)
            user.student.model_trained = True
            user.student.save()
    return True,{}

def predict(X_frame,distance_threshold=0.5):
    model_path = MODEL_DATA_PATH + "trained_knn_model.clf"
    try:
        with open(model_path, 'rb') as f:
            knn_clf = pickle.load(f)
    except Exception as e:
        return False,{"message":"Trained model not found, train a model first to mark attandace"}

    X_face_locations = face_recognition.face_locations(X_frame)

    # If no faces are found in the image, return an empty result.
    if len(X_face_locations) == 0:
        return True,[]

    # Find encodings for faces in the test image
    faces_encodings = face_recognition.face_encodings(X_frame, known_face_locations=X_face_locations)

    # Use the KNN model to find the best matches for the test face
    closest_distances = knn_clf.kneighbors(faces_encodings, n_neighbors=1)
    are_matches = [closest_distances[0][i][0] <= distance_threshold for i in range(len(X_face_locations))]

    # Predict classes and remove classifications that aren't within the threshold
    return True,[(pred, loc) if rec else ("unknown", loc) for pred, loc, rec in zip(knn_clf.predict(faces_encodings), X_face_locations, are_matches)]


def show_prediction_labels_on_image(frame, predictions, attendance_marked_for_students):
    pil_image = Image.fromarray(frame)
    draw = ImageDraw.Draw(pil_image)

    for id, (top, right, bottom, left) in predictions:
        # enlarge the predictions for the full sized image.
        if id!="unknown":
            if id in attendance_marked_for_students.keys():
                name = attendance_marked_for_students[id]
            else:
                today = datetime.date.today()
                user = CustomUser.objects.get(id=id)
                name = user.first_name + " " + user.last_name
                attendance_marked_for_students[id] = name
                try:
                    query = Attendance.objects.get(user_id=user.student.id,date=today)
                except :
                    query = None 
                if query is None:
                    image_path = os.path.join(BASE_DIR,f"media/attendance_pic/{str(user.id)}/{str(today)}.jpg")
                    pil_image.save(image_path)
                    attendance=Attendance(user=user.student,date=today,present=True,path_to_picture = image_path)
                    attendance.save()
                else:
                    query.present=True
                    query.save()
        else:
            name = id
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4
        # Draw a box around the face using the Pillow module
        draw.rectangle(((left, top), (right, bottom)), outline=(0, 255, 0))

        # There's a bug in Pillow where it blows up with non-UTF-8 text
        # when using the default bitmap font
        name = name.encode("UTF-8")

        # Draw a label with a name below the face
        text_width, text_height = draw.textsize(name)
        draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 255, 0), outline=(0, 255, 0))
        draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))

    # Remove the drawing library from memory as per the Pillow docs.
    del draw
    # Save image in open-cv format to be able to show it.
    opencvimage = np.array(pil_image)
    return opencvimage,attendance_marked_for_students

def create_dataset(request):
    students_without_dataset_created = Student.objects.filter(dataset_created=False)
    context = {'students_without_dataset_created':students_without_dataset_created}
    return render(request,"admin_templates/create_dataset.html",context)

def create_dataset_for_student(request,id):
    data = get_object_or_404(Student,user_id=id)
    context = {'data':data}
    if request.method == "POST":
        if check_student(id):
            success = create_dataset_util(id)
            if success:
                user = CustomUser.objects.get(id=id)
                user.student.dataset_created = True
                username = user.first_name + " " + user.last_name
                user.student.save()
                messages.add_message(request,messages.SUCCESS,f"Dataset created successfully for {username}")
            else:
                # if(os.path.exists(os.path.join(MODEL_DATA_PATH,f"dataset/{str(id)}"))):
                #     print("removing...")
                #     shutil.rmtree(os.path.join(MODEL_DATA_PATH,f"dataset/{str(id)}"))
                messages.add_message(request,messages.ERROR,"Something went wrong...")
        else:
            messages.add_message(request,messages.ERROR,"Student not found!")
        return HttpResponseRedirect(reverse("create_dataset"))
    return render(request,"admin_templates/create_dataset_for_student.html",context)
    

def train_model(request):
    students_without_model_trained = Student.objects.filter(dataset_created=True,model_trained=False)
    context = {'students_without_model_trained':students_without_model_trained}
    if request.method == "POST":
        print("training...")
        success,message = train_model_util()
        if success:
            messages.add_message(request,messages.SUCCESS,"Model trained successfully")
        else:
            messages.add_message(request,messages.ERROR,message["message"])
        return HttpResponseRedirect(reverse("train_model"))
    return render(request,"admin_templates/train_model.html",context)


def mark_attendance(request):
    if request.method == "POST":
        camera = 0
        video = cv2.VideoCapture(camera)
        attendance_marked_for_students = dict()
        while(True):
            # Grab a single frame of video
            ret,frame = video.read()
            if not ret:
                messages.add_message(request,messages.ERROR,"Something went wrong...")
                video.release()
                cv2.destroyAllWindows()
                return HttpResponseRedirect(reverse("mark_attendance"))

            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            success,predictions = predict(small_frame)
            if not success:
                #predictions will contain our error message
                messages.add_message(request,messages.ERROR,predictions["message"])
                video.release()
                cv2.destroyAllWindows()
                return HttpResponseRedirect(reverse("mark_attendance"))

            frame,attendance_marked_for_students = show_prediction_labels_on_image(frame, predictions,attendance_marked_for_students)
            cv2.imshow('press q to quit', frame)
            if ord('q') == cv2.waitKey(10):
                break

        video.release()
        cv2.destroyAllWindows()
        return HttpResponseRedirect(reverse("mark_attendance"))
    return render(request,"admin_templates/mark_attendance.html")