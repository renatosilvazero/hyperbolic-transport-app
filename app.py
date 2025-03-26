import streamlit as st
import numpy as np
import random
import networkx as nx
import matplotlib.pyplot as plt

from revised_code import (
    SPEEDS,
    hyperbolic_distance,
    adjusted_weight,
    generate_random_intersections,
    assign_modes,
    build_hyperbolic_road_network,
    simulate_traffic,
    add_public_transport_routes,
    shortest_route
)

def plot_network(G, points, path=None):
    """Plot the transportation network with optional path highlight and legend."""
    fig, ax = plt.subplots(figsize=(10, 10))
    pos = {i: (points[i][0], points[i][1]) for i in G.nodes}
    
    # Base network edges with improved visibility
    nx.draw_networkx_edges(G, pos, edge_color='gray', alpha=0.3, ax=ax)
    
    # Highlight public transport routes
    public_edges = [(u, v) for u, v, data in G.edges(data=True) if data.get('is_public_route', False)]
    nx.draw_networkx_edges(G, pos, edgelist=public_edges, edge_color='green', alpha=0.7, width=2.5, ax=ax)
    
    # Draw nodes with mode-based coloring
    node_colors = ['blue' if G.nodes[n].get('is_stop') else 'black' for n in G.nodes]
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=10, ax=ax)
    
    # Highlight path if provided
    if path:
        path_edges = list(zip(path[:-1], path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='red', width=2.5, ax=ax)
    
    # Legend annotations
    legend_text = [
        ("Public Transport (Green)", 'green'),
        ("Main Roads (Gray)", 'gray'),
        ("Optimal Path (Red)", 'red')
    ]
    
    for i, (text, color) in enumerate(legend_text):
        ax.text(0.05, 0.95 - (i*0.05), text, transform=ax.transAxes,
                color=color, fontsize=9, backgroundcolor='white')
    
    ax.set_title("Hyperbolic Transportation Network")
    ax.axis('off')
    plt.tight_layout()
    return fig

@st.cache_data
def generate_network(num_intersections, distance_threshold, rush_hour, num_transport_lines, seed):
    """Generate and cache network with given parameters."""
    np.random.seed(seed)
    random.seed(seed)
    intersections = generate_random_intersections(num_intersections)
    G = build_hyperbolic_road_network(intersections, distance_threshold)
    G = add_public_transport_routes(G, num_transport_lines)
    G = simulate_traffic(G, rush_hour)
    return G, intersections

def display_route(G, intersections, source, target, mode):
    """Handle route calculation and display for a single transport mode."""
    try:
        path = shortest_route(G, source, target, mode)
        
        if not path:
            st.error(f"No available {mode} route (empty path)")
            return  # Early return on empty path
            
        st.success(f"Found {mode} route: {len(path)-1} segments")
        fig = plot_network(G, intersections, path)
        st.pyplot(fig)
        
        with st.expander("Show node sequence"):
            st.write(path)
            
    except nx.NetworkXNoPath:
        st.error(f"No {mode} path exists between these nodes")
    except KeyError as e:
        st.error(f"Invalid node in path: {str(e)}")
    except Exception as e:
        st.error(f"Critical error in {mode} routing: {str(e)}")
        raise  # Re-raise for debugging

def main():
    """Main entry point for the Streamlit app."""
    st.set_page_config(page_title="Hyperbolic Transport Network", layout="wide")
    st.title("🚀 Hyperbolic Transportation Network Analyzer")
    
    # Sidebar controls
    with st.sidebar:
        st.header("Configuration")
        num_intersections = st.slider("Number of intersections", 50, 500, 200)
        distance_threshold = st.slider("Connection threshold", 1.0, 5.0, 3.0)
        rush_hour = st.checkbox("Rush Hour Traffic", True)
        num_transport_lines = st.number_input("Public Transport Lines", 1, 10, 3)
        seed = st.number_input("Random Seed", value=42)
        generate_btn = st.button("Generate New Network")
    
    # Network generation with validation
    if generate_btn or 'network' not in st.session_state:
        with st.spinner("Generating transportation network..."):
            try:
                G, intersections = generate_network(
                    num_intersections, distance_threshold,
                    rush_hour, num_transport_lines, seed
                )
                st.session_state.network = (G, intersections)
            except Exception as e:
                st.error(f"Network generation failed: {str(e)}")
                return
    
    if 'network' in st.session_state:
        G, intersections = st.session_state.network
        largest_cc = max(nx.connected_components(G), key=len)
        nodes = list(largest_cc)
        
        # Main interface columns
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Network Visualization")
            fig = plot_network(G, intersections)
            st.pyplot(fig)
        
        with col2:
            st.subheader("Path Finding")
            
            if len(nodes) < 2:
                st.warning("Network too fragmented - generate new network")
            else:
                source = st.selectbox("Start Node", nodes, key='source')
                target = st.selectbox("End Node", nodes, key='target')
                
                if st.button("Calculate Optimal Routes"):
                    # Validate node selection
                    if source not in G or target not in G:
                        st.error("Selected nodes no longer exist in network")
                        return
                        
                    for mode in ['walk', 'car', 'public']:
                        with st.expander(f"{mode.upper()} Route", expanded=True):
                            display_route(G, intersections, source, target, mode)
    
    # Documentation section
    with st.expander("📖 User Guide"):
        st.markdown("""
        ## Transportation Network Simulation Guide
        
        1. **Configure Parameters** in the sidebar
        2. Click **Generate New Network** when changing parameters
        3. Select start/end nodes from the largest connected component
        4. Click **Calculate Optimal Routes** to compare modes
        
        ### Key Features:
        - **Hyperbolic Geometry**: Efficient long-distance connections
        - **Multi-Modal Routing**: Compare walking, driving, and public transit
        - **Dynamic Simulation**: Rush hour traffic effects
        - **Persistent Networks**: Parameters preserved between runs
        """)

if __name__ == "__main__":
    main()
