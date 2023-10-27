from abc import ABC, abstractmethod
import pandas as pd
import os
from io import StringIO




# Define the abstract base class
class DataInterface(ABC):
    """
    Abstract class defining the interface for a data source.
    """

    @abstractmethod
    def get_column_names(self) -> list:
        """
        Get the names of the columns (measurement series labels).

        Returns:
            list: A list containing the names of the columns.
        """
        pass

    @abstractmethod
    def get_time_frequency(self) -> str:
        """
        Get the time frequency (step size between the individual measurement points).

        Returns:
            str: Time frequency as a string.
        """
        pass

    @abstractmethod
    def get_data(self, column_names=None, start_time=None, end_time=None, num_rows=None, ascending=True):
        """
        Retrieves data based on various filtering parameters across multiple dimensions:
        - Columns: By specifying which columns to include.
        - Rows: By limiting the number of rows to fetch. This can be done in ascending or descending order.
        - Time: By providing a time range to filter the timestamps.

        Parameters:
        -----------
        column_names : list of str, optional
            List of column names to include in the output DataFrame. If this parameter is None, 
            all columns will be included. The timestamp column is always included.
        
        start_time : str or pd.Timestamp, optional
            The starting timestamp to filter the data. Only data occurring after this timestamp 
            will be included in the output DataFrame. The timestamp should be in a format 
            that can be converted to a pandas Timestamp object. If None, no start time filter is applied.
            
        end_time : str or pd.Timestamp, optional
            The ending timestamp to filter the data. Only data occurring before this timestamp 
            will be included in the output DataFrame. The timestamp should be in a format 
            that can be converted to a pandas Timestamp object. If None, no end time filter is applied.
        
        num_rows : int, optional
            Number of rows to include in the output DataFrame. If ascending is False, the last 'num_rows' 
            from the CSV file will be read. Otherwise, the first 'num_rows' will be read. 
            If None, all rows will be included.
            
        ascending : bool, optional
            Determines the order in which rows are read from the data source. If True, rows are read in ascending 
            order of their timestamps. If False and 'num_rows' is provided, the last 'num_rows' are read. 
            Default is True.
        
        Returns:
        --------
        pd.DataFrame
            A DataFrame containing the filtered data. The DataFrame's index will be set to the timestamp column.
        """
        pass


    @abstractmethod
    def get_first_timestamp(self) -> pd.Timestamp:
        """
        Get the first timestamp from the data source.

        Returns:
            pd.Timestamp: The first timestamp.
        """
        pass

    @abstractmethod
    def get_last_timestamp(self) -> pd.Timestamp:
        """
        Get the last timestamp from the data source.

        Returns:
            pd.Timestamp: The last timestamp.
        """
        pass



