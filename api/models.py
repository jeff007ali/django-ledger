from datetime import datetime
from django.db import models
import uuid


class Users(models.Model):
    '''Stores User data like name, username, password and current balance'''

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=16)
    balance = models.FloatField(default=0.0)

    def __str__(self):
        return "User {} has {} balance".format(self.name, self.balance)


TRANSACTION_STATUS_CHOICES = (
    ("paid", "paid"),
    ("unpaid", "unpaid")
)


class Transactions(models.Model):
    '''Stores Transactional data like who has borrowed/lended how much money to whom on which date and why'''

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_date = models.DateTimeField(default=datetime.now)
    transaction_status = models.CharField(
        max_length=25, choices=TRANSACTION_STATUS_CHOICES)
    transaction_from = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="transaction_from")
    transaction_with = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="transaction_with")
    transaction_amount = models.FloatField()
    reason = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return "{} has paid {} amount to {}".format(self.transaction_from, self.transaction_amount, self.transaction_with)
