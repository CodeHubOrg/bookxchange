from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from bookx.utils import ChoiceEnum


def get_default_owner():
    return get_user_model().objects.get_or_create(
        username=settings.DEFAULT_OWNER
    )


class LoanStatus(ChoiceEnum):
    AV = "available"
    OL = "on loan"
    RQ = "requested"
    NA = "not available"


class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    cover = models.ImageField(upload_to="covers/", blank=True)
    thumb = models.ImageField(upload_to="covers/", blank=True)
    published_date = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now_add=True, null=True)
    status = models.CharField(
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

    def get_loan(self, status, latestby):
        return BookHolder.objects.filter(status=status, book=self).latest(
            latestby
        )

    def get_holder_for_status(self, status, latestby):
        loan = self.get_loan(status, latestby)
        return loan.holder

    # Book requested

    @property
    def last_requested(self):
        loan = self.get_loan("RQ", "date_requested")
        return loan.date_requested

    @property
    def latest_requester(self):
        return self.get_holder_for_status("RQ", "date_requested")

    # Book borrowed

    @property
    def last_borrowed(self):
        loan = self.get_loan("OL", "date_borrowed")
        return loan.date_borrowed

    @property
    def latest_borrower(self):
        return self.get_holder_for_status("OL", "date_borrowed")

    # Book returned

    @property
    def last_returned(self):
        loan = self.get_loan("AV", "date_returned")
        return loan.date_returned

    @property
    def returned_from(self):
        return self.get_holder_for_status("AV", "date_returned")

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


class BookHolder(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    holder = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    status = models.CharField(max_length=2, default="RQ")
    date_requested = models.DateTimeField(blank=True, null=True)
    date_borrowed = models.DateTimeField(blank=True, null=True)
    date_returned = models.DateTimeField(blank=True, null=True)
