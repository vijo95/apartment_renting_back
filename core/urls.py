from django.urls import path
from . api import (
    CreateCustomerAPIView,
    AllDeptosAPIView,
    DeptoDetailAPIView,
    ReserveDeptoAPIView,
    CustomerReservationsAPIView,
    DeleteDeptoReservationAPIView,
    SubmitCheckoutAPIView,
    SubmitPaymentAPIView,
    ReservedDatesDeptoAPIView
)

urlpatterns = [
    path('new-customer/', CreateCustomerAPIView.as_view(), name="new-customer"),

    path('deptos/', AllDeptosAPIView.as_view(), name="deptos"),
    path('depto-detail/', DeptoDetailAPIView.as_view(), name="depto-detail"),

    path('reserved-dates-depto/', ReservedDatesDeptoAPIView.as_view(), name="reserved-dates-depto"),
    path('reserve-depto/', ReserveDeptoAPIView.as_view(), name="reserve-depto"),
    path('customer-reservations/', CustomerReservationsAPIView.as_view(), name="customer-reservations"),
    path('delete-depto-reservation/', DeleteDeptoReservationAPIView.as_view(), name="delete-depto-reservation"),

    path('submit-checkout/', SubmitCheckoutAPIView.as_view(), name="submit-checkout"),
    path('submit-payment/', SubmitPaymentAPIView.as_view(), name="submit-payment"),
]
