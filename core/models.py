
from django.db import models

class Pizza(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    description = models.TextField()
    price = models.FloatField()

    class Meta:
        managed = False
        db_table = 'pizzas'
    def _str_(self): return self.name


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    phone = models.TextField()
    address = models.TextField()
    total = models.FloatField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'orders'
    def _str_(self): return f'Order #{self.id}'


class OrderItem(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING, db_column='order_id', related_name='items')
    pizza = models.ForeignKey(Pizza, on_delete=models.DO_NOTHING, db_column='pizza_id')
    qty = models.IntegerField()
    price = models.FloatField()

    class Meta:
        managed = False
        db_table = 'order_items'