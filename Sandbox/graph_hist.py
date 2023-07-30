import plotly.graph_objects as go
import numpy as np

def plot_histogram(data, num_bins=30, title='Histogram', xaxis_title='X-axis', yaxis_title='Frequency'):
    """
    Create a Plotly histogram.

    Parameters:
        data (numpy array or list): The data for the histogram.
        num_bins (int): The number of bins for the histogram. Default is 30.
        title (str): Title of the plot. Default is 'Histogram'.
        xaxis_title (str): Title of the x-axis. Default is 'X-axis'.
        yaxis_title (str): Title of the y-axis. Default is 'Frequency'.

    Returns:
        None. Shows the Plotly figure.
    """
    fig = go.Figure()

    # Create the histogram trace
    histogram_trace = go.Histogram(x=data, nbinsx=num_bins, name='Histogram')
    fig.add_trace(histogram_trace)

    # Update layout for better visualization
    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        showlegend=True,
    )

    fig.show()


if __name__ == '__main__':

# Generate some example returns data
    np.random.seed(42)
    returns_data = np.random.normal(loc=0.05, scale=0.02, size=1000)

    print(returns_data)


    plot_histogram(returns_data)