# Generated by Django 3.2.5 on 2022-01-14 08:36

import aws_app.models
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MyUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('email', models.EmailField(blank=True, max_length=255, null=True, verbose_name='email address')),
                ('access_key', models.CharField(max_length=255, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FLag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flag_name', models.CharField(choices=[('quality_issue', 'quality_issue'), ('more_faces', 'more_faces'), ('noface_for_2_sec', 'noface_for_2_sec'), ('face_not_centered', 'face_not_centered'), ('face_covered', 'face_covered'), ('mobile_detection', 'mobile_detection'), ('sun_glasses', 'sun_glasses'), ('head_covered', 'head_covered')], max_length=30)),
                ('flagged_time', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Flag',
            },
        ),
        migrations.CreateModel(
            name='ImageFrames',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_stamp', models.DateTimeField(auto_now_add=True)),
                ('image_frame', models.FileField(blank=True, max_length=500, null=True, upload_to='camera_frames', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['blp', 'bmp', 'dib', 'bufr', 'cur', 'pcx', 'dcx', 'dds', 'ps', 'eps', 'fit', 'fits', 'fli', 'flc', 'ftc', 'ftu', 'gbr', 'gif', 'grib', 'h5', 'hdf', 'png', 'apng', 'jp2', 'j2k', 'jpc', 'jpf', 'jpx', 'j2c', 'icns', 'ico', 'im', 'iim', 'tif', 'tiff', 'jfif', 'jpe', 'jpg', 'jpeg', 'mpg', 'mpeg', 'mpo', 'msp', 'palm', 'pcd', 'pdf', 'pxr', 'pbm', 'pgm', 'ppm', 'pnm', 'psd', 'bw', 'rgb', 'rgba', 'sgi', 'ras', 'tga', 'icb', 'vda', 'vst', 'webp', 'wmf', 'emf', 'xbm', 'xpm'], message="'%(extension)s' not valid Image."), aws_app.models.profile_size])),
                ('frame_captype', models.CharField(choices=[('register', 'REGISTER'), ('mentoring', 'MENTORING')], max_length=30)),
                ('is_red_flagged', models.BooleanField(default=False)),
                ('attempt_id', models.IntegerField()),
                ('test_id', models.IntegerField()),
                ('client_id', models.IntegerField()),
                ('profile_id', models.IntegerField()),
                ('flagged_as', models.ManyToManyField(blank=True, to='aws_app.FLag')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]