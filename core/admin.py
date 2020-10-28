from django.contrib import admin
from . models import (
    Customer,
    Depto,
    DeptoReservation,
    Reservation,
    Payment
)

class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'last_name',
        'phone',
        'customer_cookie_id'
    ]


class DeptoReservationAdmin(admin.ModelAdmin):
    list_display = [
        'depto',
        'customer',
        'start_date',
        'end_date',
        'total'
    ]
    list_display_links = [
        'depto',
        'customer'
    ]


class DeptoAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'price_day',
        'capacity'
    ]


class ReservationAdmin(admin.ModelAdmin):
    list_display = [
        'customer',
        'ordered',
        'total',
        'ref_code',
    ]


class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'customer',
        'reservation',
        'pending',
        'approved',
        'rejected',
        'amount',
        'time',
    ]
    list_display_links = [
        'customer',
        'reservation'
    ]
# Register your models here.

admin.site.register(Customer,CustomerAdmin)
admin.site.register(Depto,DeptoAdmin)
admin.site.register(DeptoReservation,DeptoReservationAdmin)
admin.site.register(Reservation,ReservationAdmin)
admin.site.register(Payment,PaymentAdmin)
