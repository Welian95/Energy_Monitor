# Function to read data from the simulation CSV and return a Pandas DataFrame
import pandas as pd

def get_column_names(filename):
    """
    Function to filter and return column names as a list from a csv-file.
    Args:
        filename: name of csv file if same directory as this script or the full path to the file 
    
    Returns:
        A list of column names 
    """
    
    df = pd.read_csv(filename, nrows=0)

    column_names = df.columns.tolist()


    #Remove the timestamp, because it is taken over automatically with "get_data_from_api" function
    column_names= column_names[1:]
    
    return column_names


def read_data_from_csv_with_time_range(filename, column_names=None, start_time=None, end_time=None, chunksize=10000):
    """
    Function to filter a csv-file and return a pandas DataFrame of filtered data within a specific time range.
    Reads data in chunks for efficiency. If start_time and end_time are None, all data is read.
    If column_names is None, all columns are read.

    Args:
        filename (str): Name of the CSV file if it is in the same directory as this script or the full path to the file.
                        The first column must be in timestamp format like "YYYY-MM-DD HH:MM:SS".
        column_names (list, optional): List of strings containing column names that must be in the given CSV file.
                                       Default is None (all columns are read).
        start_time (str, optional): Start time of the range in format "YYYY-MM-DD HH:MM:SS". Default is None.
        end_time (str, optional): End time of the range in format "YYYY-MM-DD HH:MM:SS". Default is None.
        chunksize (int): The number of rows per chunk. Default is 10000.

    Returns:
        pandas.DataFrame: DataFrame containing the filtered data with a datetime index. (filtered by column names and time-range)
    """
    # Get all column names from the file
    all_columns = get_column_names(filename)

    # Include the position of the timestamp column and the selected columns if column_names is not None
    columns_to_read = [0] if column_names is None else [0] + [all_columns.index(col) + 1 for col in column_names]

    # Convert start and end time to pandas Timestamp if not None
    if start_time:
        start_time = pd.Timestamp(start_time)
    if end_time:
        end_time = pd.Timestamp(end_time)

    # Initialize an empty DataFrame to hold the result
    result_data = pd.DataFrame()

    # Read data in chunks
    for chunk in pd.read_csv(filename, usecols=columns_to_read if column_names else None, chunksize=chunksize):
        # Convert the timestamp column to datetime
        chunk.columns.values[0] = 'timestamp'
        chunk['timestamp'] = pd.to_datetime(chunk['timestamp'])

        # Filter data by the time range if start_time and end_time are not None
        if start_time and end_time:
            mask = (chunk['timestamp'] >= start_time) & (chunk['timestamp'] <= end_time)
            chunk = chunk.loc[mask]

        # Append the filtered chunk to the result
        result_data = pd.concat([result_data, chunk], ignore_index=True)

    result_data = result_data.set_index('timestamp')

    return result_data





# Test the API
if __name__ == "__main__":
    import streamlit as st

    def display_checkboxes(elements):
        """
        Display checkboxes for a given list of elements and return a list of selected elements.

        Args:
            elements (list): A list of elements to be displayed with checkboxes.

        Returns:
            list: A list containing the elements that have been selected.
        """
        selected_elements = []
        st.title("Select Elements from the List")

        # Iterate through the elements and create a checkbox for each
        for element in elements:
            is_selected = st.checkbox(element)  # Create a checkbox
            if is_selected:
                selected_elements.append(element)  # If checked, add the element to the selected list

        # Display the selected elements
        st.write("You have selected:")
        st.write(selected_elements)

        return selected_elements

    st.title("Test of API")
   
    
    csv_file_path = r"C:/Users/Jwesterhorstmann/Desktop/Masterarbeit/Energy_monitor/example/energy_daten.csv"

    st.text_input("Path to csv-file:",value=csv_file_path)

    #Test funktions 
    column_names = get_column_names(csv_file_path)
    data = read_data_from_api(csv_file_path, column_names)
    
    
    st.write("Dataframe:")
    st.write(data)
    
    st.write("Column Names:")
    st.write(column_names)

    #Test selction 

    choosen_columns = display_checkboxes(column_names)
    start_time = st.text_input("Start:", value="2022-01-02" )
    end_time = st.text_input("End::", value="2022-01-05" )
  

    selected_data = read_data_from_csv_with_time_range(csv_file_path, choosen_columns, start_time, end_time)


    st.write (f"Selected Dataframe; Columns:{str (choosen_columns)}, Start: {start_time}, End: {end_time}")

    st.write (selected_data)

