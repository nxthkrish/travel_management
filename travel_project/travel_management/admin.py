from django.contrib import admin
from .models import CustomUser, TravelRequest, Manager, Employee, Approval, AdminRequestProcessing

# Register your models here
admin.site.register(CustomUser)
admin.site.register(TravelRequest)
admin.site.register(Manager)
admin.site.register(Employee)
admin.site.register(Approval)
admin.site.register(AdminRequestProcessing)
