# Matthew Conger, Jacob Harrison, John Sandberg, Luke Heaton
# A program that formates and summarizes important information about each class that a teacher teaches 

import os
import platform
import openpyxl
from openpyxl.styles import Font

def clear_screen():
    """
    Clears the terminal screen to make it easier to follow along with code.
    """
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

clear_screen()

#I Named the Pooly Organized data 1 and 2 POD1 and POD2 so theyre
#easier to type but if you want to swich them all, just Highlight one
#and click F2 and you can change all of them

POD1= openpyxl.load_workbook(r"poorly_organized_data_1.xlsx")
POD2= openpyxl.load_workbook(r"poorly_organized_data_2.xlsx")

#Reformats the whole grades sheet into the proper format but
#Creates new workbook and sorts them
current_workbook=openpyxl.Workbook()
sheet=POD1.active

#For every row, we reformat the row to split the 2nd cell into 3
#For some dumb reason i could only get itto work in a loop so it loops
#Through the sheets
for sheet in POD1:
    for row in sheet.iter_rows(min_row = 2, max_col = 3):
        #We extract the data from the cells and turn it to Varibles
        className = row[0].value
        combinedData=row[1].value
        dataList=combinedData.split("_")
        firstName=dataList[1]
        lastName=dataList[0]
        studentID=dataList[2]
        grade=row[2].value
        #we now reinsert the varibles where they are supposed to be
        #We make it a list so its easy to append into each sheet
        Student_info=[lastName,firstName,studentID,grade]

        #if there is a sheet with the same name as the students class
        #name then we .append "Student_Info" to that sheet, if there
        #is not then we create a new sheet
        if className in current_workbook.sheetnames:
            current_workbook[className].append(Student_info)
        else:
            current_workbook.create_sheet(className)
            #format the new sheet
            current_workbook[className]["A1"]="Last Name"
            current_workbook[className]["B1"]="First Name"
            current_workbook[className]["C1"]="Student ID"
            current_workbook[className]["D1"]="Grade"
            current_workbook[className].append(Student_info)


#Then at the end we need to add the stats
for sheet in current_workbook:
    if current_workbook == "Grades":
            continue
    else:
        #These are the labels for the stats on the right
        sheet["F1"]="Summary Statistics"
        sheet["G1"]="Value"
        sheet["F2"]="Highest Grade"
        sheet["F3"]="Lowest Grade"
        sheet["F4"]="Mean Grade"
        sheet["F5"]="Median Grade"
        sheet["F6"]="Number of Students"
      #these are the formulas to calculate the different stats
        sheet["G2"]="=MAX(D:D)"
        sheet["G3"]="=MIN(D:D)"
        sheet["G4"]="=AVERAGE(D:D)"
        sheet["G5"]="=MEDIAN(D:D)"
        sheet["G6"]="=COUNT(D:D)"
      #Add Filters
        furthestRowWithData = sheet.max_row
        sheet.auto_filter.ref = f'A1:D{furthestRowWithData}'

# Removes default sheet
for sheet in current_workbook:
    if sheet.title=="Sheet":
        current_workbook.remove(sheet)

font_1 = Font(bold=True)

for sheet in current_workbook:
    sheet["A1"].font = font_1
    sheet["B1"].font = font_1
    sheet["C1"].font = font_1
    sheet["D1"].font = font_1
    sheet["F1"].font = font_1
    sheet["G1"].font = font_1

    sheet.column_dimensions["A"].width = len(sheet["A1"].value) + 5
    sheet.column_dimensions["B"].width = len(sheet["B1"].value) + 5
    sheet.column_dimensions["C"].width = len(sheet["C1"].value) + 5
    sheet.column_dimensions["D"].width = len(sheet["D1"].value) + 5
    sheet.column_dimensions["F"].width = len(sheet["F1"].value) + 5
    sheet.column_dimensions["G"].width = len(sheet["G1"].value) + 5
 

#This saves the formatted grades sheet
current_workbook.save(r"formatted_grades.xlsx")
current_workbook.close()


    
        