from .models import Family, User
from rest_framework import serializers
from django.utils.crypto import get_random_string


# https://www.django-rest-framework.org/
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'nickname', 'email', 'password', 'date_of_birth', 'family_id']

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        old_password = validated_data.get('old_password', '')
        new_password = validated_data.get('new_password', '')

        if old_password != '' and new_password != '':
            if instance.check_password(old_password):
                instance.set_password(new_password)
        else:
            for k, v in validated_data.items():
                setattr(instance, k, v)

        instance.save()
        return instance