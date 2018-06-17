# Generated by Django 2.0 on 2018-06-08 14:44

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import shortuuidfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idx', shortuuidfield.fields.ShortUUIDField(blank=True, editable=False, max_length=22, unique=True)),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('is_obsolete', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=50)),
                ('url', models.CharField(max_length=50)),
                ('method', models.CharField(max_length=50)),
                ('description', models.CharField(blank=True, max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idx', shortuuidfield.fields.ShortUUIDField(blank=True, editable=False, max_length=22, unique=True)),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('is_obsolete', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('alias', models.CharField(blank=True, max_length=50)),
                ('description', models.CharField(max_length=100)),
                ('precedence', models.IntegerField(default=0)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='permissions.Role')),
                ('permissions', models.ManyToManyField(blank=True, related_name='roles', to='permissions.Permission')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='permission',
            unique_together={('name', 'method')},
        ),
    ]
