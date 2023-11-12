from django import forms

from .models import Listing, Bids, Comment


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'starting_bid', 'image_url', 'category']
        widgets = {
            "description": forms.Textarea(attrs={"cols": 80, "rows": 5}),
            "starting_bid": forms.NumberInput(attrs={'min': 0.01})
        }


class BidForm(forms.ModelForm):
    class Meta:
        model = Bids
        fields = ['bid_amount']
        widgets = {
            'bid_amount': forms.NumberInput(attrs={'min': 0.01}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'cols': 40, 'rows': 3}),
        }
