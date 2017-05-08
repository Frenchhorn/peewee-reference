'''
Created on Apr 17, 2017

@author: qinpan.zhao
'''
import peewee
from datetime import date

db = peewee.SqliteDatabase('people.db')

class Person(peewee.Model):
    name = peewee.CharField()
    birthday = peewee.DateField()
    is_relative = peewee.BooleanField()
    
    class Meta:
        database = db

class Pet(peewee.Model):
    owner = peewee.ForeignKeyField(Person, related_name='pets')
    name = peewee.CharField()
    animal_type = peewee.CharField()
    
    class Meta:
        database = db
        
def main():
    # connect or create database
    db.connect()
    # add tables
    db.create_tables([Person, Pet])
    # use the save() and create() methods to add and update people’s records
    uncle_bob = Person(name='Bob', birthday=date(1960, 1, 15), is_relative=True)
    uncle_bob.save()
    # add a person by calling the create() method, which returns a model instance
    grandma = Person.create(name='Grandma', birthday=date(1935, 3, 1), is_relative=True)
    herb = Person.create(name='Herb', birthday=date(1950, 5, 5), is_relative=False)
    # update a row
    grandma.name = 'Grandma L.'
    grandma.save()
    # add pet
    bob_kitty = Pet.create(owner=uncle_bob, name='Kitty', animal_type='cat')
    herb_fido = Pet.create(owner=herb, name='Fido', animal_type='dog')
    herb_mittens = Pet.create(owner=herb, name='Mittens', animal_type='cat')
    herb_mittens_jr = Pet.create(owner=herb, name='Mittens Jr', animal_type='cat')
    # remove pet
    herb_mittens.delete_instance()
    # update owner
    herb_fido.owner = uncle_bob
    herb_fido.save()
 
    # get a single record from the database by using SelectQuery.get()
    grandma = Person.select().where(Person.name == 'Grandma L.').get()
    # or Model.get()
    grandma = Person.get(Person.name == 'Grandma L.')
    
    # lists of records
    for person in Person.select():
        print(person.name, person.is_relative)
    # bad query example
    query = Pet.select().where(Pet.animal_type == 'cat')
    for pet in query:
        print(pet.name, pet.owner.name)
    # good query example
    query = Pet.select(Pet, Person).join(Person).where(Pet.animal_type == 'cat')
    for pet in query:
        print(pet.name, pet.owner.name)
    # use join
    for pet in Pet.select().join(Person).where(Person.name == 'Bob'):
        print(pet.name)
    # or 
    for pet in Pet.select().where(Pet.owner == uncle_bob):
        print(pet.name)
    # use order_by
    for pet in Pet.select().where(Pet.owner == uncle_bob).order_by(Pet.name):
        print(pet.name)
    # another example
    for person in Person.select().order_by(Person.birthday.desc()):
        print(person.name, person.birthday)
    # list all the people and some info about their pets
    subquery = Pet.select(peewee.fn.COUNT(Pet.id)).where(Pet.owner == Person.id)
    query = (Person.select(Person, Pet, subquery.alias('pet_count')).join(Pet, peewee.JOIN.LEFT_OUTER).order_by(Person.name))

    for person in query.aggregate_rows():  # Note the `aggregate_rows()` call.
        print(person.name, person.pet_count, 'pets')
        for pet in person.pets:
            print('    ', pet.name, pet.animal_type)
    # people before 1940 or after 1959
    d1940 = date(1940, 1, 1)
    d1960 = date(1960, 1, 1)
    query = (Person
             .select()
             .where((Person.birthday < d1940) | (Person.birthday > d1960)))
    for person in query:
        print(person.name, person.birthday)
    # use a SQL function to find all people whose names start with either an upper or lower-case G
    expression = (peewee.fn.Lower(peewee.fn.Substr(Person.name, 1, 1)) == 'g')
    for person in Person.select().where(expression):
        print(person.name)
    # close database
    db.close()
        
if __name__ == '__main__':
    main()