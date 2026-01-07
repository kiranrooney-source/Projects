import sqlite3
import pandas as pd
import os

# Database path
db_path = 'recovered_db.db'
output_dir = 'recovered_data'

# Create output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def recover_data():
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found.")
        return

    try:
        conn = sqlite3.connect(db_path)
        
        # Get all tables
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"Found tables: {tables}")
        
        for table in tables:
            try:
                print(f"Exporting table '{table}'...")
                df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
                output_file = os.path.join(output_dir, f"{table}.csv")
                df.to_csv(output_file, index=False)
                print(f"Saved {len(df)} rows to {output_file}")
            except Exception as e:
                print(f"Error exporting table {table}: {e}")
                
        conn.close()
        print("\nData recovery completed successfully.")
        
    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == '__main__':
    recover_data()
