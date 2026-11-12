#Luke Heaton, Matthew Conger, Jacob Harrison, John Sandberg
# Checks customers in to hair Salon

from datetime import *
import random
from p3_db_classes import initialize_database, Customer, Stylist, Appointment



# Hairstyles and their prices. Use if you want.
hairstyles_dict = {
    "Undercut": 22.0,
    "Mullet": 18.0,
    "Fade":	20.0,
    "Buzz Cut":	15.0,
    "Pixie Cut": 30.0,
    "Bob": 28.0,
    "Pompadour": 40.0,
    "Layered Cut": 25.0,
    "Crew Cut": 16.0,
    "Shag": 35.0
}

hairstyle_choices = {
    1: "Undercut",
    2: "Mullet",
    3: "Fade",
    4: "Buzz Cut",
    5: "Pixie Cut",
    6: "Bob",
    7: "Pompadour",
    8: "Layered Cut",
    9: "Crew Cut",
    10: "Shag"
}

# Makes a list of all the stylists
all_stylists_list = list(Stylist.select())
# Makes sure lines 114, 119, 133 function correctly
returning_appointment_obj = None
returning_customer_haircut_choice = None
returning_customer_stylist_choice = None

# Checks to make sure phone number entered is a valid phone number with 10 digits and removes " " & "-"
while True:
    phone_number = input("Hello! Welcome to Incredible Cuts. Please enter your phone number to check in: ").replace("-", "").replace(" ", "")
    if len(phone_number) == 10:
        break
    else:
        print(f"That wasn't a 10 digit phone number. Please try again.")
all_c_phone_numbers = [Customer.c_phone_number for Customer in Customer.select()]
#Check if customer is a returning customer
if phone_number in all_c_phone_numbers:
    customer_obj = Customer.get(Customer.c_phone_number == phone_number)
    returning_appointment_obj = customer_obj.returning_customer_message()
    same_options = input(f"Do you want to continue with these same options? Enter 'Y' if so, otherwise enter 'N': ").upper()
    if same_options == 'Y':
        returning_customer_haircut_choice = returning_appointment_obj.a_haircut_type
        returning_customer_stylist_choice = returning_appointment_obj.s_id
    else:
        #Customer chooses a hairstyle
        new_hair_style = int(input(f"""These are the available hairstyles: 
1: Undercut
2: Mullet
3: Fade
4: Buzz Cut
5: Pixie Cut
6: Bob
7: Pompadour
8: Layered Cut
9: Crew Cut
10: Shag
Enter the number of the hairstyle you want:"""))
        new_gender_stylist_choice = input(f"To get the first available stylist regardless of gender, enter 1. If you want your stylist to be the same gender as you, enter 2:")
        # Get's correct stylist gender
        if new_gender_stylist_choice == 1:
            new_stylist = random.choice(all_stylists_list)
        else:
            same_gender_list = list(Stylist.select().where(Stylist.s_gender == returning_appointment_obj.c_id.c_gender))
            new_stylist = random.choice(same_gender_list)
    


# If customer is not a returning customer
else:
    print(f"Thanks for joining us! Enter the following information: ")
    new_first_name = input("Enter your first name: ")
    new_last_name = input("Enter your last name: ")
    new_gender = input("Enter your gender (M or F): ")
    new_customer = Customer(c_first_name = new_first_name, c_last_name = new_last_name, c_phone_number = phone_number, c_gender = new_gender)
    #New Customer Choices 
    new_hair_style = int(input(f"""These are the available hairstyles: 
1: Undercut
2: Mullet
3: Fade
4: Buzz Cut
5: Pixie Cut
6: Bob
7: Pompadour
8: Layered Cut
9: Crew Cut
10: Shag
Enter the number of the hairstyle you want:"""))
    new_gender_stylist_choice = input(f"To get the first available stylist regardless of gender, enter 1. If you want your stylist to be the same gender as you, enter 2:")
    # Get's correct stylist gender
    if new_gender_stylist_choice == 1:
        new_stylist = random.choice(all_stylists_list)
    else:
        same_gender_list = list(Stylist.select().where(Stylist.s_gender == new_customer.c_gender))
        new_stylist = random.choice(same_gender_list)

# Creating an Appointment
# Accounts for all the different variables of haircut style and stylist choice.
if returning_customer_haircut_choice:
    haircut_style_choice = returning_customer_haircut_choice
else:
    haircut_style_choice = hairstyle_choices.get(new_hair_style)

 # Makes sure c_id and s_id work for new_appointment
if returning_customer_stylist_choice:
    final_stylist = returning_customer_stylist_choice  
else:
    final_stylist = new_stylist

if returning_appointment_obj:
    final_customer = returning_appointment_obj.c_id  
else:
    new_customer.save()
    final_customer = new_customer  # Use newly created customer


# Makes a payment based on hairstyle
payment = hairstyles_dict.get(haircut_style_choice)

print(f"{final_stylist.s_first_name} {final_stylist.s_last_name} gave you a {haircut_style_choice} haircut today!")
# Askes if customer is satisfied with thier haircut, Used in manager tools
satisfied = input(f"Are you satisfied? Enter Y or N: ").upper()
if satisfied == 'Y':
    satisfaction = True
else:
    satisfaction = False

new_appointment = Appointment.create(a_haircut_type = haircut_style_choice, a_date_time = datetime.today(), a_payment = payment, a_satisfied = satisfaction, c_id = final_customer, s_id = final_stylist.s_id)
# End message
print(f"Thank you for choosing Incredible Cuts! We hope to see you again soon")





# OLD CODE


# from p3_db_classes import *

