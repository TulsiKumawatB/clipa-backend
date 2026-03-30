from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('interactions', '0005_alter_comment_unique_together'),  # 👈 use your actual last migration
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='comment',
            unique_together={('user', 'video', 'parent')},
        ),
    ]