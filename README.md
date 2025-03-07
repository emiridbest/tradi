# Tradi

A Python-based trading strategy analysis tool that combines technical analysis with AI-powered insights.


## Features

- Moving Average Crossover Strategy
- Multiple Timeframe Analysis (1M to 5Y)
- AI-Powered Trading Insights
- Support for Stocks and Cryptocurrencies
- Interactive Charts
- Automated Trade Signal Generation

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/tradi.git
cd tradi
```

2. Create a virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:
```properties
OPENAI_API_KEY=your_api_key_here
```

## Usage

1. Start the Streamlit app:
```bash
streamlit run code/main.py
```

2. Enter a stock symbol (e.g., NVDA) or cryptocurrency (BTC, ETH, DOGE)
3. Select your preferred timeframe
4. Click "Analyze" to generate insights

## Project Structure

```
tradi/
│
├── code/
│   ├── main.py                    # Main application
│   ├── momentum_trading_strategy.py # Trading strategy implementation
│   └── README.md                  # Code documentation
│
├── results/                      # Trading results output
├── venv/                         # Virtual environment
├── .env***                       # Environment variables
├── requirements.txt              # Project dependencies
└── README.md                     # Project documentation
```

## Trading Strategies

### Moving Average Crossover
- Short-term MA (5, 10, 20, 50 days)
- Long-term MA (20, 50, 100, 200 days)
- Signal Generation:
  - Buy when short MA crosses above long MA
  - Sell when short MA crosses below long MA

## Dependencies

- Python 3.12+
- pandas
- yfinance
- streamlit
- matplotlib
- openai
- python-dotenv

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

MIT License - See LICENSE file for details

## Disclaimer

This tool is for educational purposes only. Always conduct your own research and consider consulting with a financial advisor before making investment decisions.