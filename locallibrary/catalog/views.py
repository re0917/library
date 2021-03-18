from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from .forms import RenewBookForm

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author,Book

# from django.forms import ModelForm
# from .models import BookInstance

# Create your views here.

def index(request):
    """
    View function for home page of site.
    """
    # Generate counts of some of the main objects
    num_books=Book.objects.all().count()
    num_instances=BookInstance.objects.all().count()
    # Available books (status = 'a')
    num_instances_available=BookInstance.objects.filter(status__exact='a').count()
    num_authors=Author.objects.count()  # The 'all()' is implied by default.

    # Number of visits to this view, as counted in the session variable.
    num_visits=request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits+1

    # Render the HTML template index.html with the data in the context variable
    return render(
        request,
        'index.html',
        context={'num_books':num_books,'num_instances':num_instances,'num_instances_available':num_instances_available,'num_authors':num_authors,'num_visits':num_visits},
    )

class BookListView(generic.ListView):
    model = Book
    paginate_by = 2   

class BookDetailView(generic.DetailView):
    model = Book

    def book_detail_view(request,pk):
        try:
            book_id=Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            raise Http404("Book does not exist")

        #book_id=get_object_or_404(Book, pk=pk)

        return render(
            request,
            'catalog/book_detail.html',
            context={'book':book_id,}
        )

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 2

class AuthorDetailView(generic.DetailView):
    model = Author
    def author_detail_view(request,pk):
        try:
            author_id=Author.objects.get(pk=pk)
            
        except Author.DoesNotExist:
            raise Http404("Book does not exist")

        return render(
            request,
            'catalog/author_detail.html',
            context={'author':author_id,'book':booktit}
        )

# class MyView(LoginRequiredMixin, View):
#     login_url = '/login/'
#     redirect_field_name = 'redirect_to'

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """
    Generic class-based view listing books on loan to current user.
    """
    model = BookInstance
    template_name ='catalog/borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """
    View function for renewing a specific BookInstance by librarian
    """
    book_inst=get_object_or_404(BookInstance, pk = pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('index') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst':book_inst})   

class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial={'date_of_death':'05/01/2018',}

class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name','last_name','date_of_birth','date_of_death']

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')     

# class RenewBookModelForm(ModelForm):
#     class Meta:
#         model = BookInstance
#         fields = '__all__'
    

class BookCreate(CreateView):
    model = Book
    fields = '__all__'
    # initial={'date_of_death':'05/01/2018',}

class BookUpdate(UpdateView):
    model = Book
    fields = '__all__'
    # fields = ['first_name','last_name','date_of_birth','date_of_death']

class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')  