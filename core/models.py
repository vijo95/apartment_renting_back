from django.db import models

# Create your models here.

class Customer(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True)
    last_name = models.CharField(max_length=64, blank=True, null=True)
    phone = models.CharField(max_length=32, blank=True, null=True)
    email = models.EmailField( blank=True, null=True)
    customer_cookie_id = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return f"{self.name}, {self.last_name}"


class Depto(models.Model):
    price_day = models.FloatField(blank=True, null=True)
    capacity = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=32, blank=True, null=True)
    description = models.TextField()
    imageURL1 = models.CharField(max_length=1024, blank=True, null=True)
    imageURL2 = models.CharField(max_length=1024, blank=True, null=True)
    imageURL3 = models.CharField(max_length=1024, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"


class DeptoReservation(models.Model):
    depto = models.ForeignKey(Depto, on_delete=models.SET_NULL, blank=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    total = models.FloatField(blank=True, null=True)
    creation_time = models.DateTimeField(blank=True, null=True)
    deletion_time = models.DateTimeField(blank=True, null=True)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.customer}, {self.depto}"


class Reservation(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    depto_reservation = models.ManyToManyField(DeptoReservation)
    ref_code = models.CharField(max_length=64, blank=True, null=True)
    ordered = models.BooleanField(default=False)
    total = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.ref_code}"


class Payment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    reservation = models.ForeignKey(Reservation, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField(blank=True, null=True)
    installments = models.IntegerField(blank=True, null=True)
    installment_amount = models.FloatField(blank=True, null=True)
    total_amount = models.FloatField(blank=True, null=True)
    pending = models.BooleanField(blank=True, null=True)
    approved = models.BooleanField(blank=True, null=True)
    rejected = models.BooleanField(blank=True, null=True)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer}"
