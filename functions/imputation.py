import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


def interpolate_impute(df, freq=None):
    '''
    This function interpolates missing values in a DataFrame based on time gaps, 
    only for existing data points. It then filters the result to keep only timestamps 
    that match the specified frequency. Any cell containing "None" will not be interpolated.
    
    If freq is None, the original DataFrame index will be preserved.
    
    Parameters:
    - df (pd.DataFrame): The input DataFrame with timestamps as the index.
    - freq (str, optional): The desired frequency. The options are same as in the original function.
    
    Returns:
    - pd.DataFrame: The interpolated and filtered DataFrame.
    '''
    
    def round_up_timestamp(ts, freq):
        """Round up a timestamp according to the given frequency."""
        return (ts + pd.to_timedelta(freq) - pd.Timedelta(seconds=1)).floor(freq)
    
    # Initialize DataFrame to hold the interpolated values
    interpolated = pd.DataFrame(index=df.index)
    
    # Loop through each column and interpolate only existing data points
    for col in df.columns:
        # Drop NaN values to form valid segments for interpolation
        valid_segments = df[col].dropna()
        if not valid_segments.empty:
            # Interpolate considering the time difference for each valid segment
            interpolated_segment = valid_segments.interpolate(method='time')
            # Fill the corresponding column in the interpolated DataFrame
            interpolated[col] = interpolated_segment

    if freq:
        # Adjust the start time to the next full time unit according to the given frequency
        adjusted_start = round_up_timestamp(df.index.min(), freq)
        
        # Create a new index with the desired frequency, starting from the adjusted start time
        new_index = pd.date_range(start=adjusted_start, end=df.index.max(), freq=freq)
        
        # Merge the original index with the new index
        combined_index = df.index.union(new_index)
        
        # Reindex the DataFrame with the combined index
        interpolated = interpolated.reindex(combined_index)

        # Filter the DataFrame to keep only timestamps that match the frequency
        interpolated = interpolated.loc[new_index]
    
    # Calculate the gap threshold as twice the specified frequency
    if freq:
        gap_threshold = pd.to_timedelta(freq) * 1
        time_diffs = df.index.to_series().diff()
        if any(time_diffs > gap_threshold):
            st.warning(f"Your Data: {df.columns} has been interpolated. Data gaps larger than {gap_threshold} detected.", icon="⚠️")
    
    # Calculate Mean Squared Error between interpolated and original values for shared timestamps
    common_indices = df.index.intersection(interpolated.index)
    mse = ((df.loc[common_indices] - interpolated.loc[common_indices]) ** 2).mean()
    
    for value in mse.tolist():
        if value != 0:
            st.warning(f"Your Data has been interpolated. The Mean Squared Error between interpolated and original values is: {mse}", icon="⚠️")
    
    return interpolated




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

