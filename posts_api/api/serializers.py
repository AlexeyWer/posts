from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator


from posts.models import Follow, Post, User, ReadStatus


class PostSerializers(serializers.ModelSerializer):
    author = SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    read_status = serializers.BooleanField(read_only=True)

    class Meta:
        model = Post
        fields = '__all__'
    
    def create(self, validated_data):
        post = super().create(validated_data)
        user = self.context['request'].user
        ReadStatus.objects.create(post=post, user=user)
        return post

class FollowSerializers(serializers.ModelSerializer):
    user = SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    following = SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username'
    )

    class Meta:
        model = Follow
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following')
            )
        ]

    def validate(self, data):
        if self.context['request'].user == data['following']:
            raise ValidationError(detail='Подписка на себя невозможна!')
        return data


class UserSerializer(serializers.ModelSerializer):
    posts_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ('username', 'posts_count')