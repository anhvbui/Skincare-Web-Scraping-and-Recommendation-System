from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class TestUser(models.Model):
    name = models.CharField(max_length=100)
    des=models.TextField()
    def __str__(self):
        return self.name

#  Structure of the database table
class UserInput(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    routine_steps = models.IntegerField()
    age = models.CharField(max_length=50)
    skin_type = models.CharField(max_length=100)
    skin_concerns = models.JSONField()
    soothing_adj = models.JSONField()
    sun_care_adj = models.JSONField()
    well_aging_adj = models.JSONField()
    acne = models.FloatField()
    blackheads = models.FloatField()
    brightening = models.FloatField()
    sun_care = models.FloatField()
    moisturising = models.FloatField()
    dullness = models.FloatField()
    soothing = models.FloatField()
    stress = models.FloatField()
    visible_pores = models.FloatField()
    well_aging = models.FloatField()
    sculpting = models.FloatField()
    puffiness = models.FloatField()
    scarring = models.FloatField()
    dry = models.FloatField()
    combination = models.FloatField()
    oily = models.FloatField()
    sensitive = models.FloatField()
    normal = models.FloatField()


class ProductData(models.Model):
    brand_name = models.TextField()
    prod_name = models.TextField()
    price = models.FloatField()
    rating = models.FloatField()
    category = models.TextField()
    subcategory = models.TextField()
    ingredients = models.TextField()
    review_no = models.IntegerField()
    link = models.TextField()

class ProductReviewData(models.Model):
    prod_name = models.TextField()
    user_skin_type = models.JSONField()
    user_skin_concerns = models.JSONField()