# Concrete implementation for InfluxDB 
class InfluxDB_DataInterface(DataInterface):
    """
    Concrete class implementing the DataInterface for InfluxDB .
    """
    
    def __init__(self):
        """
        Initialize the InfluxDB_DataInterface class.
        """
        pass

       
    
    def get_column_names(self):
        """
        Get the names of the columns from the CSV file.

        """
        pass

    def get_time_frequency(self):
        """
        Get the time frequency (step size between the individual measurement points) from the CSV file.
        
        """
        pass
        
        
    def _read_csv_reverse(self, num_rows):
        """
        Read the last 'num_rows' lines of the CSV file in reverse order.
        
        Returns:
            pd.DataFrame: 
            DataFrame containing the last 'num_rows' lines, read in reverse order.
        """
        pass








    def get_data(self, column_names=None, start_time=None, end_time=None, num_rows=None, ascending=True):
        """
        Retrieves data from the CSV file based on various filtering parameters.
        This function reads the CSV file in chunks to optimize memory usage and can filter the data based on column names, time range, and number of rows. The function also allows for reading the CSV file in ascending or descending order based on the timestamp.
        
        Parameters:
        -----------
        column_names : list of str, optional
            List of column names to include in the output DataFrame. If this parameter is None, all columns in the CSV file will be included. The timestamp column, defined by the 'timestamp_col' attribute, is always included regardless of this parameter.
        
        start_time : str or pd.Timestamp, optional
            The starting timestamp to filter the data. If provided, only the data after this timestamp will be included in the output DataFrame. The string should be in a format that can be converted to a pandas Timestamp object. If this parameter is None, no start time filtering is applied.
            
        end_time : str or pd.Timestamp, optional
            The ending timestamp to filter the data. If provided, only the data before this timestamp will be included in the output DataFrame. The string should be in a format that can be converted to a pandas Timestamp object. If this parameter is None, no end time filtering is applied.
        
        num_rows : int, optional
            The number of rows to include in the output DataFrame. If this parameter is provided along with 'ascending=False', the function will read the last 'num_rows' from the CSV file. Otherwise, it will read the first 'num_rows' from the file. If this parameter is None, all rows will be included.
            
        ascending : bool, optional
            Determines the order in which rows are read from the CSV file. If True, the rows are read in ascending order based on the timestamp. If False and 'num_rows' is provided, the last 'num_rows' are read from the file. Default is True.
        
        Returns:
        --------
        pd.DataFrame
            A DataFrame containing the filtered data from the CSV file. The DataFrame's index will be set to the timestamp column.
        """
        pass

    def get_first_timestamp(self):
        """
        Get the first timestamp from the CSV file.

        Returns:
            pd.Timestamp: The first timestamp.
        """
        pass
        
    def get_last_timestamp(self):
        """
        Get the last timestamp from the CSV file.

        Returns:
            pd.Timestamp: The last timestamp.
        """
        pass
        




