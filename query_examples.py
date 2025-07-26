#!/usr/bin/env python3
"""
Example queries for the NFL database
"""

import sqlite3

def run_sample_queries():
    """Run some example queries on the NFL database"""
    
    conn = sqlite3.connect('nfl_database.db')
    cursor = conn.cursor()
    
    print("=== NFL DATABASE SAMPLE QUERIES ===\n")
    
    # 1. List all teams
    print("1. All NFL Teams:")
    cursor.execute("""
        SELECT team_abbr, team_name, team_conf, team_division 
        FROM teams 
        ORDER BY team_conf, team_division, team_name
    """)
    
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]} ({row[2]} {row[3]})")
    
    # 2. Count players by team
    print("\n2. Player count by team:")
    cursor.execute("""
        SELECT team, COUNT(*) as player_count
        FROM players_2024
        GROUP BY team
        ORDER BY player_count DESC
        LIMIT 10
    """)
    
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]} players")
    
    # 3. Find quarterbacks
    print("\n3. Starting Quarterbacks (sample):")
    cursor.execute("""
        SELECT DISTINCT player_name, team, jersey_number
        FROM players_2024
        WHERE position = 'QB' AND depth_chart_position = 'QB'
        ORDER BY team
        LIMIT 10
    """)
    
    for row in cursor.fetchall():
        print(f"   #{row[2]} {row[0]} - {row[1]}")
    
    # 4. Join teams and players example
    print("\n4. Sample players with full team info:")
    cursor.execute("""
        SELECT p.player_name, p.position, t.team_name, t.team_conf, t.team_division
        FROM players_2024 p
        JOIN teams t ON p.team = t.team_abbr
        WHERE p.position = 'QB' AND p.depth_chart_position = 'QB'
        ORDER BY t.team_name
        LIMIT 5
    """)
    
    for row in cursor.fetchall():
        print(f"   {row[0]} ({row[1]}) - {row[2]} ({row[3]} {row[4]})")
    
    conn.close()

if __name__ == "__main__":
    run_sample_queries()
