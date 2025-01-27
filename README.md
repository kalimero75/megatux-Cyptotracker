Megatux-Crypticker (Cryptoprice

This is a simple cryptocurrency market tracker built using ccxt for fetching real-time crypto data and tkinter for the graphical user interface (GUI). It tracks multiple cryptocurrencies and displays their price, volatility, and trend analysis in real-time.

Features
Fetches real-time data for cryptocurrencies using Binance exchange via the ccxt library.
Tracks prices, highs, lows, volatility, and percentage changes for selected coins.
Provides trend analysis ("Rising", "Falling", "Stable") based on price changes.
Gives buy, sell, or hold recommendations based on the current price vs average price.
Allows users to list all available coins on Binance and view their data.
Displays data in a user-friendly and interactive GUI.
Supports refreshing data at a user-defined interval.
Installation
Requirements
To run this project, you need to install the following Python libraries:

ccxt
tkinter (usually comes pre-installed with Python)
Pillow (for handling images)
You can install the required libraries by running:


pip install -r requirements.txt
Clone the Repository
Clone the repository to your local machine:



git clone https://github.com/kalimero75/megatux-Cyptotracker.git
cd megatux-Cyptotracker
Install the dependencies:

pip install -r requirements.txt
Run the application:


python crypticker.py

Ensure you have a working internet connection as the app fetches real-time data from the Binance exchange.
Place a logo.png image in the same directory as the script for the app logo to display.
Make sure the Python environment you are using has access to the libraries listed in the requirements.txt.
Usage
Enter Coins: Type the coins you want to track (e.g., BTC, ETH, LTC) in the input box.
Set Fetch Interval: Enter the time in seconds for how often you want to update the market data.
Start Fetching: Click "Start" to begin fetching and displaying the data.
Stop Fetching: Click "Stop" to halt the data fetching process.
List Coins: Click the "List Coins" button to see all available coins on Binance.
