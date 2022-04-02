from datetime import datetime
from distutils.command.upload import upload
from django.db import models
from django.utils.html import format_html
from django.contrib.auth.models import User

BOOK_LEVEL_CHOICE = (
    ('B', 'Basic'),
    ('M', 'Medium'),
    ('A', 'Advance'),
)

class ContactMessage(models.Model):
    title = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    Comment = models.TextField(blank=True, null=True)
    reply = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'class ContactMessage'

    
    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Category'

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Author'

    def __str__(self):
        return self.name


 



class Book(models.Model):
    code= models.CharField(max_length=10, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    price = models.FloatField(default=0)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE)
    author = models.ManyToManyField(Author, blank=True)
    level = models.CharField(max_length=5, null=True, blank=True, choices=BOOK_LEVEL_CHOICE)
    image = models.FileField(upload_to='upload', null=True, blank=True)
    published = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']
        verbose_name_plural = 'Book'

    def __str__(self):
        return self.name

    def show_image(self):
        if self.image:
            return format_html('<img src="' + self.image.url + '" height="50px">')
        return ''
    show_image.allow_tags = True

    def get_comment_count(self):
        return self.bookcomment_set.count()

class Order(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    datetime = models.DateTimeField(max_length=100,auto_now_add=True,blank=True,null=True)
    product =  models.ForeignKey(Book,on_delete=models.CASCADE,null=True)
    qty = models.IntegerField()
    total_price = models.IntegerField()


class BookComment(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    comment = models.CharField(max_length=100)
    rating = models.IntegerField(default=0)

    class Meta:
        ordering = ['id']
        verbose_name_plural = 'Book Comment'

    def __str__(self):
        return self.comment

class ShippingAddress(models.Model):
    name = models.CharField(max_length=100,blank=True,null=True)
    tel = models.CharField(max_length=100,blank=True,null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True,null=True)
    address = models.CharField(max_length=200,blank=True, null=False)
    upload_slip = models.ImageField(upload_to="slip",blank=True,null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def str(self):
        return self.address
