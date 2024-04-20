# Youre gonna have to install pip and run the following commands to install the required packages
# pip install psycopg2
# pip install csv

import psycopg2
import csv

# Database connection parameters
# Create your database with these parameters so the code fucntions right or you can 
# change the parameters to match your database
conn_params = {
    'dbname': 'EQ Items',
    'user': 'postgres',
    'password': 'password',
    'host': 'localhost'
}

# use this to create your table in postgres
# --columns needed: itemclass, name, lore, idfile, idfileextra, id, weight, attunable, price, hp, mana, endurance, ac, regen, manaregen, classes, races, deity, reclevel, reqskill,
# Create Table items (
# itemclass varchar(300),
# name varchar(300),
# lore varchar(300),
# idfile varchar(300),
# idfileextra varchar(300),
# id int,
# weight int,
# attunable varchar(300),
# price int,
# hp int,
# mana int,
# endurance int,
# ac int,
# regen int,
# manaregen int,
# classes int,
# races int,
# deity int,
# reclevel int,
# reqskill int
# );

# ALTER TABLE items
# ADD UNIQUE (name);


# Function to insert data from the .txt file to the PostgreSQL database
def insert_data(filepath):
    with psycopg2.connect(**conn_params) as conn:
        with conn.cursor() as cur:
            with open(filepath, 'r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter='|')
                next(reader)  # Skip the header row
                for row in reader:
                    try:
                        cur.execute("""
                            INSERT INTO items (
                                itemclass, name, lore, idfile, idfileextra, id, weight, attunable, price, hp, mana, endurance, ac, regen, manaregen, classes, races, deity, reclevel, reqskill
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (name) DO NOTHING
                            """,
                            (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[9], row[12], row[29], row[30], row[31], row[32], row[33], row[34], row[36], row[37], row[38], row[50], row[51]))
                    except Exception as e:
                        print(f"Error inserting item: {e}")
                        conn.rollback()
                    else:
                        conn.commit()

# def insert_spell_data(filepath):
#     with psycopg2.connect(**conn_params) as conn:
#         with conn.cursor() as cur:
#             with open(filepath, 'r', encoding='utf-8') as file:
#                 reader = csv.reader(file, delimiter='|')
#                 next(reader)  # Skip the header row if your file has one
#                 for row in reader:
#                     if row[0] == "0" and row[1].startswith("Spell:"):  # Adjusted check
#                         try:
#                             # Extracting fields based on the example and mapping them
#                             name = row[1][6:].strip()  # Skip "Spell:" prefix and trim
#                             lore = row[2].strip()
#                             # Assuming fixed positions, adjust as necessary
#                             reqlevel = row[44].strip()
#                             reclevel = row[43].strip()
#                             mana = row[30].strip()
#                             # Placeholder for classes and races; may need processing to fit your schema
#                             classes = row[35].strip()
#                             races = row[36].strip()
#                             price = row[12].strip()
#                             delay = row[48].strip()

#                             cur.execute("""
#                                 INSERT INTO spells (
#                                     name, lore, reqlevel, reclevel, mana, classes, races, price, delay
#                                 ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
#                                 ON CONFLICT (name) DO NOTHING;
#                                 """, (name, lore, reqlevel, reclevel, mana, classes, races, price, delay))
#                         except Exception as e:
#                             print(f"Error inserting spell: {e}")
#                             conn.rollback()
#                         else:
#                             conn.commit()


#Replace with your file path to items.txt, had to use static path for now
file_path = '/Users/sean/Documents/GPTBot/items.txt'
insert_data(file_path)