# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'PermAccess.perm_user_type'
        db.add_column(u'restraint_permaccess', 'perm_user_type',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['contenttypes.ContentType'], null=True),
                      keep_default=False)

        # Adding field 'PermAccess.perm_user_id'
        db.add_column(u'restraint_permaccess', 'perm_user_id',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)


        # Changing field 'PermAccess.perm_set'
        db.alter_column(u'restraint_permaccess', 'perm_set_id', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['restraint.PermSet'], unique=True, null=True))
        # Adding unique constraint on 'PermAccess', fields ['perm_user_type', 'perm_user_id']
        db.create_unique(u'restraint_permaccess', ['perm_user_type_id', 'perm_user_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'PermAccess', fields ['perm_user_type', 'perm_user_id']
        db.delete_unique(u'restraint_permaccess', ['perm_user_type_id', 'perm_user_id'])

        # Deleting field 'PermAccess.perm_user_type'
        db.delete_column(u'restraint_permaccess', 'perm_user_type_id')

        # Deleting field 'PermAccess.perm_user_id'
        db.delete_column(u'restraint_permaccess', 'perm_user_id')


        # Changing field 'PermAccess.perm_set'
        db.alter_column(u'restraint_permaccess', 'perm_set_id', self.gf('django.db.models.fields.related.OneToOneField')(default=0, to=orm['restraint.PermSet'], unique=True))

    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'restraint.perm': {
            'Meta': {'object_name': 'Perm'},
            'display_name': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256', 'blank': 'True'})
        },
        u'restraint.permaccess': {
            'Meta': {'unique_together': "(('perm_user_type', 'perm_user_id'),)", 'object_name': 'PermAccess'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'perm_levels': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['restraint.PermLevel']", 'symmetrical': 'False'}),
            'perm_set': ('django.db.models.fields.related.OneToOneField', [], {'default': 'None', 'to': u"orm['restraint.PermSet']", 'unique': 'True', 'null': 'True'}),
            'perm_user_id': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'perm_user_type': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['contenttypes.ContentType']", 'null': 'True'})
        },
        u'restraint.permlevel': {
            'Meta': {'unique_together': "(('perm', 'name'),)", 'object_name': 'PermLevel'},
            'display_name': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'perm': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['restraint.Perm']"})
        },
        u'restraint.permset': {
            'Meta': {'object_name': 'PermSet'},
            'display_name': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256', 'blank': 'True'})
        }
    }

    complete_apps = ['restraint']