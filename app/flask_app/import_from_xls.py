import csv, datetime
import MySQLdb, time

# Establish a MySQL connection
database = MySQLdb.connect (host="localhost", user = "root", passwd = "blackberry", db = "production")
database.autocommit(True)
cursor = database.cursor()

#query = """DELETE FROM devices"""
#cursor.execute(query)
# Close the cursor
cursor.close()
database.commit()
database.close()
time.sleep(1)

database = MySQLdb.connect (host="localhost", user = "root", passwd = "blackberry", db = "production")
database.autocommit(True)
cursor = database.cursor()

query = """select * from devices"""
cursor.execute(query)
cursor.close()
database.commit()
database.close()
time.sleep(1)

database = MySQLdb.connect (host="localhost", user = "root", passwd = "blackberry", db = "production")
database.autocommit(True)
cursor = database.cursor()

# Create the INSERT INTO sql query
query = """INSERT INTO devices (variant, name, security, part_number, imei_number, mfg_country, vl_tag, purpose_group, assigned_date, assignee_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
print (query)

# Create a For loop to iterate through each row in the XLS file, starting at row 2 to skip the headers
with open("./devices inventory.csv", "r") as f:
    reader = csv.reader(f, delimiter=",")
    for row in reader:
        variant = row[0].strip().upper()
        name = row[1].strip().upper()
        security = (row[2].strip().lower() == "secure")
        part_number = row[3].strip()
        imei_number = row[4].strip()
        mfg_country = row[5].strip()
        vl_tag = row[7].strip()
        purpose_group = row[6].strip()
        assinee_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        assignee_id = 1

        # Assign values from each row
        values = (variant, name, security, part_number, imei_number, mfg_country, vl_tag,
                purpose_group, assinee_date, assignee_id)

        # Execute sql Query
        cursor.execute(query, values)

# Close the cursor
cursor.close()
database.commit()
database.close()

# Print results
print ("")
print ("All Done! Bye, for now.")
print ("")
