'''Defines the classes used for designing the Smart Grid Game.

Created on Feb 5, 2013

@author: Cam Moore
'''

from django.db import models
from django.conf import settings
from apps.managers.cache_mgr import cache_mgr
from apps.utils.utils import media_file_path
import ast
import os
import datetime
from django.core.validators import MaxValueValidator


_MEDIA_LOCATION_ACTION = os.path.join("smartgrid_library", "actions")
"""location for the uploaded files for actions."""


class ListField(models.TextField):
    """Represents a list as text. Can convert text string to python list."""
    __metaclass__ = models.SubfieldBase
    description = "Stores a python list"

    def __init__(self, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            value = []

        if isinstance(value, list):
            return value

        return ast.literal_eval(value)

    def get_prep_value(self, value):
        if value is None:
            return value

        return unicode(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value, None)


class DesignerTextPromptQuestion(models.Model):
    """Represents questions that can be asked of users in order to verify participation
    in activities."""

    action = models.ForeignKey("DesignerAction")
    question = models.TextField(help_text="The question text.")
    answer = models.CharField(max_length=255,
                              help_text="The answer of question (max 255 characters).",
                              null=True, blank=True)

    def __unicode__(self):
        return "Question: '%s' Answer: '%s'" % (self.question, self.answer)


class DesignerQuestionChoice(models.Model):
    """Represents questions's multiple choice"""

    question = models.ForeignKey("DesignerTextPromptQuestion")
    action = models.ForeignKey("DesignerAction")
    choice = models.CharField(max_length=255,
                              help_text="The choice of question (max 255 characters).")

    def __unicode__(self):
        return self.choice


class DesignerLevel(models.Model):
    """Associates the actions to different levels."""
    name = models.CharField(max_length=50,
                            help_text="The name of the level.")
    slug = models.SlugField(help_text="Automatically generated if left blank.",
                            null=True)
    priority = models.IntegerField(
        default=1,
        help_text="Levels with lower values (higher priority) will be listed first."
    )
    unlock_condition = models.CharField(
        max_length=400, null=True, blank=True,
        help_text="if the condition is True, the level will be unlocked. " +
                   settings.PREDICATE_DOC_TEXT)
    unlock_condition_text = models.CharField(
        max_length=400, null=True, blank=True,
        help_text="The description of the unlock condition.")
    admin_tool_tip = "Smart Grid Level"

    def __unicode__(self):
        return self.name

    class Meta:
        """Meta"""
        ordering = ("priority",)

    def save(self, *args, **kwargs):
        """Custom save method to set fields."""
        super(DesignerLevel, self).save(args, kwargs)
        cache_mgr.clear()


class DesignerColumnName(models.Model):
    """ColumnNames used to group actions in the Smart Grid Designer."""
    name = models.CharField(max_length=255,
                            help_text="The name of the column (max 255 characters).")
    slug = models.SlugField(help_text="Automatically generated if left blank.",
                            null=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Custom save method to set fields."""
        super(DesignerColumnName, self).save(args, kwargs)
        cache_mgr.clear()


class DesignerAction(models.Model):
    """Activity Base class."""
    TYPE_CHOICES = (
        ('activity', 'Activity'),
        ('commitment', 'Commitment'),
        ('event', 'Event'),
        ('filler', 'Filler'),
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
                  "This is the unique id of the video as identified by the YouTube video url."
    )
    video_source = models.CharField(
        null=True, blank=True,
        max_length=20,
        choices=VIDEO_SOURCE_CHOICES,
        help_text="The source of the video."
    )
    embedded_widget = models.CharField(
        null=True, blank=True,
        max_length=50,
        help_text="The name of the embedded widget (optional)."
    )
    description = models.TextField(
        help_text="The discription of the action. " + settings.MARKDOWN_TEXT
    )
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        help_text="The type of the actions."
    )
    pub_date = models.DateField(
        default=datetime.date.today(),
        verbose_name="Publication date",
        help_text="Date from which the action will be available for users."
    )
    expire_date = models.DateField(
        null=True, blank=True,
        verbose_name="Expiration date",
        help_text="Date after which the action will be marked as expired."
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


class DesignerActivity(DesignerAction):
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

    def is_active(self):
        """Determines if the activity is available for users to participate."""
        return self.is_active_for_date(datetime.date.today())

    def is_active_for_date(self, date):
        """Determines if the activity is available for user participation at the given date."""
        pub_result = date - self.pub_date
        expire_result = self.expire_date - date
        if pub_result.days < 0 or expire_result.days < 0:
            return False
        return True

    def pick_question(self, user_id):
        """Choose a random question to present to a user."""
        if self.confirm_type != "text":
            return None

        questions = DesignerTextPromptQuestion.objects.filter(action=self)
        if questions:
            return questions[user_id % len(questions)]
        else:
            return None

    class Meta:
        """meta"""
        verbose_name_plural = "Activities"


class DesignerCommitment(DesignerAction):
    """Commitments involve non-verifiable actions that a user can commit to.
    Typically, they will be worth fewer points than activities."""
    commitment_length = models.IntegerField(
        default=5,
        help_text="Duration of commitment, in days."
    )


class DesignerEvent(DesignerAction):
    """Events will be verified by confirmation code. It includes events and excursions."""

    expected_duration = models.IntegerField(
        verbose_name="Expected activity duration",
        help_text="Time (in minutes) that the activity is expected to take."
    )
    event_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date and time of the event",
        help_text="Required for events."
    )
    event_location = models.CharField(
        blank=True,
        null=True,
        max_length=200,
        verbose_name="Event Location",
        help_text="Location of the event"
    )
    event_max_seat = models.IntegerField(
        default=1000,
        help_text="Specify the max number of seats available to the event."
    )

    def is_event_completed(self):
        """Determines if the event is completed."""
        if self.event_date:
            result = datetime.datetime.today() - self.event_date
            if result.days >= 0 and result.seconds >= 0:
                return True
        return False


class DesignerFiller(DesignerAction):
    """Filler action. It is always locked"""
    pass


class DesignerColumnGrid(models.Model):
    """Defines the DesignerColumn positions in the Designer Grid."""
    level = models.ForeignKey(DesignerLevel,
        help_text="The level of the action."
    )
    column = models.IntegerField(
        default=1,
        help_text="The column of the Smart Grid this Action is in.",
        validators=[MaxValueValidator(8)]
    )
    name = models.ForeignKey(DesignerColumnName,
                                 help_text="The name of the column in this location.")

    class Meta:
        """meta."""
        unique_together = ('level', 'name')

    def __unicode__(self):
        return "DesignerColumn: %s [%s, x=%s]" % (self.name, self.level, self.column)


class DesignerGrid(models.Model):
    """Defines the Designer Smart Grid, holds the level, column, row, and DesignerAction."""
    level = models.ForeignKey(DesignerLevel,
        help_text="The level of the action."
    )
    column = models.IntegerField(
        default=1,
        help_text="The column of the Smart Grid this Action is in.",
        validators=[MaxValueValidator(8)]
    )
    row = models.IntegerField(
        default=1,
        help_text="The row of the Smart Grid this Action is in.",
        validators=[MaxValueValidator(8)]
    )
    action = models.ForeignKey(DesignerAction,
                               help_text="The Action in this location.")

    class Meta:
        """Meta"""
        ordering = ("level", "column", "row")

    def __unicode__(self):
        return "%s: [%s, x=%s, y=%s]" % (self.action, self.level, self.column, self.row)

    def get_loc_str(self):
        """Returns the location of this grid object as a string."""
        return "[%s, x=%s, y=%s]" % (self.level, self.column, self.row)
