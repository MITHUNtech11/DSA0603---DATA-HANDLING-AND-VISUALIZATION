import pandas as pd
import os
from datetime import datetime, timedelta

def main():
    print("Generating mock dataset for capstone...")
    
    # 1. Users sheet data (15 users)
    users_data = {
        "User_ID": [f"U{i}" for i in range(1, 16)],
        "Username": [
            "Alice", "Bob", "Charlie", "David", "Eve", 
            "Frank", "Grace", "Heidi", "Ivan", "Judy",
            "Kevin", "Laura", "Mallory", "Nate", "Olivia"
        ],
        "Follower_Count": [1500, 8500, 120, 25000, 450, 8900, 3100, 750, 15000, 95, 340, 1200, 5400, 11000, 620],
        "Credibility_Score": [0.85, 0.45, 0.90, 0.30, 0.50, 0.95, 0.88, 0.60, 0.40, 0.80, 0.75, 0.92, 0.35, 0.70, 0.65],
        "Region": ["North America", "Europe", "Asia", "North America", "Europe", "Asia", "Australia", "Europe", "Asia", "North America", "Europe", "North America", "Europe", "Asia", "Australia"]
    }
    df_users = pd.DataFrame(users_data)
    
    # 2. Posts sheet data (6 posts: 3 True, 3 False/Unverified)
    posts_data = {
        "Post_ID": ["P1", "P2", "P3", "P4", "P5", "P6"],
        "Content": [
            "Breaking: Scientific breakthrough in clean nuclear fusion achieves 120% net energy gain!",
            "SHOCKING: Eating raw garlic cures the flu in less than 2 hours! Pass it on before it gets deleted!",
            "Weather Warning: Heavy rainfall and flash flooding expected in the metro area tomorrow morning.",
            "ALERT: Leaked documents show government plans to ban all gasoline cars starting next week!",
            "WARNING: Popular bottled water brand contains dangerous chemical contamination. Do not drink!",
            "Sports Update: Local United FC wins the championship cup after a thrilling penalty shootout."
        ],
        "Author_ID": ["U6", "U4", "U12", "U2", "U13", "U1"],
        "Platform": ["Twitter", "Facebook", "Twitter", "Reddit", "Facebook", "Twitter"],
        "Veracity": ["True", "False", "True", "False", "False", "True"],
        "Publish_Time": [
            "2026-08-25 09:00:00",
            "2026-08-25 10:00:00",
            "2026-08-25 08:30:00",
            "2026-08-25 11:15:00",
            "2026-08-25 12:00:00",
            "2026-08-25 14:00:00"
        ]
    }
    df_posts = pd.DataFrame(posts_data)
    
    # Convert publish times to datetime
    df_posts["Publish_Time"] = pd.to_datetime(df_posts["Publish_Time"])
    
    # 3. Shares sheet data (15 shares forming cascades)
    shares_data = {
        "Share_ID": [f"S{i}" for i in range(1, 16)],
        "Post_ID": [
            "P2", "P2", "P2", "P2", "P2", # P2 cascade
            "P4", "P4", "P4",             # P4 cascade
            "P1", "P1",                   # P1 cascade
            "P3", "P3",                   # P3 cascade
            "P5",                         # P5 cascade
            "P6", "P6"                    # P6 cascade
        ],
        "Source_User": [
            "David", "Alice", "Bob", "Charlie", "Eve", # P2 cascade path
            "Bob", "David", "Ivan",                    # P4 cascade path
            "Frank", "Grace",                          # P1 cascade path
            "Laura", "Nate",                           # P3 cascade path
            "Mallory",                                 # P5 cascade path
            "Alice", "Bob"                             # P6 cascade path
        ],
        "Target_User": [
            "Alice", "Bob", "Charlie", "Eve", "Laura", # P2 cascade path
            "David", "Ivan", "Mallory",                # P4 cascade path
            "Grace", "Heidi",                          # P1 cascade path
            "Nate", "Olivia",                          # P3 cascade path
            "Kevin",                                   # P5 cascade path
            "Bob", "Charlie"                           # P6 cascade path
        ],
        "Share_Time": [
            "2026-08-25 10:05:00", # P2 David -> Alice (5 min delay)
            "2026-08-25 10:12:00", # P2 Alice -> Bob (7 min delay)
            "2026-08-25 10:25:00", # P2 Bob -> Charlie (13 min delay)
            "2026-08-25 10:35:00", # P2 Charlie -> Eve (10 min delay)
            "2026-08-25 10:50:00", # P2 Eve -> Laura (15 min delay)
            
            "2026-08-25 11:20:00", # P4 Bob -> David (5 min delay)
            "2026-08-25 11:32:00", # P4 David -> Ivan (12 min delay)
            "2026-08-25 11:55:00", # P4 Ivan -> Mallory (23 min delay)
            
            "2026-08-25 09:45:00", # P1 Frank -> Grace (45 min delay)
            "2026-08-25 11:15:00", # P1 Grace -> Heidi (90 min delay)
            
            "2026-08-25 09:30:00", # P3 Laura -> Nate (60 min delay)
            "2026-08-25 11:00:00", # P3 Nate -> Olivia (90 min delay)
            
            "2026-08-25 12:45:00", # P5 Mallory -> Kevin (45 min delay)
            
            "2026-08-25 14:15:00", # P6 Alice -> Bob (15 min delay)
            "2026-08-25 14:35:00"  # P6 Bob -> Charlie (20 min delay)
        ]
    }
    df_shares = pd.DataFrame(shares_data)
    df_shares["Share_Time"] = pd.to_datetime(df_shares["Share_Time"])
    
    # Save sheets to Excel file
    output_dir = r"c:\Users\mithu\OneDrive\Desktop\College\DSA0603 - DATA HANDLING AND VISUALIZATION\Capstone"
    os.makedirs(output_dir, exist_ok=True)
    excel_path = os.path.join(output_dir, "mock_dataset.xlsx")
    
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        df_users.to_excel(writer, sheet_name="Users", index=False)
        df_posts.to_excel(writer, sheet_name="Posts", index=False)
        df_shares.to_excel(writer, sheet_name="Shares", index=False)
        
    print(f"Mock dataset generated successfully at {excel_path}!")

if __name__ == "__main__":
    main()
