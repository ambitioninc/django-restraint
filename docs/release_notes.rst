Release Notes
=============

v2.3.1
------
* Read the Docs config file v2
* Github actions for testing psycopg3

v2.3.0
-------
* Django 3.2 & 4.0 support
* Django <3.2 dropped
* Switched testing to github actions

v2.2.0
------
* Added `restraint_db_updated` signal that is called when the restraint database is updated
* Added `is_locked` and `is_hidden` fields to `Perm` and `PermSet`

v2.1.3
------
* Update `filter_qset` to account for when a user might have access through a custom permission checker but no levels to filter on

v2.1.2
------
* When checking for permissions return early if the user has access

v2.1.1
------
* Fix for `perm_checker` being a method and not a string

v2.1.0
------
* Added `perm_checker` option to the `RESTRAINT_CONFIG` to allow for a custom permission checker

v2.0.1
------
* Added `assign_default_permissions_from_permission_set` to `PermAccess` manager

v2.0.0
------
* Removed `RESTRAINT_CONFIG` global variable, replaced with `get_restraint_config` method
* Removed `register_restraint_config` method, replaced with `RESTRAINT_CONFIGURATION` django setting
* Added `is_private` flag to PermSet model

v1.2.0
------
* Python 3.7
* Django 2.1
* Django 2.2

v1.1.0
------
* Add tox

v1.0.0
------
* Remove python 2.7 support
* Remove python 3.4 support
* Remove Django 1.9 support
* Remove Django 1.10 support
* Add Django 2.0 support

v0.7.0
------
* Add Python 3.6 support
* Remove Django 1.8 support
* Add Django 1.9 support
* Add Django 1.10 support

v0.6.0
------
* Add python 3.5 support
* Drop django 1.7 support

v0.5.1
------
* Filtering querysets can now optionally restrict a subset of a queryset based on a boolean permission, allowing the subset to be defined by arbitrary filter kwargs

v0.5.0
------
* When adding new permissions to existing permissions sets, update_restraint_db will add these new permissions while preserving any permissions already assigned to the permission set

v0.4.0
------
* Added Django 1.9 support

v0.3.0
------
* Added Django 1.8 support and dropped 1.6 support

v0.2.1
------
* Added Django 1.7 support

v0.2.0
------
* Added individual permission capabilities

v0.1
----
* This is the initial release of django-restraint.
