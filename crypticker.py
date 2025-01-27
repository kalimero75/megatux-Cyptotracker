#!/bin/python3
import ccxt
import tkinter as tk
from tkinter import scrolledtext, PhotoImage
import threading
import time
from PIL import Image, ImageTk  # Note: You need to install Pillow if not already installed


# Helper functions
def get_exchange():
    try:
        exchange = ccxt.binance()
        return exchange
    except Exception as e:
        print(f"Error initializing the exchange: {e}")
        return None

def fetch_ticker_data(exchange, symbol):
    try:
        return exchange.fetch_ticker(symbol)
    except Exception as e:
        print(f"Error fetching ticker data for {symbol}: {e}")
        return None

def calculate_volatility(high, low):
    if high and low:
        return (high - low) / low * 100
    return None

def calculate_percent_change(open_price, last_price):
    if open_price and last_price:
        return ((last_price - open_price) / open_price) * 100
    return None

def get_usd_to_eur_rate(exchange):
    try:
        ticker = exchange.fetch_ticker("EUR/USDT")
        return 1 / ticker['last']
    except Exception as e:
        print(f"Error fetching USD/EUR exchange rate: {e}")
        return None

def get_recommendation(current_price, avg_price):
    if current_price < avg_price * 0.99:
        return "Buy"
    elif current_price > avg_price * 1.01:
        return "Sell"
    else:
        return "Hold"

