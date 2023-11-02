import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


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
    Interpolates missing values in a DataFrame based on time gaps and filters 
    the result to match the specified frequency.
    
    Given a DataFrame with timestamps as its index, this function interpolates 
    missing values considering the time difference. If a frequency is provided, 
    the function also filters the result to keep only timestamps that match the 
    specified frequency. The frequency determines the time intervals for which 
    data points should be present in the output DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame with timestamps as the index. The DataFrame should 
        contain columns with numeric data that can be interpolated.
    freq : str, optional
        The desired frequency to which the DataFrame should be adjusted. Possible 
        values include:
        - '1S' : 1 second
        - '30S' : 30 seconds
        - '1T' or '1Min' : 1 minute
        - '5T' or '5Min' : 5 minutes
        - '15T' or '15Min' : 15 minutes
        - '30T' or '30Min' : 30 minutes
        - '1H' : 1 hour
        - '1D' : 1 day
        - '1W' : 1 week
        - '1M' : 1 month
        If not provided, the function will not adjust the frequency and will not 
        interpolate missing values.

    Returns
    -------
    pd.DataFrame
        The interpolated DataFrame with timestamps adjusted to the desired frequency 
        if provided. Otherwise, the DataFrame is only interpolated without any frequency 
        adjustments.

    Notes
    -----
    The interpolation method used is based on the time difference, which means that it 
    takes into account the duration between timestamps to determine interpolated values. 
    For adjusting the frequency, the function first identifies the adjusted start time 
    for the desired frequency and then creates a new index for the DataFrame. This new 
    index is then merged with the original index to ensure all relevant timestamps are 
    included. After interpolation, timestamps that don't match the desired frequency 
    are filtered out.
    
    Warnings related to interpolation, especially when large gaps exist in the data, 
    are issued by the `issue_warnings` function.

    Examples
    --------
    >>> df = pd.DataFrame({'value': [1, np.nan, 3]}, index=pd.to_datetime(['2023-01-01', '2023-01-03', '2023-01-05']))
    >>> interpolated_df = interpolate_impute(df, freq='1D')
    >>> print(interpolated_df)
                 value
    2023-01-01     1.0
    2023-01-02     2.0
    2023-01-03     2.5
    2023-01-04     3.0
    2023-01-05     3.0

    """
    
    if freq != None:
        # Adjust the start time to the next full time unit according to the given frequency
        adjusted_start = round_up_timestamp(df.index.min(), freq)
        
        # Create a new index with the desired frequency, starting from the adjusted start time
        new_index = pd.date_range(start=adjusted_start, end=df.index.max(), freq=freq)
        
        # Merge the original index with the new index
        combined_index = df.index.union(new_index)
        
        # Reindex the DataFrame with the combined index
        df_reindexed = df.reindex(combined_index)
        
        # Interpolate considering the time difference
        interpolated = df_reindexed.interpolate(method='time')

        # Filter the DataFrame to keep only timestamps that match the frequency
        interpolated = interpolated.loc[new_index]

    else:
        interpolated = df

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

    with st.expander("test: round_up_timestamp"):

        ts = pd.Timestamp("2022-01-15 08:15:32")

        freq = str(st.text_input("Frequenz:" , value="1S" , help="Can be '1d' for one day, '1H' for Hour, '1T' for Minute or '10S' for 10 Sekonds"))
        try:
            rounded_ts = round_up_timestamp(ts, freq)

            st.write(f"Originaler Zeitstempel: {ts}")
            st.success(f"Aufgerundeter Zeitstempel: {rounded_ts}")
            st.write("Erwarteter Wert (für 1H): 2022-01-15 09:00:00")
        except Exception as error:
            st.warning(f'Function failed {error}')

    with st.expander("test: interpolate_impute"):
        data = {
        'A': [1, 2, np.nan, 7, 4, np.nan, 9],
        'B': [2, np.nan, 6, np.nan, np.nan, 12, 14]
        }
        
        

        c1_1,c1_2 = st.columns(2)

        #freq = str(st.text_input("Frequenz:" , value="1D" , help="Can be '1d' for one day, '1H' for Hour, '1T' for Minute or '10S' for 10 Sekonds"))
        
        interval = c1_1.selectbox("Time interval", options= ["T", None,"d", "H", "S"], help="Can be '1d' for one day, '1H' for Hour, '1T' for Minute or '10S' for 10 Sekonds") 
        number = c1_2.number_input("Number interval ", value= 3,step=1)
        
        if interval != None:
            freq = str(number) + interval 
        else:
            freq = None

        st.write(f'Frequnz:{freq}')

        c2_1,c2_2 = st.columns(2)
        c3_1,c3_2 = st.columns(2)

        idx = pd.date_range("2022-01-01 08:00:00", periods=7, freq='5T')
        #pd.Timestamp("2022-01-15 08:15:32")
        df2 = pd.DataFrame(data, index=idx)
        c2_1.write("Originaler DataFrame:")
        df2 = c2_1.data_editor(df2)
        c3_1.pyplot(plot_series_with_matplotlib(df2))
        


        interpolated_df = interpolate_impute(df2, freq=freq)
        
        c2_2.write("Interpolierter DataFrame:")
        c2_2.write(interpolated_df)
        c3_2.pyplot(plot_series_with_matplotlib(interpolated_df))