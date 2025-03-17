import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { analyze, clear, chat, stock } from '@/app/api';
import ReactMarkdown from 'react-markdown';
import { useToast } from '@/components/ui/toaster';
import StockChart, { StockData } from './StockChart';
import LoadingSpinner from '@/components/LoadingSpinner';

// Mock data for testing
const TIMEFRAMES = ['1D', '1W', '1M', '3M', '6M', '1Y', '5Y'];
const INTERVALS = ['minute', '5min', '15min', '30min', 'hour', 'day', 'week', 'month'];

const Analyze: React.FC = () => {
  const { toast } = useToast();
  const [symbol, setSymbol] = useState('BTC');
  const [timeframe, setTimeframe] = useState('3M');
  const [interval, setInterval] = useState('hour');
  const [isLoading, setIsLoading] = useState(false);
  const [stockData, setStockData] = useState<StockData | null>(null);
  const [analysis, setAnalysis] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<{ role: string, content: string }[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isChatLoading, setIsChatLoading] = useState(false);

  const handleAnalyze = async () => {
    setIsLoading(true);
    await clearData();
    
    try {
      // First fetch the stock data
      console.log("Fetching stock data for", symbol, timeframe, interval);
      const stockResponse = await stock({
        symbol,
        timeframe,
        interval
      });
      console.log("Stock data received:", stockResponse);
      setStockData(stockResponse);
      
      // Then analyze the chart
      console.log("Analyzing chart data");
      const analysisResponse = await analyze({
        symbol,
        timeframe,
        interval
      });
      console.log("Analysis response:", analysisResponse);
      
      setAnalysis(analysisResponse.response);
      setSessionId(analysisResponse.session_id);

      // Add the analysis as the first system message
      setMessages([{
        role: 'system',
        content: analysisResponse.response
      }]);
      
    } catch (error) {
      console.error('Error during analysis:', error);
      toast({
        title: "Analysis Failed",
        description: "Could not analyze the chart data.",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  const clearData = async () => {
    if (sessionId) {
      try {
        await clear({ session_id: sessionId });
      } catch (error) {
        console.error('Error clearing session:', error);
      }
    }
    
    setSessionId(null);
    setAnalysis(null);
    setMessages([]);
    setInputMessage('');
  };
  
  const handleSendMessage = async (message: string) => {
    if (!sessionId || !message.trim()) return;

    // Clear the input field immediately
    setInputMessage('');
    
    // Add user message to the list
    setMessages(prev => [...prev, { role: 'user', content: message }]);
    
    // Show loading state
    setIsChatLoading(true);

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
    } finally {
      setIsChatLoading(false);
    }
  };

  useEffect(() => {
    // Load initial data when component mounts
    handleAnalyze();
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
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
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
          
          <select
            value={interval}
            onChange={(e) => setInterval(e.target.value)}
            className="h-9 rounded-md border border-input px-3 py-1 text-sm"
          >
            {INTERVALS.map(it => (
              <option key={it} value={it}>{it}</option>
            ))}
          </select>

          <Button onClick={handleAnalyze} disabled={isLoading}>
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
              <CardDescription>
                {stockData ? 
                  `${timeframe} - ${interval} interval` : 
                  'No data available'}
              </CardDescription>
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
                    <div className="prose max-w-none dark:prose-invert">
                      <ReactMarkdown>{analysis}</ReactMarkdown>
                    </div>
                  ) : (
                    <p className="text-muted-foreground">No analysis available. Click "Analyze" to generate insights.</p>
                  )}
                </CardContent>
                <CardFooter>
                  <Button
                    variant="outline"
                    onClick={handleAnalyze}
                    disabled={isLoading}
                  >
                    Refresh Analysis
                  </Button>
                </CardFooter>
              </TabsContent>

              <TabsContent value="chat" className="space-y-4">
                <CardContent className="h-[400px] overflow-y-auto">
                  {messages.length > 0 ? (
                    <div className="space-y-4">
                      {messages.map((message, index) => (
                        <div 
                          key={index}
                          className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                          <div 
                            className={`rounded-lg px-4 py-2 max-w-[80%] ${
                              message.role === 'user' 
                                ? 'bg-primary text-primary-foreground' 
                                : message.role === 'system'
                                  ? 'bg-muted text-foreground'
                                  : 'bg-secondary'
                            }`}
                          >
                            <ReactMarkdown>{message.content}</ReactMarkdown>
                          </div>
                        </div>
                      ))}
                      
                      {isChatLoading && (
                        <div className="flex justify-start">
                          <div className="bg-secondary rounded-lg px-4 py-2">
                            <LoadingSpinner size="sm" />
                          </div>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="flex items-center justify-center h-full">
                      <p className="text-muted-foreground">No conversation yet. Start chatting with the AI assistant.</p>
                    </div>
                  )}
                </CardContent>
                <CardFooter className="flex gap-2">
                  <Input 
                    placeholder="Ask something about this stock..." 
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && inputMessage.trim() && handleSendMessage(inputMessage)}
                    disabled={!sessionId || isChatLoading}
                  />
                  <Button 
                    onClick={() => handleSendMessage(inputMessage)}
                    disabled={!sessionId || !inputMessage.trim() || isChatLoading}
                  >
                    Send
                  </Button>
                </CardFooter>
              </TabsContent>
            </Tabs>
          </Card>
        </div>
      )}
    </div>
  );
};

export default Analyze;