# Concrete implementation for CSV files
class CSVDataInterface(DataInterface):
    """
    Concrete class implementing the DataInterface for CSV files.
    """
    csv_file_path = r"example/example_data1.csv"
    
    def __init__(self, filename=csv_file_path, timestamp_col=0, sep=';', decimal=',', encoding=None):
        """
        Initialize the CSVDataInterface class.

        Parameters
        ----------
        filename : str, optional
            The path to the CSV file. The default is defined by `csv_file_path`.
        timestamp_col : int or str, optional
            The index or name of the timestamp column. Default is 0.
        sep : str, optional
            The field delimiter for the CSV file. Default is ';'.
        decimal : str, optional
            The decimal separator. Default is ','.
        encoding : str, optional
            The encoding to use. Default is None.

        """
        self.filename = filename
        self.timestamp_col = timestamp_col
        self.sep = sep
        self.decimal = decimal
        self.encoding = encoding

    def get_column_names(self):
        """
        Get the names of the columns from the CSV file, excluding the timestamp column.
        
        Returns
        -------
        list of str
            A list of column names, excluding the timestamp column.
        
        Raises
        ------
        FileNotFoundError
            If the specified file does not exist.
        """
        with open(self.filename, 'r', encoding=self.encoding) as f:
            header_line = f.readline().strip()
        column_names = header_line.split(self.sep)
        
        timestamp_column = column_names[self.timestamp_col]
        column_names.remove(timestamp_column)
        
        return column_names
    
    def get_time_frequency(self):
        """
        Get the time frequency (step size between the individual measurement points) from the CSV file.
        This method starts by reading a small number of rows and incrementally increases the number of rows until it can infer the frequency.
        
        Returns
        -------
        str
            The inferred frequency of the time series data.

        Raises
        ------
        ValueError
            If the time frequency of the data could not be inferred after a predefined number of attempts.
        """
        frequency = None
        num_rows = 5  # Starting with a smaller number
        max_attempts = 50
        attempts = 0

        while frequency is None and attempts < max_attempts:
            df = pd.read_csv(self.filename, sep=self.sep, decimal=self.decimal, usecols=[self.timestamp_col], nrows=num_rows)
            first_column_name = df.columns[0]
            df[first_column_name] = pd.to_datetime(df[first_column_name])
            frequency = pd.infer_freq(df[first_column_name])
            attempts += 1
            num_rows += 5  # Increment the number of rows for the next attempt
        
        if frequency is None:
            raise ValueError("Could not infer the time frequency of the data.")
        
        return frequency
        
        
    def _read_csv_reverse(self, num_rows):
        """
        Read the last 'num_rows' lines of the CSV file in reverse order.

        Parameters
        ----------
        num_rows : int
            The number of rows to read from the end of the file.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the last 'num_rows' lines, read in reverse order.
        """
        lines = []
        
        with open(self.filename, 'rb') as f:
            f.seek(0, 2)
            position = f.tell()
            line = b''
            
            while position >= 0 and len(lines) < num_rows:
                f.seek(position)
                char = f.read(1)
                position -= 1
                
                if char != b'\n':
                    line = char + line
                else:
                    if line.strip():
                        lines.append(line.decode('utf-8'))
                    line = b''
        
        # Create the DataFrame with header=None
        reverse_df = pd.read_csv(StringIO('\n'.join(lines[::-1])), sep=self.sep, header=None, index_col=self.timestamp_col)
        reverse_df.columns = self.get_column_names()
        
        # Convert the index to datetime
        reverse_df.index = pd.to_datetime(reverse_df.index)
        
        # Manually convert columns to float, replacing the decimal separator
        for col in reverse_df.columns:
            reverse_df[col] = reverse_df[col].apply(lambda x: float(str(x).replace(',', '.')))
        
        return reverse_df









    def get_data(self, column_names=None, start_time=None, end_time=None, num_rows=None, ascending=True):
        """
        Retrieves data from the CSV file based on various filtering parameters.
        This function reads the CSV file in chunks to optimize memory usage and can filter the data based on column names, time range, and number of rows. The function also allows for reading the CSV file in ascending or descending order based on the timestamp.
        
        Parameters:
        -----------
        column_names : list of str, optional
            List of column names to include in the output DataFrame. If this parameter is None, all columns in the CSV file will be included. The timestamp column, defined by the 'timestamp_col' attribute, is always included regardless of this parameter.
        
        start_time : str or pd.Timestamp, optional
            The starting timestamp to filter the data. If provided, only the data after this timestamp will be included in the output DataFrame. The string should be in a format that can be converted to a pandas Timestamp object. If this parameter is None, no start time filtering is applied.
            
        end_time : str or pd.Timestamp, optional
            The ending timestamp to filter the data. If provided, only the data before this timestamp will be included in the output DataFrame. The string should be in a format that can be converted to a pandas Timestamp object. If this parameter is None, no end time filtering is applied.
        
        num_rows : int, optional
            The number of rows to include in the output DataFrame. If this parameter is provided along with 'ascending=False', the function will read the last 'num_rows' from the CSV file. Otherwise, it will read the first 'num_rows' from the file. If this parameter is None, all rows will be included.
            
        ascending : bool, optional
            Determines the order in which rows are read from the CSV file. If True, the rows are read in ascending order based on the timestamp. If False and 'num_rows' is provided, the last 'num_rows' are read from the file. Default is True.
        
        Returns:
        --------
        pd.DataFrame
            A DataFrame containing the filtered data from the CSV file. The DataFrame's index will be set to the timestamp column.
        """
        all_columns = self.get_column_names()
        
        result_data_list = []  # Initialize an empty list to hold the chunks

        if num_rows is not None and not ascending:
            result_data = self._read_csv_reverse(num_rows)
            if column_names:
                result_data = result_data[column_names]

            result_data.index.name = 'timestamp'
        else:
            columns_to_read = [self.timestamp_col] if column_names else None
            
            if column_names:
                #index_shift = self.timestamp_col if isinstance(self.timestamp_col, int) else 0
                columns_to_read += [all_columns.index(col) + 1 for col in column_names if col in all_columns]


                
            
            for chunk in pd.read_csv(self.filename, sep=self.sep, decimal=self.decimal, encoding=self.encoding, usecols=columns_to_read, chunksize=10000):
                first_column_name = chunk.columns[0]
                chunk[first_column_name] = pd.to_datetime(chunk[first_column_name])
                
                
                if start_time or end_time:
                    mask = True
                    if start_time:
                        mask = (chunk[first_column_name] >= pd.Timestamp(start_time))
                    if end_time:
                        mask &= (chunk[first_column_name] <= pd.Timestamp(end_time))
                    chunk = chunk.loc[mask]
                
                result_data_list.append(chunk)
            
            result_data = pd.concat(result_data_list, ignore_index=True)
            result_data = result_data.set_index(first_column_name)
            result_data.index.name = 'timestamp'

        
        return result_data


    def get_first_timestamp(self):
        """
        Get the first timestamp from the CSV file.

        Returns:
        --------
        pd.Timestamp: 
            The first timestamp.
        """
        # Read only the first row from the CSV
        df = pd.read_csv(self.filename, sep=self.sep, decimal=self.decimal, encoding=self.encoding, nrows=1, usecols=[self.timestamp_col])
        # Convert the timestamp to a pandas Timestamp object
        timestamp = pd.Timestamp(df.iloc[0, 0])
        return timestamp

    def get_last_timestamp(self):
        """
        Get the last timestamp from the CSV file.

        Returns:
        --------
        pd.Timestamp: 
            The last timestamp.
        """
        with open(self.filename, 'rb') as f:
            f.seek(-2, 2)  # Jump to the second last byte
            while f.read(1) != b'\n':
                f.seek(-2, 1)
            last_line = f.readline().decode()
        
        last_timestamp = last_line.split(self.sep)[self.timestamp_col]
        return pd.Timestamp(last_timestamp)
















