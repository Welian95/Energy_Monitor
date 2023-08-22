import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def interpolate_impute(df, freq=None):
    '''
    This function interpolates missing values in a DataFrame based on time gaps, 
    and then filters the result to keep only timestamps that match the specified frequency.
    
    Parameters:
    - df (pd.DataFrame): The input DataFrame with timestamps as the index.
    - freq (str): The desired frequency. Can be one of the following:
        '1S' : 1 second
        '30S' : 30 seconds
        '1T' or '1Min' : 1 minute
        '5T' or '5Min' : 5 minutes
        '15T' or '15Min' : 15 minutes
        '30T' or '30Min' : 30 minutes
        '1H' : 1 hour
      Default is '1T' (1 minute).
    
    Returns:
    - pd.DataFrame: The interpolated and filtered DataFrame.
    '''
    
    def round_up_timestamp(ts, freq):
        """Round up a timestamp according to the given frequency."""
        return (ts + pd.to_timedelta(freq) - pd.Timedelta(seconds=1)).floor(freq)

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
    filtered = interpolated.loc[new_index]

    ### Test of Interpolation

    # Calculate the gap threshold as twice the specified frequency
    gap_threshold = pd.to_timedelta(freq) * 1

    # Check for large data gaps and warn
    time_diffs = df.index.to_series().diff()
    if any(time_diffs > gap_threshold):
        st.warning( f"Your Data: {df.columns} has been interpolated the Data gaps are larger than {gap_threshold} detected.", icon="⚠️")





    # Calculate Mean Squared Error between interpolated and original values for shared timestamps
    common_indices = df.index.intersection(interpolated.index)
    mse = ((df.loc[common_indices] - interpolated.loc[common_indices]) ** 2).mean()
    
    for value in mse.tolist():
        if value != 0:
            st.warning(f"Your Data has been interpolated the Mean Squared Error between interpolated and original values is: {mse}", icon="⚠️")


    return filtered


def plot_series_with_matplotlib(series, title='Pandas Series Visualization'):
    """
    Visualisiert eine Pandas Series mit einem datetime-Index als Liniendiagramm mit Matplotlib.
    
    Parameters:
    - series (pd.Series): Die zu visualisierende Serie.
    - title (str): Titel des Diagramms.
    
    Returns:
    - matplotlib.figure.Figure: Ein Matplotlib-Figure-Objekt.
    """
    
    # Erstellen eines Liniendiagramms mit Matplotlib
    fig, ax = plt.subplots()
    ax.plot(series.index, series.values)
    
    # Titel und Achsentitel hinzufügen
    ax.set(title=title, xlabel='Date', ylabel='Value')
    
    return fig










# Test Funktion if only this skript is running

if __name__ == "__main__":

    st.title("Test of Imputation.py")

    # Erstellen eines Beispiel-DataFrames zur Überprüfung der Funktion
    example_data = {
        'Leistung (Watt)': [100, 150, 180, 200, 230, 255, 270],
        'Energie (Wattstunden)': [25, 17, 16, 2, 51, 56, 66],
    }
    example_timestamps = pd.to_datetime(['2023-08-11 10:00:50', '2023-08-11 10:01:30', '2023-08-11 10:03:00', '2023-08-11 10:05:20', '2023-08-11 10:07:05', '2023-08-11 10:08:27', '2023-08-11 10:10:00'])
    example_df = pd.DataFrame(data=example_data, index=example_timestamps)

    frequency = pd.infer_freq(example_df.index)

    st.write("F:", frequency)

    

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

