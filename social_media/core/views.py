from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse
from .models import Profile, Post, LikePost, FollowersCount
from django.views.decorators.cache import never_cache
from itertools import chain
import random


# Create your views here.
@never_cache
def admin_dashboard(request):
    if request.user.is_staff:
        return render(request, 'admin_dashboard.html')
    else:
        return redirect('signup')
def all_users(request):
    if request.user.is_staff:
        if request.method == "POST":
            delete_user_id = request.POST.get('deleteUserId')
            if delete_user_id:
                try:
                    user_to_delete = User.objects.get(pk=delete_user_id)
                    user_to_delete.delete()
                    messages.success(request, 'User deleted successfully')
                except User.DoesNotExist:
                    messages.error(request, 'User not found')

                return redirect('all_users')

            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']
            confirmPassword = request.POST['confirmPassword']

            if password == confirmPassword:
                if User.objects.filter(email=email).exists():
                    messages.info(request, 'Email Taken')
                    return redirect('all_users')
                elif User.objects.filter(username=username).exists():
                    messages.info(request, 'Username Taken')
                    return redirect('all_users')
                else:
                    user = User.objects.create_user(username=username, email=email, password=password)
                    user.save()

                    user_login = auth.authenticate(username=username, password=password)
                    auth.login(request, user_login)

                    user_model = User.objects.get(username=username)
                    new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                    new_profile.save()
                    return redirect('all_users')
            else:
                messages.info(request, 'Password Not Matching')
                return redirect('all_users')

        else:
            users = User.objects.all()
            return render(request, 'all_users.html', {'users': users})
    else:
        return redirect('signup')

def all_profiles(request):
    if request.user.is_staff:
        if request.method == "POST":
            profile_id = request.POST.get('delete_profile')
            profile_to_delete = get_object_or_404(Profile, id_user=profile_id)
            profile_to_delete.delete()
            return redirect('all_profiles')
        else:
            profiles = Profile.objects.all().order_by('user__username')
            return render(request, 'all_profiles.html', {'profiles': profiles})
    else:
        return redirect('signup')

def all_posts(request):
    if request.user.is_staff:
        if request.method == "POST":
            post_id = request.POST.get('delete_post')
            post_to_delete = get_object_or_404(Post, id=post_id)
            post_to_delete.delete()
            return redirect('all_posts')
        else:
            posts = Post.objects.all()
            return render(request, 'all_posts.html', {'posts': posts})
    else:
        return redirect('signup')
def all_followers(request):
    if request.user.is_staff:
        if request.method == "POST":
            follower = request.POST['delete_follower']
            user = request.POST['delete_user']

            if FollowersCount.objects.filter(follower=follower, user=user).first():
                delete_follower = FollowersCount.objects.get(follower=follower, user=user)
                delete_follower.delete()

            return redirect('all_followers')
        else:
            followers_count = FollowersCount.objects.all()
            return render(request, 'all_followers.html', {'followers_count': followers_count})
    else:
        return redirect('signup')

def all_likedPosts(request):
    if request.user.is_staff:
        if request.method == "POST":
            username = request.user.username
            post_id = request.POST.get('delete_like')

            post = Post.objects.get(id=post_id)

            if LikePost.objects.filter(post_id=post_id, username=username).first():
                print("aa")
                like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()
                like_filter.delete()
                post.no_of_likes = post.no_of_likes - 1
                post.save()

            return redirect('all_likedPosts')
        else:
            like_posts = LikePost.objects.all()
            return render(request, 'all_likedPosts.html', {'like_posts': like_posts})
    else:
        return redirect('signup')
def index(request):
    if request.user.is_authenticated:
        user_object = User.objects.get(username=request.user.username)
        user_profile = Profile.objects.get(user=user_object)

        user_following_list = []
        feed = []

        user_following = FollowersCount.objects.filter(follower=request.user.username)

        for users in user_following:
            user_following_list.append(users.user)

        for usernames in user_following_list:
            feed_lists = Post.objects.filter(user=usernames)
            feed.append(feed_lists)

        feed_list = list(chain(*feed))

        all_users = User.objects.all()
        user_following_all = []

        for user in user_following:
            user_list = User.objects.get(username=user.user)
            user_following_all.append(user_list)

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

        return render(request, 'index.html', {'user_profile': user_profile, 'posts':feed_list, 'suggestions_username_profile_list': suggestions_username_profile_list[:4]})
    else:
        return redirect('signup')
    
def upload(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            user = request.user.username
            image = request.FILES.get('image_upload')
            caption = request.POST['caption']

            new_post = Post.objects.create(user=user, image=image, caption=caption)
            new_post.save()

            return redirect('/')
        else:
            return redirect('/')
    else:
        return redirect('signup')

def like_post(request):
    if request.user.is_authenticated:
        username = request.user.username
        post_id = request.GET.get('post_id')

        post = Post.objects.get(id=post_id)

        like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

        if like_filter == None:
            new_like = LikePost.objects.create(post_id=post_id, username=username)
            new_like.save()
            post.no_of_likes = post.no_of_likes+1
            post.save()
            return redirect('/')
        else:
            like_filter.delete()
            post.no_of_likes = post.no_of_likes-1
            post.save()
            return redirect('/')
    else:
        return redirect('signup')
    
def profile(request, pk):
    if request.user.is_authenticated:
        user_object = User.objects.get(username=pk)
        user_profile = Profile.objects.get(user=user_object)
        user_posts = Post.objects.filter(user=pk)
        user_post_length = len(user_posts)

        follower = request.user.username
        user = pk

        if FollowersCount.objects.filter(follower=follower, user=user).first():
            button_text = "Unfollow"
        else:
            button_text = "Follow"

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
    else:
        return redirect('signup')   
    
def follow(request):
    if request.user.is_authenticated:
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
    else:
        return redirect('signup')

def settings(request):
    if request.user.is_authenticated:
        user_profile = Profile.objects.get(user=request.user)

        if request.method == "POST":
            if request.FILES.get('image') == None:
                image = user_profile.profileimg
                bio = request.POST['bio']
                location = request.POST['location']

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
    else:
        return redirect('signup')
    
def search(request):
    if request.user.is_authenticated:
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
    else:
        return redirect('signup')

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(request, 'Password Not Matching')
            return redirect('signup')

    else:
        return render(request, 'signup.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            if user.is_staff:
                return redirect('admin_dashboard')  # Înlocuiește 'admin_dashboard' cu ruta către panoul de administrare
            else:
                return redirect('/')

        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('signin')
    else:
        return render(request, 'signin.html')

def logout(request):
    if request.user.is_authenticated:
        auth.logout(request)
        return redirect('signin')
    else:
        return HttpResponse("You are not logged in.")
    