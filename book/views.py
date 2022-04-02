from importlib.resources import Package
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from slugify import slugify
from .models import *
from .forms import BookForm
from django.core.files.storage import FileSystemStorage


def index(request):
    categories = Category.objects.all()
    books = Book.objects.filter(published=True)

    categ_id = request.GET.get('categoryid')
    if categ_id:
        # ถ้ามีค่า category
        books = books.filter(category_id=categ_id)

    paginator = Paginator(books, 10)
    page = request.GET.get('page')
    try:
        books = paginator.page(page)
    except PageNotAnInteger:
        books = paginator.page(1)
    except EmptyPage:
        books = paginator.page(paginator.num_pages)

    return render(request, 'book/index.html', {
        'categories':categories,
        'books':books,
        'categ_id': categ_id,
    })
def About(request):
    return render(request,'book/about.html')

def detail(request, slug):
    book = get_object_or_404(Book, slug=slug)
    return render(request, 'book/detail.html', {
        'book': book,
    })

def Service(request):
    return render(request,'book/service.html')

def Contact(request):
    context ={}
    if request.method == 'POST':
        data = request.POST.copy()
        title = data.get('title')
        email = data.get('email')
        comment = data.get('Comment')
        print(title,email,comment)

        if title == '' or email == '':
            context['status'] = 'alert'
            return render(request,'myapp/contact.html',context)

        new = ContactMessage()
        new.title = title
        new.email = email
        new.Comment = comment
        new.save()
        context['status'] = 'success'
    return render(request,'book/contact.html',context)

def book_add(request):
    form = BookForm()

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.slug = slugify(book.name)
            book.published= True
            book.save()
            form.save_m2m()
            messages.success(request, 'Save success')
            return HttpResponseRedirect(reverse('book:index', kwargs={}))
        messages.error(request, 'Save failed!')
    return render(request, 'book/add.html', {
        'form': form,
    })


from django.views.generic import ListView, DetailView


class BookListView(ListView):
    model = Book
    template_name = 'book/index.html'
    context_object_name = 'books'
    paginate_by = 5

    def get_queryset(self):
        return Book.objects.filter(published=True)
    
    def get_context_data(self, *args, **kwargs):
        cd = super(BookListView, self).get_context_data(*args, **kwargs)
        cd.update({
            'categories': Category.objects.all(),
        })
        return cd


class BookDetailView(DetailView):
    model = Book
    template_name = 'book/detail.html'
    slug_url_kwarg = 'slug'



def cart_add(request, slug):
    book = get_object_or_404(Book, slug=slug)
    cart_items = request.session.get('cart_items') or []

    # update existing item
    duplicated = False
    for c in cart_items:
        if c.get('slug') == book.slug:
            c['qty'] = int(c.get('qty') or '1') + 1
            duplicated = True
    
    # insert new item
    if not duplicated:
        cart_items.append({
            'id': book.id,
            'slug': book.slug,
            'name': book.name,
            'price': book.price,
            'qty': 1,
        })
    
    request.session['cart_items'] = cart_items
    return HttpResponseRedirect(reverse('book:cart_list', kwargs={}))


def cart_list(request):
    data = request.POST.copy()
    username = request.user.username
    user = User.objects.get(username=username)
    cart_items = request.session.get('cart_items') or []
    
    total_qty = 0
    for c in cart_items:
        total_qty = total_qty + c.get('qty')

    request.session['cart_qty'] = total_qty
    page = data.get('page')
    od = Order()
    

  
            

    return render(request, 'book/cart.html', {
        'cart_items': cart_items,
    })

def order(request):
    data = request.POST.copy()
    cart_items = request.session.get('cart_items') or []
    user = request.user.username
    od = Order.objects.get(user=user)
    page = data.get('page')
    if page == 'confirm':   
        total_qty = 0
        for c in cart_items:
            total_qty = total_qty + c.get('qty')
        od.total_price = total_qty
        od.save()

    return render(request, 'book/cart.html', {
        'cart_items': cart_items,
    })


def cart_delete(request, slug):
    cart_items = request.session.get('cart_items') or []

    for i in range(len(cart_items)):
        if cart_items[i]['slug'] == slug:
            del cart_items[i]
            break
    
    request.session['cart_items'] = cart_items
    return HttpResponseRedirect(reverse('book:cart_list', kwargs={}))


from django.core.mail import EmailMessage



def checkout(request):
    data = request.POST.copy()
    username = request.user.username
    user = User.objects.get(username=username)
    cart_items = request.session.get('cart_items') 
    od = Order()
    sh = ShippingAddress()
    page = data.get('page2')
    if request.method == 'POST':
        if page == 'con':   
            total_qty = 0
            for c in cart_items:
                total_qty = total_qty + c.get('qty')
                od.total_price = c.get('price') * c.get('qty')
                co = c.get('id')
                b = Book.objects.get(id=co)
                od.user = user
                od.product = b
                od.qty = c.get('qty')
                od.datetime = datetime.now()
                od.save()   

        if page == 'con':
            o = od.id
            od2 = Order.objects.get(id=o)
            data = request.POST.copy()
            name = data.get('name')
            tel = data.get('tel')
            addr = data.get('address')
           
            
            sh.order = od2
            sh.name = name
            sh.tel = tel
            sh.address = addr

         
    
            ########### Save Image ############
    
    if request.method == 'POST' and request.FILES['slip']:
        upload = request.FILES['slip']
        fss = FileSystemStorage()
        file = fss.save(upload.name, upload)
        file_url = fss.url(file)
        sh.upload_slip = file_url[6:]
        sh.save()
        cart_items.clear()
        return render(request, 'book/cart.html', {'file_url': file_url})
    
    return render(request, 'book/checkout.html', {
        'cart_items': cart_items,
    })
           

        
    


def cart_checkout(request):
    subject = 'Test Email'
    body = '''
        <p>This is a test mail message</p>
    '''
    email = EmailMessage(subject=subject, body=body, from_email='xxx@mail.com', to=['yyyy@gmail.com'])
    email.content_subtype = 'html'
    email.send()
    return HttpResponseRedirect(reverse('book:index', kwargs={})) 