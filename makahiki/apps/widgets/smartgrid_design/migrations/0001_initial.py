# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'DesignerTextPromptQuestion'
        db.create_table('smartgrid_design_designertextpromptquestion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartgrid_design.DesignerAction'])),
            ('question', self.gf('django.db.models.fields.TextField')()),
            ('answer', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('smartgrid_design', ['DesignerTextPromptQuestion'])

        # Adding model 'DesignerQuestionChoice'
        db.create_table('smartgrid_design_designerquestionchoice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartgrid_design.DesignerTextPromptQuestion'])),
            ('action', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartgrid_design.DesignerAction'])),
            ('choice', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('smartgrid_design', ['DesignerQuestionChoice'])

        # Adding model 'DesignerLevel'
        db.create_table('smartgrid_design_designerlevel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, null=True, db_index=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('unlock_condition', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
            ('unlock_condition_text', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
        ))
        db.send_create_signal('smartgrid_design', ['DesignerLevel'])

        # Adding model 'DesignerCategory'
        db.create_table('smartgrid_design_designercategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, null=True, db_index=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal('smartgrid_design', ['DesignerCategory'])

        # Adding model 'DesignerAction'
        db.create_table('smartgrid_design_designeraction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, db_index=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=255, null=True, blank=True)),
            ('video_id', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('video_source', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('embedded_widget', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('level', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartgrid_design.DesignerLevel'], null=True, blank=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartgrid_design.DesignerCategory'], null=True, blank=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=1000)),
            ('pub_date', self.gf('django.db.models.fields.DateField')(default=datetime.date(2013, 3, 19))),
            ('expire_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('unlock_condition', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
            ('unlock_condition_text', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
            ('related_resource', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('social_bonus', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('point_value', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('smartgrid_design', ['DesignerAction'])

        # Adding model 'Activity'
        db.create_table('smartgrid_design_activity', (
            ('designeraction_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['smartgrid_design.DesignerAction'], unique=True, primary_key=True)),
            ('expected_duration', self.gf('django.db.models.fields.IntegerField')()),
            ('point_range_start', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('point_range_end', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('confirm_type', self.gf('django.db.models.fields.CharField')(default='text', max_length=20)),
            ('confirm_prompt', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('admin_note', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('smartgrid_design', ['Activity'])

        # Adding model 'Commitment'
        db.create_table('smartgrid_design_commitment', (
            ('designeraction_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['smartgrid_design.DesignerAction'], unique=True, primary_key=True)),
            ('commitment_length', self.gf('django.db.models.fields.IntegerField')(default=5)),
        ))
        db.send_create_signal('smartgrid_design', ['Commitment'])

        # Adding model 'Event'
        db.create_table('smartgrid_design_event', (
            ('designeraction_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['smartgrid_design.DesignerAction'], unique=True, primary_key=True)),
            ('expected_duration', self.gf('django.db.models.fields.IntegerField')()),
            ('event_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('event_location', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('event_max_seat', self.gf('django.db.models.fields.IntegerField')(default=1000)),
        ))
        db.send_create_signal('smartgrid_design', ['Event'])

        # Adding model 'Filler'
        db.create_table('smartgrid_design_filler', (
            ('designeraction_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['smartgrid_design.DesignerAction'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('smartgrid_design', ['Filler'])


    def backwards(self, orm):
        
        # Deleting model 'DesignerTextPromptQuestion'
        db.delete_table('smartgrid_design_designertextpromptquestion')

        # Deleting model 'DesignerQuestionChoice'
        db.delete_table('smartgrid_design_designerquestionchoice')

        # Deleting model 'DesignerLevel'
        db.delete_table('smartgrid_design_designerlevel')

        # Deleting model 'DesignerCategory'
        db.delete_table('smartgrid_design_designercategory')

        # Deleting model 'DesignerAction'
        db.delete_table('smartgrid_design_designeraction')

        # Deleting model 'Activity'
        db.delete_table('smartgrid_design_activity')

        # Deleting model 'Commitment'
        db.delete_table('smartgrid_design_commitment')

        # Deleting model 'Event'
        db.delete_table('smartgrid_design_event')

        # Deleting model 'Filler'
        db.delete_table('smartgrid_design_filler')


    models = {
        'smartgrid_design.activity': {
            'Meta': {'ordering': "('level', 'category', 'priority')", 'object_name': 'Activity', '_ormbases': ['smartgrid_design.DesignerAction']},
            'admin_note': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'confirm_prompt': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'confirm_type': ('django.db.models.fields.CharField', [], {'default': "'text'", 'max_length': '20'}),
            'designeraction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['smartgrid_design.DesignerAction']", 'unique': 'True', 'primary_key': 'True'}),
            'expected_duration': ('django.db.models.fields.IntegerField', [], {}),
            'point_range_end': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'point_range_start': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'smartgrid_design.commitment': {
            'Meta': {'ordering': "('level', 'category', 'priority')", 'object_name': 'Commitment', '_ormbases': ['smartgrid_design.DesignerAction']},
            'commitment_length': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'designeraction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['smartgrid_design.DesignerAction']", 'unique': 'True', 'primary_key': 'True'})
        },
        'smartgrid_design.designeraction': {
            'Meta': {'ordering': "('level', 'category', 'priority')", 'object_name': 'DesignerAction'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['smartgrid_design.DesignerCategory']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'embedded_widget': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'expire_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['smartgrid_design.DesignerLevel']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'point_value': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1000'}),
            'pub_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date(2013, 3, 19)'}),
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
        'smartgrid_design.designercategory': {
            'Meta': {'ordering': "('priority',)", 'object_name': 'DesignerCategory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'null': 'True', 'db_index': 'True'})
        },
        'smartgrid_design.designerlevel': {
            'Meta': {'ordering': "('priority',)", 'object_name': 'DesignerLevel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'null': 'True', 'db_index': 'True'}),
            'unlock_condition': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'unlock_condition_text': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'})
        },
        'smartgrid_design.designerquestionchoice': {
            'Meta': {'object_name': 'DesignerQuestionChoice'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['smartgrid_design.DesignerAction']"}),
            'choice': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['smartgrid_design.DesignerTextPromptQuestion']"})
        },
        'smartgrid_design.designertextpromptquestion': {
            'Meta': {'object_name': 'DesignerTextPromptQuestion'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['smartgrid_design.DesignerAction']"}),
            'answer': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.TextField', [], {})
        },
        'smartgrid_design.event': {
            'Meta': {'ordering': "('level', 'category', 'priority')", 'object_name': 'Event', '_ormbases': ['smartgrid_design.DesignerAction']},
            'designeraction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['smartgrid_design.DesignerAction']", 'unique': 'True', 'primary_key': 'True'}),
            'event_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'event_location': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'event_max_seat': ('django.db.models.fields.IntegerField', [], {'default': '1000'}),
            'expected_duration': ('django.db.models.fields.IntegerField', [], {})
        },
        'smartgrid_design.filler': {
            'Meta': {'ordering': "('level', 'category', 'priority')", 'object_name': 'Filler', '_ormbases': ['smartgrid_design.DesignerAction']},
            'designeraction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['smartgrid_design.DesignerAction']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['smartgrid_design']
