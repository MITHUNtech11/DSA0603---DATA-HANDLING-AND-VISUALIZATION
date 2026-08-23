import math
import os

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Load and prepare the data
if not os.path.exists("volcano_elevation.csv"):
    rows = []
    for y in range(25):
        for x in range(25):
            d1 = ((x - 12) ** 2 + (y - 12) ** 2) / 120
            d2 = ((x - 8) ** 2 + (y - 17) ** 2) / 50
            d3 = ((x - 18) ** 2 + (y - 6) ** 2) / 70
            elevation = 160 * math.exp(-d1) + 30 * math.exp(-d2) - 10 * math.exp(-d3)
            rows.append({"x": x, "y": y, "elevation": round(float(elevation), 2)})

    pd.DataFrame(rows).to_csv("volcano_elevation.csv", index=False)

# Read the generated or provided volcano dataset
df = pd.read_csv("volcano_elevation.csv")

# Pivot from long format (x, y, elevation) to a 2D matrix (grid)
elevation_grid = df.pivot(index='y', columns='x', values='elevation').sort_index(ascending=False).values

# 2. Create the Figure with side-by-side subplots (3D and 2D)
fig = make_subplots(
    rows=1, cols=2,
    specs=[[{"type": "surface"}, {"type": "heatmap"}]],
    subplot_titles=("3D Surface Map", "2D Top-Down Heatmap")
)

# Add 3D Surface
fig.add_trace(
    go.Surface(z=elevation_grid, colorscale='Earth', showscale=False,
               hovertemplate="X: %{x}<br>Y: %{y}<br>Elevation: %{z}m<extra></extra>"),
    row=1, col=1
)

# Add 2D Heatmap
fig.add_trace(
    go.Heatmap(z=elevation_grid, colorscale='Earth',
               hovertemplate="X: %{x}<br>Y: %{y}<br>Elevation: %{z}m<extra></extra>"),
    row=1, col=2
)

# Update layout
fig.update_layout(
    title_text="Maunga Whau (Mt Eden) Volcano Topography",
    height=600,
    width=1100
)

# Adjust 3D axis labels
fig.update_scenes(
    xaxis_title='X Grid',
    yaxis_title='Y Grid',
    zaxis_title='Elevation (m)'
)

fig.write_html("volcano_topography.html")
print("Saved interactive plot to volcano_topography.html")
fig.show()