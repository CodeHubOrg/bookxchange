import datetime
from django.utils import timezone
from django.core.validators import MaxValueValidator
from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from django_fsm import FSMField, transition
from django.conf import settings
from bookx.utils import ChoiceEnum


def get_default_owner():
    def_user = get_user_model().objects.get_or_create(
        username=settings.DEFAULT_OWNER, email=settings.DEFAULT_OWNER_EMAIL
    )
    return def_user[0]


def current_year():
    return datetime.date.today().year


class LoanStatus(ChoiceEnum):
    AV = "available"
    RQ = "requested"
    OL = "on loan"
    LB = "loan confirmed" # confirmed by borrower (stronger than OL)
    RB = "returned" # confirmed by borrower (weaker than AV)
    NA = "not available"


class BookQueryset(models.QuerySet):
    def get_books_in_category(self, category):
        return self.filter(category__name=category)

    def get_books_in_supercategory(self, supercategory):
        if supercategory == "Nonfiction":
            books = self.get_books_nonfiction()
        else:
            books = self.get_books_in_category(supercategory)
        return books

    def get_category_id(self, category):
        try:
            cat = Category.objects.get(name=category)
            return cat.id
        except Category.DoesNotExist:
            return None

    def get_books_nonfiction(self):
        cat_list = [
            self.get_category_id(cat)
            for cat in ["Programming", "Technology", "Fiction"]
        ]
        return Book.objects.exclude(category__in=cat_list)


class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    cover = models.ImageField(upload_to="covers/", blank=True)
    thumb = models.ImageField(upload_to="covers/", blank=True)
    published_date = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now_add=True, null=True)
    isbn = models.CharField("ISBN", max_length=17, null=True)
    description = models.TextField(
        max_length=1000,
        help_text="Enter \
        a brief description of the book",
        null=True,
    )
    year_published = models.PositiveIntegerField(
        blank=True, null=True, validators=[MaxValueValidator(current_year())]
    )
    status = FSMField(
        max_length=50,
        choices=[(tag.name, tag.value) for tag in LoanStatus],
        default=(LoanStatus.AV.name),
    )
    owner = models.ForeignKey(
        get_user_model(),
        related_name="books_owned",
        on_delete=models.SET(get_default_owner),
    )
    holders = models.ManyToManyField(
        get_user_model(), related_name="books_held", through="BookHolder"
    )
    category = models.ForeignKey(
        "Category", null=True, blank=True, on_delete=models.CASCADE
    )
    at_framework = models.BooleanField(default=False)
    objects = BookQueryset.as_manager()

    @transition(field=status, source=[LoanStatus.AV.name], target=LoanStatus.RQ.name)
    def request_item(self, borrower):
        self.log_loan_event(borrower, LoanStatus.RQ.name)

    @transition(
        field=status,
        source=[LoanStatus.RQ.name],
        target=LoanStatus.OL.name,
    )
    def loan_item(self, borrower):
        self.log_loan_event(borrower, LoanStatus.OL.name)

    # additional status to confirm loan
    @transition(field=status, source=[LoanStatus.RQ.name, LoanStatus.OL.name], target=LoanStatus.LB.name)
    def confirm_loan_borrower(self, borrower):
        self.log_loan_event(borrower, LoanStatus.LB.name)

    # additional status, return not yet confirmed by lender
    @transition(field=status, source=[LoanStatus.OL.name, LoanStatus.LB.name], target=LoanStatus.RB.name)
    def return_by_borrower(self, borrower):
        self.log_loan_event(borrower, LoanStatus.RB.name)

    @transition(field=status, source=[LoanStatus.OL.name, LoanStatus.LB.name, LoanStatus.RB.name], target=LoanStatus.AV.name)
    def return_item(self, lenderadmin):        
        self.log_loan_event(lenderadmin, LoanStatus.AV.name)

    @transition(field=status, source='*', target=LoanStatus.AV.name)
    def make_available(self, lenderadmin):
        self.log_loan_event(lenderadmin, LoanStatus.AV.name)

    @transition(field=status, source='*', target=LoanStatus.NA.name)
    def withdraw(self, lenderadmin):
        self.log_loan_event(lenderadmin, LoanStatus.NA.name)
   

    def log_loan_event(self, lenderadminborrower, status):
        BookLoanEvent.objects.create(
            book=self, holder=lenderadminborrower, date=timezone.now(), status=status
        )

    def get_loan(self, status):
        try:
            loan = BookLoanEvent.objects.filter(status=status, book=self).latest("date")
        except BookLoanEvent.DoesNotExist:
            loan = None
        return loan

    def get_holder_for_status(self, status):
        loan = self.get_loan(status)
        if loan is None:
            return None
        else:
            return loan.holder

    def get_holder_for_current_status(self):
        return self.get_holder_for_status(self.status)


    @property
    def display_author(self):
        name = self.author.split(" ")
        if len(name) > 1:
            name[-1] = name[-1] + ", "
        lastfirst = name[-1:] + name[:-1]
        return "".join(lastfirst)

    def get_absolute_url(self):
        return reverse("book_detail", kwargs={"pk": self.pk})

    @property
    def absolute_url(self):
        return self.get_absolute_url()

    def __str__(self):
        return self.title

class Category(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class BookLoanEvent(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    holder = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    status = models.CharField(max_length=2, default=LoanStatus.RQ.name)
    date = models.DateTimeField(blank=True, null=True)

class BookHolder(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    holder = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    status = models.CharField(max_length=2, default="RQ")
    date_requested = models.DateTimeField(blank=True, null=True)
    date_borrowed = models.DateTimeField(blank=True, null=True)
    date_returned = models.DateTimeField(blank=True, null=True)
