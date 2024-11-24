from flask import Flask, request, render_template, redirect, url_for
import json
import plotly.graph_objs as go
import plotly
import networkx as nx

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        json_file = request.files['json_file']
        if json_file:
            data = json.load(json_file)
            graph = create_graph(data)
            graph_json = plotly.utils.PlotlyJSONEncoder().encode(graph)
            return render_template('index.html', graph_json=graph_json)
    return render_template('index.html')

def create_graph(data):
    G = nx.Graph()

    # Assuming JSON structure has 'nodes' and 'edges'
    nodes = data.get('nodes', [])
    edges = data.get('edges', [])

    for node in nodes:
        G.add_node(node['id'], **node['attributes'])

    for edge in edges:
        G.add_edge(edge['source'], edge['target'], **edge['attributes'])

    pos = nx.spring_layout(G)

    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    node_text = []
    for node in G.nodes(data=True):
        x, y = pos[node[0]]
        node_x.append(x)
        node_y.append(y)
        attrs = node[1]
        attr_text = '<br>'.join([f"{key}: {value}" for key, value in attrs.items()])
        node_text.append(f"ID: {node[0]}<br>{attr_text}")

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        text=node_text,
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            size=10,
            color=[],
            colorbar=dict(
                thickness=15,
                title='Attribute',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    # Example: Color nodes based on a specific attribute, e.g., 'group'
    node_color = []
    for node in G.nodes(data=True):
        node_color.append(node[1].get('group', 1))  # Default color if 'group' not present
    node_trace.marker.color = node_color

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='<br>Interactive Graph Visualization',
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20,l=5,r=5,t=40),
                        annotations=[ dict(
                            text="",
                            showarrow=False,
                            xref="paper", yref="paper") ],
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                   )
    return fig

if __name__ == '__main__':
    app.run(debug=True) 