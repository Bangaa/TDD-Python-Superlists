from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError

from lists.models import Item, List
from lists.forms import ItemForm, NewListForm, ExistingListItemForm

from django.contrib.auth import get_user_model

User = get_user_model()

def home_page(request):
    return render(request, 'home.html', {'form': ItemForm()})

# GET /lists/{id}/
# POST /lists/{id}/
def view_list(request, list_id):
    list_ = List.objects.get(id=list_id)
    form = ItemForm()

    if request.method == 'POST':
        form = ItemForm(data=request.POST, for_list=list_)
        if form.is_valid():
            form.save()
            return redirect(list_)

    return render(request, 'list.html', {'list': list_, 'form': form})

def new_list(request):
    form = NewListForm(data=request.POST)

    if form.is_valid():
        list_ = form.save(owner=request.user)
        return redirect(list_)
    return render(request, 'home.html', {'form': form})
