from .models import Book, Category


def get_books_in_category(category):
    if category == "Nonfiction":
        books = get_books_nonfiction()
    else:
        cat_id = get_category_id(category)
        if cat_id:
            books = Book.objects.filter(category=cat_id)
        else:
            books = None

    return books


def get_category_id(category):
    try:
        cat = Category.objects.get(name=category)
        return cat.id
    except Category.DoesNotExist:
        return None


def get_books_nonfiction():
    cat_list = [
        get_category_id(cat)
        for cat in ["Programming", "Technology", "Fiction"]
    ]
    return Book.objects.exclude(category__in=cat_list)
