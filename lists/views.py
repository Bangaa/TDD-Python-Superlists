from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError

from lists.models import Item, List
from lists.forms import ItemForm

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
            form.save_for_list(list_)
            return redirect(list_)

    return render(request, 'list.html', {'list': list_, 'form': form})

# POST /new
def new_list(request):
    form = ItemForm(data=request.POST)

    if form.is_valid():
        list_ = List()
        list_.owner = request.user
        list_.save()
        form.save_for_list(list_)
        return redirect(list_)
    else:
        return render(request, 'home.html', {'form': form})

# GET /lists/users/{email}/
def my_lists(request, email):
    owner = User.objects.get(email=email)
    return render(request, 'my_lists.html', {'owner': owner})
