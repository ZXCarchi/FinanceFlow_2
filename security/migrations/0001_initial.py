from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [migrations.CreateModel(name='AuthRateBucket', fields=[
        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        ('key', models.CharField(max_length=64, unique=True)),
        ('window', models.BigIntegerField()),
        ('count', models.PositiveIntegerField(default=0)),
    ])]
