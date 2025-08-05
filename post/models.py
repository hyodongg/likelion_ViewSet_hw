from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)

class Post(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=30)
    writer = models.ForeignKey(User,on_delete = models.CASCADE,related_name="written_posts")
    content = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag,blank=True)
    likes = models.PositiveIntegerField(default = 0)
    
    
class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    writer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    post = models.ForeignKey(Post,null=False,blank=False,on_delete=models.CASCADE,related_name='comments')
    