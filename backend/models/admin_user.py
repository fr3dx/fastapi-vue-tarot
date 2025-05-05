from tortoise import fields
from tortoise.models import Model

class AdminUser(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    password = fields.CharField(max_length=128)

    def __str__(self):
        return self.username
