from django.contrib import admin
from fileprocess.models import ProductFile, AwsUserAccessDetails, AwsUploadDetails
# Register your models here.
admin.site.register(ProductFile)
admin.site.register(AwsUserAccessDetails)
admin.site.register(AwsUploadDetails)
