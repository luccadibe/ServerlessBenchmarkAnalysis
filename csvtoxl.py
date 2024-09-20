# convert csv to excel
import csv
import openpyxl
import os

# csv file name
filename = "pricing.csv"

# initialize workbook

wb = openpyxl.Workbook()
ws = wb.active

# open csv file
with open(filename, "r") as csvfile:
    # create a csv reader object
    csvreader = csv.reader(csvfile)

    # read each row and write to excel
    for row in csvreader:
        ws.append(row)
    # save workbook
    wb.save("pricing.xlsx")
    print("Conversion successful")
    # close csv file
    csvfile.close()
    # close excel file
    wb.close()
