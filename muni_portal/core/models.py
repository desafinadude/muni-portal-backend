from django.db import models
from django.contrib.postgres.fields import JSONField
from wagtail.core.fields import RichTextField
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, PageChooserPanel
from wagtail.api import APIField
from wagtail.snippets.models import register_snippet
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.core.models import Page, Orderable
from rest_framework import serializers as drf_serializers
from rest_framework.fields import DateTimeField
from wagtail.images.api.fields import ImageRenditionField

from muni_portal.core.serializers import (
    RelatedPagesSerializer,
    RelatedPersonPageSerializer,
    RelatedPersonPageListSerializer,
    SerializerMethodNestedSerializer,
    RelatedCouncillorGroupPageSerializer, RichTextFieldSerializer, RelatedNoticePagesSerializer
)

NON_LINK_FEATURES = ["h2", "h3", "bold", "italic", "ol", "ul", "hr"]
NON_EMBEDS_FEATURES = NON_LINK_FEATURES + ["link"]


class ServiceContact(Orderable, models.Model):
    page = ParentalKey(
        "core.ServicePage", on_delete=models.CASCADE, related_name="service_contacts"
    )
    contact = models.ForeignKey(
        "ContactDetail", on_delete=models.CASCADE, related_name="+"
    )

    class Meta(Orderable.Meta):
        verbose_name = "service contact"
        verbose_name_plural = "service contacts"

    panels = [
        SnippetChooserPanel("contact"),
    ]

    def __str__(self):
        return self.page.title + " -> " + self.contact


class PersonContact(Orderable, models.Model):
    page = ParentalKey(
        "core.PersonPage", on_delete=models.CASCADE, related_name="person_contacts"
    )
    contact = models.ForeignKey(
        "ContactDetail", on_delete=models.CASCADE, related_name="+"
    )

    class Meta(Orderable.Meta):
        verbose_name = "person contact"
        verbose_name_plural = "person contacts"

    panels = [
        SnippetChooserPanel("contact"),
    ]

    def __str__(self):
        return self.page.title + " -> " + self.contact


class ServicePointContact(Orderable, models.Model):
    page = ParentalKey(
        "core.ServicePointPage", on_delete=models.CASCADE, related_name="service_point_contacts"
    )
    contact = models.ForeignKey(
        "ContactDetail", on_delete=models.CASCADE, related_name="+"
    )

    class Meta(Orderable.Meta):
        verbose_name = "service point contact"
        verbose_name_plural = "service point contacts"

    panels = [
        SnippetChooserPanel("contact"),
    ]

    def __str__(self):
        return self.page.title + " -> " + self.contact


class ContactDetailTypeManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class ContactDetailType(models.Model):
    label = models.CharField(max_length=100, unique=True)
    slug = models.CharField(max_length=100, unique=True)
    icon_classes = models.CharField(max_length=100, blank=True)

    objects = ContactDetailTypeManager()

    def natural_key(self):
        return (self.slug,)

    def __str__(self):
        return self.label


class Webhook(models.Model):
    data = JSONField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)


class ContactDetailTypeSerializer(drf_serializers.ModelSerializer):
    class Meta:
        model = ContactDetailType
        exclude = ["id"]


class ContactSerializer(drf_serializers.Serializer):
    value = drf_serializers.SerializerMethodField()
    type = SerializerMethodNestedSerializer(ContactDetailTypeSerializer)
    annotation = drf_serializers.SerializerMethodField()

    class Meta:
        fields = [
            "value",
            "type",
            "annotation",
        ]
        depth = 1

    def get_value(self, obj):
        return obj.contact.value

    def get_type(self, obj):
        return obj.contact.type

    def get_annotation(self, obj):
        return obj.contact.annotation


class PersonContactSerializer(ContactSerializer):
    class Meta(ContactSerializer.Meta):
        model = PersonContact


class ServiceContactSerializer(ContactSerializer):
    class Meta(ContactSerializer.Meta):
        model = ServiceContact


class ServicePointContactSerializer(ContactSerializer):
    class Meta(ContactSerializer.Meta):
        model = ServicePointContact


@register_snippet
class ContactDetail(models.Model):
    value = models.CharField(max_length=250)
    type = models.ForeignKey("ContactDetailType", on_delete=models.CASCADE)
    annotation = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        help_text=('Optional public note of what this contact is for, e.g. '
                   '"Senior Library Assistant Ms A Jones" or "John Smith'
                   'Cell phone number"'),
    )
    purpose = models.CharField(
        max_length=250,
        help_text=('Internal reminder of what this represents - e.g. "Office '
                   'number for Joanne Smith"'),
    )

    panels = [
        FieldPanel("type"),
        FieldPanel("value"),
        FieldPanel("annotation"),
        FieldPanel("purpose"),
    ]

    def __str__(self):
        return f"{ self.value } ({ self.purpose })"


