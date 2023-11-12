from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField("listing", blank=True, related_name="watchlisted_by")


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True)
    category = models.CharField(max_length=64)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings_created")
    active = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now_add=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="listings_won")

    def __str__(self):
        return f"{self.title} ({'Active' if self.active else 'Closed'})"


class Bids(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids", null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids_made")
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user} bid on {self.listing} with amount ${self.bid_amount}"


class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments_made")
    comment = models.TextField()

    def __str__(self):
        return f"Comment by {self.user} on {self.listing}"
