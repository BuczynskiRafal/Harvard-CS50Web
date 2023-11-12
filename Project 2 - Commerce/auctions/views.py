from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from .models import User, Listing, Bids
from .forms import ListingForm, BidForm, CommentForm


def index(request):
    listings = Listing.objects.filter(active=True)
    return render(
        request, "auctions/index.html",
        context={"listings": listings}
    )


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def create_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            new_listing = form.save(commit=False)
            new_listing.current_price = new_listing.starting_bid
            new_listing.creator = request.user
            new_listing.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        form = ListingForm()
    return render(request, "auctions/create.html", context={
        "form": form})


def toggle_watchlist(request, listing, on_watchlist, listing_id):
    if on_watchlist:
        request.user.watchlist.remove(listing)
    else:
        request.user.watchlist.add(listing)
    return HttpResponseRedirect(reverse("listing", args=[listing_id]))


def submit_comment(request, listing, listing_id):
    comment_form = CommentForm(request.POST)
    if comment_form.is_valid():
        new_comment = comment_form.save(commit=False)
        new_comment.user = request.user
        new_comment.listing = listing
        new_comment.save()
        return HttpResponseRedirect(reverse("listing", args=[listing_id]))


def reopen_auction(request, listing):
    listing.active = True
    listing.save()
    return HttpResponseRedirect(reverse("index"))


def place_bid(request, listing, listing_id):
    bid_form = BidForm(request.POST)
    if bid_form.is_valid():
        new_bid = bid_form.save(commit=False)
        new_bid.user = request.user
        new_bid.listing = listing
        if new_bid.bid_amount > listing.current_price:
            new_bid.save()
            listing.current_price = new_bid.bid_amount
            listing.save()
            return None
        else:
            return "Your bid must be higher than the current price."


def close_auction(request, listing):
    highest_bid = Bids.objects.filter(listing=listing).order_by('-bid_amount').first()
    if highest_bid:
        listing.winner = highest_bid.user
    print(highest_bid)
    print(listing.winner)
    listing.active = False
    listing.save()
    return HttpResponseRedirect(reverse("index"))


def listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    on_watchlist = False
    bid_form = BidForm()
    comments = listing.comments.all()
    comment_form = CommentForm()
    message = None
    user_is_winner = False

    if request.user.is_authenticated and not listing.active:
        user_is_winner = listing.winner == request.user

    if request.user.is_authenticated:
        if listing in request.user.watchlist.all():
            on_watchlist = True

        if request.method == "POST":
            if "place_bid" in request.POST:
                message = place_bid(request, listing, listing_id)
                if message:
                    bid_form = BidForm()
            if "toggle_watchlist" in request.POST:
                toggle_watchlist(request, listing, on_watchlist, listing_id)
                on_watchlist = listing in request.user.watchlist.all()
            if "close_auction" in request.POST:
                close_auction(request, listing)
            if "reopen_auction" in request.POST:
                reopen_auction(request, listing)
            if "submit_comment" in request.POST:
                submit_comment(request, listing, listing_id)

        context = {
            "listing": listing,
            "comments": comments,
            "on_watchlist": on_watchlist,
            "bid_form": bid_form,
            "comment_form": comment_form,
            "message": message,
            "user_is_winner": user_is_winner,
        }
        return render(request, "auctions/listing.html", context=context)

    return HttpResponseRedirect(reverse("login"))


@login_required
def watchlist(request):
    watchlist_items = request.user.watchlist.all()
    return render(request, "auctions/watchlist.html", context={
        "watchlist_items": watchlist_items
    })


def categories(request):
    categories = Listing.objects.values_list('category', flat=True).distinct()
    return render(request, 'auctions/categories.html', {
        'categories': categories
    })


def category_listing(request, category_name):
    listings = Listing.objects.filter(category=category_name, active=True)

    return render(request, 'auctions/category_listing.html', {
        'listings': listings,
        'category_name': category_name
    })


def my_listings(request):
    my_listings = Listing.objects.filter(creator=request.user)
    return render(request, 'auctions/my_listings.html', {
        'my_listings': my_listings
    })