class PersonPage(Page):
    job_title = models.CharField(max_length=200, blank=True)
    overview = RichTextField(features=NON_LINK_FEATURES, blank=True)
    profile_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = Page.content_panels + [
        FieldPanel("job_title"),
        FieldPanel("overview"),
        ImageChooserPanel('profile_image'),
        InlinePanel("person_contacts", label="Contacts"),
    ]

    api_fields = [
        APIField("job_title"),
        APIField("overview"),
        APIField("profile_image"),
        APIField("profile_image_thumbnail", ImageRenditionField("max-100x100", source='profile_image')),
        APIField("person_contacts", serializer=PersonContactSerializer(many=True)),
        APIField("ancestor_pages", serializer=RelatedPagesSerializer(source='get_ancestors')),
        APIField("child_pages", serializer=RelatedPagesSerializer(source='get_children')),
    ]


PersonPage._meta.get_field("title").verbose_name = "Name"


@register_snippet
class PoliticalParty(models.Model):
    name = models.CharField(max_length=1000)
    abbreviation = models.CharField(max_length=20)
    logo_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    panels = [
        FieldPanel('name'),
        FieldPanel('abbreviation'),
        ImageChooserPanel('logo_image'),
    ]

    class Meta:
        verbose_name_plural = "Political parties"

    def __str__(self):
        return self.name


class PoliticalPartySerializer(drf_serializers.ModelSerializer):
    logo_image_tumbnail = ImageRenditionField("max-100x100", source='logo_image')

    class Meta:
        model = PoliticalParty
        exclude = ["id"]
        depth = 1


