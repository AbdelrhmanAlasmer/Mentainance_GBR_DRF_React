from rest_framework import serializers
from django.core.validators import MinValueValidator
from .models import Reception, ReceptionPhoto, Call, RepairNote
from customers.serializers import CustomerSerializer
from users.serializers import UserSerializer
from tvs.serializers import TvSerializer


class ReceptionPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceptionPhoto
        fields = ['id', 'photo', 'description']
        read_only_fields = ['id']

class ReceptionCreateSerializer(serializers.ModelSerializer):
    reception_photos = ReceptionPhotoSerializer(many=True, required=False)
    
    class Meta:
        model = Reception
        fields = [
            'id', 'customer', 'tv', 'case_number', 'initial_damage',
            'initial_tax', 'initial_cost', 'in_guarantee', 'have_guarantee',
            'warranty_expiry_date', 'who_receive_it', 'reception_photos',
            'priority', 'notes'
        ]
        read_only_fields = ['id', 'case_number']
        extra_kwargs = {
            'initial_tax': {'validators': [MinValueValidator(0)]},
            'initial_cost': {'validators': [MinValueValidator(0)]},
        }

    def validate(self, data):
        if data.get('in_guarantee') and not data.get('have_guarantee'):
            raise serializers.ValidationError(
                "Device cannot be under guarantee without having a valid guarantee."
            )
        return data

    def create(self, validated_data):
        photos_data = validated_data.pop('reception_photos', [])
        reception = Reception.objects.create(**validated_data)
        
        for photo_data in photos_data:
            ReceptionPhoto.objects.create(reception=reception, **photo_data)
            
        return reception

class InspectionSerializer(serializers.Serializer):
    current_place = serializers.ChoiceField(
        choices=Reception.Place.choices, 
        default=Reception.Place.MAINTENANCE
    )
    
    def update(self, instance, validated_data):
        instance.check_tv(
            engineer=self.context['request'].user,
            current_place=validated_data.get('current_place')
        )
        return instance

class InspectionFeedbackSerializer(serializers.Serializer):
    findings = serializers.CharField(source='check_feedback_description')
    estimated_cost = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2,
        source='initial_cost',
        validators=[MinValueValidator(0)]
    )
    current_place = serializers.ChoiceField(
        choices=Reception.Place.choices, 
        default=Reception.Place.MAINTENANCE
    )
    
    def update(self, instance, validated_data):
        instance.check_feedback(
            engineer=self.context['request'].user,
            findings=validated_data.get('check_feedback_description'),
            estimated_cost=validated_data.get('initial_cost'),
            current_place=validated_data.get('current_place')
        )
        return instance

class RefusalSerializer(serializers.Serializer):
    reason = serializers.CharField(source='refused_reason')
    
    def update(self, instance, validated_data):
        instance.refuse_repair(
            reason=validated_data.get('refused_reason')
        )
        return instance

class MaintenanceSerializer(serializers.Serializer):
    actual_damage = serializers.CharField(source='damage_full_description')
    final_cost = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    current_place = serializers.ChoiceField(
        choices=Reception.Place.choices, 
        default=Reception.Place.MAINTENANCE
    )
    expected_completion_date = serializers.DateField(required=False)
    
    def update(self, instance, validated_data):
        instance.start_maintenance(
            engineer=self.context['request'].user,
            actual_damage=validated_data.get('damage_full_description'),
            final_cost=validated_data.get('final_cost'),
            current_place=validated_data.get('current_place')
        )
        if 'expected_completion_date' in validated_data:
            instance.expected_completion_date = validated_data['expected_completion_date']
            instance.save()
        return instance

class ReadyForPickupSerializer(serializers.Serializer):
    current_place = serializers.ChoiceField(
        choices=Reception.Place.choices, 
        default=Reception.Place.RECEPTION
    )
    
    def update(self, instance, validated_data):
        instance.mark_ready_for_pickup(
            current_place=validated_data.get('current_place')
        )
        return instance

class DeliverySerializer(serializers.Serializer):
    delivery_method = serializers.CharField(source='how_actually_take_it')
    current_place = serializers.ChoiceField(
        choices=Reception.Place.choices, 
        default=Reception.Place.CUSTOMER
    )
    
    def update(self, instance, validated_data):
        instance.deliver_to_customer(
            delivery_method=validated_data.get('how_actually_take_it'),
            receptionist=self.context['request'].user,
            current_place=validated_data.get('current_place')
        )
        return instance

class ReceptionDetailSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    tv = TvSerializer(read_only=True)
    receptionist = UserSerializer(read_only=True)
    check_tv_eng = UserSerializer(read_only=True)
    check_feedback_eng = UserSerializer(read_only=True)
    maintenance_eng = UserSerializer(read_only=True)
    given_to_customer_receptionist = UserSerializer(read_only=True)
    reception_photos = ReceptionPhotoSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    current_place_display = serializers.CharField(source='get_current_place_display', read_only=True)
    
    class Meta:
        model = Reception
        fields = '__all__'
        read_only_fields = [field.name for field in Reception._meta.fields]

class CallSerializer(serializers.ModelSerializer):
    caller = UserSerializer(read_only=True)
    call_type_display = serializers.CharField(source='get_call_type_display', read_only=True)
    
    class Meta:
        model = Call
        fields = '__all__'
        read_only_fields = ['datetime', 'caller']

    def create(self, validated_data):
        validated_data['caller'] = self.context['request'].user
        return super().create(validated_data)

class RepairNoteSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = RepairNote
        fields = '__all__'
        read_only_fields = ['created_at', 'author']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)