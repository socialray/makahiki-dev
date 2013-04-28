import datetime
import os.path
from django.conf import settings

from django.db import models
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.utils.translation import ugettext as _
from apps.managers.cache_mgr import cache_mgr
from apps.widgets.smartgrid.models import ActionMember

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    from PIL import Image
except ImportError:
    import Image

from apps.lib.avatar import AVATAR_STORAGE_DIR, AVATAR_RESIZE_METHOD

def avatar_file_path(instance=None, filename=None, user=None):
    user = user or instance.user
    return os.path.join(settings.MAKAHIKI_MEDIA_PREFIX,
                        AVATAR_STORAGE_DIR,
                        user.username,
                        filename)


class Avatar(models.Model):
    user = models.ForeignKey(User)
    primary = models.BooleanField(default=False)
    avatar = models.ImageField(max_length=1024,
                               upload_to=avatar_file_path,
                               blank=True)
    date_uploaded = models.DateTimeField(default=datetime.datetime.now)

    def __unicode__(self):
        return _(u'Avatar for %s') % self.user

    def save(self, *args, **kwargs):
        if self.primary:
            avatars = Avatar.objects.filter(user=self.user, primary=True)\
            .exclude(id=self.id)
            avatars.update(primary=False)

        super(Avatar, self).save(*args, **kwargs)

        # Invalidate info bar cache.
        user = self.user
        cache_mgr.invalidate_template_cache("RIB", user.username)
        # Invalidate team action avatar cache.
        team = user.get_profile().team
        if team:
            cache_mgr.invalidate_template_cache("team_member_avatar", team.id)
            for member in ActionMember.objects.filter(user=user):
                cache_mgr.invalidate_template_cache("team_avatar", member.action.id, team.id)

    def thumbnail_exists(self, size):
        return self.avatar.storage.exists(self.avatar_name(size))

    def create_thumbnail(self, size):
        try:
            orig = self.avatar.storage.open(self.avatar.name, 'rb').read()
            image = Image.open(StringIO(orig))
        except IOError:
            return  # What should we do here?  Render a "sorry,
            # didn't work" img?
        (w, h) = image.size
        if w != size or h != size:
            if w > h:
                diff = (w - h) / 2
                image = image.crop((diff, 0, w - diff, h))
            else:
                diff = (h - w) / 2
                image = image.crop((0, diff, w, h - diff))
            image = image.resize((size, size), AVATAR_RESIZE_METHOD)
            if image.mode != "RGB":
                image = image.convert("RGB")
            thumb = StringIO()
            image.save(thumb, "JPEG")
            thumb_file = ContentFile(thumb.getvalue())
        else:
            thumb_file = ContentFile(orig)
        self.avatar.storage.delete(self.avatar_name(size))
        thumb = self.avatar.storage.save(self.avatar_name(size), thumb_file)

    def avatar_url(self, size):
        return self.avatar.storage.url(self.avatar_name(size))

    def avatar_name(self, size):
        return os.path.join(settings.MAKAHIKI_MEDIA_PREFIX,
                            AVATAR_STORAGE_DIR,
                            self.user.username,
                            'resized',
                            str(size),
                            self.avatar.name)
