"""
Serializers for Forum API.
"""
from rest_framework import serializers
from forum.models import Post, Comment
from ELW.models import MainQuestion, SubQuestion


class CommentSerializer(serializers.ModelSerializer):
    """评论序列化器"""
    author_name = serializers.CharField(source='name', read_only=True)
    author_username = serializers.SerializerMethodField()
    author_role = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_at', 'is_top', 'is_marked', 
                  'author_name', 'author_username', 'author_role', 'is_anonymous',
                  'parent_comment', 'replies']
        read_only_fields = ['id', 'created_at']
    
    def get_author_username(self, obj):
        """获取作者用户名"""
        if obj.student:
            return obj.student.username
        elif obj.teacher:
            return obj.teacher.username
        return obj.author
    
    def get_author_role(self, obj):
        """获取作者角色"""
        if obj.student:
            return 'student'
        elif obj.teacher:
            return 'teacher'
        return None
    
    def get_replies(self, obj):
        """获取回复列表"""
        replies = Comment.objects.filter(parent_comment=obj).order_by('created_at')
        return CommentSerializer(replies, many=True).data


class PostSerializer(serializers.ModelSerializer):
    """帖子序列化器"""
    author_name = serializers.CharField(source='name', read_only=True)
    author_username = serializers.SerializerMethodField()
    author_role = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    main_question_id = serializers.IntegerField(source='main_question.id', read_only=True, allow_null=True)
    sub_question_id = serializers.IntegerField(source='sub_question.id', read_only=True, allow_null=True)
    comments = CommentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'created_at', 'is_top', 'top_score',
                  'is_question', 'is_public', 'is_anonymous', 'is_announcement',
                  'author_name', 'author_username', 'author_role',
                  'main_question_id', 'sub_question_id', 'comments_count', 'comments']
        read_only_fields = ['id', 'created_at']
    
    def get_author_username(self, obj):
        """获取作者用户名"""
        if obj.student:
            return obj.student.username
        elif obj.teacher:
            return obj.teacher.username
        return obj.author
    
    def get_author_role(self, obj):
        """获取作者角色"""
        if obj.student:
            return 'student'
        elif obj.teacher:
            return 'teacher'
        return None
    
    def get_comments_count(self, obj):
        """获取评论数量"""
        return obj.comments.count()


class PostCreateSerializer(serializers.ModelSerializer):
    """创建帖子序列化器"""
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'is_public', 'is_anonymous', 'anonymous_name',
                  'main_question_id', 'sub_question_id', 'is_question']
    
    main_question_id = serializers.IntegerField(required=False, allow_null=True)
    sub_question_id = serializers.IntegerField(required=False, allow_null=True)


class PostUpdateSerializer(serializers.ModelSerializer):
    """更新帖子序列化器"""
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'is_public', 'is_top', 'is_anonymous', 'anonymous_name']


class CommentCreateSerializer(serializers.ModelSerializer):
    """创建评论序列化器"""
    
    class Meta:
        model = Comment
        fields = ['content', 'is_anonymous', 'anonymous_name', 'parent_comment_id']
    
    parent_comment_id = serializers.IntegerField(required=False, allow_null=True)


class CommentUpdateSerializer(serializers.ModelSerializer):
    """更新评论序列化器"""
    
    class Meta:
        model = Comment
        fields = ['content', 'is_anonymous', 'anonymous_name']











