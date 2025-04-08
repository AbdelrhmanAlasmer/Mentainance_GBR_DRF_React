from django.db import models
from customers.models import Customer
from users.models import CustomUser
from tvs.models import TV
from django.core.validators import MinValueValidator
from django.utils import timezone
class Reception(models.Model):
    class Status(models.TextChoices):  # More modern way to define choices (Django 3.0+)
        RECEIVED = 'received', 'Received'
        IN_CHECK = 'in_check', 'In Check'
        CHECK_FEEDBACK = 'check_feedback', 'Check Feedback'
        CALLING_CUSTOMER = 'calling_customer', 'Calling Customer'
        WAIT_IN_RECEPTION = 'wait_in_reception', 'Wait in Reception'
        IN_MAINTENANCE = 'in_maintenance', 'In Maintenance'
        GIVEN_TO_CUSTOMER = 'given_to_customer', 'Given to Customer'
        REFUSED_OR_NOT_ACCEPT = 'refused_or_not_accept', 'Refused or Not Accept'
    
    class CallType(models.TextChoices):
        CONFIRM_MAINTENANCE = 'confirm_maintenance', 'Confirm Maintenance'
        PICKUP_DEVICE = 'pickup_device', 'Call to Pick Up Device'


    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='receptions')  # PROTECT to prevent accidental deletion
    tv = models.ForeignKey(TV, on_delete=models.PROTECT, related_name='receptions')
    receptionist = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='handled_receptions')
    
    initial_damage = models.TextField(verbose_name="Initial Damage Description")
    the_date = models.DateTimeField(auto_now_add=True, verbose_name="Reception Date")
    initial_tax = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Initial Service Fee"
    )
    returned = models.BooleanField(default=False, verbose_name="Device Returned?")
    case_number = models.CharField(max_length=255, unique=True)  # Should be unique
    photos = models.ImageField(upload_to='receptions/%Y/%m/%d/')  # Better file organization

    # Reception details
    who_receive_it = models.CharField(max_length=255, blank=True, verbose_name="Received By")
    the_time = models.DateTimeField(null=True, blank=True, verbose_name="Completion Time")

    # Guarantee details
    in_guarantee = models.BooleanField(default=False, verbose_name="Under Guarantee?")
    have_guarantee = models.BooleanField(default=False, verbose_name="Has Guarantee?")
    
    status = models.CharField(
        max_length=50, 
        choices=Status.choices, 
        default=Status.RECEIVED,
        verbose_name="Repair Status"
    )

    # current place is changed by each operation chang the place
    class Place(models.TextChoices):
        RECEPTION = 'reception', 'Reception'
        MAINTENANCE = 'maintenance', 'Maintenance'
        CUSTOMER = 'customer', 'Customer'
        WAREHOUSE = 'warehouse', 'Warehouse'
    current_place = models.CharField(max_length=255, blank=True, verbose_name="Current Location")

    # check_tv
    check_tv_date = models.DateTimeField(null=True, blank=True, verbose_name="Check TV Date")
    check_tv_eng = models.CharField(max_length=255, blank=True, verbose_name="Check TV Engineer Name")
   

    # check_feedback
    check_feedback_date = models.DateTimeField(null=True, blank=True, verbose_name="Check Feedback Date")
    check_feedback_eng = models.CharField(max_length=255, blank=True, verbose_name="Check Feedback Engineer Name")
    check_feedback_description = models.TextField(verbose_name="Check Feedback Description", blank=True)
    initial_Cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Initial Cost"
    )

    # refused_or_not_accept
    refused_reson = models.TextField(verbose_name="Refusal Reason", blank=True)
    refused_date = models.DateTimeField(null=True, blank=True, verbose_name="Refusal Date")

    # Maintenance details
    maintenance_eng = models.CharField(max_length=255, blank=True, verbose_name="Engineer Name")
    damage_full_description = models.CharField(max_length=255, blank=True, verbose_name="Actual Damage Found")
    final_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Repair Cost"
    )
    maintenance_date = models.DateTimeField(null=True, blank=True, verbose_name="Maintenance Date")
    

    # Given to customer
    given_to_customer_date = models.DateTimeField(null=True, blank=True, verbose_name="Given to Customer Date")
    given_to_customer_receptionist = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='handled_receptions')
    how_actually_tack_it = models.CharField(max_length=255, blank=True, verbose_name="How Given to Customer")


    class Meta:
        ordering = ['-the_date']  # Default ordering
        verbose_name = "Device Reception"
        verbose_name_plural = "Device Receptions"
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['customer']),
            models.Index(fields=['case_number']),
        ]

    def __str__(self):
        return f"Case #{self.case_number} - {self.customer.name} ({self.tv})"
    


    def current_place(self, place):
        self.current_place = place
        self.save()
        # the current place is changed by each operation chang the place

