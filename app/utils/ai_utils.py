import os
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)
def generate_chart_analysis(symbol: str, signals: pd.DataFrame) -> str:
    """Generate analysis of trading signals using OpenAI."""
    try:


        # Calculate metrics
        total_trades = len(signals[signals['positions'] != 0])
        buy_signals = len(signals[signals['positions'] == 1.0])
        sell_signals = len(signals[signals['positions'] == -1.0])
        price_change = ((signals['price'].iloc[-1] - signals['price'].iloc[0]) / 
                       signals['price'].iloc[0] * 100)

        prompt = f"""
        Analyze this trading data for {symbol}:
        - Total number of trades: {total_trades}
        - Buy signals: {buy_signals}
        - Sell signals: {sell_signals}
        - Price change: {price_change:.2f}%
        - Current price trend relative to moving averages: 
          Last price: {signals['price'].iloc[-1]:.2f}
          Short MA: {signals['short_mavg'].iloc[-1]:.2f}
          Long MA: {signals['long_mavg'].iloc[-1]:.2f}

        Provide a brief trading analysis and recommendation.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {"role": "system", "content": "You are a professional stock market analyst."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Could not generate analysis: {str(e)}"
    