class CouncillorPage(PersonPage):
    subpage_types = []

    political_party = models.ForeignKey(
        'core.PoliticalParty',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    councillor_groups = ParentalManyToManyField(
        'core.CouncillorGroupPage',
        blank=True,
        related_name="councillors"
    )

    content_panels = Page.content_panels + [
        FieldPanel("job_title"),
        FieldPanel("overview"),
        ImageChooserPanel('profile_image'),
        SnippetChooserPanel('political_party'),
        FieldPanel("councillor_groups"),
        InlinePanel("person_contacts", label="Contacts"),
    ]

    api_fields = [
        APIField("job_title"),
        APIField("overview"),
        APIField("profile_image"),
        APIField("profile_image_thumbnail", ImageRenditionField("max-100x100", source='profile_image')),
        APIField("political_party", serializer=PoliticalPartySerializer()),
        APIField("councillor_groups"),
        APIField("person_contacts", serializer=PersonContactSerializer(many=True)),
        APIField("ancestor_pages", serializer=RelatedPagesSerializer(source='get_ancestors')),
        APIField("child_pages", serializer=RelatedPagesSerializer(source='get_children')),
    ]


class CouncillorListPage(Page):
    subpage_types = [
        "core.CouncillorPage",
    ]
    max_count_per_parent = 1

    overview = RichTextField(features=NON_LINK_FEATURES)

    content_panels = Page.content_panels + [
        FieldPanel("overview"),
    ]

    api_fields = [
        APIField("overview"),
        APIField("ancestor_pages", serializer=RelatedPagesSerializer(source='get_ancestors')),
        APIField("child_pages", serializer=RelatedPersonPageListSerializer(source='get_children')),
    ]


class CouncillorGroupPage(Page):
    subpage_types = []

    overview = RichTextField(features=NON_LINK_FEATURES)
    icon_classes = models.CharField(max_length=250)
    members_label = models.CharField(max_length=100, default="Members of this group are")

    content_panels = Page.content_panels + [
        FieldPanel("overview"),
        FieldPanel("icon_classes"),
        FieldPanel("members_label"),
    ]

    api_fields = [
        APIField("overview"),
        APIField("icon_classes"),
        APIField("members_label"),
        APIField("councillors", serializer=RelatedPersonPageListSerializer()),
        APIField("ancestor_pages", serializer=RelatedPagesSerializer(source='get_ancestors')),
        APIField("child_pages", serializer=RelatedPagesSerializer(source='get_children')),
    ]

    @property
    def councillors_count(self):
        return self.councillors.count()


class AdministratorPage(PersonPage):
    subpage_types = []


class AdministrationIndexPage(Page):
    subpage_types = [
        "core.AdministratorPage",
    ]
    max_count_per_parent = 1

    overview = RichTextField(features=NON_LINK_FEATURES)

    content_panels = Page.content_panels + [
        FieldPanel("overview"),
    ]

    api_fields = [
        APIField("overview"),
        APIField("ancestor_pages", serializer=RelatedPagesSerializer(source='get_ancestors')),
        APIField("child_pages", serializer=RelatedPersonPageListSerializer(source='get_children')),
    ]


class PoliticalRepsIndexPage(Page):
    subpage_types = [
        "core.CouncillorGroupPage",
        "core.CouncillorListPage",
    ]
    max_count_per_parent = 1

    overview = RichTextField(features=NON_LINK_FEATURES)

    content_panels = Page.content_panels + [
        FieldPanel("overview"),
    ]

    api_fields = [
        APIField("overview"),
        APIField("ancestor_pages", serializer=RelatedPagesSerializer(source='get_ancestors')),
        APIField("child_pages", serializer=RelatedCouncillorGroupPageSerializer(source='get_children')),
    ]


class ServicePointPage(Page):
    subpage_types = []

    overview = RichTextField(features=NON_LINK_FEATURES, blank=True)
    office_hours = RichTextField(features=NON_LINK_FEATURES, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("overview"),
        FieldPanel("office_hours"),
        InlinePanel("service_point_contacts", label="Contacts"),
    ]

    api_fields = [
        APIField("overview"),
        APIField("office_hours"),
        APIField("service_point_contacts", serializer=ServicePointContactSerializer(many=True)),
        APIField("ancestor_pages", serializer=RelatedPagesSerializer(source='get_ancestors')),
        APIField("child_pages", serializer=RelatedPagesSerializer(source='get_children')),
    ]


class ServicePage(Page):
    subpage_types = [
        "core.ServicePointPage"
    ]

    icon_classes = models.CharField(max_length=250)
    overview = RichTextField(features=NON_LINK_FEATURES, blank=True)
    office_hours = RichTextField(features=NON_LINK_FEATURES, blank=True)
    head_of_service = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    content_panels = Page.content_panels + [
        FieldPanel("icon_classes"),
        FieldPanel("overview"),
        FieldPanel("office_hours"),
        PageChooserPanel('head_of_service', 'core.AdministratorPage'),
        InlinePanel("service_contacts", label="Contacts"),
    ]

    api_fields = [
        APIField("icon_classes"),
        APIField("overview"),
        APIField("office_hours"),
        APIField("head_of_service", serializer=RelatedPersonPageSerializer()),
        APIField("service_contacts", serializer=ServiceContactSerializer(many=True)),
        APIField("ancestor_pages", serializer=RelatedPagesSerializer(source='get_ancestors')),
        APIField("child_pages", serializer=RelatedPagesSerializer(source='get_children')),
    ]


class MyMuniPage(Page):
    subpage_types = [
        "core.PoliticalRepsIndexPage",
        "core.AdministrationIndexPage",
        "core.NoticeIndexPage",
    ]
    max_count_per_parent = 1

    api_fields = [
        APIField("ancestor_pages", serializer=RelatedPagesSerializer(source='get_ancestors')),
        APIField("child_pages", serializer=RelatedPagesSerializer(source='get_children')),
    ]


class ServicesIndexPage(Page):
    subpage_types = [
        "core.ServicePage",
    ]
    max_count_per_parent = 1

    api_fields = [
        APIField("ancestor_pages", serializer=RelatedPagesSerializer(source='get_ancestors')),
        APIField("child_pages", serializer=RelatedPagesSerializer(source='get_children')),
    ]


class HomePage(Page):
    subpage_types = [
        "core.ServicesIndexPage",
        "core.MyMuniPage",
    ]
    max_count_per_parent = 1

    api_fields = [
        APIField("ancestor_pages", serializer=RelatedPagesSerializer(source='get_ancestors')),
        APIField("child_pages", serializer=RelatedPagesSerializer(source='get_children')),
    ]


class NoticeIndexPage(Page):
    subpage_types = [
        "core.NoticePage",
    ]

    api_fields = [
        APIField("ancestor_pages", serializer=RelatedPagesSerializer(source='get_ancestors')),
        APIField("child_pages", serializer=RelatedNoticePagesSerializer(source='get_children')),
    ]


class NoticePage(Page):
    subpage_types = []

    body = RichTextField(features=NON_EMBEDS_FEATURES)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    api_fields = [
        APIField("title"),
        APIField("body"),
        APIField("body_html", serializer=RichTextFieldSerializer(source="body")),
        APIField("publication_date", serializer=DateTimeField(source="last_published_at")),
        APIField("ancestor_pages", serializer=RelatedPagesSerializer(source='get_ancestors')),
        APIField("child_pages", serializer=RelatedPagesSerializer(source='get_children')),
    ]


class ServiceRequest(models.Model):
    """ Service Request as defined by the Collaborator Web API template object (id=9) """

    ASSIGNED = "assigned"
    REGISTERED = "registered"

    STATUS_CHOICES = (
        (ASSIGNED, "Assigned"),
        (REGISTERED, "Registered"),
    )

    object_id = models.PositiveIntegerField()
    type = models.CharField(max_length=254, blank=True, null=True)
    user_name = models.CharField(max_length=254, )
    user_surname = models.CharField(max_length=254)
    user_mobile_number = models.CharField(max_length=30)
    user_email_address = models.EmailField(max_length=254)
    municipal_account_number = models.CharField(max_length=254, blank=True, null=True)
    street_name = models.CharField(max_length=254)
    street_number = models.CharField(max_length=254)
    suburb = models.CharField(max_length=254)
    description = models.CharField(max_length=1024)
    coordinates = models.CharField(max_length=254, blank=True, null=True)
    request_date = models.DateField(default=None)
    mobile_reference = models.CharField(max_length=254, blank=True, null=True)
    on_premis_reference = models.CharField(max_length=254, blank=True, null=True)
    status = models.CharField(max_length=254, choices=STATUS_CHOICES, default=None, blank=True, null=True)
    demarcation_code = models.CharField(max_length=254, blank=True, null=True)
