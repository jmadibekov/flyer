from django.db import models

class Flight(models.Model):
    # both of the following contain the respective city codes
    fly_from = models.CharField(max_length=10)
    fly_to = models.CharField(max_length=10)

    date_time = models.DateTimeField()
    
    # price in EUR
    price = models.DecimalField(max_digits=6, decimal_places=2)
    
    # booking_token is used to check the flight
    booking_token = models.CharField(max_length=1000)

    # last_fetched is when used Search API to search for the flight
    last_fetched = models.DateTimeField()

    # last_updated is when used Booking API to check the flight
    last_updated = models.DateTimeField(auto_now=True)

