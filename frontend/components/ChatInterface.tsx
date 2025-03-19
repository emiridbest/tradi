import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { AlertCircle } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { LineChart } from "lucide-react";
import LoadingSpinner from './LoadingSpinner';
import StockChart from './StockChart';
import { stock } from '@/app/api';




interface Analysis {
  response: string;
  session_id: string;
  symbol: string;
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

const ChatInterface: React.FC = () => {
  const [symbol, setSymbol] = useState<string>('NVDA');
  const [timeframe, setTimeframe] = useState<string>('1Y');
  const [interval, setInterval] = useState<string>('hour');
  const [signals, setSignals] = useState<any>(null);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState<string>('');
  const [isChatLoading, setIsChatLoading] = useState<boolean>(false);

  // Fetch stock data and generate analysis
  const analyze = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Fetch stock data from your API
      const response = await stock({
        symbol,
        timeframe,
        interval
      });
      if (!response.ok) throw new Error('Failed to fetch stock data');

      const data = await response.json();
      setSignals(data.signals);

      // Send signals to the chart analysis endpoint
      await generateAnalysis(data.signals);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  // Generate chart analysis
  const generateAnalysis = async (signals: any) => {
    try {
      const response = await fetch('/chart-analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symbol,
          signals,
        }),
      });

      if (!response.ok) throw new Error('Failed to generate analysis');

      const analysisResult = await response.json();
      setAnalysis(analysisResult);
      setSessionId(analysisResult.session_id);

      // Initialize chat with the analysis
      setChatMessages([
        {
          role: 'assistant',
          content: analysisResult.response
        }
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze chart data');
    }
  };

  // Send a chat message to the AI
  const sendChatMessage = async () => {
    if (!inputMessage.trim() || !sessionId) return;

    // Add user message to chat
    const userMessage = { role: 'user' as const, content: inputMessage };
    setChatMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsChatLoading(true);

    try {
      const response = await fetch('/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage.content,
          session_id: sessionId,
        }),
      });

      if (!response.ok) throw new Error('Failed to get AI response');

      const result = await response.json();
      setChatMessages(prev => [...prev, { role: 'assistant', content: result.response }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to communicate with AI');
      setChatMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }]);
    } finally {
      setIsChatLoading(false);
    }
  };

  // Clear the current chat session
  const clearChat = async () => {
    if (!sessionId) return;

    try {
      await fetch(`/clear?session_id=${sessionId}`, {
        method: 'POST',
      });
      setChatMessages([]);
      setAnalysis(null);
      setSessionId(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to clear chat session');
    }
  };

  // Initial stock data fetch
  useEffect(() => {
    clearChat();
    analyze();
      // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="container mx-auto py-6 space-y-6">
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Stock Analysis Dashboard</CardTitle>
          <CardDescription>Analyze stock movements and get AI-powered insights</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="w-full md:w-1/3 space-y-2">
              <label htmlFor="symbol" className="text-sm font-medium">Stock Symbol</label>
              <div className="flex gap-2">
                <Input
                  id="symbol"
                  value={symbol}
                  onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                  placeholder="Enter stock symbol"
                  className="flex-1"
                />
                <Select value={timeframe} onValueChange={setTimeframe}>
                  <SelectTrigger className="w-28">
                    <SelectValue placeholder="Timeframe" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1M">1 Month</SelectItem>
                    <SelectItem value="3M">3 Months</SelectItem>
                    <SelectItem value="6M">6 Months</SelectItem>
                    <SelectItem value="1Y">1 Year</SelectItem>
                    <SelectItem value="2Y">2 Years</SelectItem>
                    <SelectItem value="5Y">5 Years</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={interval} onValueChange={setInterval}>
                  <SelectTrigger className="w-28">
                    <SelectValue placeholder="Interval" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="minute">1 Minute</SelectItem>
                    <SelectItem value="5min">5 Minutes</SelectItem>
                    <SelectItem value="15min">15 Minutes</SelectItem>
                    <SelectItem value="30min">30 Minutes</SelectItem>
                    <SelectItem value="hour">Hourly</SelectItem>
                    <SelectItem value="day">Daily</SelectItem>
                    <SelectItem value="week">Weekly</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button onClick={clearChat} className="w-full" variant="default">
                <LineChart className="mr-2 h-4 w-4" /> Analyze
              </Button>
            </div>

            <div className="w-full md:w-2/3">
              {error && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertTitle>Error</AlertTitle>
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {isLoading ? (
                <div className="w-full h-64 flex items-center justify-center">
                  <LoadingSpinner />
                </div>
              ) : signals ? (
                <StockChart data={signals} />
              ) : (
                <div className="w-full h-64 border border-dashed rounded-md flex items-center justify-center">
                  <p className="text-gray-500">Select a stock and timeframe to analyze</p>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="chat" className="w-full">
        <TabsList className="grid grid-cols-2">
          <TabsTrigger value="chat">AI Chat Assistant</TabsTrigger>
          <TabsTrigger value="analysis">Technical Analysis</TabsTrigger>
        </TabsList>

        <TabsContent value="chat" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Injective Chat Assistant</CardTitle>
              <CardDescription>Chat with our AI about the analyzed stock and execute actions on Injective Chain</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[400px] overflow-y-auto border rounded-md p-4 space-y-4 mb-4">
                {chatMessages.length > 0 ? (
                  chatMessages.map((msg, index) => (
                    <div key={index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div
                        className={`max-w-[80%] rounded-lg p-3 ${msg.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'
                          }`}
                      >
                        <p className="whitespace-pre-wrap">{msg.content}</p>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="h-full flex items-center justify-center">
                    <p className="text-gray-500">No messages yet. Start by analyzing a stock.</p>
                  </div>
                )}
              </div>

              <div className="flex gap-2">
                <Input
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="Ask about the analyzed stock..."
                  onKeyPress={(e) => e.key === 'Enter' && sendChatMessage()}
                  disabled={!sessionId || isChatLoading}
                  className="flex-1"
                />
                <Button onClick={sendChatMessage} disabled={!sessionId || isChatLoading}>
                  {isChatLoading ? <LoadingSpinner size="sm" /> : "Send"}
                </Button>
                <Button onClick={analyze} variant="outline" disabled={!sessionId}>
                  Clear
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analysis" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Technical Analysis</CardTitle>
              <CardDescription>Detailed technical indicators and analysis</CardDescription>
            </CardHeader>
            <CardContent>
              {analysis ? (
                <div className="prose max-w-none">
                  <h3>{symbol} Analysis</h3>
                  <div dangerouslySetInnerHTML={{ __html: analysis.response }}></div>
                </div>
              ) : (
                <div className="h-[200px] flex items-center justify-center">
                  <p className="text-gray-500">No analysis available. Analyze a stock first.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ChatInterface;