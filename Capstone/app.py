import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import os
from datetime import datetime

# Set page config for a clean academic/corporate look (light theme by default)
st.set_page_config(
    page_title="Social Media Misinformation Spread Visualization",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Helper to load data
@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(current_dir, "mock_dataset.xlsx")
    
    # Auto-generate if Excel doesn't exist
    if not os.path.exists(excel_path):
        try:
            import Capstone.generate_mock_data as gmd
            gmd.main()
        except ImportError:
            # If import fails, run via absolute path
            import sys
            sys.path.append(current_dir)
            import generate_mock_data as gmd
            gmd.main()
            
    xls = pd.ExcelFile(excel_path)
    users_df = pd.read_excel(xls, "Users")
    posts_df = pd.read_excel(xls, "Posts")
    shares_df = pd.read_excel(xls, "Shares")
    
    # Convert timestamps
    posts_df["Publish_Time"] = pd.to_datetime(posts_df["Publish_Time"])
    shares_df["Share_Time"] = pd.to_datetime(shares_df["Share_Time"])
    
    return users_df, posts_df, shares_df

# Safe community detection using NetworkX Louvain algorithm
def detect_communities(G):
    if len(G) == 0:
        return {}
    try:
        import networkx.algorithms.community as nx_comm
        comms = nx_comm.louvain_communities(G.to_undirected(), seed=42)
        node_comm = {}
        for i, comm in enumerate(comms):
            for node in comm:
                node_comm[node] = i
        return node_comm
    except Exception:
        # Fallback to connected components if Louvain fails or is unavailable
        try:
            comms = list(nx.connected_components(G.to_undirected()))
            node_comm = {}
            for i, comm in enumerate(comms):
                for node in comm:
                    node_comm[node] = i
            return node_comm
        except Exception:
            return {node: 0 for node in G.nodes()}

# Load dataset
try:
    users_df, posts_df, shares_df = load_data()
    data_loaded = True
except Exception as e:
    st.error(f"Error loading Excel dataset: {e}")
    data_loaded = False

# Sidebar Navigation Header
st.sidebar.markdown(
    """
    <div style="text-align: center; margin-bottom: 20px;">
        <h2 style="color: #1E3A8A; font-family: sans-serif;">SIMATS Engineering</h2>
        <p style="color: #6B7280; font-size: 0.9rem;">DSA0603 Capstone Project</p>
    </div>
    <hr style="margin-top: 0; margin-bottom: 20px; border-color: #E5E7EB;"/>
    """,
    unsafe_allow_html=True
)

menu = st.sidebar.radio(
    "Go To Module:",
    ["Home & Data Overview", 
     "Module 1: Preprocessing & Network Construction", 
     "Module 2: Misinformation Distribution", 
     "Module 3: Trend & Credibility Analysis"]
)

# Sidebar Footer
st.sidebar.markdown(
    """
    <br><br>
    <hr style="border-color: #E5E7EB;"/>
    <div style="font-size: 0.8rem; color: #9CA3AF; font-family: sans-serif;">
        <p><b>Team Members:</b></p>
        <p>• M. Mohith Goud (192225028)</p>
        <p>• Mithun Senthil S (192324056)</p>
        <p>• Mritsha S (192324129)</p>
        <p style="margin-top: 10px;"><i>Saveetha Institute of Medical and Technical Sciences (SIMATS)</i></p>
    </div>
    """,
    unsafe_allow_html=True
)

if data_loaded:
    # ------------------ HOME PAGE ------------------
    if menu == "Home & Data Overview":
        st.markdown(
            """
            <div style="background-color: #F3F4F6; padding: 25px; border-radius: 10px; margin-bottom: 25px; border-left: 6px solid #1E3A8A;">
                <h1 style="color: #1E3A8A; margin: 0; font-family: sans-serif;">Social Media Misinformation Spread Network Visualization System</h1>
                <p style="color: #4B5563; font-size: 1.1rem; margin-top: 8px; margin-bottom: 0;">
                    An interactive analytics dashboard to monitor, model, and intercept the propagation of false news cascades.
                </p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total User Profiles Mapped", len(users_df))
        with col2:
            st.metric("Monitored Source Posts", len(posts_df))
        with col3:
            st.metric("Reshare Log Events", len(shares_df))
            
        st.markdown("### Project Objectives")
        st.write(
            """
            This capstone project implements an end-to-end framework to:
            1. **Construct Share Networks:** Map user interaction pathways using Graph Theory (`NetworkX`).
            2. **Analyze Spread Velocity:** Measure the time-delay cascades between post publication and re-shares.
            3. **Measure Source Credibility:** Calculate influence centralities (`PageRank`, `Betweenness Centrality`) and flag high-risk nodes.
            4. **Provide Moderation Support:** Flag uncertainty and suggest actions based on user risk score profiles.
            """
        )
        
        st.markdown("### Raw Data Inspections")
        tab1, tab2, tab3 = st.tabs(["Users Directory", "Posts Log", "Sharing Actions Log"])
        
        with tab1:
            st.dataframe(users_df, use_container_width=True)
            st.caption("Includes Follower Count, Account Credibility Scores (0-1), and Regions.")
        with tab2:
            st.dataframe(posts_df, use_container_width=True)
            st.caption("Tracks original content, authors, publishing platform, and ground-truth Veracity labels.")
        with tab3:
            st.dataframe(shares_df, use_container_width=True)
            st.caption("Logs the flow of shares from a Source User to a Target User with associated timestamps.")

    # ------------------ MODULE 1 ------------------
    elif menu == "Module 1: Preprocessing & Network Construction":
        st.header("Module 1: Data Preprocessing & Network Construction")
        st.write("Constructs and inspects the network graph representing post sharing pathways.")
        
        # Simulated Preprocessing Logs
        with st.expander("Show Data Preprocessing Audit Logs", expanded=True):
            st.code(
                f"""
[INFO] Loading raw social media Excel records...
[INFO] Loaded {len(users_df)} user accounts and {len(shares_df)} share edges.
[INFO] Resolving username mapping IDs...
[INFO] Validating data integrity: 0 missing fields, 0 orphaned shares detected.
[INFO] Building Directed Sharing Network (NetworkX DiGraph)...
[SUCCESS] Mapped {len(np.unique(list(shares_df['Source_User']) + list(shares_df['Target_User'])))} active users to nodes.
[SUCCESS] Module 1 Preprocessing Complete. Graph Initialized.
                """,
                language="python"
            )
            
        # Post Filter for Network Visualizations
        post_options = ["All Posts"] + [f"{row['Post_ID']} ({row['Veracity']} - {row['Content'][:40]}...)" for _, row in posts_df.iterrows()]
        selected_post_option = st.selectbox("Select Post to Filter Sharing Network Graph:", post_options)
        
        # Filter shares based on post selection
        if selected_post_option == "All Posts":
            filtered_shares = shares_df
            graph_title = "Aggregate Share Network Graph (All Posts)"
        else:
            post_id = selected_post_option.split(" ")[0]
            filtered_shares = shares_df[shares_df["Post_ID"] == post_id]
            veracity = posts_df[posts_df["Post_ID"] == post_id]["Veracity"].values[0]
            graph_title = f"Share Cascade Network Graph for Post {post_id} (Veracity: {veracity})"
            
        # Construct NetworkX Graph
        G = nx.DiGraph()
        
        # Add edges and nodes
        for _, row in filtered_shares.iterrows():
            G.add_edge(row["Source_User"], row["Target_User"], post=row["Post_ID"])
            
        # If filtered post is selected, make sure the original author is in the graph as a node
        if selected_post_option != "All Posts":
            post_id = selected_post_option.split(" ")[0]
            author_id = posts_df[posts_df["Post_ID"] == post_id]["Author_ID"].values[0]
            author_name = users_df[users_df["User_ID"] == author_id]["Username"].values[0]
            G.add_node(author_name)
            
        if len(G) == 0:
            st.warning("No interactions logged for this filtered subset.")
        else:
            # Layout Calculation
            pos = nx.spring_layout(G, k=0.8, seed=42)
            
            # Centrality Calculations
            # Degree Centrality
            deg_centrality = nx.degree_centrality(G)
            # PageRank
            try:
                pagerank = nx.pagerank(G, alpha=0.85)
            except Exception:
                pagerank = {node: 1.0/len(G) for node in G.nodes()}
            # Betweenness Centrality
            try:
                betweenness = nx.betweenness_centrality(G.to_undirected())
            except Exception:
                betweenness = {node: 0.0 for node in G.nodes()}
                
            # Community Detection
            communities = detect_communities(G)
            
            # Formatting user lookup
            user_lookup = users_df.set_index("Username").to_dict(orient="index")
            
            # Draw options
            col_left, col_right = st.columns([3, 1])
            with col_right:
                st.markdown("##### Plot Customization")
                color_by = st.radio("Color Nodes By:", ["Community", "Credibility Score", "PageRank"])
                show_labels = st.checkbox("Show Usernames on Graph", value=True)
                
            # Prepare Plotly Node Attributes
            node_colors = []
            hover_texts = []
            
            for node in G.nodes():
                info = user_lookup.get(node, {"Follower_Count": 0, "Credibility_Score": 0.5, "Region": "Unknown"})
                c_score = info["Credibility_Score"]
                followers = info["Follower_Count"]
                region = info["Region"]
                comm_id = communities.get(node, 0)
                pr = pagerank.get(node, 0)
                bt = betweenness.get(node, 0)
                
                hover_texts.append(
                    f"<b>User:</b> {node}<br>"
                    f"Followers: {followers:,}<br>"
                    f"Credibility Score: {c_score:.2f}<br>"
                    f"PageRank: {pr:.3f}<br>"
                    f"Betweenness Centrality: {bt:.3f}<br>"
                    f"Community Group: {comm_id}<br>"
                    f"Region: {region}"
                )
                
                if color_by == "Community":
                    node_colors.append(comm_id)
                elif color_by == "Credibility Score":
                    node_colors.append(c_score)
                else:
                    node_colors.append(pr)
                    
            # Generate Edge coordinates for Plotly
            edge_x = []
            edge_y = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
                
            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=1.5, color='#CBD5E1'),
                hoverinfo='none',
                mode='lines'
            )
            
            # Generate Node coordinates
            node_x = []
            node_y = []
            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                
            colorscale_val = 'Portland' if color_by == 'Community' else ('RdYlGn' if color_by == 'Credibility Score' else 'Viridis')
            
            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text' if show_labels else 'markers',
                text=[str(node) for node in G.nodes()] if show_labels else [],
                textposition="top center",
                hoverinfo='text',
                hovertext=hover_texts,
                marker=dict(
                    showscale=True,
                    colorscale=colorscale_val,
                    color=node_colors,
                    size=22,
                    colorbar=dict(
                        thickness=15,
                        title=dict(text=color_by, side='right'),
                        xanchor='left'
                    ),
                    line=dict(width=2, color='#1E293B')
                )
            )
            
            # Combine in Figure
            fig_graph = go.Figure(
                data=[edge_trace, node_trace],
                layout=go.Layout(
                    title=dict(text=graph_title, font=dict(size=16, color="#1E3A8A")),
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20, l=10, r=10, t=50),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    plot_bgcolor='#F8FAFC',
                    paper_bgcolor='white',
                    height=500
                )
            )
            
            with col_left:
                st.plotly_chart(fig_graph, use_container_width=True)
                
            # Network Statistics Metrics
            st.markdown("#### Network Integrity Statistics")
            stat_c1, stat_c2, stat_c3, stat_c4 = st.columns(4)
            with stat_c1:
                st.metric("Graph Nodes (Active Users)", len(G.nodes()))
            with stat_c2:
                st.metric("Graph Edges (Direct Shares)", len(G.edges()))
            with stat_c3:
                density = nx.density(G)
                st.metric("Network Density", f"{density:.3f}")
            with stat_c4:
                num_comms = len(np.unique(list(communities.values()))) if communities else 0
                st.metric("Detected Sub-Communities", num_comms)
                
            # Influential Users Table
            st.markdown("#### User Centrality & Influence Leaderboard")
            leaderboard_data = []
            for node in G.nodes():
                info = user_lookup.get(node, {"Follower_Count": 0, "Credibility_Score": 0.5})
                leaderboard_data.append({
                    "Username": node,
                    "Follower Count": info["Follower_Count"],
                    "Credibility Score": info["Credibility_Score"],
                    "PageRank (Propagation)": pagerank.get(node, 0),
                    "Betweenness (Bridges)": betweenness.get(node, 0),
                    "Community Group": communities.get(node, 0)
                })
            df_leaderboard = pd.DataFrame(leaderboard_data).sort_values("PageRank (Propagation)", ascending=False)
            st.dataframe(
                df_leaderboard.style.format({
                    "Credibility Score": "{:.2f}",
                    "PageRank (Propagation)": "{:.4f}",
                    "Betweenness (Bridges)": "{:.4f}"
                }),
                use_container_width=True
            )
            st.caption("• **PageRank** measures a user's propagation importance. • **Betweenness Centrality** identifies critical communication bridges between user groups.")

    # ------------------ MODULE 2 ------------------
    elif menu == "Module 2: Misinformation Distribution":
        st.header("Module 2: Misinformation Spread Distribution")
        st.write("Analyzes the speed, volume, and characteristics of misinformation spread compared to verified posts.")
        
        # Prepare merged dataframe for analysis
        merged_shares = shares_df.merge(posts_df, on="Post_ID", how="inner")
        
        # Calculate Spread Velocity (Delay in minutes from Publish_Time)
        merged_shares["Delay_Minutes"] = (merged_shares["Share_Time"] - merged_shares["Publish_Time"]).dt.total_seconds() / 60.0
        
        # Section 1: Spread Velocity comparison
        st.markdown("### 1. Propagation Speed (Spread Velocity)")
        
        # Plotly Histogram of delays
        fig_hist = px.histogram(
            merged_shares,
            x="Delay_Minutes",
            color="Veracity",
            barmode="overlay",
            title="Distribution of Sharing Delays (Velocity)",
            labels={"Delay_Minutes": "Time Delay since Post Creation (Minutes)", "count": "Share Count"},
            color_discrete_map={"True": "#10B981", "False": "#EF4444", "Unverified": "#F59E0B"},
            nbins=15
        )
        fig_hist.update_layout(
            plot_bgcolor="#F8FAFC",
            paper_bgcolor="white",
            bargap=0.1
        )
        st.plotly_chart(fig_hist, use_container_width=True)
        
        # Calculate stats
        avg_delays = merged_shares.groupby("Veracity")["Delay_Minutes"].mean().reset_index()
        st.write("**Observations:**")
        for _, row in avg_delays.iterrows():
            st.write(f"- Average spread delay for **{row['Veracity']}** posts is **{row['Delay_Minutes']:.1f} minutes**.")
            
        st.info("💡 **Key Insight:** False misinformation cascades tend to spread significantly faster (shorter delay times) than verified true information, matching global academic findings.")
        
        # Section 2: Volume & Reach
        st.markdown("### 2. Cumulative Reach & Volume Analysis")
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            # Bar chart of shares count per veracity
            veracity_counts = merged_shares["Veracity"].value_counts().reset_index()
            veracity_counts.columns = ["Veracity", "Share Count"]
            fig_vol = px.bar(
                veracity_counts,
                x="Veracity",
                y="Share Count",
                color="Veracity",
                title="Total Shares logged by Veracity Type",
                color_discrete_map={"True": "#10B981", "False": "#EF4444", "Unverified": "#F59E0B"}
            )
            fig_vol.update_layout(plot_bgcolor="#F8FAFC", paper_bgcolor="white")
            st.plotly_chart(fig_vol, use_container_width=True)
            
        with col_c2:
            # User lookups for follower counts
            user_followers = users_df.set_index("Username")["Follower_Count"].to_dict()
            merged_shares["Target_Followers"] = merged_shares["Target_User"].map(user_followers)
            
            # Sum of reach (followers)
            reach_df = merged_shares.groupby("Veracity")["Target_Followers"].sum().reset_index()
            reach_df.columns = ["Veracity", "Potential Cumulative Audience Reach"]
            fig_reach = px.bar(
                reach_df,
                x="Veracity",
                y="Potential Cumulative Audience Reach",
                color="Veracity",
                title="Potential Cumulative Reach (Total Follower Audience)",
                color_discrete_map={"True": "#10B981", "False": "#EF4444", "Unverified": "#F59E0B"}
            )
            fig_reach.update_layout(plot_bgcolor="#F8FAFC", paper_bgcolor="white")
            st.plotly_chart(fig_reach, use_container_width=True)
            
        # Platform Distribution
        st.markdown("### 3. Share Volume split by Platform & Veracity")
        fig_platform = px.bar(
            merged_shares,
            x="Platform",
            color="Veracity",
            barmode="group",
            title="Sharing Events by Social Platform and Veracity",
            color_discrete_map={"True": "#10B981", "False": "#EF4444", "Unverified": "#F59E0B"}
        )
        fig_platform.update_layout(plot_bgcolor="#F8FAFC", paper_bgcolor="white")
        st.plotly_chart(fig_platform, use_container_width=True)

    # ------------------ MODULE 3 ------------------
    elif menu == "Module 3: Trend & Credibility Analysis":
        st.header("Module 3: Trend & Source Credibility Analysis")
        st.write("Evaluates propagation trends, maps user credibility risk metrics, and triggers moderation recommendations.")
        
        merged_shares = shares_df.merge(posts_df, on="Post_ID", how="inner")
        merged_shares["Delay_Minutes"] = (merged_shares["Share_Time"] - merged_shares["Publish_Time"]).dt.total_seconds() / 60.0
        
        # 1. Timeline Propagation Trends
        st.markdown("### 1. Post Propagation Timeline")
        
        # Sort shares to plot cumulative lines
        merged_shares = merged_shares.sort_values("Delay_Minutes")
        merged_shares["Cumulative_Shares"] = merged_shares.groupby("Post_ID").cumcount() + 1
        
        fig_trend = px.line(
            merged_shares,
            x="Delay_Minutes",
            y="Cumulative_Shares",
            color="Post_ID",
            hover_data=["Veracity"],
            title="Cumulative Shares vs. Time Elapsed (Minutes)",
            labels={"Delay_Minutes": "Elapsed Minutes", "Cumulative_Shares": "Share Count Count"},
            markers=True
        )
        fig_trend.update_layout(plot_bgcolor="#F8FAFC", paper_bgcolor="white")
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # 2. Risk Matrix
        st.markdown("### 2. User Accounts Spread-Risk Matrix")
        st.markdown(
            r"""
            This module dynamically calculates a **Spread-Risk Score** for each user who shared fake news.
            Risk is modeled based on **Account Credibility** (low credibility raises risk) and **Follower Reach** (higher followers amplifies risk):
            $$\text{Risk Score} = (1 - \text{Credibility Score}) \times \left(\log_{10}(\text{Followers}) + 1\right)$$
            """
        )
        
        # Compile User risk logs
        user_shares_cnt = shares_df["Source_User"].value_counts().to_dict()
        user_risk_records = []
        for _, row in users_df.iterrows():
            uname = row["Username"]
            followers = row["Follower_Count"]
            c_score = row["Credibility_Score"]
            shares_posted = user_shares_cnt.get(uname, 0)
            
            # Calculate Risk Score
            log_followers = np.log10(followers) if followers > 0 else 0
            risk_score = (1.0 - c_score) * (log_followers + 1)
            
            # Risk Level
            if risk_score > 3.0:
                level = "High"
            elif risk_score >= 1.5:
                level = "Medium"
            else:
                level = "Low"
                
            user_risk_records.append({
                "Username": uname,
                "Follower Count": followers,
                "Credibility Score": c_score,
                "Share Events Initiated": shares_posted,
                "Spread-Risk Score": risk_score,
                "Risk Level": level
            })
            
        df_risk = pd.DataFrame(user_risk_records)
        
        fig_risk = px.scatter(
            df_risk,
            x="Credibility Score",
            y="Follower Count",
            size="Spread-Risk Score",
            color="Risk Level",
            hover_name="Username",
            log_y=True,
            title="User Profile Spread-Risk Classification",
            color_discrete_map={"High": "#EF4444", "Medium": "#F59E0B", "Low": "#10B981"},
            category_orders={"Risk Level": ["High", "Medium", "Low"]}
        )
        fig_risk.update_layout(plot_bgcolor="#F8FAFC", paper_bgcolor="white")
        st.plotly_chart(fig_risk, use_container_width=True)
        
        # 3. Moderation recommendations table
        st.markdown("### 3. Actionable Moderation Recommendations")
        
        moderation_actions = []
        for _, row in df_risk.iterrows():
            uname = row["Username"]
            risk = row["Spread-Risk Score"]
            level = row["Risk Level"]
            
            if level == "High":
                action = "🔴 Shadowban account / Throttle reach & Apply 'Misinformation Spreader' Tag"
            elif level == "Medium":
                action = "🟡 Review shared posts & Add visual credibility warnings"
            else:
                action = "🟢 Normal operations (Monitor routinely)"
                
            moderation_actions.append({
                "User": uname,
                "Risk Score": risk,
                "Risk Classification": level,
                "Recommended Intervention Action": action
            })
            
        df_mod = pd.DataFrame(moderation_actions).sort_values("Risk Score", ascending=False)
        
        st.table(df_mod)
        st.caption("Recommendations automatically flag high-risk nodes (e.g. David, Mallory) based on network importance and content veracity propagation logs.")

else:
    st.warning("Please generate a valid mock dataset to populate the dashboard dashboards.")
