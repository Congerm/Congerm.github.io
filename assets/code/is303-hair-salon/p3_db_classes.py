# John Sandberg, Luke Heaton, Matt Conger & Jacob Harrison
from peewee import * #import peewee
import pandas as pd # import pandas
import random as r # import random
from datetime import datetime # import datetime function

db = SqliteDatabase('hair_salon.db')

#create the Customer Class with all of its respective fields
class Customer(Model):
    c_id = AutoField(primary_key = True) # make it the primary key
    c_first_name = CharField()
    c_last_name = CharField()
    c_phone_number = CharField()
    c_gender = CharField()

    class Meta: # add in the Meta class so that it all runs correctly
        database = db


# Part 3 Message for returning customers
    def returning_customer_message(self):
        # Get's the number of appointsments for returning customer
        customer_appointments = Appointment.select().where(Appointment.c_id == self)
        num_of_appointments = len(customer_appointments)
        print(f"Welcome! You've had {num_of_appointments} appointments with us!")
        # If there have been no previous appointments end here
        if num_of_appointments == 0:
            return None
        # Get's most recent appointment information & returns it
        recent_appointment_data = Appointment.select().where(Appointment.c_id == self).order_by(Appointment.a_date_time.desc()).first()
        print(f"At your last haircut on {recent_appointment_data.a_date_time} you got a {recent_appointment_data.a_haircut_type} haircut with {recent_appointment_data.s_id.s_first_name} as your stylist")
        return recent_appointment_data
    


    
 
#create the Stylist Class with all of its respective fields

class Stylist(Model):
    s_id = AutoField(primary_key=True)
    s_first_name= CharField()
    s_last_name= CharField()
    s_hire_date= DateField()
    s_gender= CharField()
    class Meta:
        database = db

#create the Appointment Class with all of its respective fields

class Appointment(Model):
    a_id = AutoField(primary_key = True)
    a_haircut_type = CharField()
    a_date_time = DateTimeField()
    a_payment = FloatField()
    a_satisfied = BooleanField()
    c_id = ForeignKeyField(Customer, backref='appointments', on_delete='CASCADE') 
    # needs to reference Customer, call the backreference 'appointments'. set on_delete to be 'CASCADE'
    s_id = ForeignKeyField(Stylist,backref='appointments', on_delete='CASCADE') 
    # call the backreference 'appointments'. set on_delete to be 'CASCADE'
    
    class Meta:
        database = db

    def delete_stylist():
    # Display all stylists with their IDs, first name, and last name
        stylists = Stylist.select()  # Fetch all stylists from the database
        for stylist in stylists:
            print(f"{stylist.s_id}: {stylist.s_first_name} {stylist.s_last_name}")
        
        # Prompt the user for the ID of the stylist to delete
        stylist_id = int(input("Enter the ID of a stylist to delete: "))
        
        try:
            # Fetch the stylist with the provided ID
            stylist_to_delete = Stylist.get(Stylist.s_id == stylist_id)
            
            # Store their name for confirmation
            stylist_first_name = stylist_to_delete.s_first_name
            stylist_last_name = stylist_to_delete.s_last_name
            
            # Delete the stylist
            stylist_to_delete.delete_instance()
            
            # Confirmation message
            print(f"{stylist_first_name} {stylist_last_name} was deleted from the database.")
        except Stylist.DoesNotExist:
            print("Stylist not found. Please enter a valid ID.")

    def show_unsatisfied_appointments():
        unsatisfied_appointments = (Appointment
                                    .select()
                                    .where(Appointment.a_satisfied == False)
                                    .order_by(Appointment.a_date_time.desc())
                                    .limit(5))
        for appointment in unsatisfied_appointments:
            print(f"{appointment.get_appointment_info()}")
        


    def get_appointment_info(self):
        #gai_customer stands for get appointment info customer 
        gai_customer = self.c_id
        gai_stylist = self.s_id

        #this line of code changes depending on if they were satisfied or not
        if self.a_satisfied:
            satisfaction_status = "was satisified"
        else:
            satisfaction_status = "was not satisfied"

        return f"Appointment {self.a_id} on {self.a_date_time}: {gai_customer.c_first_name} {gai_customer.c_last_name} got a {self.a_haircut_type} from {gai_stylist.s_first_name} {gai_stylist.s_last_name}. {gai_customer.c_first_name} {satisfaction_status}."

        
        


# creates the initialize database function
def initialize_database():
    db.connect()
    db.create_tables([Customer,Stylist,Appointment])
    return db

def start_from_scratch():
    """
    Drops specified tables ('appointment', 'stylist', 'customer') in the SQLite database if they exist.
    """
    tables_to_drop = ['appointment', 'stylist', 'customer']
    db.connect()

    with db.atomic():
        for table in tables_to_drop:
            db.execute_sql(f"DROP TABLE IF EXISTS {table};")
            print(f"Dropped table: {table}")
    db.close()


    
