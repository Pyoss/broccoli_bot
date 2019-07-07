lst = [1, 2, 3, 3.4, 3.56, 78.43]


def ans(lst):
    new_lst = []
    for i in lst:
        new_lst.append(i + 10)
    return new_lst

print(ans(lst))


class Book:
    def __init__(self, pages: int, author):
        self.pages = pages
        self.author = author

    def desc(self):
        print('Автор:' + self.author + '\n' + 'Кол-во страниц:' + str(self.pages))

my_book = Book(40, 'Имя_автора')
my_book.desc()