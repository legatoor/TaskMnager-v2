from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('members', '0001_alter_category_options_alter_task_priority_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='observers',
            field=models.ManyToManyField(blank=True, related_name='observed_tasks', to='auth.user'),
        ),
    ]