if __name__ == "__main__":
    '''
    Streamlit UI to test the function in development
    '''
    import streamlit as st 
    # Pfad zum Verzeichnis der aktuellen Datei (api.py) ermitteln
    current_file_directory = os.path.dirname(__file__)

    # Pfad zur CSV-Datei relativ zum aktuellen Verzeichnis setzen
    csv_file_path = os.path.join(current_file_directory, '../example/example_data1.csv')


    st.title("Test of API")
    #csv_file_path = r"example/example_data1.csv"
    
    csv_file_path = st.text_input("Path to csv-file:",value=csv_file_path)
    c1,c2,c3,c4 = st.columns (4)
    timestamp_col=c1.number_input("Index of timestamp column:",value=0) 
    sep=c2.text_input("CSV seperator:", value=';') 
    decimal=c3.text_input("Decimal divider:",value=',') 
    encoding=c4.text_input("CSV encoding",value=None)
    if encoding == "None":
        encoding = None

    #Intitilize CSVDataInterface
    csv_interface = CSVDataInterface(csv_file_path, timestamp_col=timestamp_col, sep=sep, decimal=decimal, encoding=encoding)  
    
    # Test the get_column_names method
    "column_names"
    column_names = csv_interface.get_column_names()
    column_names

    "time_freq"
    time_freq = csv_interface.get_time_frequency()
    time_freq

    "data"
    data = csv_interface.get_data()
    data


    # Nur die letzte Zeile der CSV-Datei auslesen
    "last_row"
    last_row = csv_interface.get_data(num_rows=1, ascending=False)
    last_row
 

    # Nur die letzte Zeile der CSV-Datei auslesen
    "first_rows"
    first_rows = csv_interface.get_data(num_rows=3, ascending=True)
    first_rows
    

    # Nur die erste Spalte der CSV-Datei auslesen
    "first_column"
    first_column = csv_interface.get_data(column_names=[column_names[0]])
    first_column

    "filtert_2cols_3rows"
    filtert_2cols_3rows = csv_interface.get_data(column_names=[column_names[1],column_names[3]], num_rows=3)
    filtert_2cols_3rows

    "filtert_by_start_date"
    filtert_by_start_date = csv_interface.get_data(start_time="2020-01-10")
    filtert_by_start_date

    "filtert_by_end_date"
    end_time = pd.Timestamp("2020-01-01 03:00:00")
    filtert_by_end_date = csv_interface.get_data(start_time="2020-01-01 02:20:00" ,end_time=end_time)
    filtert_by_end_date

    "first_timestamp"
    first_timestamp = csv_interface.get_first_timestamp()
    first_timestamp

    "last_timestamp"
    last_timestamp = csv_interface.get_last_timestamp()
    last_timestamp


    f"{column_names[6]}"
    another_test = csv_interface.get_data([column_names[6]])
    st.write(another_test)