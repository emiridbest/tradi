import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { handler, analyze, clear, chat } from '@/app/api';

import { useToast } from '@/components/ui/toaster';
import StockChart from '@/components/StockChart';
import ChatInterface from '@/components/ChatInterface';
import LoadingSpinner from '@/components/LoadingSpinner';

// Mock data for testing
const TIMEFRAMES = ['1D', '1W', '1M', '3M', '6M', '1Y', '5Y'];

interface StockData {
  symbol: string;
  price: number[];
  dates: string[];
  short_mavg: number[];
  long_mavg: number[];
  positions: number[];
}

const Analyze = () => {
  const { toast } = useToast();
  const [symbol, setSymbol] = useState('NVDA');
  const [timeframe, setTimeframe] = useState('3M');
  const [isLoading, setIsLoading] = useState(false);
  const [stockData, setStockData] = useState<StockData | null>(null);
  const [analysis, setAnalysis] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<{role: string, content: string}[]>([]);

  const fetchStockData = async () => {
    setIsLoading(true);
    try {
      //  fetch from your backend but for now, we'll simulate with some mock data
      const mockData = {
        symbol,
        price: Array(30).fill(0).map((_, i) => 100 + Math.random() * 20 - i/2),
        dates: Array(30).fill(0).map((_, i) => new Date(Date.now() - (30-i) * 86400000).toISOString().split('T')[0]),
        short_mavg: Array(30).fill(0).map((_, i) => 105 + Math.random() * 15 - i/3),
        long_mavg: Array(30).fill(0).map((_, i) => 102 + Math.random() * 10 - i/4),
        positions: Array(30).fill(0).map(() => Math.random() > 0.8 ? (Math.random() > 0.5 ? 1 : -1) : 0)
      };
      
      setStockData(mockData);
      
      // Analyze the data
      await analyzeChart(mockData);
      
      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching stock data:', error);
      toast({
        title: "Failed to fetch data",
        description: "Could not retrieve stock data. Please try again.",
        variant: "destructive"
      });
      setIsLoading(false);
    }
  };

  const analyzeChart = async (data: StockData) => {
    try {
      const signals = {
        price: data.price,
        short_mavg: data.short_mavg,
        long_mavg: data.long_mavg,
        positions: data.positions
      };
      
      const response = await analyze({
        symbol: data.symbol,
        signals
      });
      
      setAnalysis(response.response);
      setSessionId(response.session_id);
      
      // Add the analysis as the first system message
      setMessages([{
        role: 'system',
        content: response.response
      }]);
      
    } catch (error) {
      console.error('Error analyzing chart:', error);
      toast({
        title: "Analysis Failed",
        description: "Could not analyze the chart data.",
        variant: "destructive"
      });
    }
  };

  const handleSendMessage = async (message: string) => {
    if (!sessionId) return;
    
    // Add user message to the list
    setMessages(prev => [...prev, { role: 'user', content: message }]);
    
    try {
      const response = await chat({
        message,
        session_id: sessionId
      });
      
      // Add response to messages
      setMessages(prev => [...prev, { role: 'assistant', content: response.response }]);
      
    } catch (error) {
      console.error('Error sending message:', error);
      toast({
        title: "Message Failed",
        description: "Could not send your message.",
        variant: "destructive"
      });
      
      // Add error message
      setMessages(prev => [...prev, { 
        role: 'system', 
        content: "Sorry, I couldn't process that message. Please try again." 
      }]);
    }
  };

  useEffect(() => {
    // Load initial data when component mounts
    fetchStockData();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between space-y-4 md:space-y-0 md:space-x-4">
        <div className="flex-1">
          <h1 className="text-3xl font-bold tracking-tight">Stock Analysis</h1>
          <p className="text-muted-foreground">Analyze stock data and get AI-powered insights.</p>
        </div>
        
        <div className="flex space-x-2">
          <Input 
            value={symbol}
            onChange={(e: { target: { value: string; }; }) => setSymbol(e.target.value.toUpperCase())}
            placeholder="Stock Symbol"
            className="w-32"
          />
          
          <select 
            value={timeframe}
            onChange={(e) => setTimeframe(e.target.value)}
            className="h-9 rounded-md border border-input px-3 py-1 text-sm"
          >
            {TIMEFRAMES.map(tf => (
              <option key={tf} value={tf}>{tf}</option>
            ))}
          </select>
          
          <Button onClick={fetchStockData} disabled={isLoading}>
            {isLoading ? <LoadingSpinner /> : 'Analyze'}
          </Button>
        </div>
      </div>

      {isLoading ? (
        <Card className="flex items-center justify-center" style={{ height: '400px' }}>
          <CardContent className="flex flex-col items-center gap-2">
            <LoadingSpinner size="lg" />
            <p>Loading data and generating analysis...</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Chart Card */}
          <Card>
            <CardHeader>
              <CardTitle>{symbol} Chart Analysis</CardTitle>
              <CardDescription>Stock price and moving averages</CardDescription>
            </CardHeader>
            <CardContent>
              {stockData ? (
                <StockChart data={stockData} />
              ) : (
                <div className="h-64 flex items-center justify-center border rounded">
                  <p className="text-muted-foreground">No chart data available</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* AI Analysis & Chat Card */}
          <Card>
            <Tabs defaultValue="analysis">
              <CardHeader className="pb-0">
                <div className="flex items-center justify-between">
                  <CardTitle>AI Trading Assistant</CardTitle>
                  <TabsList>
                    <TabsTrigger value="analysis">Analysis</TabsTrigger>
                    <TabsTrigger value="chat">Chat</TabsTrigger>
                  </TabsList>
                </div>
                <CardDescription>AI-powered analysis and recommendations</CardDescription>
              </CardHeader>

              <TabsContent value="analysis" className="space-y-4">
                <CardContent>
                  {analysis ? (
                    <div className="prose max-w-none">
                      <h3>Analysis for {symbol}</h3>
                      <div dangerouslySetInnerHTML={{ __html: analysis }} />
                    </div>
                  ) : (
                    <p className="text-muted-foreground">No analysis available. Click "Analyze" to generate insights.</p>
                  )}
                </CardContent>
                <CardFooter>
                  <Button 
                    variant="outline" 
                    onClick={fetchStockData}
                    disabled={isLoading}
                  >
                    Refresh Analysis
                  </Button>
                </CardFooter>
              </TabsContent>

              <TabsContent value="chat">
                <ChatInterface 
                  messages={messages}
                  onSendMessage={handleSendMessage}
                  sessionId={sessionId}
                />
              </TabsContent>
            </Tabs>
          </Card>
        </div>
      )}
    </div>
  );
};

export default Analyze;