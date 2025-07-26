#!/usr/bin/env python3
"""
Script to create an SQLite database from NFL teams and players CSV files.
Creates two tables: teams and players_2024
"""

import sqlite3
import pandas as pd
import sys

def create_nfl_database():
    """Create SQLite database with teams and players tables"""
    
    # Database file name
    db_file = 'nfl_database.db'
    
    try:
        # Read the CSV files
        print("Reading CSV files...")
        teams_df = pd.read_csv('teams.csv')
        players_df = pd.read_csv('players_2024.csv')
        
        print(f"Teams data: {len(teams_df)} records")
        print(f"Players data: {len(players_df)} records")
        
        # Create SQLite connection
        print(f"Creating SQLite database: {db_file}")
        conn = sqlite3.connect(db_file)
        
        # Write dataframes to SQLite tables
        print("Creating teams table...")
        teams_df.to_sql('teams', conn, if_exists='replace', index=False)
        
        print("Creating players_2024 table...")
        players_df.to_sql('players_2024', conn, if_exists='replace', index=False)
        
        # Get table info
        cursor = conn.cursor()
        
        print("\n=== DATABASE CREATED SUCCESSFULLY ===")
        print(f"Database file: {db_file}")
        
        # Show table info
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables created: {[table[0] for table in tables]}")
        
        # Show teams table info
        print("\n--- TEAMS TABLE ---")
        cursor.execute("PRAGMA table_info(teams);")
        teams_columns = cursor.fetchall()
        print("Columns:")
        for col in teams_columns:
            print(f"  - {col[1]} ({col[2]})")
        
        cursor.execute("SELECT COUNT(*) FROM teams;")
        teams_count = cursor.fetchone()[0]
        print(f"Records: {teams_count}")
        
        # Show players table info
        print("\n--- PLAYERS_2024 TABLE ---")
        cursor.execute("PRAGMA table_info(players_2024);")
        players_columns = cursor.fetchall()
        print("Columns:")
        for col in players_columns:
            print(f"  - {col[1]} ({col[2]})")
        
        cursor.execute("SELECT COUNT(*) FROM players_2024;")
        players_count = cursor.fetchone()[0]
        print(f"Records: {players_count}")
        
        # Sample queries
        print("\n--- SAMPLE QUERIES ---")
        print("Sample teams:")
        cursor.execute("SELECT team_abbr, team_name, team_conf, team_division FROM teams LIMIT 5;")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} ({row[2]} {row[3]})")
        
        print("\nSample players:")
        cursor.execute("SELECT player_name, team, position FROM players_2024 LIMIT 5;")
        for row in cursor.fetchall():
            print(f"  {row[0]} - {row[1]} {row[2]}")
        
        # Close connection
        conn.close()
        print(f"\nDatabase successfully created: {db_file}")
        
    except Exception as e:
        print(f"Error creating database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_nfl_database()
