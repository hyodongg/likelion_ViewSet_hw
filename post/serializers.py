from rest_framework import serializers
from .models import *

class PostSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField(read_only=True)
    writer = serializers.CharField(source='writer.username',read_only=True)
    
    
    def get_tags(self,instance):
        tag = instance.tags.all()
        return [t.name for t in tag]
    
    def get_comments(self,instance):
        serializer = CommentSerializer(instance.comments, many=True)
        return serializer.data
    
    class Meta:
        model = Post
        fields = ['id','title','writer','content','created_time','updated_time','tags','comments','likes']
        read_only_fields = [
            "id",
            "created_time",
            "updated_time",
            "comments"
        ]

class CommentSerializer(serializers.ModelSerializer):
    writer = serializers.CharField(source='writer.username', read_only=True)
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['post']
        
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        
class PostListSerializer(serializers.ModelSerializer):
    comments_cnt = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    writer = serializers.CharField(source='writer.username',read_only=True)
    
    def get_comments_cnt(self,instance):
        return instance.comments.count()
    
    def get_tags(self,instance):
        tag = instance.tags.all()
        return [t.name for t in tag]
    
    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "writer",
            "content",
            "created_time",
            "updated_time",
            "tags",
            "comments_cnt",
            "likes"
        ]