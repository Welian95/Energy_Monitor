# Energy Monitor

## Overview

The Energy Monitor is a comprehensive software solution for analyzing and visualizing energy flows and data. Developed in Python using Streamlit, it allows users to select different system modules, map data, and perform energy analyses.

## Structure

The project follows a modular architecture, subdivided into:

- **Main Script**: Controls the execution of modules and presentation.
- **System Modules**: Specific modules for different technical systems.
- **Data API**: Interface for retrieving data. (See [Data Access API Documentation](#data-access-api-documentation))
- **Presentation and Analysis Layers**: User interfaces for displaying and analyzing data.

## Main Features

- **Data Access**: Support for CSV files and InfluxDB.
- **Modular Analysis**: Various modules for specific techniques like heat pumps, PV modules, etc.
- **Data Imputation**: Interpolates missing data points.
- **Visualization**: Displays energy flows and technology-specific metrics.
- **Analysis Layer**: Enables historical analyses with interactive Plotly charts.

## Current Status

The project is in an advanced stage of development with a clear structure and defined functions. The user interface, modules, and data access layers are implemented. Further improvements and expansions are planned.

## Next Steps

- **Expand Modules**: Additional analysis and visualization functions.
- **Integration of Additional Data Sources**: Support for more databases or APIs.
- **User Interface and UX Optimization**: Enhancing user experience.
- **Testing and Validation**: Implementing quality assurance tests.
- **Documentation and Training**: Creating comprehensive documentation.

## Installation

1. **Download the Repository**: Clone or download the repository to your local machine.
2. **Install Required Modules**: Navigate to the project folder and install all the modules from the `requirements.txt` file by running:
   `pip install -r requirements.txt`
4. **Configure the API**: Adapt the API to your datasets (CSV or Database), or use the "example" folder provided in the repository.
5. **Start the Application**: Simply run the `Main.py` script to start the application.

## Usage

An instruction guide will follow shortly.

## Data Access API Documentation

### Overview

The Data Access API is designed to provide a consistent interface for accessing different data sources. Currently, there is an implementation for accessing CSV files, but the API is extensible and can be adapted for other data sources like SQL databases, InfluxDB, APIs, etc.

### Main Components

- **DataInterface (Abstract Base Class)**: Defines the basic methods that must be provided by concrete implementations.
    - **`get_column_names()`**: Returns the names of the columns.
    - **`get_time_frequency()`**: Returns the time frequency of the measurement data.
    - **`get_data()`**: Reads and filters the data based on various parameters. It allows multi-dimensional filtering based on columns, rows (both forward and backward), and timestamps.
    - **`get_first_timestamp()`**: Returns the first timestamp in the data.
    - **`get_last_timestamp()`**: Returns the last timestamp in the data.
- **CSVDataInterface (Concrete Class)**: Implements the **`DataInterface`** methods for accessing CSV files.

### Usage

1. **Initialization**: Create an instance of the concrete class (e.g., **`CSVDataInterface`**) and specify the file path and the index of the timestamp column.
    
    ```python
    csv_interface = CSVDataInterface("path/to/file.csv", timestamp_col=0)
    ```
    
2. **Retrieve Metadata**: Use methods like **`get_column_names()`** and **`get_time_frequency()`** to get metadata.
    
    ```python
    columns = csv_interface.get_column_names()
    frequency = csv_interface.get_time_frequency()
    ```
    
3. **Read Data**: Use the **`get_data()`** method to retrieve data with various filters.
    
    ```python
    data = csv_interface.get_data(column_names=['Temperature', 'Humidity'], start_time='2022-01-01', end_time='2022-01-10')
    ```
    

### Creating a New Concrete Class

To create a new concrete class that, for example, works on an SQL or InfluxDB database, you need to implement the abstract methods from the **`DataInterface`** class.

#### Example: SQLDataInterface
```python
import sqlite3
import pandas as pd

class SQLDataInterface(DataInterface):
    def __init__(self, db_path, table_name, timestamp_col="timestamp"):
        self.db_path = db_path
        self.table_name = table_name
        self.timestamp_col = timestamp_col

    def get_column_names(self):
        # Implementation here
        pass

    def get_time_frequency(self):
        # Implementation here
        pass

    def get_data(self, column_names=None, start_time=None, end_time=None, num_rows=None, ascending=True):
        # Implementation here
        pass

    def get_first_timestamp(self):
        # Implementation here
        pass

    def get_last_timestamp(self):
        # Implementation here
        pass
```

#### Note
Make sure the get_data() method supports similar filter parameters as the CSVDataInterface class to maintain consistency.
Ensure that timestamps are returned as pd.Timestamp objects to maintain consistency with other implementations.

## License

Considering this is a project for a scientific thesis and relies on open-source modules, the project is under [MIT License](https://opensource.org/licenses/MIT). It allows for free use, modification, and distribution, with an acknowledgment of the original creation.

## Contact

For any questions or suggestions, please contact via GitHub or email at [westerhorstmann@bode.ms](mailto:westerhorstmann@bode.ms).
