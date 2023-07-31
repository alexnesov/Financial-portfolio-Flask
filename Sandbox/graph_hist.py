import plotly.graph_objects as go
import numpy as np
from scipy.stats import norm, kurtosis, skew

def plot_histogram(data, num_bins=30, title='Distribution of Returns from a Normal Distribution (μ=0.05, σ=0.02)', xaxis_title='Returns', yaxis_title='Frequency',
                   mean_value=None, std_dev=None, kurt=None, skewness=None):
    """
    Create a Plotly histogram with a probability density function (PDF) overlay.

    Parameters:
        data (numpy array or list): The data for the histogram.
        num_bins (int): The number of bins for the histogram. Default is 30.
        title (str): Title of the plot. Default is 'Distribution of Returns from a Normal Distribution (μ=0.05, σ=0.02)'.
        xaxis_title (str): Title of the x-axis. Default is 'Returns'.
        yaxis_title (str): Title of the y-axis. Default is 'Frequency'.
        mean_value (float): Mean of the data. If not provided, it will be calculated.
        std_dev (float): Standard deviation of the data. If not provided, it will be calculated.
        kurt (float): Kurtosis of the data. If not provided, it will be calculated.
        skewness (float): Skewness of the data. If not provided, it will be calculated.

    Returns:
        None. Shows the Plotly figure.
    """
    if mean_value is None:
        mean_value = np.mean(data)
    if std_dev is None:
        std_dev = np.std(data)
    if kurt is None:
        kurt = kurtosis(data)
    if skewness is None:
        skewness = skew(data)

    fig = go.Figure()

    # Create the histogram trace
    histogram_trace = go.Histogram(x=data, nbinsx=num_bins, name='Histogram', opacity=0.7)
    fig.add_trace(histogram_trace)

    # Calculate PDF values
    bin_edges = np.histogram_bin_edges(data, bins=num_bins)
    bin_centers = 0.5 * (bin_edges[1:] + bin_edges[:-1])
    pdf_values = norm.pdf(bin_centers, loc=mean_value, scale=std_dev)

    # Normalize PDF values to match the histogram
    pdf_values *= len(data) * np.diff(bin_edges)

    # Create the PDF trace
    pdf_trace = go.Scatter(x=bin_centers, y=pdf_values, mode='lines', line=dict(color='red'), name='PDF')
    fig.add_trace(pdf_trace)

    # Create annotations for mean, standard deviation, kurtosis, and skewness
    annotations = [
        dict(
            x=0.75,
            y=0.95,
            xref='paper',
            yref='paper',
            text=f'Mean: {mean_value:.2f}',
            showarrow=False,
            font=dict(size=12),
        ),
        dict(
            x=0.75,
            y=0.9,
            xref='paper',
            yref='paper',
            text=f'Standard Deviation: {std_dev:.2f}',
            showarrow=False,
            font=dict(size=12),
        ),
        dict(
            x=0.75,
            y=0.85,
            xref='paper',
            yref='paper',
            text=f'Kurtosis: {kurt:.2f}',
            showarrow=False,
            font=dict(size=12),
        ),
        dict(
            x=0.75,
            y=0.8,
            xref='paper',
            yref='paper',
            text=f'Skewness: {skewness:.2f}',
            showarrow=False,
            font=dict(size=12),
        ),
    ]

    # Update layout for better visualization
    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        showlegend=True,
        annotations=annotations,
    )

    fig.show()


if __name__ == '__main__':
    # Generate some example returns data
    np.random.seed(42)
    returns_data = np.random.normal(loc=0.05, scale=0.02, size=1000)

    # Calculate statistics
    mean_value = np.mean(returns_data)
    std_dev = np.std(returns_data)
    kurt = kurtosis(returns_data)
    skewness = skew(returns_data)

    plot_histogram(returns_data, mean_value=mean_value, std_dev=std_dev,
                   kurt=kurt, skewness=skewness)
