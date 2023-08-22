# Energy Monitor

## Overview

The Energy Monitor is a comprehensive software solution for analyzing and visualizing energy flows and data. Developed in Python using Streamlit, it allows users to select different system modules, map data, and perform energy analyses.

## Structure

The project follows a modular architecture, subdivided into:

- **Main Script**: Controls the execution of modules and presentation.
- **System Modules**: Specific modules for different technical systems.
- **Data API**: Interface for retrieving data.
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
   \`\`\`
   pip install -r requirements.txt
   \`\`\`
3. **Configure the API**: Adapt the API to your datasets (CSV or Database), or use the "example" folder provided in the repository.
4. **Start the Application**: Simply run the `Main.py` script to start the application.

## Usage

An instruction guide will follow shortly.

## License

Considering this is a project for a scientific thesis and relies on open-source modules, the project is under [MIT License](https://opensource.org/licenses/MIT). It allows for free use, modification, and distribution, with an acknowledgment of the original creation.

## Contact

For any questions or suggestions, please contact via GitHub or email at [westerhorstmann@bode.ms](mailto:westerhorstmann@bode.ms).
