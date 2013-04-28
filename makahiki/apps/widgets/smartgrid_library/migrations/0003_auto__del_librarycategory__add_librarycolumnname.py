# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'LibraryCategory'
        db.delete_table('smartgrid_library_librarycategory')

        # Adding model 'LibraryColumnName'
        db.create_table('smartgrid_library_librarycolumnname', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, null=True, db_index=True)),
        ))
        db.send_create_signal('smartgrid_library', ['LibraryColumnName'])


    def backwards(self, orm):
        
        # Adding model 'LibraryCategory'
        db.create_table('smartgrid_library_librarycategory', (
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, null=True, db_index=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('smartgrid_library', ['LibraryCategory'])

        # Deleting model 'LibraryColumnName'
        db.delete_table('smartgrid_library_librarycolumnname')


    models = {
        'smartgrid_library.libraryaction': {
            'Meta': {'object_name': 'LibraryAction'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'embedded_widget': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'point_value': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'related_resource': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'social_bonus': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'unlock_condition': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'unlock_condition_text': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'video_id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'video_source': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        'smartgrid_library.libraryactivity': {
            'Meta': {'object_name': 'LibraryActivity', '_ormbases': ['smartgrid_library.LibraryAction']},
            'admin_note': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'confirm_prompt': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'confirm_type': ('django.db.models.fields.CharField', [], {'default': "'text'", 'max_length': '20'}),
            'expected_duration': ('django.db.models.fields.IntegerField', [], {}),
            'libraryaction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['smartgrid_library.LibraryAction']", 'unique': 'True', 'primary_key': 'True'}),
            'point_range_end': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'point_range_start': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'smartgrid_library.librarycolumnname': {
            'Meta': {'ordering': "('name',)", 'object_name': 'LibraryColumnName'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'null': 'True', 'db_index': 'True'})
        },
        'smartgrid_library.librarycommitment': {
            'Meta': {'object_name': 'LibraryCommitment', '_ormbases': ['smartgrid_library.LibraryAction']},
            'commitment_length': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'libraryaction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['smartgrid_library.LibraryAction']", 'unique': 'True', 'primary_key': 'True'})
        },
        'smartgrid_library.libraryevent': {
            'Meta': {'object_name': 'LibraryEvent', '_ormbases': ['smartgrid_library.LibraryAction']},
            'expected_duration': ('django.db.models.fields.IntegerField', [], {}),
            'libraryaction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['smartgrid_library.LibraryAction']", 'unique': 'True', 'primary_key': 'True'})
        },
        'smartgrid_library.libraryquestionchoice': {
            'Meta': {'object_name': 'LibraryQuestionChoice'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['smartgrid_library.LibraryAction']"}),
            'choice': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['smartgrid_library.LibraryTextPromptQuestion']"})
        },
        'smartgrid_library.librarytextpromptquestion': {
            'Meta': {'object_name': 'LibraryTextPromptQuestion'},
            'answer': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'libraryaction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['smartgrid_library.LibraryAction']"}),
            'question': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['smartgrid_library']
