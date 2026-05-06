### Model Serializer case

from rest_framework import serializers
from .models import Post, Comment, Category # Post 모델과 Comment 모델을 가져옴

class PostSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True, required=False, allow_empty=True)
    #category 필드를 지정하지 않아도 post 생성 가능하도록 required=False, allow_empty=True 옵션 추가
    class Meta:
        model = Post    # serializer가 어떤 모델을 기반으로 만들어지는지 >> post
        fields = "__all__"  # 모델에서 어떤 필드를 가져올지 >> 전체 필드

class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ('post',) # 댓글 생성 시 post_id를 URL에서 받아와서 serializer.save()할 때 post=post로 전달하기 때문에 read_only_fields에 'post' 추가 -> 클라이언트가 post 필드 입력하지 않아도 됨