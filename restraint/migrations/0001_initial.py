# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PermSet'
        db.create_table(u'restraint_permset', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=256)),
        ))
        db.send_create_signal(u'restraint', ['PermSet'])

        # Adding model 'Perm'
        db.create_table(u'restraint_perm', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=256)),
        ))
        db.send_create_signal(u'restraint', ['Perm'])

        # Adding model 'PermLevel'
        db.create_table(u'restraint_permlevel', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('perm', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['restraint.Perm'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal(u'restraint', ['PermLevel'])

        # Adding unique constraint on 'PermLevel', fields ['perm', 'name']
        db.create_unique(u'restraint_permlevel', ['perm_id', 'name'])

        # Adding model 'PermAccess'
        db.create_table(u'restraint_permaccess', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('perm_set', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['restraint.PermSet'], unique=True)),
        ))
        db.send_create_signal(u'restraint', ['PermAccess'])

        # Adding M2M table for field perm_levels on 'PermAccess'
        m2m_table_name = db.shorten_name(u'restraint_permaccess_perm_levels')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('permaccess', models.ForeignKey(orm[u'restraint.permaccess'], null=False)),
            ('permlevel', models.ForeignKey(orm[u'restraint.permlevel'], null=False))
        ))
        db.create_unique(m2m_table_name, ['permaccess_id', 'permlevel_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'PermLevel', fields ['perm', 'name']
        db.delete_unique(u'restraint_permlevel', ['perm_id', 'name'])

        # Deleting model 'PermSet'
        db.delete_table(u'restraint_permset')

        # Deleting model 'Perm'
        db.delete_table(u'restraint_perm')

        # Deleting model 'PermLevel'
        db.delete_table(u'restraint_permlevel')

        # Deleting model 'PermAccess'
        db.delete_table(u'restraint_permaccess')

        # Removing M2M table for field perm_levels on 'PermAccess'
        db.delete_table(db.shorten_name(u'restraint_permaccess_perm_levels'))


    models = {
        u'restraint.perm': {
            'Meta': {'object_name': 'Perm'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'})
        },
        u'restraint.permaccess': {
            'Meta': {'object_name': 'PermAccess'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'perm_levels': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['restraint.PermLevel']", 'symmetrical': 'False'}),
            'perm_set': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['restraint.PermSet']", 'unique': 'True'})
        },
        u'restraint.permlevel': {
            'Meta': {'unique_together': "(('perm', 'name'),)", 'object_name': 'PermLevel'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'perm': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['restraint.Perm']"})
        },
        u'restraint.permset': {
            'Meta': {'object_name': 'PermSet'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'})
        }
    }

    complete_apps = ['restraint']