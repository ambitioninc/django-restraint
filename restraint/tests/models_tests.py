from django.test import SimpleTestCase
from django_dynamic_fixture import N

from restraint.models import PermSet, Perm, PermLevel


class PermSetTest(SimpleTestCase):
    def test_unicode(self):
        ps = N(PermSet, display_name='My Perm Set', persist_dependencies=False)
        self.assertTrue(ps.__unicode__(), 'My Perm Set')


class PermTest(SimpleTestCase):
    def test_unicode(self):
        ps = N(Perm, display_name='My Perm', persist_dependencies=False)
        self.assertTrue(ps.__unicode__(), 'My Perm')


class PermLevelTest(SimpleTestCase):
    def test_unicode(self):
        ps = N(PermLevel, display_name='My Perm Level', persist_dependencies=False)
        self.assertTrue(ps.__unicode__(), 'My Perm Level')
