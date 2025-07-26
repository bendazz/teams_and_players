select team_name,player_name,position,jersey_number,week,team_color,team_color2,team_color3,team_color4,team_logo_espn,headshot_url
from players_2024 inner join teams  
on players_2024.team = teams.team_abbr;
