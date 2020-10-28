from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from datetime import date
import random
import string
import mercadopago
import datetime
from django.utils import timezone

from . models import (
    Customer,
    Depto,
    DeptoReservation,
    Reservation,
    Payment
)
from . serializers import (
    CustomerSerializer,
    DeptoSerializer,
    DeptoReservationSerializer,
    ReservationSerializer,
    PaymentSerializer
)

from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

mp = mercadopago.MP(settings.MERCADOPAGO_SECRET_KEY)

def create_ref_code():
    return ''.join(random.choices(
        string.ascii_lowercase + string.digits,
        k=random.randint(32,64)))

def send_email(email, details):
    context = {
        'customer': details[0],
        'ref_code': details[1],
        'amount': details[2],
        'installments': details[3],
        'installment_amount': details[4],
        'total_amount': details[5],
        'message':details[6]
    }

    template = get_template('details_email.html')
    content = template.render(context)

    email = EmailMultiAlternatives(
        'Detalles Reserva',
        'puto el que lo lee',
        settings.EMAIL_HOST_USER,
        [email],
    )

    email.attach_alternative(content,'text/html')
    email.send()


class CreateCustomerAPIView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        customer_cookie_id = request.data.get('customer_cookie_id', None)
        customer = Customer.objects.create(
            customer_cookie_id=customer_cookie_id
        )
        customer.save()

        return Response(
            {'message':'New Customer'},
            status=HTTP_200_OK
        )

# ---------------------------------------- #

class AllDeptosAPIView(APIView):
    permission_classes = (AllowAny,)
    def get(self, request, format=None):

        depto_list = []
        for depto in Depto.objects.all():
            depto_list.append(DeptoSerializer(depto).data)

        context = {
            'depto_list':depto_list
        }

        return Response(context,status=HTTP_200_OK)


class DeptoDetailAPIView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        depto_id = request.data.get('depto_id', None)
        try:
            depto = Depto.objects.get(id=int(depto_id))
            context = {
                'depto':DeptoSerializer(depto).data
            }

            return Response(context,status=HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(
                {"message":"Depto not found"},
                status=HTTP_400_BAD_REQUEST
            )

# ---------------------------------------- #

class ReservedDatesDeptoAPIView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        try:
            now_time = timezone.now()
            today = date.today()
            depto_id = request.data.get('depto_id', None)
            depto = Depto.objects.get(id=depto_id)

            depto_reservation_list = []
            for depto_reservation in DeptoReservation.objects.filter(depto=depto):
                if(depto_reservation.deletion_time <= now_time and depto_reservation.ordered == False):
                    depto_reservation.delete()
                else:
                    if today <= depto_reservation.end_date:
                        depto_reservation_list.append(
                            DeptoReservationSerializer(depto_reservation).data
                        )

            context = {
                'depto_reservation_list': depto_reservation_list
            }

            return Response(context,status=HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(context,status=HTTP_400_BAD_REQUEST)


class ReserveDeptoAPIView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):

        # data fetched from frontend
        depto_id = request.data.get('depto_id', None)
        customer_cookie_id = request.data.get('customer_cookie_id', None)
        start_date = request.data.get('start_date', None)
        end_date = request.data.get('end_date')

        # depto to reserve
        depto = Depto.objects.get(id=depto_id)

        # calculate days and total
        d_start = date(start_date[0],start_date[1],start_date[2])
        d_end = date(end_date[0],end_date[1],end_date[2])
        total = depto.price_day*((d_end - d_start).days)

        # customer that does the reservation
        customer = Customer.objects.get(customer_cookie_id=customer_cookie_id)
        reservation_qs = Reservation.objects.filter(customer=customer, ordered=False)

        # check that start day hasn't passed already
        today = date.today()
        if d_start < today:
            return Response(
                {'message':'Already passed'},
                status=HTTP_200_OK
            )

        # check that no one else reserved in those days during the time selecting days
        previous_reservations = DeptoReservation.objects.filter(end_date__gt=d_start, depto=depto)
        for prev_res in previous_reservations:
            if prev_res.end_date <= d_end:
                return Response(
                    {'message':'Already taken'},
                    status=HTTP_200_OK
                )
            elif prev_res.start_date <= d_end:
                return Response(
                    {'message':'Already taken'},
                    status=HTTP_200_OK
                )

        creation_time = datetime.datetime.now()
        hours = datetime.timedelta(hours = 1)
        deletion_time = creation_time + hours
        depto_reservation = DeptoReservation.objects.create(
            depto=depto,
            customer=customer,
            start_date=d_start,
            end_date=d_end,
            total=total,
            creation_time=creation_time,
            deletion_time=deletion_time
        )
        depto_reservation.save()

        if reservation_qs.exists():
            reservation = reservation_qs[0]
            reservation.depto_reservation.add(depto_reservation)
            reservation.total += total
            reservation.save()
        else:
            reservation = Reservation.objects.create(
                customer=customer,
                ordered=False,
                total=total,
                ref_code=create_ref_code()
            )
            reservation.depto_reservation.add(depto_reservation)
            reservation.save()


        return Response(
            {'message':'New Reservation'},
            status=HTTP_200_OK
        )


class CustomerReservationsAPIView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        try:
            customer_cookie_id = request.data.get('customer_cookie_id', None)
            customer = Customer.objects.get(customer_cookie_id=customer_cookie_id)
            reservation = Reservation.objects.get(customer=customer, ordered=False)

            depto_reservation_list = []
            for depto_reservation in reservation.depto_reservation.all():
                depto_reservation_list.append(DeptoReservationSerializer(depto_reservation).data)

            context = {
                'reservation': ReservationSerializer(reservation).data,
                'depto_reservation_list':depto_reservation_list
            }

            return Response(context, status=HTTP_200_OK)
        except Exception as e:
            depto_reservation_list = []
            context = {
                'depto_reservation_list':depto_reservation_list
            }
            return Response(
                context,
                status=HTTP_200_OK
            )


class DeleteDeptoReservationAPIView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        try:
            customer_cookie_id = request.data.get('customer_cookie_id', None)
            depto_reservation_id = request.data.get('depto_reservation_id', None)

            customer = Customer.objects.get(customer_cookie_id=customer_cookie_id)
            reservation = Reservation.objects.get(customer=customer, ordered=False)
            depto_reservation = DeptoReservation.objects.get(id=depto_reservation_id)

            reservation.total -= depto_reservation.total
            reservation.save()

            DeptoReservation.objects.get(id=depto_reservation_id).delete()

            return Response(
                {"message":"Depto Reservation Deleted"},
                status=HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"message":"Depto Reservation Not Found"},
                status=HTTP_200_OK
            )

