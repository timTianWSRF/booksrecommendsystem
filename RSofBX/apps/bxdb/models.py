from django.db import models

# Create your models here.


class admin_info(models.Model):
    admin_user  = models.CharField(max_length=32)
    admin_pwd = models.CharField(max_length=32)

    def __str__(self):
        return str(self.admin_user)


class bx_info(models.Model):
    book_id = models.IntegerField(primary_key=True)
    gb_id = models.IntegerField(blank=True,null=True)
    work_id = models.IntegerField(blank=True,null=True)
    isbn = models.CharField(max_length=15)
    book_author = models.CharField(max_length=255)
    publication_year = models.PositiveIntegerField()
    original_title = models.CharField(max_length=255,blank=True,null=True)
    book_title = models.CharField(max_length=255)
    language_code = models.CharField(max_length=10)
    average_rating = models.FloatField(max_length=10,blank=True,null=True)
    ratings_count = models.IntegerField(blank=True,null=True)
    image_url = models.CharField(max_length=255,blank=True,null=True)
    publisher = models.CharField(max_length=100,blank=True,null=True)

    def __str__(self):
        return str(self.book_title)




class user_info(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=100)
    password = models.CharField(max_length=20)
    age = models.IntegerField(blank=True,null=True)
    location = models.CharField(max_length=250,blank=True,null=True)

    def __str__(self):
        return str(self.user_name)


class tags(models.Model):
    tag_id = models.IntegerField(primary_key=True)
    tag_name = models.CharField(max_length=255)

    def __str__(self):
        return str(self.tag_name)


class book_tags(models.Model):
    gb_id = models.IntegerField()
    tag_id = models.IntegerField()
    count = models.IntegerField()

    def __str__(self):
        return str(self.gb_id)

class book_ratings(models.Model):
    user_id = models.IntegerField()
    book_id = models.IntegerField()
    rating = models.IntegerField()

    def __str__(self):
        return str(self.user_id)