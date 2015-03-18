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


class PermAccess(models.Model):
    perm_set = models.OneToOneField(PermSet)
    perm_levels = models.ManyToManyField(PermLevel)