# ---------------------------------------- #

class SubmitCheckoutAPIView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        customer_cookie_id = request.data.get('customer_cookie_id', None)
        name = request.data.get("name", None)
        last_name = request.data.get("last_name", None)
        phone = request.data.get("phone", None)
        email = request.data.get("email", None)

        try:
            customer = Customer.objects.get(customer_cookie_id=customer_cookie_id)
            customer.name = name
            customer.last_name = last_name
            customer.phone = phone
            customer.email = email
            customer.save()

            return Response(
                {"message":"ok"},
                status=HTTP_200_OK
            )
        except Exception as e:
            print(e)
            return Response(status=HTTP_400_BAD_REQUEST)


class SubmitPaymentAPIView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, *args, **kwargs):
        customer_cookie_id = request.data.get('customer_cookie_id', None)
        reservation_id = request.data.get("reservation_id", None)
        amount = request.data.get("amount", None)
        token = request.data.get("token", None)
        installments = request.data.get("installments", None)
        payment_method_id = request.data.get("payment_method_id", None)

        try:
            customer = Customer.objects.get(customer_cookie_id=customer_cookie_id)
            reservation = Reservation.objects.get(id=reservation_id)
        except Exception as e:
            print(e)
            return Response(status=HTTP_400_BAD_REQUEST)

        charge = mp.post("/v1/payments",{
            "transaction_amount": round(amount,2),
            "payment_method_id": payment_method_id,
            "token": token,
            "installments": installments,
            "payer": {
                "email": "test_user_43865662@testuser.com" # e-mail de prueba
            }
        })


        if charge['response']['status'] == 'approved':
            payment = Payment.objects.create(
                customer=customer,
                reservation=reservation,
                amount=amount,
                approved=True,
                installments=charge['response']['installments'],
                total_amount=charge['response']['transaction_details']['total_paid_amount'],
                installment_amount=charge['response']['transaction_details']['installment_amount']
            )

            reservation.ordered = True
            for depto_reservation in reservation.depto_reservation.all():
                depto_reservation.ordered = True
                depto_reservation.save()
            reservation.save()

            customer_email = customer.email
            details = [
                customer.name + ", " + customer.last_name,
                reservation.ref_code,
                amount,
                installments,
                charge['response']['transaction_details']['installment_amount'],
                charge['response']['transaction_details']['total_paid_amount'],
                "Su pago se acreditó correctamente"
            ]
            send_email(customer_email,details)

            return Response(
                {"message":"ok"},
                status=HTTP_200_OK
            )
        elif charge['response']['status'] == 'in_process':
            payment = Payment.objects.create(
                customer=customer,
                reservation=reservation,
                amount=amount,
                pending=True,
                installments=charge['response']['installments'],
                total_amount=charge['response']['transaction_details']['total_paid_amount'],
                installment_amount=charge['response']['transaction_details']['installment_amount']
            )

            reservation.ordered = True
            for depto_reservation in reservation.depto_reservation.all():
                depto_reservation.ordered = True
                depto_reservation.save()
            reservation.save()

            customer_email = customer.email
            details = [
                customer.name + ", " + customer.last_name,
                reservation.ref_code,
                amount,
                installments,
                charge['response']['transaction_details']['installment_amount'],
                charge['response']['transaction_details']['installment_amount'],
                "Su pago aún esta pendiente, se acreditará en los próximos días"
            ]
            send_email(customer_email,details)

            return Response(
                {"message":"pending"},
                status=HTTP_200_OK
            )
        elif charge['response']['status'] == 'rejected':
            if(charge['response']['status_detail'] == 'cc_rejected_bad_filled_card_number'):
                return Response(
                    {"message":"bad_filled_card_number"},status=HTTP_200_OK
                )
            elif(charge['response']['status_detail'] == 'cc_rejected_bad_filled_date'):
                return Response(
                    {"message":"bad_filled_date"},status=HTTP_200_OK
                )
            elif(charge['response']['status_detail'] == 'cc_rejected_bad_filled_other'):
                return Response(
                    {"message":"bad_filled_other"},status=HTTP_200_OK
                )
            elif(charge['response']['status_detail'] == 'cc_rejected_bad_filled_security_code'):
                return Response(
                    {"message":"bad_filled_security_code"},status=HTTP_200_OK
                )
            elif(charge['response']['status_detail'] == 'cc_rejected_blacklist'):
                return Response(
                    {"message":"blacklist"},status=HTTP_200_OK
                )
            elif(charge['response']['status_detail'] == 'cc_rejected_call_for_authorize'):
                return Response(
                    {"message":"call_for_authorize"},status=HTTP_200_OK
                )
            elif(charge['response']['status_detail'] == 'cc_rejected_card_disabled'):
                return Response(
                    {"message":"card_disabled"},status=HTTP_200_OK
                )
            elif(charge['response']['status_detail'] == 'cc_rejected_card_error'):
                return Response(
                    {"message":"card_error"},status=HTTP_200_OK
                )
            elif(charge['response']['status_detail'] == 'cc_rejected_duplicated_payment'):
                return Response(
                    {"message":"duplicated_payment"},status=HTTP_200_OK
                )
            elif(charge['response']['status_detail'] == 'cc_rejected_high_risk'):
                return Response(
                    {"message":"high_risk"},status=HTTP_200_OK
                )
            elif(charge['response']['status_detail'] == 'cc_rejected_insufficient_amount'):
                return Response(
                    {"message":"insufficient_amount"},status=HTTP_200_OK
                )
            elif(charge['response']['status_detail'] == 'cc_rejected_invalid_installments'):
                return Response(
                    {"message":"invalid_installments"},status=HTTP_200_OK
                )
            elif(charge['response']['status_detail'] == 'cc_rejected_max_attempts'):
                return Response(
                    {"message":"max_attempts"},status=HTTP_200_OK
                )
            elif(charge['response']['status_detail'] == 'cc_rejected_other_reason'):
                return Response(
                    {"message":"other_reason"},status=HTTP_200_OK
                )
            else:
                return Response(
                    {"message":"rejected"},status=HTTP_200_OK
                )
        else:
            return Response(status=HTTP_400_BAD_REQUEST)
