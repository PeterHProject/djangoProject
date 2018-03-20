from django.db import models
from django.contrib.auth.models import User
import datetime
from django.utils import timezone
from django.urls import reverse
from django.conf import settings

#to override the default media upload - looking at protected non amazon storange
from django.core.files.storage import FileSystemStorage
from django.conf import settings

#when updating to AWS
from fileproject.aws.utils import ProtectedS3Storage
from fileproject.aws.download.utils import AWSDownload

from fileproject.aws.edit_requested_file.edit_req_class import Config, EditRequested

# Create your models here.

class Document(models.Model):
    document = models.FileField(upload_to="file", storage=ProtectedS3Storage())
    document_name = models.CharField(max_length=200)
    date_uploaded = models.DateTimeField(default=timezone.now)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)


    def __str__(self):
        return self.document_name

#this is to allow detail view to work - to check
    def get_absolute_url(self):
        return reverse("list")

    def get_choices(self):
        list(zip(self.document_name, self.pk))


def upload_product_file_loc(instance, file_name):
    location = "protected/{file}/".format(file=instance.uploaded_by)
    return location + file_name


class ProductFile(models.Model):
    file_name = models.CharField(max_length=200)
    file = models.FileField(upload_to=upload_product_file_loc,storage=ProtectedS3Storage())
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    date_uploaded = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.file_name

    def get_absolute_url(self):
        return reverse("list")

    def generate_download_url(self):
        bucket = getattr(settings, 'AWS_STORAGE_BUCKET_NAME')
        region = getattr(settings, 'S3DIRECT_REGION')
        access_key = getattr(settings, 'AWS_ACCESS_KEY_ID')
        secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY')
        PROTECTED_DIR_NAME = getattr(settings, 'PROTECTED_DIR_NAME')
        path = "{base}/{file_path}".format(base=PROTECTED_DIR_NAME, file_path=str(self.file))

        aws_dl_object =  AWSDownload(access_key, secret_key, bucket, region)
        file_url = aws_dl_object.generate_url(path)#, new_filename='New awesome file')

        return file_url

    def return_sql(self, file_path, table_name):
        access_key = getattr(settings, 'AWS_ACCESS_KEY_ID')
        secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY')
        bucket = getattr(settings, 'AWS_STORAGE_BUCKET_NAME')
        self.file_path = file_path
        item = EditRequested(access_key, secret_key, bucket).return_SQL(file_path, table_name)
        return item

    def return_names(self, file_path):
        access_key = getattr(settings, 'AWS_ACCESS_KEY_ID')
        secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY')
        bucket = getattr(settings, 'AWS_STORAGE_BUCKET_NAME')
        self.file_path = file_path
        item = EditRequested(access_key, secret_key, bucket).find_name(file_path)
        return item

    def excel_function(self, file_path, request_list):
        access_key = getattr(settings, 'AWS_ACCESS_KEY_ID')
        secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY')
        bucket = getattr(settings, 'AWS_STORAGE_BUCKET_NAME')
        self.file_path = file_path
        self.request_list = request_list
        item = EditRequested(access_key, secret_key, bucket).excel_function(file_path, request_list)
        #this function will auto go to the function

    def get_download_url(self):
        return reverse('product_download', kwargs={"pk":self.pk})

    @property
    def name(self):
        return self.file_name

class AwsUserAccessDetails(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    host = models.CharField(max_length=200)
    database = models.CharField(max_length=200)
    aws_user_name = models.CharField(max_length=200)
    aws_password = models.CharField(max_length=200, default='pre-test')

class AwsUploadDetails(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    table_name = models.CharField(max_length=200)
    date_uploaded = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.table_name



#This is how origionally done - and then update to AWS
# class ProductFile(models.Model):
#     file_name = models.CharField(max_length=200)
#     file = models.FileField(upload_to=upload_product_file_loc,storage=FileSystemStorage(location=settings.PROTECTED_ROOT))
#
#     def __str__(self):
#         return self.file_name
#
#         #this function will auto go to the function
#     def get_download_url(self):
#         return reverse('product_download', kwargs={"pk":self.pk})
#
#     @property
#     def name(self):
#         return self.file_name
