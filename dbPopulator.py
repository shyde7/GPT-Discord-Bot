import psycopg2
import csv

# Database connection parameters
conn_params = {
    'dbname': 'EQ Items',
    'user': 'postgres',
    'password': 'password',
    'host': 'localhost'
}

# Function to insert data from the .txt file to the PostgreSQL database
def insert_data(filepath):
    with psycopg2.connect(**conn_params) as conn:
        with conn.cursor() as cur:
            with open(filepath, 'r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter='|')
                next(reader) #skip the header row
                for row in reader:
                    try:
                        # Extracting only the necessary fields based on their indices
                        cur.execute("""
                            INSERT INTO items (
                                item_class, name, lore, idfile, idfileextra, id, weight, 
                                size, attunable, slots, price, mana, regen, manaregen, 
                                classes, races, deity, reclevel, reqskill, damage, itemtype
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (name) DO NOTHING;
                            """,
                            (
                                row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                                row[9], bool(row[10] == '1'), row[11], row[12], row[30],
                                row[33], row[34], row[35], row[36], row[37], row[43],
                                row[44], row[45], row[49]
                            ))
                    except Exception as e:
                        print(f"Error inserting item: {e}")
                        conn.rollback()
                    else:
                        conn.commit()

file_path = 'items.txt'
insert_data(file_path)
