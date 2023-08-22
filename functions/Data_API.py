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

def read_data_from_api(filename,column_names):
    """
    Function to filter a csv-file and return a pandas.dataframe of filtered data with dateime-Index .
    Args:
        filename: str; name of csv file if same directory as this script or the full path to the file; the first column has to be timestampe format like "YYYY-MM-DD MM:SS"
        column_names: list of strings witch contains columnames witch must be in the given csv-file 
    
    Returns:
        A list of column names 

    """
    # Fügt den Namen der ersten Spalte zur Liste der auszuwählenden Spalten hinzu
   

    time_Series = pd.read_csv(filename, usecols=[0])


    data_by_columns = pd.read_csv(filename, usecols=column_names)

    data = pd.concat([time_Series, data_by_columns], axis=1)


    data = data.set_index(data.columns[0])
    data.index = pd.to_datetime(data.index)

    return data


# Test the API
if __name__ == "__main__":
   

    csv_file_path = r"C:/Users/Jwesterhorstmann/Desktop/Masterarbeit/5_Testdata/energiedaten.csv"

    #Test funktions 
    column_names = get_column_names(csv_file_path)
    data = read_data_from_api(csv_file_path, column_names)
    

    
    print("Filepath:")
    print(csv_file_path)
    print("Dataframe:")
    print(data)
    print("Column Names:")
    print(column_names)
