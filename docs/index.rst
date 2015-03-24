Django-restraint Documentation
==============================
Restraint is a dynamic object-level permission system for Django. An overview of Django restraint is below, followed by :doc:`Installation<installation>`, :doc:`Setup<setup>`, :doc:`Usage<usage>`,
and :doc:`API documentation <ref/restraint>`

Overview
--------
The key purposes of Restraint are:

1. To provide a high-performance method of obtaining permissions over various object levels.
2. To prevent the user from having to sync permission objects while the properties of their accounts change. In other words, all permissions are determined dynamically.

The above is performed by registering a Restraint configuration, which details all of the permission sets and permissions / permission levels that are defined for those sets.

The terms mentioned above are defined as follows:

* Permission - A permission is an action that can be performed.
* Permission level - A permission level is a level of control over that action. Even boolean permissions, i.e. those that are on and off, always have a global control level set on them.
* Permission set - A permission set is a grouping of permission levels. Think of Django users belonging to groups that have permissions assigned to them. The concept is similar.

How are permission sets of users determined? Dynamically. A function is registered in the Restraint configuration that accepts a user and returns a list of strings that constitute their permission sets. These strings could be determined from fields on the model or even group relationships of users. Note that a user can be any model.

How do I figure out the permissions of a user? Dynamically. You instantiate a `Restraint` object with the user and the permissions you are interested in obtaining. The `Restraint` object can then easily tell you if a user has certain permissions and limit querysets by the permissions they own.

How can I get started using this?

1. Read the :doc:`Setup Documentation<setup>` first.
2. Read the :doc:`Usage Documentation<usage>` next.


Requirements
------------
Django restraint currently only supports Django 1.6 and above, although it can easily be upgraded to support more versions than the original user of the code.
