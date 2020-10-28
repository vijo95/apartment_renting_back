from rest_framework import serializers

from . models import (
    Customer,
    Depto,
    DeptoReservation,
    Reservation,
    Payment
)

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            'id','name','last_name',
            'phone','email','cookie_id',
        ]


class DeptoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Depto
        fields = [
            'id','price_day','capacity','name',
            'description','imageURL1','imageURL2','imageURL3',
        ]


class DeptoReservationSerializer(serializers.ModelSerializer):
    depto_name = serializers.ReadOnlyField(source='depto.name')
    depto_capacity = serializers.ReadOnlyField(source='depto.capacity')
    class Meta:
        model = DeptoReservation
        fields = [
            'id','depto',
            'customer',
            'start_date',
            'end_date',
            'total',
            'depto_name',
            'depto_capacity'
    ]


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = [
            'id','customer','depto_reservation',
            'ref_code','ordered','total'
        ]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id','customer',
            'reservation',
            'amount','time'
        ]
