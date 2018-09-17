class Foo(object):
    BEBUG = True

    def __init__(self):
        self.name = 'hehe'
    def __str__(self):
        return self.name

o = Foo()
print(str(o))