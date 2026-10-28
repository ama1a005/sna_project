"""Bounded network subgraph visualization."""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

from echochamber.logging_utils import setup_logger

logger = setup_logger("echochamber.visualization.subview")


def plot_community_subgraph(
    di_graph: nx.DiGraph,
    communities: dict[str, list[str]],
    max_nodes: int = 150,
    output_path: Path | str | None = None,
) -> plt.Figure:
    """Plot an induced subgraph of the top communities bounded by max_nodes."""
    selected_nodes: list[str] = []
    node_color_map: dict[str, str] = {}
    palette = ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00", "#ffff33", "#a65628", "#f781bf"]

    for idx, (cid, nodes) in enumerate(communities.items()):
        color = palette[idx % len(palette)]
        for n in nodes:
            if len(selected_nodes) < max_nodes and n in di_graph:
                selected_nodes.append(n)
                node_color_map[n] = color

    sub_g = di_graph.subgraph(selected_nodes)

    fig, ax = plt.subplots(figsize=(10, 8))
    pos = nx.spring_layout(sub_g, seed=42, k=0.3)

    colors = [node_color_map.get(n, "#888888") for n in sub_g.nodes()]
    degrees = [d for _, d in sub_g.degree()]
    node_sizes = [max(50, min(500, d * 30)) for d in degrees]

    nx.draw_networkx_nodes(sub_g, pos, node_color=colors, node_size=node_sizes, alpha=0.85, ax=ax)
    nx.draw_networkx_edges(sub_g, pos, alpha=0.3, edge_color="#666666", arrows=True, arrowsize=8, ax=ax)

    # Label top 10 highest degree nodes
    top_nodes = sorted(sub_g.nodes(), key=lambda n: sub_g.degree(n), reverse=True)[:10]
    labels = {n: n for n in top_nodes}
    nx.draw_networkx_labels(sub_g, pos, labels=labels, font_size=8, font_family="sans-serif", ax=ax)

    ax.set_title(f"Network Communities Subview (N={sub_g.number_of_nodes()}, E={sub_g.number_of_edges()})", fontsize=13, fontweight="bold")
    ax.axis("off")
    plt.tight_layout()

    if output_path:
        dest = Path(output_path).resolve()
        dest.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(dest, dpi=300)
        plt.close(fig)

    return fig