# the tv status is received by default

    def check_tv(self, check_tv_eng,current_place="reception"):
        self.status = self.Status.IN_CHECK
        self.check_tv_date = timezone.now()
        self.check_tv_eng = check_tv_eng
        self.current_place = current_place
        self.save()
        
        

        self.save()
    def check_feedback(self,check_feedback_eng, check_feedback_description,initial_cost, current_place="maintenance"): 
        self.status = self.Status.CHECK_FEEDBACK
        self.check_feedback_date= timezone.now()
        self.check_feedback_description =check_feedback_description
        self.check_feedback_eng = check_feedback_eng
        self.initial_cost = initial_cost
        self.current_place = current_place
        self.save()
        # you have to add calling required to the customer in dachboard

    def refused_or_not_accept(self,reson):
        self.status = self.Status.REFUSED_OR_NOT_ACCEPT
        self.refused_date = timezone.now()
        self.refused_reson = reson
        self.save()

    def in_maintenance(self, maintenance_eng, final_cost, damage_full_description="the exact damage in the check", current_place="maintenance"):
        self.status = self.Status.IN_MAINTENANCE
        self.maintenance_date = timezone.now()
        self.damage_full_description=damage_full_description
        self.maintenance_eng = maintenance_eng
        self.final_cost = final_cost
        self.current_place = current_place
        self.save()
    def wait_in_reception(self, current_place="reception"):
        self.status = self.Status.WAIT_IN_RECEPTION
        self.current_place = current_place
        self.save()
    def given_to_customer(self, current_place="customer", how_actually_tack_it="the customer himself", receptionist=None):
        self.status = self.Status.GIVEN_TO_CUSTOMER
        self.given_to_customer_date = timezone.now()
        self.how_actually_tack_it = how_actually_tack_it
        self.given_to_customer_receptionist = receptionist
        self.current_place= current_place
        self.save()
   

class TvAttatchment(models.Model):
    reception = models.ForeignKey(Reception, on_delete=models.CASCADE, related_name='attachments')
    attachment = models.FileField(upload_to='attachments/%Y/%m/%d/')
    description = models.TextField(verbose_name="Attachment Description", blank=True)

    class Meta:
        verbose_name = "TV Attachment"
        verbose_name_plural = "TV Attachments"

    def __str__(self):
        return f"Attachment for {self.reception} - {self.description}"
class Call(models.Model):  # Singular name as each instance represents one call
    reception = models.ForeignKey(Reception, on_delete=models.CASCADE, related_name='calls')
    call_type = models.CharField(max_length=50, choices=Reception.CallType.choices)
    summary = models.TextField(verbose_name="Call Summary")
    datetime = models.DateTimeField(default=timezone.now) 
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateTimeField(null=True, blank=True)
    caller= models.foreignkey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='calls_made')

    class Meta:
        ordering = ['-datetime']
        verbose_name = "Service Call"
        verbose_name_plural = "Service Calls"

    def __str__(self):
        return f"Call on {self.datetime.strftime('%Y-%m-%d')} for {self.reception}"