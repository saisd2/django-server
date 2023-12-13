from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings

from focus_user.models import FocusUser, Upload, Comment
from focus_user.forms import UploadForm

from urllib.parse import urlparse

from PIL import Image

import json
import base64
import os

# create new user
@csrf_exempt
def create_user(request):
    if request.method == "POST":
        # get data
        data = json.loads(request.body.decode())
        name = data["name"]
        email = data["email"]
        password = data["password"]
        user_bio = data["bio"]

        # check email
        if User.objects.filter(email=email):
            return HttpResponse("email already has associated account", status=409)
        
        # check name
        if User.objects.filter(username=name):
            return HttpResponse("username already exists", status=409)

        # create User model
        userObj = User.objects.create_user(name, email, password)

        # connect to FocusUser model
        focus_user = FocusUser.objects.create(user=userObj, bio=user_bio)
        focus_user.save()

        return HttpResponse("new user created: " + str(focus_user))
    else:
        HttpResponse(status=400)

# for testing only - get users
@csrf_exempt
def get_users(request):
    Upload.objects.all().delete()
    info = []
    if request.method == "GET":
        users = FocusUser.objects.all()
        
        for user in users:
            followers = []
            for follower in user.followers.all():
                followers.append(follower.user.username)

            info.append({
                "name": user.user.username,
                "bio": user.bio,
                "followers": followers,
            })

        return HttpResponse(info)

# login existing user
@csrf_exempt
def login_user(request):
    print("logging in")
    data = json.loads(request.body.decode())
    username = data["name"]
    password = data["password"]

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponse("login success")
    else:
        return HttpResponse("login failed", status=400)


# logout user
@csrf_exempt
def logout_user(request):
    logout(request)
    return HttpResponse("logout success")

# follow user
@csrf_exempt
def follow_user(request):
    if request.method != "PUT":
        return HttpResponse(status=400)

    # get data
    data = json.loads(request.body.decode())
    username_to_follow = data["user"]

    # get users
    users = FocusUser.objects.all()
    user_to_follow = None
    
    for user in users:
        if user.user.username == username_to_follow:
            user_to_follow = user

    if user is None:
        return HttpResponse(username_to_follow + " does not exist")
    else:
        current_user = None

        try:
            current_user = FocusUser.objects.get(user=request.user)
        except:
            return HttpResponse("no user logged in", status=401)
        
        if current_user.user.username == username_to_follow:
            return HttpResponse("user cannot follow themselves", status=403)

        # create follow/following relationship
        user_to_follow.followers.add(current_user)
        current_user.following.add(user_to_follow)

        return HttpResponse("follow success")
    
# unfollow user
@csrf_exempt
def unfollow_user(request):
    if request.method != "PUT":
        return HttpResponse(status=400)
    
    # get data
    data = json.loads(request.body.decode())
    username_to_unfollow = data["user"]

    # get users
    users = FocusUser.objects.all()
    user_to_unfollow = None
    
    for user in users:
        if user.user.username == username_to_unfollow:
            user_to_follow = user

    if user is None:
        return HttpResponse(username_to_unfollow + " does not exist")
    else:
        current_user = None

        try:
            current_user = FocusUser.objects.get(user=request.user)
        except:
            return HttpResponse("no user logged in", status=401)

        # remove follow/following relationship
        user_to_follow.followers.remove(current_user)
        current_user.following.remove(user_to_follow)

        return HttpResponse("unfollow success")

# upload image
@csrf_exempt
def upload_image(request):
    if request.method != "POST":
        return HttpResponse(status=400)
    
    title = request.POST["title"]
    caption = request.POST["caption"]
    category = request.POST["category"]
    image = request.FILES["upload_image"]

    # check for image type
    try:
        Image.open(image)
    except:
        return HttpResponse("invalid image", status=415)

    current_user = None

    # check for login
    try:
        current_user = FocusUser.objects.get(user=request.user)
    except:
        return HttpResponse("no user logged in", status=401)
    
    upload = Upload()
    upload.title = title
    upload.caption = caption
    upload.category = category
    upload.image = image
    upload.average_rating = 0
    upload.total_ratings = 0
    upload.upload_user = current_user

    upload.save()
    return HttpResponse("image uploaded")

# create comment
@csrf_exempt
def create_comment(request):
    if request.method != "POST":
        HttpResponse(400)

    # get data
    data = json.loads(request.body.decode())
    upload_id = data["upload_id"]
    comment_text = data["comment"]

    current_user = None
    
    # check for login
    try:
        current_user = FocusUser.objects.get(user=request.user)
    except:
        return HttpResponse("no user logged in", status=401)
    
    comment = Comment()

    comment.upload = Upload.objects.get(id=upload_id)
    comment.user = current_user
    comment.comment = comment_text

    comment.save()

    return HttpResponse("comment created")

# get filtered images
@csrf_exempt
def get_filtered_uploads(request, category):
    # Filter Upload objects based on the provided category
    filtered_uploads = Upload.objects.filter(category=category)

    # Create a list to store information about each filtered upload
    uploads_info = []

    for upload in filtered_uploads:
        with open("." + upload.image.url, mode='rb') as file:
            img = file.read()
        encoded_image = base64.encodebytes(img).decode('utf-8')

        uploads_info.append({
            "title": upload.title,
            "caption": upload.caption,
            "average_rating": upload.average_rating,
            "total_ratings": upload.total_ratings,
            "uploaded_by": upload.upload_user.user.username,
            "image_data": encoded_image,
            "image_id": upload.id
        })

    return HttpResponse(json.dumps(uploads_info))


