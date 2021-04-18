from django.db import models


class Date(models.Model):
    date = models.DateField(unique=True)

    def __str__(self):
        return f'{self.date.strftime("%d %b, %Y")}'

    class Meta:
        ordering = ["date"]


class Flight(models.Model):
    # both of the following contain the respective city codes
    fly_from = models.CharField(max_length=10)
    fly_to = models.CharField(max_length=10)

    utc_departure = models.DateTimeField()
    utc_arrival = models.DateTimeField()

    # price in EUR
    price = models.DecimalField(max_digits=6, decimal_places=2)

    # booking_token is used to check the flight
    booking_token = models.CharField(max_length=1000)

    # last_fetched is when used Search API to search for the flight
    last_fetched = models.DateTimeField(auto_now_add=True)

    # last_updated is when used Booking API to check the flight
    last_updated = models.DateTimeField(auto_now=True)

    # deep_link is a hyperlink which links a customer to Kiwi.com website
    deep_link = models.URLField(max_length=500)

    date = models.ForeignKey(Date, on_delete=models.CASCADE)

    class Meta:
        ordering = ["price"]

    def __str__(self):
        return f'{self.fly_from} -> {self.fly_to} | €{self.price} | {self.utc_departure.strftime("%d %b, %Y")}'