# # Hairstyles and their prices. Use if you want.
# hairstyles_dict = {
#     "Undercut": 22.0,
#     "Mullet": 18.0,
#     "Fade":	20.0,
#     "Buzz Cut":	15.0,
#     "Pixie Cut": 30.0,
#     "Bob": 28.0,
#     "Pompadour": 40.0,
#     "Layered Cut": 25.0,
#     "Crew Cut": 16.0,
#     "Shag": 35.0
# }

# hairstyle_choices = {
#     "1": "Undercut",
#     "2": "Mullet",
#     "3": "Fade",
#     "4": "Buzz Cut",
#     "5": "Pixie Cut",
#     "6": "Bob",
#     "7": "Pompadour",
#     "8": "Layered Cut",
#     "9": "Crew Cut",
#     "10": "Shag"}

# # creates the variable for all customers
# all_customers = Customer.select()

# # starts the loop to get the input for the phone number
# while True:
#     check_in_number = str(input("Hello! Welcome to Incredible Cuts. Please enter your phone number to check in: ")).replace("-", "").replace(" ", "")
#     if len(check_in_number) == 10:
#         break
#     else:
#         print("That wasn't a 10 digit phone number. Please try again.")


# returning_customer = Customer.get_or_none(Customer.c_phone_number == check_in_number)

# #creates the if statement for whether or not they area returning customer and determines the specifics of their transaction.

# if returning_customer:
#     returning_customer.returning_customer_message()
#     same_options = input(f"Do you want to continue with these same options? Enter 'Y' if so, otherwise enter 'N': ").upper()
#     r_a_data = (Appointment.select().where(Appointment.c_id == returning_customer).order_by(Appointment.a_date_time.desc()).first())
#     if same_options == "Y":
#         #this will be used in step 5
#         choice_of_cutter = r_a_data.s_id
#         selected_hairstyle = r_a_data.a_haircut_type
#     # If they selection "N"
#     else:
    
#         current_gender = returning_customer.c_gender
#         selected_hairstyle = input(f"""These are the available hairstyles: 
#         1: Undercut
#         2: Mullet
#         3: Fade
#         4: Buzz Cut
#         5: Pixie Cut
#         6: Bob
#         7: Pompadour
#         8: Layered Cut
#         9: Crew Cut
#         10: Shag
#         Enter the number of the hairstyle you want: """)
#         gender_of_stylist = input(f"To get the first available stylist regardless of gender, enter 1. If you want your stylist to be the same gender as you, enter 2: ")
#         all_cutters = list(Stylist.select())
#         if gender_of_stylist == 1:
#             choice_of_cutter = r.choice(all_cutters)
#         else:
#             same_gender_cutters = Stylist.select().where(Stylist.s_gender == current_gender)
#             choice_of_cutter = r.choice(same_gender_cutters)

# # Part 3 creation of new customer
# else:
#     print(f"Thanks for joining us! Enter the following information: ")
#     new_first_name = input(f"Enter your first name: ")
#     new_last_name = input(f"Enter your last name: ")
#     new_gender = input(f" Enter your gender (M or F): ")
#     new_customer_obj = Customer.create(c_first_name = new_first_name, c_last_name = new_last_name, c_phone_number = check_in_number, c_gender = new_gender)
#     # Choosing a new hairstyle and stylist
#     selected_hairstyle = input(f"""These are the available hairstyles: 
#     1: Undercut
#     2: Mullet
#     3: Fade
#     4: Buzz Cut
#     5: Pixie Cut
#     6: Bob
#     7: Pompadour
#     8: Layered Cut
#     9: Crew Cut
#     10: Shag
#     Enter the number of the hairstyle you want: """)
#     gender_of_stylist = input(f"To get the first available stylist regardless of gender, enter 1. If you want your stylist to be the same gender as you, enter 2: ")
#     all_cutters = list(Stylist.select())
#     if gender_of_stylist == 1:
#         choice_of_cutter = r.choice(all_cutters)
#     else:
#         same_gender_cutters = list(Stylist.select().where(Stylist.s_gender == new_gender))
#         choice_of_cutter = r.choice(same_gender_cutters)
    


# #Step 5 Create an Appointment
# if returning_customer:
#     print(f"{choice_of_cutter} gave you a {selected_hairstyle} haircut today!")
#     payment = hairstyles_dict.get(selected_hairstyle)
# else:
#     selected_hairstyle_name = hairstyle_choices.get(selected_hairstyle)
#     payment = hairstyles_dict.get(selected_hairstyle_name)
#     print(f"{choice_of_cutter} gave you a {selected_hairstyle_name} haircut today!")

# satisfied = input(f"Are you satisfied? Enter Y or N: ").upper()
# if satisfied == 'Y':
#     satisfaction = True
# else:
#     satisfaction = False


# final_object = Appointment.create(a_id = returning_customer or new_customer_obj, a_haircut_type = selected_hairstyle or selected_hairstyle_name, a_date_time = datetime.today(),a_payment = payment, c_id = returning_customer or new_customer_obj, s_id = r_a_data.s_id or choice_of_cutter.s_id )


# if returning_customer:
#     new_appointment = Appointment.create(a_date_time = datetime.today(), a_haircut_type =selected_hairstyle, a_payment = payment, a_satisfied = satisfaction, c_id = returning_customer or new_customer_obj, s_id = final_object.s_id)
#     print("Thank you for choosing Incredible Cuts! We hope to see you again soon.")
# else:
#     new_appointment = Appointment.create(a_date_time = datetime.today(), a_haircut_type =selected_hairstyle_name, a_payment = payment, a_satisfied = satisfaction, c_id = returning_customer or new_customer_obj, s_id = final_object.s_id)
#     print("Thank you for choosing Incredible Cuts! We hope to see you again soon.")



