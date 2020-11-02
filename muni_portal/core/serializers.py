from rest_framework import serializers
from rest_framework.fields import Field
from wagtail.images.api.fields import ImageRenditionField
from . import models


class SerializerMethodNestedSerializer(serializers.SerializerMethodField):
    """
    Returns nested serializer in serializer method field
    https://stackoverflow.com/a/63676418
    """

    def __init__(self, serializer, serializer_kwargs=None, **kwargs):
        self.serializer = serializer
        self.serializer_kwargs = serializer_kwargs or {}
        super(SerializerMethodNestedSerializer, self).__init__(**kwargs)

    def to_representation(self, value):
        repr_value = super(SerializerMethodNestedSerializer, self).to_representation(value)
        if repr_value is not None:
            return self.serializer(repr_value, **self.serializer_kwargs).data


class ImageSerializerField(Field):
    """A custom serializer for image field."""

    def to_representation(self, value):
        return {
            "url": value.file.url,
            "width": value.width,
            "height": value.height,
            "alt": value.title
        }


class RelatedPagesSerializer(Field):
    @staticmethod
    def page_representation(page):
        return {
            "id": page.id,
            "title": page.title,
            "slug": page.slug,
            "url": page.url,
            "icon_classes": page.icon_classes if hasattr(page, "icon_classes") else None,
        }

    def to_representation(self, pages):
        return [RelatedPagesSerializer.page_representation(page) for page in pages.specific()]


class RelatedPersonPageSerializer(Field):
    """A custom serializer for related PersonPage."""

    read_only = True
    write_only = False

    @staticmethod
    def get_representation(value):
        return {
            "id": value.id,
            "title": value.title,
            "slug": value.slug,
            "url": value.url,
            "icon_classes": value.icon_classes if hasattr(value, "icon_classes") else None,
            "profile_image": None,
            "profile_image_thumbnail": None,
            "job_title": None,
        }

    def to_representation(self, value):
        result = self.get_representation(value)
        if value.specific.profile_image:
            result["profile_image"] = ImageSerializerField().to_representation(
                value.specific.profile_image
            )
            result["profile_image_thumbnail"] = ImageRenditionField("max-100x100").to_representation(
                value.specific.profile_image
            )
        if value.specific.job_title:
            result["job_title"] = value.specific.job_title
        return result


class RelatedPersonPageListSerializer(RelatedPersonPageSerializer):

    def to_representation(self, pages):
        pages = pages if pages is list else pages.all()
        return [super(RelatedPersonPageListSerializer, self).to_representation(page) for page in pages]
