from django.db import models


class PermSet(models.Model):
    name = models.CharField(max_length=256, unique=True)


class Perm(models.Model):
    name = models.CharField(max_length=256, unique=True)


class PermLevel(models.Model):
    perm = models.ForeignKey(Perm)
    name = models.CharField(max_length=256)

    class Meta:
        unique_together = ('perm', 'name')


class PermAccessManager(models.Manager):
    def update_perm_set_access(self, config, flush_previous_config=False):
        for perm_set in PermSet.objects.all():
            perm_access, created = PermAccess.objects.get_or_create(perm_set=perm_set)
            if not created and not flush_previous_config:
                # If we are not flushing the previous config, continue if it exists
                continue

            perm_access_levels = []
            for perm, perm_levels in config.get(perm_set.name, {}).items():
                assert(perm_levels)
                perm_access_levels.extend(PermLevel.objects.filter(perm__name=perm, name__in=perm_levels))

            perm_access.perm_levels.clear()
            perm_access.perm_levels.add(*perm_access_levels)


class PermAccess(models.Model):
    perm_set = models.OneToOneField(PermSet)
    perm_levels = models.ManyToManyField(PermLevel)

    objects = PermAccessManager()
