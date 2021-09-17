import myorm

mydb = myorm.Database('mydb')


class Author(myorm.Model):
    # Implicit id field is included
    name = myorm.CharField()
    email = myorm.CharField()


Author.create_table(mydb)

author = Author(name='John', email="john@abc.com")
author.save()

del author

author = Author.filter(email="john@abc.com")[0]
assert author.name == 'John'

author.name = 'John Doe'
author.save()
author_id = author.id

# del author

author = Author.filter(id=author_id)[0]
print(author.name)
