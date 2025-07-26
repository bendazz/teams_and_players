from flask import Flask, render_template, request, jsonify
import pandas as pd
import json

app = Flask(__name__)

# Load the roster data
def load_roster_data():
    """Load and return the roster data"""
    try:
        df = pd.read_csv('rosters.csv')
        return df
    except Exception as e:
        print(f"Error loading roster data: {e}")
        return pd.DataFrame()

def get_available_data():
    """Get lists of available teams and weeks"""
    df = load_roster_data()
    if df.empty:
        return [], []
    
    teams = sorted(df['team_name'].unique())
    weeks = sorted(df['week'].unique())
    return teams, weeks

def organize_players_by_position(players_df):
    """Organize players by position groups"""
    position_groups = {
        'Quarterbacks': ['QB'],
        'Running Backs': ['RB', 'FB'],
        'Wide Receivers': ['WR'],
        'Tight Ends': ['TE'],
        'Offensive Line': ['OL', 'C', 'G', 'T'],
        'Defensive Line': ['DL', 'DE', 'DT', 'NT'],
        'Linebackers': ['LB', 'ILB', 'OLB'],
        'Defensive Backs': ['DB', 'CB', 'S', 'FS', 'SS'],
        'Special Teams': ['K', 'P', 'LS'],
        'Other': []
    }
    
    organized = {}
    used_positions = set()
    
    # Organize known positions
    for group_name, positions in position_groups.items():
        if group_name == 'Other':
            continue
        group_players = players_df[players_df['position'].isin(positions)]
        if not group_players.empty:
            # Convert to dict and clean up data types for JSON serialization
            players_list = []
            for _, player in group_players.iterrows():
                player_dict = {}
                for key, value in player.items():
                    # Convert numpy types to Python native types
                    if pd.isna(value):
                        player_dict[key] = None
                    elif hasattr(value, 'dtype'):
                        if 'int' in str(value.dtype):
                            player_dict[key] = int(value) if not pd.isna(value) else None
                        elif 'float' in str(value.dtype):
                            player_dict[key] = float(value) if not pd.isna(value) else None
                        elif 'bool' in str(value.dtype):
                            player_dict[key] = bool(value)
                        else:
                            player_dict[key] = str(value)
                    else:
                        player_dict[key] = value
                players_list.append(player_dict)
            organized[group_name] = players_list
            used_positions.update(positions)
    
    # Add any remaining positions to 'Other'
    all_positions = set(players_df['position'].unique())
    remaining_positions = all_positions - used_positions
    if remaining_positions:
        other_players = players_df[players_df['position'].isin(remaining_positions)]
        if not other_players.empty:
            # Same data type conversion for 'Other' group
            players_list = []
            for _, player in other_players.iterrows():
                player_dict = {}
                for key, value in player.items():
                    if pd.isna(value):
                        player_dict[key] = None
                    elif hasattr(value, 'dtype'):
                        if 'int' in str(value.dtype):
                            player_dict[key] = int(value) if not pd.isna(value) else None
                        elif 'float' in str(value.dtype):
                            player_dict[key] = float(value) if not pd.isna(value) else None
                        elif 'bool' in str(value.dtype):
                            player_dict[key] = bool(value)
                        else:
                            player_dict[key] = str(value)
                    else:
                        player_dict[key] = value
                players_list.append(player_dict)
            organized['Other'] = players_list
    
    return organized

@app.route('/')
def index():
    """Main page with team and week selectors"""
    teams, weeks = get_available_data()
    return render_template('index.html', teams=teams, weeks=weeks)

@app.route('/team_weeks')
def get_team_weeks():
    """API endpoint to get available weeks for a specific team"""
    team_name = request.args.get('team')
    
    if not team_name:
        return jsonify({'error': 'Team is required'}), 400
    
    df = load_roster_data()
    if df.empty:
        return jsonify({'error': 'No roster data available'}), 500
    
    team_data = df[df['team_name'] == team_name]
    if team_data.empty:
        return jsonify({'error': f'No data found for team: {team_name}'}), 404
    
    available_weeks = sorted(team_data['week'].unique())
    # Convert numpy int64 to regular Python int for JSON serialization
    available_weeks = [int(week) for week in available_weeks]
    return jsonify({'available_weeks': available_weeks})

@app.route('/roster')
def get_roster():
    """API endpoint to get roster data for a specific team and week"""
    try:
        team_name = request.args.get('team')
        week = request.args.get('week')
        
        print(f"Roster request: team={team_name}, week={week}")
        
        if not team_name or not week:
            return jsonify({'error': 'Team and week are required'}), 400
        
        try:
            week = int(week)
        except ValueError:
            return jsonify({'error': 'Week must be a number'}), 400
        
        df = load_roster_data()
        if df.empty:
            print("No roster data loaded")
            return jsonify({'error': 'No roster data available'}), 500
        
        print(f"Loaded {len(df)} records")
        
        # Filter for the specific team and week
        roster_df = df[(df['team_name'] == team_name) & (df['week'] == week)]
        print(f"Found {len(roster_df)} records for {team_name} week {week}")
        
        if roster_df.empty:
            # Try to find the team's most recent available week data
            team_data = df[df['team_name'] == team_name]
            if team_data.empty:
                print(f"No data found for team: {team_name}")
                return jsonify({'error': f'No data found for team: {team_name}'}), 404
            
            # Get the closest available week (prefer earlier weeks if exact week not found)
            available_weeks = sorted(team_data['week'].unique())
            print(f"Available weeks for {team_name}: {available_weeks}")
            closest_week = None
            
            # Try to find the closest week that's <= requested week
            for w in reversed(available_weeks):
                if w <= week:
                    closest_week = w
                    break
            
            # If no week <= requested week, use the first available week
            if closest_week is None:
                closest_week = available_weeks[0]
            
            print(f"Using closest week: {closest_week}")
            roster_df = df[(df['team_name'] == team_name) & (df['week'] == closest_week)]
            
            if roster_df.empty:
                print(f"Still no roster data for {team_name}")
                return jsonify({'error': f'No roster data available for {team_name}'}), 404
        
        # Get team info (colors, logo) from the first row
        team_info = {
            'name': team_name,
            'logo': roster_df.iloc[0]['team_logo_espn'],
            'colors': {
                'primary': roster_df.iloc[0]['team_color'],
                'secondary': roster_df.iloc[0]['team_color2'],
                'tertiary': roster_df.iloc[0]['team_color3'] if pd.notna(roster_df.iloc[0]['team_color3']) else None,
                'quaternary': roster_df.iloc[0]['team_color4'] if pd.notna(roster_df.iloc[0]['team_color4']) else None
            }
        }
        
        # Get the actual week from the data (might be different from requested week)
        actual_week = roster_df.iloc[0]['week']
        
        # Organize players by position
        organized_roster = organize_players_by_position(roster_df)
        
        print(f"Returning roster data for {team_name} week {actual_week}")
        
        return jsonify({
            'team_info': team_info,
            'week': int(actual_week),
            'requested_week': week,
            'week_available': bool(actual_week == week),  # Convert numpy bool to Python bool
            'roster': organized_roster
        })
    
    except Exception as e:
        print(f"Error in get_roster: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
