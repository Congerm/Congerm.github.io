# John Sandberg, Luke Heaton, Matt Conger, Jacob Harrison
from p3_db_classes import *

while True:
    manager_options = int(input(f"""Welcome to Manager Tools. Choose an option below: 
    1. See the 5 most recent appointments that weren't satisfied
    2. Delete a stylist from the database
    3. Exit
    Enter an option: """))

    if 1 <= manager_options <= 3:
        if manager_options == 1:
           Appointment.show_unsatisfied_appointments()
            
        if manager_options == 2:
            Appointment.delete_stylist()

        if manager_options == 3:
            print("Thank you for using the program.")
            break
    else:
        print("Invalid selection. Try Again.")

