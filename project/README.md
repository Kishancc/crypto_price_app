# Crypto Dashboard Project

This project is a cryptocurrency dashboard application that fetches and displays cryptocurrency data using the free CoinGecko API. It includes features such as latest listings, historical price data, and charts.

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. Clone the repository or download the project files.

2. Navigate to the project directory:

```bash
cd path/to/project
```

3. (Optional) It is recommended to create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment:

- On Windows:

```bash
venv\Scripts\activate
```

- On macOS/Linux:

```bash
source venv/bin/activate
```

4. Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Running the Application

Run the main application script:

```bash
streamlit run app.py
```

This will start the Streamlit development server and open the application in your default web browser.

## Configuration

- The application uses the free CoinGecko API and does not require an API key.
- Historical data queries are limited to the past 365 days due to API restrictions.

## Attribution

This project uses data provided by CoinGecko. Please attribute as follows when displaying data:

- Data provided by CoinGecko
- Price data by CoinGecko
- Source: CoinGecko
- Powered by CoinGecko API

## Troubleshooting

- Ensure you have a stable internet connection to fetch data from the API.
- If you encounter errors related to API requests, check the console output for details.

## License

This project is provided as-is without any warranty.
