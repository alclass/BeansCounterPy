from rest_framework import serializers
from rent.models import Person


class PersonSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    nomecompleto = serializers.CharField(required=True, allow_blank=True, max_length=100)
    cpf = serializers.CharField(required=True, allow_blank=True, max_length=11)
    address = serializers.CharField(required=True, allow_blank=True, max_length=100)

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return Person.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.nomecompleto = validated_data.get("nomecompleto", instance.nomecompleto)
        instance.cpf = validated_data.get("cpf", instance.cpf)
        instance.address = validated_data.get("address", instance.address)
        instance.save()
        return instance