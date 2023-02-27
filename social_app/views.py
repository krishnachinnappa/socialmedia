from django.shortcuts import render, redirect
# this model is used to check the unique ness of the user. it can also be
# configured to any attributes, like email.
from django.contrib.auth.models import User, auth
from django.contrib import messages
from social_app.models import Profile, Post, LikePost, FollowersCount
from django.contrib.auth.decorators import login_required
from itertools import chain
# email configurations
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMessage
from django.conf import settings as conf_settings
import random, os
from django.shortcuts import get_object_or_404
# Create your views here.

@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    user_following_list = []
    feed = []

    # Index page is the main page where all the post feed will appear to the user from his followers.
    user_following = FollowersCount.objects.filter(follower=request.user.username)

    for users in user_following:
        user_following_list.append(users.user)

    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)
        feed.append(feed_lists)

    feed_list = list(chain(*feed))

    # user suggestion starts
    all_users = User.objects.all()
    user_following_all = []

    for user in user_following:
        user_list = User.objects.get(username = user.user)
        user_following_all.append(user_list)

    #  for new friend suggestions in his feed.
    new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list = [x for x in list(new_suggestions_list) if (x not in list(current_user))]
    random.shuffle(final_suggestions_list)

    username_profile = []
    username_profile_list = []

    for users in final_suggestions_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)

    suggestions_username_profile_list = list(chain(*username_profile_list))
    return render(request, 'index.html', {'user_profile': user_profile, 'posts': feed_list,'suggestions_username_profile_list': suggestions_username_profile_list[:4]})

# USer registration.
def signup(request):
    if request.method == 'POST':
        # it takes the value for the name field.
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            # The filter() method is used to filter your search, and allows you to return only the rows that matches the search term.
            if User.objects.filter(email = email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username = username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username = username, email = email, password = password)
                mydict = {'username': username}
                # log user in and redirect to settings page
                user_login = auth.authenticate(username = username, password = password)
                auth.login(request, user_login)
                user.save()
                # create a profile object for the new user
                user_model = User.objects.get(username = username)
                new_profile = Profile.objects.create(user = user_model, id_user = user_model.id)
                new_profile.save()

                # email connection
                html_template = 'success.html'
                html_message = render_to_string(html_template, context=mydict)
                subject = 'Welcome to Connect...'
                email_from = conf_settings.EMAIL_HOST_USER
                recipient_list = [user.email, ]
                message = EmailMessage(subject, html_message,
                                       email_from, recipient_list)
                message.content_subtype = 'html'
                message.send()
                return redirect('settings')
    else:
        return render(request, 'signup.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # using user authenticate
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Crendentials invalid')
            return redirect('signin')
    else:
        return render(request, 'signin.html')


@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')


@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        if request.FILES.get('image') == None:
            image = user_profile.profileimg
            bio = request.POST['bio']
            location = request.POST['location']
            # HTML render
            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()

        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        return redirect('settings')
    return render(request, 'setting.html', {'user_profile': user_profile})


@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']
        email = request.user.email
        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

        # # email generation
        subject = 'Happy that you are connecting to real world...'
        content = f'Hi, {user} thank you for uploading. Get connected to people.'
        email_from = conf_settings.EMAIL_HOST_USER
        recipient_list = [email, ]
        # send_mail(subject, message, email_from, recipient_list)
        # return redirect('/')

        email = EmailMessage(
            subject,
            content,
            email_from,
            recipient_list,
        )
        if request.FILES:
            uploaded_file = request.FILES[
                'image_upload']  # file is the name value which you have provided in form for file field
            email.attach(uploaded_file.name, uploaded_file.read(), uploaded_file.content_type)
            email.send()
        return redirect('/')
    else:
        return redirect('/')


# edited
@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list = []

        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)

    username_profile_list = list(chain(*username_profile_list))
    return render(request, 'search.html', {'user_profile': user_profile, 'username_profile_list': username_profile_list})



@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')
    post = Post.objects.get(id=post_id)
    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes = post.no_of_likes + 1
        post.save()
        return redirect('/')
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes - 1
        post.save()
        return redirect('/')

@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_post_length = len(user_posts)

    follower = request.user.username
    user = pk

    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
    }
    return render(request, 'profile.html', context)

@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/'+user)
    else:
        return redirect('/')

# self profile
def self_profile(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    context = {
        'user_profile': user_profile
    }
    return render(request,'profile.html', context)


def deleteProduct(request, pk):
    prod = Post.objects.filter(id=pk)
    prod.delete()
    messages.success(request, "Product Deleted Successfuly")
    return redirect('/')