# get all images
@csrf_exempt
def get_uploads(request):
    if request.method != "GET":
        return HttpResponse(400)
    
    upload_objects = Upload.objects.all()
    all_uploads = []

    for upload in upload_objects:
        with open("." + upload.image.url, mode='rb') as file:
            img = file.read()
        encoded_image = base64.encodebytes(img).decode('utf-8')

        all_uploads.append({
            "title": upload.title,
            "caption": upload.caption,
            "category": upload.category,
            "average_rating": upload.average_rating,
            "total_ratings": upload.total_ratings,
            "uploaded_by": upload.upload_user.user.username,
            "image_data": encoded_image,
            "image_id": upload.id
        })

    return HttpResponse(json.dumps(all_uploads))

# get specific upload
@csrf_exempt
def handle_upload_by_id(request, upload_id):
    if request.method == "GET":
        upload = None

        try:
            upload = Upload.objects.get(id=upload_id)
        except:
            HttpResponse("image does not exist", 404)

        if upload is None:
            return HttpResponse("image does not exist", 404)
        
        with open("." + upload.image.url, mode='rb') as file:
            img = file.read()
        encoded_image = base64.encodebytes(img).decode('utf-8')

        comment_data = []
        comments = upload.comments.all()

        for comment in comments:
            comment_data.append({
                "comment" : comment.comment,
                "user" : comment.user.user.username
            })

        data = {
            "title": upload.title,
            "caption": upload.caption,
            "category": upload.category,
            "average_rating": upload.average_rating,
            "total_ratings": upload.total_ratings,
            "uploaded_by": upload.upload_user.user.username,
            "image_data": encoded_image,
            "image_id": upload.id,
            "comments": comment_data
        }

        return HttpResponse(json.dumps(data))
    if request.method == "DELETE":
        to_delete = None

        try:
            to_delete = Upload.objects.get(id=upload_id)
        except:
            return HttpResponse("upload with id " + upload_id + " does not exist", 404)
        
        if to_delete == None:
            return HttpResponse("upload with id " + upload_id + " does not exist", 404)
        
        to_delete.delete()

        return HttpResponse("upload " + upload_id + " deleted")
    else:
        return HttpResponse(400)

# get logged in user
@csrf_exempt
def get_logged_in_user(request):
    if request.method != "GET":
        return HttpResponse(400)

    # check for login
    current_user = None

    try:
        current_user = FocusUser.objects.get(user=request.user)
    except:
        return HttpResponse("no user logged in", status=401)
    
    followers = []

    for follower in current_user.followers.all():
        followers.append(follower.user.username)
    
    following = []

    for follow in current_user.following.all():
        following.append(follow.user.username)

    upload_ids = []

    for upload in current_user.uploads.all():
        upload_ids.append(upload.id)

    user_info = {
        "username" : current_user.user.username,
        "bio" : current_user.bio,
        "followers" : followers,
        "following" : following,
        "upload_ids": upload_ids
    }

    return HttpResponse(json.dumps(user_info))
    
# get specific user
@csrf_exempt
def get_user(request, user):
    if request.method != "GET":
        return HttpResponse(400)
    
    # find user
    requested_user = None

    try:
        requested_user = User.objects.get(username=user)
    except:
        return HttpResponse("user " + user + " does not exist", 404)

    # find user
    focus_user = FocusUser.objects.get(user=requested_user)

    # format data
    followers = []

    for follower in focus_user.followers.all():
        followers.append(follower.user.username)
    
    following = []

    for follow in focus_user.following.all():
        following.append(follow.user.username)

    upload_ids = []

    for upload in focus_user.uploads.all():
        upload_ids.append(upload.id)

    user_info = {
        "username" : focus_user.user.username,
        "bio" : focus_user.bio,
        "followers" : followers,
        "following" : following
    }

    return HttpResponse(json.dumps(user_info))

# add rating
@csrf_exempt
def add_rating(request):
    if request.method != "POST":
        return HttpResponse(400)

    # get data
    data = json.loads(request.body.decode())
    upload_id = data["upload_id"]
    rating = data["rating"]

    current_user = None
    

    upload = Upload.objects.get(id=upload_id)

    # check for login
    try:
        current_user = FocusUser.objects.get(user=request.user)
    except:
        return HttpResponse("no user logged in", status=401)
    
    if upload.raters.filter(user=current_user.user).exists():
        return HttpResponse("this image has already been rated by the user", 401)
    else:
        # track what user has rated
        upload.raters.add(current_user)
        current_user.rated_uploads.add(upload)

        # update rating
        upload.total_ratings += 1
        upload.average_rating = ((upload.average_rating * (upload.total_ratings - 1)) + rating) / upload.total_ratings

        print(upload.total_ratings)
        print(upload.average_rating)

        upload.save()
        current_user.save()

    return HttpResponse("rating added")