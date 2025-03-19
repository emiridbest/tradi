import os
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
import json
import asyncio
import aiohttp
from datetime import datetime
from injective_functions.factory import InjectiveClientFactory
from injective_functions.utils.function_helper import (
    FunctionSchemaLoader,
    FunctionExecutor,
)

load_dotenv()

class InjectiveChatAgent:
    def __init__(self):
        # Load environment variables
        load_dotenv()

        # Get API key from environment variable
        self.api_key = os.getenv("OPENAI_API_KEY")  

        if not self.api_key:
            raise ValueError(
                "No OpenAI API key found. Please set the OPENAI_API_KEY environment variable."
            )

        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)

        # Initialize conversation histories
        self.conversations = {}
        # Initialize token context
        self.token_contexts = {}
        # Initialize injective agents
        self.agents = {}
        schema_paths = [
            "./injective_functions/account/account_schema.json",
            "./injective_functions/auction/auction_schema.json",
            "./injective_functions/authz/authz_schema.json",
            "./injective_functions/bank/bank_schema.json",
            "./injective_functions/exchange/exchange_schema.json",
            "./injective_functions/staking/staking_schema.json",
            "./injective_functions/token_factory/token_factory_schema.json",
            "./injective_functions/utils/utils_schema.json",
        ]
        self.function_schemas = FunctionSchemaLoader.load_schemas(schema_paths)

    def generate_chart_analysis(self, symbol: str, signals: pd.DataFrame) -> str:
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

            response = self.client.chat.completions.create(
                model="gpt-4o-mini", 
                messages=[
                    {"role": "system", "content": "You are a professional stock market analyst."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Could not generate analysis: {str(e)}"

    def add_token_context(self, session_id: str, symbol: str, analysis_result: str):
        """Add token analysis context to the session"""
        self.token_contexts[session_id] = {
            "symbol": symbol,
            "analysis": analysis_result,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add the analysis to the conversation history
        if session_id not in self.conversations:
            self.conversations[session_id] = []
            
        # Add system message with the analysis context
        self.conversations[session_id].append({
            "role": "system", 
            "content": f"Initial analysis for {symbol}: {analysis_result}\n\nThe user may ask follow-up questions about {symbol}."
        })

    async def initialize_agent(
        self, agent_id: str, private_key: str, environment: str = "testnet"
    ) -> None:
        """Initialize Injective clients if they don't exist"""
        private_key = os.getenv("INJECTIVE_PRIVATE_KEY")
        environment = os.getenv("INJECTIVE_ENVIRONMENT")

        print(private_key)
        print(environment)
        if agent_id not in self.agents:
            clients = await InjectiveClientFactory.create_all(
                private_key=private_key, network_type=environment
            )
            self.agents[agent_id] = clients

    async def execute_function(
        self, function_name: str, arguments: dict, agent_id: str
    ) -> dict:
        """Execute the appropriate Injective function with error handling"""
        try:
            # Get the client dictionary for this agent
            clients = self.agents.get(agent_id)
            if not clients:
                return {
                    "error": "Agent not initialized. Please provide valid credentials."
                }

            return await FunctionExecutor.execute_function(
                clients=clients, function_name=function_name, arguments=arguments
            )

        except Exception as e:
            return {
                "error": str(e),
                "success": False,
                "details": {"function": function_name, "arguments": arguments},
            }

    async def get_response(
        self,
        message,
        session_id="default",
        private_key=None,
        agent_id=None,
        environment="testnet",
    ):
        """Get response from OpenAI API."""
        await self.initialize_agent(
            agent_id=agent_id, private_key=private_key, environment=environment
        )
        print("initialized agents")
        try:
            # Initialize conversation history for new sessions
            if session_id not in self.conversations:
                self.conversations[session_id] = []

            # Add user message to conversation history
            self.conversations[session_id].append({"role": "user", "content": message})

            # Build system message with token context if available
            system_message = """You are a helpful AI assistant on Injective Chain. `{self.conversations[session_id]}` is the conversation history for this session.
            You will be helping me make decisions on the analysis and predictions made by the other agent as it will be passed onto you.
            You will be answering all things related to injective chain, and help out with
            on-chain functions.
            
            When handling market IDs, always use these standardized formats:
            - For BTC perpetual: "BTC/USDT PERP" maps to "btcusdt-perp"
            - For ETH perpetual: "ETH/USDT PERP" maps to "ethusdt-perp"
            
            When users mention markets:
            1. If they use casual terms like "Bitcoin perpetual" or "BTC perp", interpret it as "BTC/USDT PERP"
            2. If they mention "Ethereum futures" or "ETH perpetual", interpret it as "ETH/USDT PERP"
            3. Always use the standardized format in your responses
            
            Before performing any action:
            1. Describe what you're about to do
            2. Ask for explicit confirmation
            3. Only proceed after receiving a "yes"
            
            When making function calls:
            1. Convert the standardized format (e.g., "BTC/USDT PERP") to the internal format (e.g., "btcusdt-perp")
            2. When displaying results to users, convert back to the standard format
            3. Always confirm before executing any functions
            
            For general questions, provide informative responses.
            When users want to perform actions, describe the action and ask for confirmation but for fetching data you dont have to ask for confirmation."""
            
            # Add token context if available
            token_context = self.token_contexts.get(session_id)
            if token_context:
                system_message += f"\n\nRecently analyzed token: {token_context['symbol']}\nAnalysis summary: {token_context['analysis']}\n\nRefer to this analysis when the user asks about {token_context['symbol']} and suggest trading actions based on this analysis."

            # Get response from OpenAI
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": system_message,
                    }
                ]
                + self.conversations[session_id],
                functions=self.function_schemas,
                function_call="auto",
                max_tokens=2000,
                temperature=0.7,
            )

            response_message = response.choices[0].message
            print(response_message)
            # Handle function calling
            if (
                hasattr(response_message, "function_call")
                and response_message.function_call
            ):
                # Extract function details
                function_name = response_message.function_call.name
                function_args = json.loads(response_message.function_call.arguments)
                # Execute the function
                function_response = await self.execute_function(
                    function_name, function_args, agent_id
                )

                # Add function call and response to conversation
                self.conversations[session_id].append(
                    {
                        "role": "assistant",
                        "content": None,
                        "function_call": {
                            "name": function_name,
                            "arguments": json.dumps(function_args),
                        },
                    }
                )

                self.conversations[session_id].append(
                    {
                        "role": "function",
                        "name": function_name,
                        "content": json.dumps(function_response),
                    }
                )

                # Get final response
                second_response = await asyncio.to_thread(
                    self.client.chat.completions.create,
                    model="gpt-4-turbo-preview",
                    messages=self.conversations[session_id],
                    max_tokens=2000,
                    temperature=0.7,
                )

                final_response = second_response.choices[0].message.content.strip()
                self.conversations[session_id].append(
                    {"role": "assistant", "content": final_response}
                )

                return {
                    "response": final_response,
                    "function_call": {
                        "name": function_name,
                        "result": function_response,
                    },
                    "session_id": session_id,
                }

            # Handle regular response
            bot_message = response_message.content
            if bot_message:
                self.conversations[session_id].append(
                    {"role": "assistant", "content": bot_message}
                )

                return {
                    "response": bot_message,
                    "function_call": None,
                    "session_id": session_id,
                }
            else:
                default_response = "I'm here to help you with trading on Injective Chain. You can ask me about trading, checking balances, making transfers, or staking. How can I assist you today?, Do you want my opinion on `{self.conversations[session_id]}`?"
                self.conversations[session_id].append(
                    {"role": "assistant", "content": default_response}
                )

                return {
                    "response": default_response,
                    "function_call": None,
                    "session_id": session_id,
                }

        except Exception as e:
            error_response = f"I apologize, but I encountered an error: {str(e)}. How else can I help you?"
            return {
                "response": error_response,
                "function_call": None,
                "session_id": session_id,
            }

    async def analyze_chart(self, symbol: str, signals: pd.DataFrame, session_id: str = None):
        """Analyze chart data and initialize conversation"""
        try:
            if session_id is None:
                session_id = f"analysis_{symbol}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Generate analysis
            analysis_result = self.generate_chart_analysis(symbol, signals)
            
            # Add analysis to token context for the session
            self.add_token_context(session_id, symbol, analysis_result)
            
            return {
                "response": analysis_result,
                "session_id": session_id,
                "symbol": symbol
            }
        except Exception as e:
            return {
                "error": str(e),
                "response": f"I apologize, but I encountered an error analyzing the chart data: {str(e)}",
            }

    def clear_history(self, session_id="default"):
        """Clear conversation history for a specific session."""
        if session_id in self.conversations:
            self.conversations[session_id].clear()
        if session_id in self.token_contexts:
            del self.token_contexts[session_id]

    def get_history(self, session_id="default"):
        """Get conversation history for a specific session."""
        return self.conversations.get(session_id, [])

    def get_token_context(self, session_id="default"):
        """Get token context for a specific session."""
        return self.token_contexts.get(session_id)
    
    __all__ = ["InjectiveChatAgent"]