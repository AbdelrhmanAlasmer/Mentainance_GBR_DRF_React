from django.db import models
from customers.models import Customer
from users.models import CustomUser
from tvs.models import TV
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError


class Reception(models.Model):
    class Status(models.TextChoices):
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
        FOLLOW_UP = 'follow_up', 'Follow Up Call'
        WARRANTY_CHECK = 'warranty_check', 'Warranty Verification'

    class Place(models.TextChoices):
        RECEPTION = 'reception', 'Reception'
        MAINTENANCE = 'maintenance', 'Maintenance'
        CUSTOMER = 'customer', 'Customer'
        WAREHOUSE = 'warehouse', 'Warehouse'
        SHIPPING = 'shipping', 'Shipping'

    # Core Fields
    customer = models.ForeignKey(Customer,on_delete=models.PROTECT, related_name='receptions', verbose_name="Customer")
    tv = models.ForeignKey(TV,on_delete=models.PROTECT, related_name='receptions', verbose_name="TV Device")
    receptionist = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='receptions', verbose_name="Receptionist")
    
    # Case Information
    case_number = models.CharField( max_length=255, unique=True,verbose_name="Case Number",help_text="Unique identifier for this repair case")        
    initial_damage = models.TextField( verbose_name="Initial Damage Description",help_text="Customer's description of the problem")
    the_date = models.DateTimeField(auto_now_add=True, verbose_name="Reception Date" )
    
    # Financial Information
    initial_tax = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Initial Service Fee",
        help_text="Diagnostic fee charged at reception"
    )
    initial_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Estimated Repair Cost",
        help_text="Initial cost estimate after inspection"
    )
    final_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Final Repair Cost",
        help_text="Actual cost after maintenance completion"
    )
    
    # Status Tracking
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.RECEIVED, verbose_name="Repair Status")
    current_place = models.CharField(max_length=20, choices=Place.choices, default=Place.RECEPTION,verbose_name="Current Location")
    returned = models.BooleanField( default=False, verbose_name="Device Returned?")
    
    # Reception Details
    who_receive_it = models.CharField(max_length=255, blank=True, verbose_name="Received By",help_text="Person who physically received the device" )
    reception_photos = models.ManyToManyField(
        'ReceptionPhoto', 
        blank=True,
        verbose_name="Reception Photos",
        help_text="Photos taken at reception",
        related_name='related_reception'
    )    
    # Warranty Information
    in_guarantee = models.BooleanField(default=False, verbose_name="Under Warranty?")
    have_guarantee = models.BooleanField(default=False,  verbose_name="Has Valid Warranty?")
    warranty_expiry_date = models.DateField( null=True,  blank=True, verbose_name="Warranty Expiry Date")
    
    # Check TV Phase
    check_tv_date = models.DateTimeField(null=True,  blank=True,  verbose_name="Inspection Date")
    check_tv_eng = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='inspected_receptions',
        verbose_name="Inspecting Engineer"
    )
   
    # Check Feedback Phase
    check_feedback_date = models.DateTimeField(null=True, blank=True, verbose_name="Feedback Date")
    check_feedback_eng = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='feedback_receptions',
        verbose_name="Feedback Engineer"
    )
    check_feedback_description = models.TextField(verbose_name="Inspection Findings", blank=True
    )

    # Refusal Information
    refused_reason = models.TextField(verbose_name="Refusal Reason", blank=True)
    refused_date = models.DateTimeField(null=True, blank=True, verbose_name="Refusal Date")

    # Maintenance Details
    maintenance_eng = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='maintained_receptions',
        verbose_name="Repair Engineer"
    )
    damage_full_description = models.TextField(verbose_name="Actual Damage Found",  blank=True)
    maintenance_date = models.DateTimeField( null=True,  blank=True,  verbose_name="Repair Date")
    expected_completion_date = models.DateField(null=True,blank=True,verbose_name="Expected Completion Date")
    
    # Delivery Information
    given_to_customer_date = models.DateTimeField(null=True, blank=True, verbose_name="Delivery Date")
    given_to_customer_receptionist = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='delivered_receptions',
        verbose_name="Delivery Handled By"
    )
    how_actually_take_it = models.CharField(max_length=255, blank=True, verbose_name="Delivery Method",help_text="How the device was returned to customer")
    
    # Additional Information
    notes = models.TextField( blank=True, verbose_name="Additional Notes", help_text="Any additional observations about this case")
    priority = models.PositiveSmallIntegerField(default=3,choices=[(1, 'High'), (2, 'Medium'), (3, 'Low')],verbose_name="Repair Priority")

    class Meta:
        ordering = ['-the_date']
        verbose_name = "Device Reception"
        verbose_name_plural = "Device Receptions"
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['customer']),
            models.Index(fields=['case_number']),
            models.Index(fields=['priority']),
        ]

    def __str__(self):
        return f"Case #{self.case_number} - {self.customer.name} ({self.tv})"
    
    def clean(self):
        """Validate model before saving."""
        if self.in_guarantee and not self.have_guarantee:
            raise ValidationError("Device cannot be under guarantee without having a valid guarantee.")
        
        if self.final_cost and not self.maintenance_date:
            raise ValidationError("Final cost cannot be set without maintenance date.")
    
    def set_current_place(self, place):
        """Update the device's current location with validation."""
        if place not in self.Place.values:
            raise ValueError(f"{place} is not a valid location")
        self.current_place = place
        self.save()
    
    def check_tv(self, engineer, current_place=Place.MAINTENANCE):
        """Mark device as being inspected by engineer."""
        self.status = self.Status.IN_CHECK
        self.check_tv_date = timezone.now()
        self.check_tv_eng = engineer
        self.current_place = current_place
        self.save()
        
    def check_feedback(self, engineer, findings, estimated_cost, current_place=Place.MAINTENANCE):
        """Record inspection findings and estimated cost."""
        self.status = self.Status.CHECK_FEEDBACK
        self.check_feedback_date = timezone.now()
        self.check_feedback_description = findings
        self.check_feedback_eng = engineer
        self.initial_cost = estimated_cost
        self.current_place = current_place
        self.save()

    def refuse_repair(self, reason):
        """Mark repair as refused by customer."""
        self.status = self.Status.REFUSED_OR_NOT_ACCEPT
        self.refused_date = timezone.now()
        self.refused_reason = reason
        self.current_place = self.Place.RECEPTION
        self.save()

    def start_maintenance(self, engineer, actual_damage, final_cost, current_place=Place.MAINTENANCE):
        """Begin the repair process."""
        self.status = self.Status.IN_MAINTENANCE
        self.maintenance_date = timezone.now()
        self.damage_full_description = actual_damage
        self.maintenance_eng = engineer
        self.final_cost = final_cost
        self.current_place = current_place
        self.save()

    def mark_ready_for_pickup(self, current_place=Place.RECEPTION):
        """Mark device as repaired and ready for customer pickup."""
        self.status = self.Status.WAIT_IN_RECEPTION
        self.current_place = current_place
        self.save()

    def deliver_to_customer(self, delivery_method, receptionist=None, current_place=Place.CUSTOMER):
        """Complete the process by delivering device to customer."""
        self.status = self.Status.GIVEN_TO_CUSTOMER
        self.given_to_customer_date = timezone.now()
        self.how_actually_take_it = delivery_method
        self.given_to_customer_receptionist = receptionist
        self.current_place = current_place
        self.returned = True
        self.save()