# GUI Implementation
class CryptoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Megatux-Crypticker")

        # Exchange Initialization
        self.exchange = get_exchange()
        if not self.exchange:
            self.show_error("Failed to initialize exchange. Please restart.")
            return

        self.running = False

        # UI Components
        input_frame = tk.Frame(root)
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        # Add logo here, with scaling to maintain proportions
        original_img = Image.open("logo.png")
        width, height = original_img.size
        max_size = 120
        if width > height:
            new_width = max_size
            new_height = int(height * max_size / width)
        else:
            new_height = max_size
            new_width = int(width * max_size / height)
        
        resized_img = original_img.resize((new_width, new_height), Image.LANCZOS)
        self.logo = ImageTk.PhotoImage(resized_img)
        
        logo_label = tk.Label(input_frame, image=self.logo)
        logo_label.image = self.logo  # Keep a reference!
        logo_label.pack(side=tk.LEFT, padx=5)

        tk.Label(input_frame, text="Enter coins (e.g., LTC,BTC,SOL):").pack(side=tk.LEFT, padx=5)
        self.coin_entry = tk.Entry(input_frame, width=30)
        self.coin_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(input_frame, text="Fetch Interval (seconds):").pack(side=tk.LEFT, padx=5)
        self.interval_entry = tk.Entry(input_frame, width=10)
        self.interval_entry.pack(side=tk.LEFT, padx=5)

        self.start_button = tk.Button(input_frame, text="Start", command=self.start_fetching)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(input_frame, text="Stop", command=self.stop_fetching, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.list_coins_button = tk.Button(input_frame, text="List Coins", command=self.list_all_coins)
        self.list_coins_button.pack(side=tk.LEFT, padx=5)

        self.exit_button = tk.Button(input_frame, text="Exit", command=self.exit_app)
        self.exit_button.pack(side=tk.LEFT, padx=5)


        header_frame = tk.Frame(root)
        header_frame.pack(fill=tk.X, padx=5, pady=5)

        headers = ["Symbol", "Price (EUR)", "High (EUR)", "Low (EUR)", "Volatility (%)", "Change (%)", "Trend", "Recommendation"]
        for header in headers:
            tk.Label(header_frame, text=header, width=15, anchor="w", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)

        self.output_area = scrolledtext.ScrolledText(root, wrap=tk.WORD)
        self.output_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Define tags for styling
        self.output_area.tag_config("rising", foreground="green")
        self.output_area.tag_config("falling", foreground="red")
        self.output_area.tag_config("stable", foreground="orange")
        self.output_area.tag_config("buy", foreground="green", font=("Arial", 10, "bold"))
        self.output_area.tag_config("sell", foreground="red", font=("Arial", 10, "bold"))
        self.output_area.tag_config("hold", foreground="orange", font=("Arial", 10, "bold"))

        self.output_area.insert(tk.END, "Welcome to the Crypto Market Tracker!\n")

    def start_fetching(self):
        coins = self.coin_entry.get()
        interval = self.interval_entry.get()

        if not coins:
            self.show_error("Please enter at least one coin.")
            return

        try:
            interval = int(interval)
        except ValueError:
            self.show_error("Invalid interval. Please enter a number.")
            return

        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        self.symbols = [f"{coin.strip().upper()}/USDT" for coin in coins.split(",")]
        self.interval = interval

        self.fetch_thread = threading.Thread(target=self.fetch_data_loop)
        self.fetch_thread.start()

    def stop_fetching(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def exit_app(self):
        self.running = False
        self.root.quit()

    def list_all_coins(self):
        try:
            markets = self.exchange.load_markets()
            symbols = sorted(list(markets.keys()))  # Alphabetically sort
            self.output_area.delete(1.0, tk.END)
            self.output_area.insert(tk.END, "Available Coins (Alphabetically Sorted):\n")

            # Arrange coins in rows and columns for readability
            coins_per_row = 5  # Adjust this number for desired column count
            for i, symbol in enumerate(symbols):
                self.output_area.insert(tk.END, f"{symbol:<15}")  # Fixed-width for alignment
                if (i + 1) % coins_per_row == 0:  # Newline after every coins_per_row items
                    self.output_area.insert(tk.END, "\n")
        except Exception as e:
            self.show_error(f"Error fetching available coins: {e}")

    def fetch_data_loop(self):
        usd_to_eur_rate = get_usd_to_eur_rate(self.exchange)
        if usd_to_eur_rate is None:
            self.show_error("Failed to fetch USD/EUR rate.")
            self.running = False
            return

        while self.running:
            self.output_area.delete(1.0, tk.END)
            self.output_area.insert(tk.END, "Current Market Data:\n")

            for symbol in self.symbols:
                ticker = fetch_ticker_data(self.exchange, symbol)
                if ticker:
                    high = ticker['high']
                    low = ticker['low']
                    open_price = ticker['open']
                    last_price = ticker['last']
                    avg_price = ticker['average']

                    volatility = calculate_volatility(high, low)
                    percent_change = calculate_percent_change(open_price, last_price)

                    if last_price:
                        price_eur = last_price * usd_to_eur_rate
                        high_eur = high * usd_to_eur_rate if high else None
                        low_eur = low * usd_to_eur_rate if low else None

                        trend = "Rising" if percent_change and percent_change > 0 else "Falling" if percent_change and percent_change < 0 else "Stable"
                        recommendation = get_recommendation(price_eur, avg_price * usd_to_eur_rate if avg_price else price_eur)

                        # Add tags for styling
                        trend_tag = "rising" if trend == "Rising" else "falling" if trend == "Falling" else "stable"
                        recommendation_tag = "buy" if recommendation == "Buy" else "sell" if recommendation == "Sell" else "hold"

                        self.output_area.insert(tk.END, f"{symbol:<10} {price_eur:<15.2f} {high_eur:<15.2f} {low_eur:<15.2f} {volatility:<15.2f} {percent_change:<15.2f} ", (trend_tag,))
                        self.output_area.insert(tk.END, f"{trend:<10} ")
                        self.output_area.insert(tk.END, f"{recommendation}\n", (recommendation_tag,))
                    else:
                        self.output_area.insert(tk.END, f"{symbol:<10} Price data not available.\n")
                else:
                    self.output_area.insert(tk.END, f"{symbol:<10} Ticker data not available.\n")

            time.sleep(self.interval)

    def show_error(self, message):
        self.output_area.insert(tk.END, f"Error: {message}\n")

# Main Application
if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoApp(root)
    root.mainloop()
