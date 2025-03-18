from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.hashers import make_password

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('employee', 'Employee'),
        ('manager', 'Manager'),
    )
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('disabled', 'Disabled'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return f"{self.username} ({self.role})"

class Manager(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='manager_profile')
    department = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.username} - {self.department}"

class Employee(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='employee_profile')
    position = models.CharField(max_length=50, default="Employee")
    manager = models.ForeignKey(Manager, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_employees')

    def __str__(self):
        return f"{self.user.username} - {self.position}"
# Travel Request Model
class TravelRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Clarification Requested', 'Clarification Requested'),
        ('Closed', 'Closed'),
    ]
    
    STATUS_UPDATED_BY_CHOICES = [
        ('Employee', 'Employee'),
        ('Manager', 'Manager'),
        ('Admin', 'Admin'),
    ]
    
    TRAVEL_MODE_CHOICES = [
        ('Flight', 'Flight'),
        ('Train', 'Train'),
        ('Bus', 'Bus'),
        ('Car', 'Car'),
    ]

    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="travel_requests")
    destination = models.CharField(max_length=255, null=True, blank=True)
    from_location = models.CharField(max_length=255, null=True, blank=True)
    to_location = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    purpose = models.TextField()
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='Pending')
    status_updated_by = models.CharField(max_length=10, choices=STATUS_UPDATED_BY_CHOICES, null=True, blank=True)
    travel_mode = models.CharField(max_length=10, choices=TRAVEL_MODE_CHOICES, null=True, blank=True)
    lodging_required = models.BooleanField(default=False)
    lodging_location = models.CharField(max_length=255, null=True, blank=True)
    additional_requests = models.TextField(null=True, blank=True)
    requested_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="requested_travel_changes")
    resubmitted = models.BooleanField(default=False)
    detail_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request {self.id} by {self.employee.username} ({self.status})"
    #manager models
    def update_status(self, status, updated_by, remarks=None, clarification_details=None):
        """
        Update the status of the travel request.
        Only allow updates if the request is in the "Pending" or "Clarification Requested" state.
        """
        if self.status in ['Pending', 'Clarification Requested']:
            self.status = status
            self.status_updated_by = updated_by
            self.manager_remarks = remarks  # Save manager's remarks
            self.clarification_details = clarification_details  # Save clarification details
            self.save()
            return True
        return False
    #admin models
    def close_request(self, updated_by):
        if self.status == 'Approved':  # Only allow closing approved requests
            self.status = 'Closed'
            self.status_updated_by = updated_by
            self.save()
            return True
        return False

    def request_clarification(self, updated_by, clarification_details):
        if self.status in ['Pending', 'Rejected']:  # Allow clarification for pending or rejected requests
            self.status = 'Clarification Requested'
            self.status_updated_by = updated_by
            self.clarification_details = clarification_details
            self.save()
            return True
        return False



# Approval Model (Manager Approves Travel Requests)
class Approval(models.Model):
    travel_request = models.ForeignKey(TravelRequest, on_delete=models.CASCADE, related_name='approvals')
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE, related_name='approved_requests')
    approved = models.BooleanField(null=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Approval for Request {self.travel_request.id} by {self.manager.user.username}"


# Admin Request Processing Model
class AdminRequestProcessing(models.Model):
    travel_request = models.ForeignKey(TravelRequest, on_delete=models.CASCADE, related_name='admin_processings')
    admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'admin'}, related_name='processed_requests')
    clarification_needed = models.BooleanField(default=False)
    closed = models.BooleanField(default=False)

    def __str__(self):
        return f"Processing for Request {self.travel_request.id} by {self.admin.username}"