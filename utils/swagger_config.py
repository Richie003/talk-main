from drf_yasg.inspectors import FieldInspector, NotHandled
from drf_yasg import openapi
from drf_yasg.openapi import Parameter
from rest_framework import serializers

class MultipleImageField(serializers.ListField):
    child = serializers.ImageField()

    def __init__(self, *args, **kwargs):
        kwargs['child'] = serializers.ImageField()
        super().__init__(*args, **kwargs)

    def to_representation(self, data):
        return [super(MultipleImageField, self).child.to_representation(item) for item in data]

class MultipleImageFieldInspector(FieldInspector):
    def process_result(self, result, method_name, obj, **kwargs):
        if isinstance(obj, MultipleImageField):
            return openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_STRING, format=openapi.FORMAT_BINARY)
            )
        return result or NotHandled
