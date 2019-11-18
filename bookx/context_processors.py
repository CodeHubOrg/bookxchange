from django.urls import resolve
from books.models import Book

# from users.models import CustomUser


def books(request):
    def _get_book(request):
        view, args, kwargs = resolve(request.path)
        book_id = kwargs.get("pk", None)
        if book_id is None:
            return None
        else:
            return Book.objects.get(pk=book_id)

    def _get_book_context(request):
        if _get_book(request) is None:
            return {}
        else:
            book = _get_book(request)            
            holder = book.get_holder_for_current_status()
            date = None
            if holder:
                loan = book.get_loan(book.status)
                date = loan.date
            return {"ct_book": book, "ct_holder": holder, "ct_date": date}

    return _get_book_context(request)


def books_action(request):
    def _get_status(request):
        view, args, kwargs = resolve(request.path)
        action = kwargs.get("action", None)
        if action is None:
            return None
        else:
            if action == "withdraw":
                new_status = "not available"
            elif action == "set_available":
                new_status = "available"
            else:
                new_status = None
            return new_status

    return {"ct_status": _get_status(request)}
