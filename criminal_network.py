# ============================================================
#  criminal_network.py
#  Drug Criminal Network Mapping using NetworkX + Matplotlib
#  Case: DF-2024-0847
#  Requirements: pip install networkx matplotlib pandas
# ============================================================

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
from collections import defaultdict

# ─────────────────────────────────────────────
# 1. DEFINE SUSPECTS AND THEIR ROLES
# ─────────────────────────────────────────────
suspects = {
    "K-01":  {"name": "Boss",    "role": "kingpin"},
    "D-01":  {"name": "Rahman",  "role": "distributor"},
    "D-02":  {"name": "Anwar",   "role": "distributor"},
    "DL-01": {"name": "Kumar",   "role": "dealer"},
    "DL-02": {"name": "Ravi",    "role": "dealer"},
    "DL-03": {"name": "Syed",    "role": "dealer"},
    "B-01":  {"name": "Buyer1",  "role": "buyer"},
    "B-02":  {"name": "Buyer2",  "role": "buyer"},
    "B-03":  {"name": "Buyer3",  "role": "buyer"},
    "B-04":  {"name": "Buyer4",  "role": "buyer"},
    "U-01":  {"name": "Unknown", "role": "unknown"},
}

# ─────────────────────────────────────────────
# 2. COMMUNICATION EDGES (source, destination, message_count)
# ─────────────────────────────────────────────
edges = [
    ("K-01",  "D-01",  487),
    ("K-01",  "D-02",  241),
    ("D-01",  "DL-01", 312),
    ("D-01",  "DL-02", 198),
    ("D-02",  "DL-03", 156),
    ("D-02",  "U-01",  34),
    ("DL-01", "B-01",  94),
    ("DL-01", "B-02",  87),
    ("DL-02", "B-03",  62),
    ("DL-03", "B-04",  54),
]

# ─────────────────────────────────────────────
# 3. BUILD DIRECTED GRAPH
# ─────────────────────────────────────────────
G = nx.DiGraph()

for node_id, attrs in suspects.items():
    G.add_node(node_id, **attrs)

for src, dst, weight in edges:
    G.add_edge(src, dst, weight=weight)

# ─────────────────────────────────────────────
# 4. CENTRALITY ANALYSIS
# ─────────────────────────────────────────────
betweenness  = nx.betweenness_centrality(G, weight="weight")
in_degree    = dict(G.in_degree())
out_degree   = dict(G.out_degree())
total_degree = dict(G.degree())

print("\n========== FORENSIC NETWORK ANALYSIS ==========")
print(f"Total Suspects : {G.number_of_nodes()}")
print(f"Total Links    : {G.number_of_edges()}")

print("\n--- Betweenness Centrality (higher = more critical node) ---")
for node, score in sorted(betweenness.items(), key=lambda x: -x[1]):
    name = suspects[node]["name"]
    role = suspects[node]["role"].upper()
    print(f"  {node} ({name}) [{role}] : {score:.4f}")

print("\n--- Message Volume per Suspect ---")
df_stats = pd.DataFrame([
    {
        "ID"         : nid,
        "Name"       : suspects[nid]["name"],
        "Role"       : suspects[nid]["role"],
        "Sent"       : sum(G[nid][nb]["weight"] for nb in G.successors(nid)),
        "Received"   : sum(G[nb][nid]["weight"] for nb in G.predecessors(nid)),
        "Centrality" : round(betweenness[nid], 4),
    }
    for nid in G.nodes()
])
df_stats = df_stats.sort_values("Centrality", ascending=False)
print(df_stats.to_string(index=False))
df_stats.to_csv("network_analysis.csv", index=False)
print("\n[+] Saved analysis to network_analysis.csv")

# ─────────────────────────────────────────────
# 5. VISUALIZE THE NETWORK
# ─────────────────────────────────────────────
role_colors = {
    "kingpin"     : "#E24B4A",
    "distributor" : "#378ADD",
    "dealer"      : "#BA7517",
    "buyer"       : "#639922",
    "unknown"     : "#7F77DD",
}

node_colors = [role_colors[G.nodes[n]["role"]] for n in G.nodes()]
node_sizes  = [800 + total_degree[n] * 300 for n in G.nodes()]
edge_widths = [G[u][v]["weight"] / 80 for u, v in G.edges()]
labels      = {n: f"{n}\n({suspects[n]['name']})" for n in G.nodes()}

pos = nx.spring_layout(G, seed=42, k=2.5)

fig, ax = plt.subplots(figsize=(13, 8))
fig.patch.set_facecolor("#0f0f0f")
ax.set_facecolor("#0f0f0f")

# Draw edges
nx.draw_networkx_edges(
    G, pos,
    width=edge_widths,
    edge_color="#aaaaaa",
    alpha=0.5,
    arrows=True,
    arrowsize=18,
    arrowstyle="-|>",
    connectionstyle="arc3,rad=0.1",
    ax=ax,
)

# Draw nodes
nx.draw_networkx_nodes(
    G, pos,
    node_color=node_colors,
    node_size=node_sizes,
    alpha=0.92,
    ax=ax,
)

# Draw labels
nx.draw_networkx_labels(
    G, pos,
    labels=labels,
    font_size=8,
    font_color="white",
    font_weight="bold",
    ax=ax,
)

# Edge weight labels
edge_labels = {(u, v): f"{G[u][v]['weight']} msgs" for u, v in G.edges()}
nx.draw_networkx_edge_labels(
    G, pos,
    edge_labels=edge_labels,
    font_size=7,
    font_color="#cccccc",
    ax=ax,
)

# Legend
legend_handles = [
    mpatches.Patch(color="#E24B4A", label="Kingpin"),
    mpatches.Patch(color="#378ADD", label="Distributor"),
    mpatches.Patch(color="#BA7517", label="Dealer"),
    mpatches.Patch(color="#639922", label="Buyer"),
    mpatches.Patch(color="#7F77DD", label="Unknown"),
]
ax.legend(handles=legend_handles, loc="upper left",
          framealpha=0.3, labelcolor="white",
          facecolor="#1a1a1a", edgecolor="#444444")

ax.set_title(
    "Drug Criminal Network — Case DF-2024-0847\n"
    "Node size = degree | Edge width = message volume",
    color="white", fontsize=13, pad=14,
)
ax.axis("off")
plt.tight_layout()
plt.savefig("network.png", dpi=150, facecolor=fig.get_facecolor())
print("[+] Saved graph to network.png")
plt.show()