# In your models.py
class ReceptionPhoto(models.Model):
    reception = models.ForeignKey(
    'Reception',
    on_delete=models.CASCADE,
    related_name='photos',
    null=True,  # Add this
    blank=True  # Add this if you want admin to allow blank
)
    photo = models.ImageField(upload_to='receptions/%Y/%m/%d/', verbose_name="Photo")
    description = models.CharField(max_length=255, blank=True, verbose_name="Description")
    
    class Meta:
        verbose_name = "Reception Photo"
        verbose_name_plural = "Reception Photos"
        ordering = ['-id']

class Call(models.Model):
    reception = models.ForeignKey(Reception, on_delete=models.CASCADE, related_name='calls')
    call_type = models.CharField(max_length=50, choices=Reception.CallType.choices,verbose_name="Call Type")
    caller = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='made_calls',
        verbose_name="Call Made By"
    )
    summary = models.TextField(verbose_name="Call Summary")
    datetime = models.DateTimeField(default=timezone.now)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, verbose_name="Additional Notes")

    class Meta:
        ordering = ['-datetime']
        verbose_name = "Service Call"
        verbose_name_plural = "Service Calls"

    def __str__(self):
        return f"Call on {self.datetime.strftime('%Y-%m-%d')} for {self.reception}"


class RepairNote(models.Model):
    reception = models.ForeignKey(Reception,on_delete=models.CASCADE,related_name='repair_notes')
    note = models.TextField(verbose_name="Note Content")
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='repair_notes'
    )
   
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Repair Note"
        verbose_name_plural = "Repair Notes"

    def __str__(self):
        return f"Note by {self.author} on {self.created_at.strftime('%Y-%m-%d')}"