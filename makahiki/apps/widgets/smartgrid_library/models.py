"""Smart Grid Game Library model definition."""

from django.db import models
from apps.utils.utils import media_file_path
from apps.managers.cache_mgr import cache_mgr
from django.conf import settings
import os

_MEDIA_LOCATION_ACTION = os.path.join("smartgrid_library", "actions")
"""location for the uploaded files for actions."""


class LibraryTextPromptQuestion(models.Model):
    """Represents questions that can be asked of users in order to verify participation
    in activities."""

    libraryaction = models.ForeignKey("LibraryAction")
    question = models.TextField(help_text="The question text.")
    answer = models.CharField(max_length=255,
                              help_text="The answer of question (max 255 characters).",
                              null=True, blank=True)

    def __unicode__(self):
        return "Question: '%s' Answer: '%s'" % (self.question, self.answer)


class LibraryQuestionChoice(models.Model):
    """Represents questions's multiple choice"""

    question = models.ForeignKey("LibraryTextPromptQuestion")
    action = models.ForeignKey("LibraryAction")
    choice = models.CharField(max_length=255,
                              help_text="The choice of question (max 255 characters).")

    def __unicode__(self):
        return self.choice


class LibraryColumnName(models.Model):
    """Defined ColumnNames used to group actions in the Smart Grid Game."""
    name = models.CharField(max_length=255,
                            help_text="The name of the column (max 255 characters).")
    slug = models.SlugField(help_text="Automatically generated if left blank.",
                            null=True)

    class Meta:
        """Meta"""
        ordering = ("name",)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Custom save method to set fields."""
        super(LibraryColumnName, self).save(args, kwargs)
        cache_mgr.clear()


class LibraryAction(models.Model):
    """Activity Base class."""
    TYPE_CHOICES = (
        ('activity', 'Activity'),
        ('commitment', 'Commitment'),
        ('event', 'Event'),
        )
    RESOURCE_CHOICES = (
        ('energy', 'Energy'),
        ('water', 'Water'),
        ('waste', 'Waste'),
    )

    VIDEO_SOURCE_CHOICES = (
        ('youtube', 'youtube'),
    )

    name = models.CharField(
        max_length=20,
        help_text="The name of the action.")
    slug = models.SlugField(
        help_text="A unique identifier of the action. Automatically generated if left blank.",
        unique=True,
        )
    title = models.CharField(
        max_length=200,
        help_text="The title of the action.")
    image = models.ImageField(
        max_length=255, blank=True, null=True,
        upload_to=media_file_path(_MEDIA_LOCATION_ACTION),
        help_text="Uploaded image for the activity. This will appear under the title when "
                  "the action content is displayed.")
    video_id = models.CharField(
        null=True, blank=True,
        max_length=200,
        help_text="The id of the video (optional). Currently only YouTube video is supported. "
                  "This is the unique id of the video as identified by the YouTube video url.")
    video_source = models.CharField(
        null=True, blank=True,
        max_length=20,
        choices=VIDEO_SOURCE_CHOICES,
        help_text="The source of the video.")
    embedded_widget = models.CharField(
        null=True, blank=True,
        max_length=50,
        help_text="The name of the embedded widget (optional).")
    description = models.TextField(
        help_text="The discription of the action. " + settings.MARKDOWN_TEXT)
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        help_text="The type of the actions."
    )
    unlock_condition = models.CharField(
        max_length=400, null=True, blank=True,
        help_text="if the condition is True, the action will be unlocked. " +
                  settings.PREDICATE_DOC_TEXT)
    unlock_condition_text = models.CharField(
        max_length=400, null=True, blank=True,
        help_text="The description of the unlock condition. It will be displayed to players when "
                  "the lock icon is clicked.")
    related_resource = models.CharField(
        max_length=20,
        null=True, blank=True,
        choices=RESOURCE_CHOICES,
        help_text="The resource type this action related.")
    social_bonus = models.IntegerField(
        default=0,
        help_text="Social bonus point value.")
    point_value = models.IntegerField(
        default=0,
        help_text="The point value to be awarded."
    )

    def get_classname(self):
        """Returns the classname."""
        return self._meta.module_name

    def __unicode__(self):
        return "%s: %s" % (self.type.capitalize(), self.title)

    def get_action(self, action_type):
        """Returns the concrete action object by type."""
        return action_type.objects.get(action_ptr=self.pk)


class LibraryActivity(LibraryAction):
    """Activities involve verifiable actions that users commit to.  These actions can be
   verified by asking questions or posting an image attachment that verifies the user did
   the activity."""

    CONFIRM_CHOICES = (
        ('text', 'Question and Answer'),
        ('image', 'Image Upload'),
        ('free', 'Free Response'),
        ('free_image', 'Free Response and Image Upload'),
        )

    expected_duration = models.IntegerField(
        verbose_name="Expected activity duration",
        help_text="Time (in minutes) that the activity is expected to take."
    )
    point_range_start = models.IntegerField(
        null=True,
        blank=True,
        help_text="Minimum number of points possible for a variable point activity."
    )
    point_range_end = models.IntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of points possible for a variable point activity."
    )
    confirm_type = models.CharField(
        max_length=20,
        choices=CONFIRM_CHOICES,
        default="text",
        help_text="If the type is 'Question and Answer', please provide the "
                  "'Text prompt questions' section below.",
        verbose_name="Confirmation Type"
    )
    confirm_prompt = models.TextField(
        blank=True,
        verbose_name="Confirmation prompt",
        help_text=settings.MARKDOWN_TEXT
    )
    admin_note = models.TextField(
        null=True, blank=True,
        help_text="Notes for admins when approving this activity. " + settings.MARKDOWN_TEXT)

    def pick_question(self, user_id):
        """Choose a random question to present to a user."""
        if self.confirm_type != "text":
            return None

        questions = LibraryTextPromptQuestion.objects.filter(action=self)
        if questions:
            return questions[user_id % len(questions)]
        else:
            return None

    class Meta:
        """meta"""
        verbose_name_plural = "library activities"


class LibraryCommitment(LibraryAction):
    """Commitments involve non-verifiable actions that a user can commit to.
    Typically, they will be worth fewer points than activities."""
    commitment_length = models.IntegerField(
        default=5,
        help_text="Duration of commitment, in days."
    )


class LibraryEvent(LibraryAction):
    """Events will be verified by confirmation code. It includes events and excursions."""

    expected_duration = models.IntegerField(
        verbose_name="Expected activity duration",
        help_text="Time (in minutes) that the activity is expected to take."
    )
