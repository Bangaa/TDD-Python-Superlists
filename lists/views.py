from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError

from django.http import HttpResponse
from lists.models import Item, List
from lists.forms import ItemForm

def home_page(request):
    return render(request, 'home.html', {'form': ItemForm()})

def view_list(request, list_id):
    list_ = List.objects.get(id=list_id)
    error = None

    if request.method == 'POST':
        try:
            item = Item(text=request.POST['item_text'], list=list_)
            item.full_clean()
            item.save()
            return redirect(list_)
        except ValidationError:
            error = "No puedes crear un item sin texto"

    return render(request, 'list.html', {'list': list_, 'error': error})

def new_list(request):
    list_ = List.objects.create()
    item = Item.objects.create(text=request.POST['item_text'], list=list_)
    try:
        item.full_clean()
    except ValidationError:
        list_.delete()
        error = "No puedes crear un item sin texto"
        return render(request, 'home.html', {'error': error})

    return redirect(list_)
