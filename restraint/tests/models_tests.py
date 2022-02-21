from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import SimpleTestCase, TestCase
from django_dynamic_fixture import N, G, F

from restraint.models import PermSet, Perm, PermLevel, PermAccess


class PermSetTest(SimpleTestCase):
    def test_str(self):
        ps = N(PermSet, display_name='My Perm Set')
        self.assertTrue(str(ps), 'My Perm Set')


class PermTest(SimpleTestCase):
    def test_str(self):
        ps = N(Perm, display_name='My Perm')
        self.assertTrue(str(ps), 'My Perm')


class PermLevelTest(TestCase):
    def test_str(self):
        ps = N(PermLevel, display_name='My Perm Level')
        self.assertTrue(str(ps), 'My Perm Level')


class PermAccessTest(TestCase):
    def test_set_default(self):
        """
        Test setting default access
        """
        permission_set = G(PermSet, name='my_set')
        permission_level = G(PermLevel, perm=F(name='my_perm'), name='my_level')
        PermAccess.objects.set_default(
            permission_set_name=permission_set.name,
            permission_name='my_perm',
            levels=[permission_level.name]
        )
        pa = PermAccess.objects.get(perm_user_id=0, perm_user_type=None, perm_set=permission_set)
        self.assertEquals(list(pa.perm_levels.all()), [permission_level])

        # Set defaults to none
        PermAccess.objects.set_default(
            permission_set_name=permission_set.name,
            permission_name='my_perm',
        )
        pa = PermAccess.objects.get(perm_user_id=0, perm_user_type=None, perm_set=permission_set)
        self.assertEquals(list(pa.perm_levels.all()), [])

    def test_add_individual_access_level_exists(self):
        """
        Tests adding an individual permission to a user.
        """
        u = G(User)
        pl = G(PermLevel, perm=F(name='my_perm'), name='my_level')

        PermAccess.objects.add_individual_access(u, 'my_perm', 'my_level')
        PermAccess.objects.add_individual_access(u, 'my_perm', 'my_level')

        pa = PermAccess.objects.get(perm_user_id=u.id, perm_user_type=ContentType.objects.get_for_model(u))
        self.assertEquals(list(pa.perm_levels.all()), [pl])

    def test_remove_individual_access_level_exists(self):
        """
        Tests adding an individual permission to a user.
        """
        u = G(User)
        G(PermLevel, perm=F(name='my_perm'), name='my_level')

        PermAccess.objects.add_individual_access(u, 'my_perm', 'my_level')
        PermAccess.objects.add_individual_access(u, 'my_perm', 'my_level')
        PermAccess.objects.remove_individual_access(u, 'my_perm', 'my_level')

        pa = PermAccess.objects.get(perm_user_id=u.id, perm_user_type=ContentType.objects.get_for_model(u))
        self.assertEquals(list(pa.perm_levels.all()), [])
