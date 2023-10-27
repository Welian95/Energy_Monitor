import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


def round_up_timestamp(ts, freq):
    """
    Round up a timestamp according to the given frequency.

    Parameters
    ----------
    ts : pd.Timestamp
        The timestamp to round up.
    freq : str
        The frequency string compatible with pandas.

    Returns
    -------
    pd.Timestamp
        The rounded-up timestamp.
    """
    return (ts + pd.to_timedelta(freq) - pd.Timedelta(seconds=1)).floor(freq)

def interpolate_columns(df):
    """
    Interpolate the DataFrame columns based on time.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with time index and columns to interpolate.

    Returns
    -------
    pd.DataFrame
        DataFrame with interpolated values.
    """
    interpolated = pd.DataFrame(index=df.index)
    for col in df.columns:
        valid_segments = df[col].dropna()
        if not valid_segments.empty:
            interpolated_segment = valid_segments.interpolate(method='time')
            interpolated[col] = interpolated_segment
    return interpolated

def issue_warnings(df, interpolated, freq=None):
    """
    Issue warnings related to data interpolation.

    Parameters
    ----------
    df : pd.DataFrame
        The original DataFrame.
    interpolated : pd.DataFrame
        The interpolated DataFrame.
    freq : str, optional
        The desired frequency.

    """
    if freq:
        gap_threshold = pd.to_timedelta(freq) * 1
        time_diffs = df.index.to_series().diff()
        if any(time_diffs > gap_threshold):
            st.warning(f"Your Data: {df.columns} has been interpolated. Data gaps larger than {gap_threshold} detected.")
    
    common_indices = df.index.intersection(interpolated.index)
    mse = ((df.loc[common_indices] - interpolated.loc[common_indices]) ** 2).mean()
    
    for value in mse.tolist():
        if value != 0:
            st.warning(f"Your Data has been interpolated. The Mean Squared Error between interpolated and original values is: {mse}")

def interpolate_impute(df, freq=None):
    """
    Interpolates missing values in a DataFrame based on time gaps.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame with timestamps as the index.
    freq : str, optional
        The desired frequency. 

    Returns
    -------
    pd.DataFrame
        The interpolated and filtered DataFrame.
    """
    # Interpolate the DataFrame
    interpolated = interpolate_columns(df)
    
    # Frequency adjustment
    if freq:
        adjusted_start = round_up_timestamp(df.index.min(), freq)
        new_index = pd.date_range(start=adjusted_start, end=df.index.max(), freq=freq)
        combined_index = df.index.union(new_index)
        interpolated = interpolated.reindex(combined_index)
        interpolated = interpolated.loc[new_index]

    # Issue warnings related to interpolation
    issue_warnings(df, interpolated, freq)
    
    return interpolated

def plot_series_with_matplotlib(series, title='Pandas Series Visualization'):
    """
    Visualize a Pandas Series with a datetime index as a line chart with Matplotlib.

    Parameters
    ----------
    series : pd.Series
        The Series to be visualized.
    title : str
        The title of the chart.

    Returns
    -------
    matplotlib.figure.Figure
        A Matplotlib Figure object.
    """
    
    # Erstellen eines Liniendiagramms mit Matplotlib
    fig, ax = plt.subplots()
    ax.plot(series.index, series.values)
    
    # Titel und Achsentitel hinzufügen
    ax.set(title=title, xlabel='Date', ylabel='Value')
    
    return fig




if __name__ == "__main__":
    '''
    Streamlit UI to test the function in development
    '''

    st.title("Test of Imputation.py")

    # Erstellen eines Beispiel-DataFrames zur Überprüfung der Funktion
    example_data = {
        'Leistung (Watt)': [100, None, 180, 200, None, 255, 270],
        'Energie (Wattstunden)': [25, 17, 16, 2, 51, 56, 66],
    }
    example_timestamps = pd.to_datetime(['2023-08-11 10:00:50', '2023-08-11 10:01:30', '2023-08-11 10:03:00', '2023-08-11 10:05:20', '2023-08-11 10:07:05', '2023-08-11 10:08:27', '2023-08-11 10:10:00'])
    example_df = pd.DataFrame(data=example_data, index=example_timestamps)

    frequency = pd.infer_freq(example_df.index)

    st.write("F:", frequency)

    test  = interpolate_impute(example_df, None)
    test

    

    ### Input data
    c1, c2  = st.columns(2)
    c1_fig, c2_fig  = st.columns(2)

    st.subheader("Input DF:")
    st.write(example_df)

    c1, c2  = st.columns(2)
    c1_fig, c2_fig  = st.columns(2)




    freq = '1T'
   

    resampled = example_df.resample(freq).asfreq() #Here you can change the frequenz of the Timestamp

    Exampel_fig = plot_series_with_matplotlib(example_df, title='Original DataFrame Visualization')

    c1_fig.pyplot(Exampel_fig)
    
    c1.subheader (f"Resampeld DF (Frequenz:{freq})")
    c1.write(resampled)

    
    
    ###  Interpolatet df 

    linear_df = interpolate_impute(example_df, "1T")
    
    Interpolate_fig = plot_series_with_matplotlib(linear_df, title='Linear Interpolated DF Visualization')
    

    c2.subheader(f"Linear Interpolated DF (Frequenz:{freq}):")
    c2.write(linear_df)
    c2_fig.pyplot(Interpolate_fig)

