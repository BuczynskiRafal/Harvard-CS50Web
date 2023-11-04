import random
import markdown2

from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.urls import reverse

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    entry_markdown = util.get_entry(title=title)
    if entry_markdown:
        return render(
            request=request,
            template_name="encyclopedia/entry.html",
            context={
                "title": title,
                "entry": markdown2.markdown(entry_markdown),
            }
        )
    else:
        return HttpResponseNotFound("The requested title was not found.")


def search(request):
    query = request.GET.get("q", "")
    if not query:
        return redirect("index")
    entries = util.list_entries()
    matches = [entry for entry in entries if query.lower() in entry.lower()]

    if query.lower() in (entry.lower() for entry in entries):
        return entry(request, query)

    return render(request, "encyclopedia/search.html", {
        "matches": matches,
        "query": query,
    })


def new(request):
    if request.method == "POST":
        title = request.POST["title"]
        content = request.POST["content"]
        if not util.get_entry(title):
            util.save_entry(title, content)
            return HttpResponseRedirect(
                reverse("entry", kwargs={"title": title})
            )
        return render(
            request, "encyclopedia/new.html", {
                "error": "Page with this title already exists."
            }
        )
    else:
        return render(request, "encyclopedia/new.html")


def edit(request, title):
    if request.method == "POST":
        content = request.POST["content"]
        util.save_entry(title, content)
        return HttpResponseRedirect(
            reverse("entry", kwargs={"title": title})
        )
    else:
        content = util.get_entry(title)
        if not content:
            return render(request, "encyclopedia/edit.html", {
                "message": "Page with this title does not exist."
            })
        else:
            return render(request, "encyclopedia/edit.html", {
                "title": title,
                "content": content,
            })


def random_page(request):
    entries = util.list_entries()
    random_entry = random.choice(entries)
    return HttpResponseRedirect(
        reverse("entry", kwargs={"title": random_entry})
    )
