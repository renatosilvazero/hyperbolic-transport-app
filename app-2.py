"""
Hyperbolic Transport Network Analyzer
-------------------------------------
Este aplicativo em Streamlit simula redes de transporte urbano baseadas em
geometria hiperbólica. Ele permite gerar interseções aleatórias, conectar
nós com base em distância hiperbólica, simular tráfego e rotas públicas, e
encontrar os caminhos mais eficientes entre dois pontos para diferentes modais.

Autor: Renato
Licença: CC0 1.0 Universal
"""

import streamlit as st
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# Import functions from the revised_code
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
    """Função para plotar a rede de transporte com destaque para rotas."""
    fig, ax = plt.subplots(figsize=(10, 10))
    pos = {i: (points[i][0], points[i][1]) for i in G.nodes}

    # Desenhar rede base
    nx.draw_networkx_edges(G, pos, edge_color='gray', alpha=0.2, ax=ax)

    # Destacar rotas de transporte público
    public_edges = [(u, v) for u, v, data in G.edges(data=True)
                    if data.get('is_public_route', False)]
    nx.draw_networkx_edges(G, pos, edgelist=public_edges,
                           edge_color='green', alpha=0.5, width=1.5, ax=ax)

    # Desenhar nós
    node_colors = ['blue' if G.nodes[n].get('is_stop') else 'black'
                   for n in G.nodes]
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=20, ax=ax)

    # Destacar caminho, se fornecido
    if path:
        path_edges = list(zip(path[:-1], path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges,
                               edge_color='red', width=2.5, ax=ax)

    ax.set_title("Hyperbolic Transportation Network")
    ax.axis('off')
    return fig

def main():
    """Função principal da aplicação Streamlit."""
    st.set_page_config(page_title="Hyperbolic Transport Network", layout="wide")

    st.title("🚀 Hyperbolic Transportation Network Analyzer")

    # Controles laterais
    with st.sidebar:
        st.header("Configuration")
        num_intersections = st.slider("Number of intersections", 50, 500, 200)
        distance_threshold = st.slider("Connection threshold", 1.0, 5.0, 3.0)
        rush_hour = st.checkbox("Rush Hour Traffic", True)
        num_transport_lines = st.number_input("Public Transport Lines", 1, 10, 3)
        seed = st.number_input("Random Seed", value=42)
        generate_btn = st.button("Generate New Network")

    # Inicialização da rede
    if 'network' not in st.session_state or generate_btn:
        np.random.seed(seed)
        with st.spinner("Generating network..."):
            intersections = generate_random_intersections(num_intersections)
            G = build_hyperbolic_road_network(intersections, distance_threshold)
            G = add_public_transport_routes(G, num_transport_lines)
            G = simulate_traffic(G, rush_hour)
            st.session_state.network = (G, intersections)

    if 'network' in st.session_state:
        G, intersections = st.session_state.network

        # Visualização da rede
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Network Visualization")
            fig = plot_network(G, intersections)
            st.pyplot(fig)

        # Controles de rota
        with col2:
            st.subheader("Path Finding")

            largest_cc = max(nx.connected_components(G), key=len)
            nodes = list(largest_cc)

            if len(nodes) < 2:
                st.warning("A rede gerada possui menos de dois nós conectados. Gere uma nova rede.")
            else:
                source = st.selectbox("Start Node", nodes)
                target = st.selectbox("End Node", nodes)

                if st.button("Find Best Routes"):
                    for mode in ['walk', 'car', 'public']:
                        with st.expander(f"{mode.upper()} Route", expanded=True):
                            try:
                                path = shortest_route(G, source, target, mode)
                                if path:
                                    st.success(f"Route found with {len(path)-1} segments")
                                    fig = plot_network(G, intersections, path)
                                    st.pyplot(fig)
                                    st.write(f"Path nodes: {path}")
                                else:
                                    st.error("No available path for this transport mode")
                            except nx.NetworkXNoPath:
                                st.error(f"No path found between {source} and {target} for {mode} mode.")
                            except Exception as e:
                                st.error(f"An error occurred: {e}")

    # Documentação
    with st.expander("How to use this app"):
        st.markdown("""
        ## Hyperbolic Transportation Network Guide

        1. **Configure Parameters** in the sidebar
        2. Click **Generate New Network** to create a new configuration
        3. Select start and end nodes from the dropdowns
        4. Click **Find Best Routes** to calculate optimal paths

        ### Parameters Explained:
        - **Connection Threshold**: Maximum hyperbolic distance for connections
        - **Rush Hour**: Simulates traffic congestion
        - **Transport Lines**: Number of public transport routes
        """)

if __name__ == "__main__":
    main()
