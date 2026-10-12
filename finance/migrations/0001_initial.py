from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(name='Category', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('name', models.CharField(max_length=80)), ('code', models.SlugField(blank=True, max_length=50)),
            ('kind', models.CharField(choices=[('expense','Expense'),('income','Income'),('both','Both')], default='expense', max_length=10)),
            ('icon', models.CharField(default='•', max_length=16)), ('color', models.CharField(default='#6c5ce7', max_length=16)),
            ('is_default', models.BooleanField(default=False)),
            ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to=settings.AUTH_USER_MODEL)),
        ], options={'ordering':['kind','name']}),
        migrations.CreateModel(name='SavingsGoal', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('name', models.CharField(max_length=120)), ('target_amount', models.DecimalField(decimal_places=2,max_digits=12)),
            ('saved_amount', models.DecimalField(decimal_places=2,default=0,max_digits=12)), ('target_date', models.DateField(blank=True,null=True)),
            ('icon', models.CharField(default='🎯',max_length=16)), ('created_at', models.DateTimeField(auto_now_add=True)),
            ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='goals', to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name='Wallet', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('name', models.CharField(max_length=80)), ('wallet_type', models.CharField(choices=[('card','Card'),('cash','Cash'),('savings','Savings'),('other','Other')],default='card',max_length=20)),
            ('opening_balance', models.DecimalField(decimal_places=2,default=0,max_digits=12)), ('is_active', models.BooleanField(default=True)), ('created_at',models.DateTimeField(auto_now_add=True)),
            ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wallets', to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name='Transaction', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('kind', models.CharField(choices=[('income','Income'),('expense','Expense')],max_length=10)), ('amount',models.DecimalField(decimal_places=2,max_digits=12)),
            ('title',models.CharField(max_length=120)), ('date',models.DateField(default=django.utils.timezone.localdate)), ('note',models.CharField(blank=True,max_length=250)), ('created_at',models.DateTimeField(auto_now_add=True)),
            ('category',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.SET_NULL,related_name='transactions',to='finance.category')),
            ('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='transactions',to=settings.AUTH_USER_MODEL)),
            ('wallet',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='transactions',to='finance.wallet')),
        ], options={'ordering':['-date','-created_at']}),
        migrations.CreateModel(name='RecurringPayment', fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')), ('title',models.CharField(max_length=120)), ('amount',models.DecimalField(decimal_places=2,max_digits=12)),
            ('kind',models.CharField(choices=[('income','Income'),('expense','Expense')],default='expense',max_length=10)), ('day_of_month',models.PositiveSmallIntegerField(default=1)), ('is_active',models.BooleanField(default=True)), ('created_at',models.DateTimeField(auto_now_add=True)),
            ('category',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.SET_NULL,to='finance.category')),
            ('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='recurring_payments',to=settings.AUTH_USER_MODEL)),
            ('wallet',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='recurring_payments',to='finance.wallet')),
        ]),
        migrations.CreateModel(name='BudgetLimit', fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')), ('monthly_limit',models.DecimalField(decimal_places=2,max_digits=12)),
            ('category',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='limits',to='finance.category')),
            ('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='budget_limits',to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.AddConstraint(model_name='budgetlimit', constraint=models.UniqueConstraint(fields=('user','category'), name='unique_user_category_budget')),
    ]
