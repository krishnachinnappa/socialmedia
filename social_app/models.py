from django.db import models
# this is to create the custom user model.
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime
user = get_user_model()
# Create your models here.

# by default the django will provide the user model.
# we need to have the user bio, his profile image and location
# linking the user model to the foriegn key
class Profile(models.Model):
    # linking th profile model to the user model.
    user = models.ForeignKey(user, on_delete = models.CASCADE)
    # on delete = moels.Cascade will delete all the users related to the foriegn
    # key are deleted.
    id_user = models.IntegerField()
    bio = models.TextField(blank=True)
    # upload_to = 'folder name profile_images' in media folder
    profileimg = models.ImageField(upload_to='profile_images', default='blank.jpg')
    location = models.CharField(max_length=100,blank=True)

    def __str__(self):
        # this will show the user as username
        return self.user.username


class Post(models.Model):
    # create the POST model data base so that each user has their own posts stored in the data base
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.CharField(max_length=100)
    image = models.ImageField(upload_to='post_images')
    caption = models.TextField()
    # time creation of the post
    created_at = models.DateTimeField(default=datetime.now)
    # user post likes
    no_of_likes = models.IntegerField(default=0)

    def __str__(self):
        return self.user

# creation of likes for each user for their post posted.
class LikePost(models.Model):
    post_id= models.CharField(max_length=500)
    username=models.CharField(max_length=100)

    def __str__(self):
        return self.username

# followers count.
class FollowersCount(models.Model):
    follower = models.CharField(max_length=100)
    user = models.CharField(max_length=100)

    def __str__(self):
        return self.user

