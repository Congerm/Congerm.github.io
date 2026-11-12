# Luke Heaton, Matt Conger, John Sandberg, & Jacob Harrison

#This imports all of the code from our other tab db_classes
from p3_db_classes import *

#imports pandas 
import pandas as pd

#this imports 
combined_df = pd.read_excel('starting_hair_salon_data.xlsx')

c_df = combined_df[['c_first_name', 'c_last_name', 'c_phone_number', 'c_gender']].copy()

c_df.drop_duplicates(inplace=True)
c_df.reset_index(drop=True, inplace=True)
c_df['c_id'] = c_df.index


s_df = combined_df[['s_first_name', 's_last_name', 's_gender', 's_hire_date']].copy()

s_df.drop_duplicates(inplace=True)
s_df.reset_index(drop=True, inplace=True)
s_df['s_id'] = s_df.index



 # combine the original df and the c_df to add the new c_id column
a_df = combined_df.merge(c_df, on=['c_first_name', 'c_last_name', 'c_phone_number', 'c_gender'])

  # now combine the new a_df with the stylist df to put the s_id column into it
a_df = a_df.merge(s_df, on=['s_first_name', 's_last_name', 's_gender', 's_hire_date'])

  # now get rid of c_ and s_ columns except for the s_id and c_id foreign keys
a_df.drop(['c_first_name', 'c_last_name', 'c_phone_number', 'c_gender', 's_first_name', 's_last_name', 's_hire_date', 's_gender'], axis=1, inplace=True)

  # create a primary key column for appointments
a_df["a_id"] = a_df.index


c_df['c_phone_number'] = c_df['c_phone_number'].str.replace("-", "")

start_from_scratch()
db = initialize_database()


c_df.to_sql('customer', db, if_exists='append', index=False)
s_df.to_sql('stylist', db, if_exists='append', index=False)
a_df.to_sql('appointment', db, if_exists='append', index=False)