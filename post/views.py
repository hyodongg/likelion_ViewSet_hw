from django.shortcuts import render,get_object_or_404
from rest_framework import viewsets,mixins
import re
from .models import Post,Comment,Tag
from .serializers import PostSerializer,CommentSerializer,TagSerializer,PostListSerializer

from rest_framework.response import Response
from .permissions import IsOwnerOrReadOnly
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import action

# Create your views here.
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all();
    #serializer_class = PostSerializer;
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_permissions(self):
        if self.action in ["update","destroy","partial_update"]:
            return [IsOwnerOrReadOnly()]
        if self.action == "create":
            return [IsAuthenticatedOrReadOnly()]
        return [IsAuthenticatedOrReadOnly()]
    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        return PostSerializer
    
    def create(self,request):
        if not request.user.is_authenticated:
            raise PermissionDenied("로그인한 사용자만 글을 작성할 수 있습니다.")
    
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(writer = request.user)
        
        post = serializer.instance
        self.handle_tags(post)
        
        return Response(serializer.data)
    
    def perform_update(self,serializer):
        post = serializer.save()
        post.tags.clear()
        self.handle_tags(post)
    
    def handle_tags(self,post):
        words = re.split(r'[\s,]+',post.content.strip())
        tag_list = []
        for w in words:
            if len(w)>0:
                if w[0] == '#':
                    tag_list.append(w[1:])
        for t in tag_list:
            tag , _ = Tag.objects.get_or_create(name=t)
            post.tags.add(tag)
            
        post.save()
        
    @action(methods = ["GET"],detail=True)
    def like(self,request,pk=None):
        post=self.get_object()
        post.likes+=1
        post.save()
        return Response()
        
    @action(methods = ["GET"],detail=False)
    def top3(self,request):
        top_posts = Post.objects.order_by('-likes')[:3]
        serializer = PostListSerializer(top_posts, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.GenericViewSet,mixins.RetrieveModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin):
    queryset = Comment.objects.all();
    serializer_class = CommentSerializer
    
    def get_permissions(self):
        if self.action in ["update","destroy","partial_update"]:
            return [IsOwnerOrReadOnly()]
        return []
    
class PostCommentViewSet(viewsets.GenericViewSet,mixins.ListModelMixin,mixins.CreateModelMixin):
    #queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]
    
    def get_queryset(self):
        post = self.kwargs.get("post_id")
        queryset = Comment.objects.filter(post_id=post)
        return queryset
    
    #def list(self,request,post_id=None):
    #    post = get_object_or_404(Post,id=post_id)
    #    queryset = self.filter_queryset(self.get_queryset().filter(post=post))
    #    serializer = self.get_serializer(queryset,many=True)
    #    return Response(serializer.data)
    def create(self,request,post_id=None):
        if not request.user.is_authenticated:
            raise PermissionDenied("로그인한 사용자만 댓글을 작성할 수 있습니다.")
    
        post = get_object_or_404(Post,id=post_id);
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception = True)
        serializer.save(post=post,writer = request.user)
        return Response(serializer.data)
    
class TagViewSet(viewsets.GenericViewSet,mixins.RetrieveModelMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = "name"
    lookup_url_kwarg = "tag_name"
    
    def retrieve(self,request,*args,**kwargs):
        tag_name = kwargs.get("tag_name")
        tags = get_object_or_404(Tag,name=tag_name)
        posts = Post.objects.filter(tags=tags)
        serializer = PostSerializer(posts,many=True)
        return Response(serializer.data)
    