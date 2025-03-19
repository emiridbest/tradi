import { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast"
import { AlertCircle, TrendingUp, RefreshCcw, AlertTriangle } from 'lucide-react';
import LoadingSpinner from '@/components/LoadingSpinner';
import PredictionChart from '@/components/PredictionChart';
import { AnalyzeParams, predict, reset } from '@/app/api';
// Define types for predictions
export interface PredictionData {
  symbol: string;
  current_price: number;
  predictions: {
    // For hourly intervals
    "1h"?: number;
    "4h"?: number;
    "8h"?: number;
    "24h"?: number;
    // For daily intervals
    "1d"?: number;
    "7d"?: number;
    "30d"?: number;
    "90d"?: number;
  };
  performance: {
    mse: number;
    mae: number;
    r2: number;
    accuracy: number;
  };
  dates?: string[];
  historical?: number[];
  predicted?: number[];
}

// Mock data for testing without API
const TIMEFRAMES = ['1D', '1W', '1M', '3M', '6M', '1Y'];
const INTERVALS = [ 'hour', 'day'];
const DEFAULT_SYMBOLS = ['AAPL', 'NVDA', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'BTC'];

const PredictionPage: React.FC = () => {
  const { toast } = useToast();
  const [symbol, setSymbol] = useState('NVDA');
  const [timeframe, setTimeframe] = useState('3M');
  const [interval, setInterval] = useState('day');
  const [isLoading, setIsLoading] = useState(false);
  const [predictionData, setPredictionData] = useState<PredictionData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('predictions');
  const [customSymbol, setCustomSymbol] = useState('');

  // Generate price prediction for selected symbol
  const generatePrediction = async (symbolParam?: string | AnalyzeParams, timeframeParam?: string, intervalParam?: string) => {
    setIsLoading(true);
    setError(null);
    try {
      // Create analyze params
      const analyzeParams: AnalyzeParams = {
        symbol: typeof symbolParam === 'string' ? symbolParam : symbol,
        timeframe: timeframeParam || timeframe,
        interval: intervalParam || interval
      };

      // Make API call to get predictions
      const response = await predict(analyzeParams);
      setPredictionData(response);
      console.log('Prediction data:', response);
      toast({
        title: "Prediction Generated",
        description: `Successfully generated price forecast for ${symbol}`,
      });
    } catch (err) {
      console.error('Error generating prediction:', err);
      setError(err instanceof Error ? err.message : 'Failed to generate prediction');

      toast({
        title: "Error",
        description: "Failed to generate prediction. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Reset the ML model
  const resetModel = async () => {
    try {
      await reset()
      toast({
        title: "Model Reset",
        description: "The prediction model has been reset successfully.",
      });

      // Regenerate predictions with fresh model
      generatePrediction(symbol, timeframe, interval);
    } catch (err) {
      console.error('Error resetting model:', err);
      toast({
        title: "Error",
        description: "Failed to reset the model. Please try again.",
        variant: "destructive",
      });
    }
  };

  // Handle custom symbol input
  const handleCustomSymbolChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCustomSymbol(e.target.value.toUpperCase());
  };

  // Submit custom symbol
  const handleCustomSymbolSubmit = () => {
    if (customSymbol) {
      setSymbol(customSymbol);
      setCustomSymbol('');
    }
  };

  // Format currency number
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  // Calculate price change percentage
  const calculateChange = (current: number, predicted: number) => {
    const change = ((predicted - current) / current) * 100;
    return change.toFixed(2);
  };

  // Get color based on value (positive/negative)
  const getChangeColor = (change: number) => {
    return change >= 0 ? 'text-green-600' : 'text-red-600';
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-center mb-6 gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Price Predictions</h1>
          <p className="text-muted-foreground">ML-powered price forecasts for your selected assets</p>
        </div>

        <div className="flex flex-wrap gap-2 items-center">
          <Select value={symbol} onValueChange={setSymbol}>
            <SelectTrigger className="w-[120px]">
              <SelectValue placeholder="Symbol" />
            </SelectTrigger>
            <SelectContent>
              {DEFAULT_SYMBOLS.map((s) => (
                <SelectItem key={s} value={s}>{s}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          <div className="flex gap-2 items-center">
            <Input
              value={customSymbol}
              onChange={handleCustomSymbolChange}
              placeholder="Custom symbol"
              className="w-24 md:w-32"
              onKeyPress={(e) => e.key === 'Enter' && handleCustomSymbolSubmit()}
            />
            <Button
              variant="outline"
              size="sm"
              onClick={handleCustomSymbolSubmit}
            >
              Add
            </Button>
          </div>

          <Select value={timeframe} onValueChange={setTimeframe}>
            <SelectTrigger className="w-[90px]">
              <SelectValue placeholder="Timeframe" />
            </SelectTrigger>
            <SelectContent>
              {TIMEFRAMES.map((tf) => (
                <SelectItem key={tf} value={tf}>{tf}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={interval} onValueChange={setInterval}>
            <SelectTrigger className="w-[100px]">
              <SelectValue placeholder="Interval" />
            </SelectTrigger>
            <SelectContent>
              {INTERVALS.map((int) => (
                <SelectItem key={int} value={int}>{int}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Button
            variant="default"
            onClick={() => generatePrediction(symbol, timeframe, interval)}
            disabled={isLoading}
          >
            {isLoading ? <LoadingSpinner size="sm" /> : <TrendingUp className="mr-2 h-4 w-4" />}
            Predict
          </Button>
        </div>
      </div>

      {error && (
        <Alert variant="destructive" className="mb-4">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main prediction card */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex justify-between items-center">
              <span>{symbol} Price Forecast</span>
              <Button variant="outline" size="sm" onClick={resetModel}>
                <RefreshCcw className="mr-2 h-4 w-4" />
                Reset Model
              </Button>
            </CardTitle>
            <CardDescription>
              {isLoading ? 'Generating predictions...' : `Based on ${timeframe} ${interval} data`}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="mb-4">
                <TabsTrigger value="predictions">Predictions</TabsTrigger>
                <TabsTrigger value="chart">Chart</TabsTrigger>
                <TabsTrigger value="performance">Performance</TabsTrigger>
              </TabsList>

              <TabsContent value="predictions" className="space-y-4">
                {isLoading ? (
                  <div className="space-y-3">
                    <Skeleton className="h-12 w-full" />
                    <Skeleton className="h-12 w-full" />
                    <Skeleton className="h-12 w-full" />
                    <Skeleton className="h-12 w-full" />
                  </div>
                ) : predictionData ? (
                  <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <Card>
                        <CardHeader className="py-3">
                          <CardTitle className="text-sm font-medium">Current Price</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <p className="text-2xl font-bold">
                            {formatCurrency(predictionData.current_price)}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            Last updated: {new Date().toLocaleString()}
                          </p>
                        </CardContent>
                      </Card>

                      <Card>
                        <CardHeader className="py-3">
                          <CardTitle className="text-sm font-medium">
                            {interval.includes('min') || interval === 'hour' ? 'Next Hour Forecast' : 'Next Day Forecast'}
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <p className="text-2xl font-bold">
                            {formatCurrency(predictionData.predictions["1h"] || predictionData.predictions["1d"] || 0)}
                          </p>
                          <p className={`text-sm ${getChangeColor(
                            parseFloat(calculateChange(predictionData.current_price,
                              predictionData.predictions["1h"] || predictionData.predictions["1d"] || 0))
                          )}`}>
                            {calculateChange(predictionData.current_price,
                              predictionData.predictions["1h"] || predictionData.predictions["1d"] || 0)}% from current
                          </p>
                        </CardContent>
                      </Card>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {/* Conditionally render hourly or daily predictions */}
                      {interval.includes('min') || interval === 'hour' ? (
                        // Hourly predictions
                        <>
                          <Card>
                            <CardHeader className="py-2">
                              <CardTitle className="text-sm font-medium">4-Hour Forecast</CardTitle>
                            </CardHeader>
                            <CardContent>
                              <p className="text-xl font-bold">
                                {formatCurrency(predictionData.predictions["4h"] || 0)}
                              </p>
                              <p className={`text-xs ${getChangeColor(
                                parseFloat(calculateChange(predictionData.current_price, predictionData.predictions["4h"] || 0))
                              )}`}>
                                {calculateChange(predictionData.current_price, predictionData.predictions["4h"] || 0)}%
                              </p>
                            </CardContent>
                          </Card>

                          <Card>
                            <CardHeader className="py-2">
                              <CardTitle className="text-sm font-medium">8-Hour Forecast</CardTitle>
                            </CardHeader>
                            <CardContent>
                              <p className="text-xl font-bold">
                                {formatCurrency(predictionData.predictions["8h"] || 0)}
                              </p>
                              <p className={`text-xs ${getChangeColor(
                                parseFloat(calculateChange(predictionData.current_price, predictionData.predictions["8h"] || 0))
                              )}`}>
                                {calculateChange(predictionData.current_price, predictionData.predictions["8h"] || 0)}%
                              </p>
                            </CardContent>
                          </Card>

                          <Card>
                            <CardHeader className="py-2">
                              <CardTitle className="text-sm font-medium">24-Hour Forecast</CardTitle>
                            </CardHeader>
                            <CardContent>
                              <p className="text-xl font-bold">
                                {formatCurrency(predictionData.predictions["24h"] || 0)}
                              </p>
                              <p className={`text-xs ${getChangeColor(
                                parseFloat(calculateChange(predictionData.current_price, predictionData.predictions["24h"] || 0))
                              )}`}>
                                {calculateChange(predictionData.current_price, predictionData.predictions["24h"] || 0)}%
                              </p>
                            </CardContent>
                          </Card>
                        </>
                      ) : (
                        // Daily predictions
                        <>
                          <Card>
                            <CardHeader className="py-2">
                              <CardTitle className="text-sm font-medium">7-Day Forecast</CardTitle>
                            </CardHeader>
                            <CardContent>
                              <p className="text-xl font-bold">
                                {formatCurrency(predictionData.predictions["7d"] || 0)}
                              </p>
                              <p className={`text-xs ${getChangeColor(
                                parseFloat(calculateChange(predictionData.current_price, predictionData.predictions["7d"] || 0))
                              )}`}>
                                {calculateChange(predictionData.current_price, predictionData.predictions["7d"] || 0)}%
                              </p>
                            </CardContent>
                          </Card>

                          <Card>
                            <CardHeader className="py-2">
                              <CardTitle className="text-sm font-medium">30-Day Forecast</CardTitle>
                            </CardHeader>
                            <CardContent>
                              <p className="text-xl font-bold">
                                {formatCurrency(predictionData.predictions["30d"] || 0)}
                              </p>
                              <p className={`text-xs ${getChangeColor(
                                parseFloat(calculateChange(predictionData.current_price, predictionData.predictions["30d"] || 0))
                              )}`}>
                                {calculateChange(predictionData.current_price, predictionData.predictions["30d"] || 0)}%
                              </p>
                            </CardContent>
                          </Card>

                          <Card>
                            <CardHeader className="py-2">
                              <CardTitle className="text-sm font-medium">90-Day Forecast</CardTitle>
                            </CardHeader>
                            <CardContent>
                              <p className="text-xl font-bold">
                                {formatCurrency(predictionData.predictions["90d"] || 0)}
                              </p>
                              <p className={`text-xs ${getChangeColor(
                                parseFloat(calculateChange(predictionData.current_price, predictionData.predictions["90d"] || 0))
                              )}`}>
                                {calculateChange(predictionData.current_price, predictionData.predictions["90d"] || 0)}%
                              </p>
                            </CardContent>
                          </Card>
                        </>
                      )}
                    </div>

                    <Alert>
                      <AlertTriangle className="h-4 w-4" />
                      <AlertTitle>Disclaimer</AlertTitle>
                      <AlertDescription className="text-sm">
                        Price predictions are generated using machine learning models and should not be considered
                        financial advice. Past performance is not indicative of future results.
                      </AlertDescription>
                    </Alert>
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-64">
                    <p className="text-muted-foreground">No prediction data available</p>
                  </div>
                )}
              </TabsContent>
              <TabsContent value="chart">
                {isLoading ? (
                  <Skeleton className="h-80 w-full" />
                ) : predictionData ? (
                  <PredictionChart data={predictionData} />
                ) : (
                  <div className="flex items-center justify-center h-80">
                    <p className="text-muted-foreground">No chart data available</p>
                  </div>
                )}
              </TabsContent>

              <TabsContent value="performance">
                {isLoading ? (
                  <div className="space-y-3">
                    <Skeleton className="h-12 w-full" />
                    <Skeleton className="h-12 w-full" />
                    <Skeleton className="h-12 w-full" />
                  </div>
                ) : predictionData?.performance ? (
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <Card>
                        <CardHeader className="py-2">
                          <CardTitle className="text-sm font-medium">Mean Squared Error</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <p className="text-xl font-bold">{predictionData.performance.mse.toFixed(4)}</p>
                          <p className="text-xs text-muted-foreground">Lower is better</p>
                        </CardContent>
                      </Card>

                      <Card>
                        <CardHeader className="py-2">
                          <CardTitle className="text-sm font-medium">Mean Abs Error</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <p className="text-xl font-bold">{predictionData.performance.mae.toFixed(4)}</p>
                          <p className="text-xs text-muted-foreground">Lower is better</p>
                        </CardContent>
                      </Card>

                      <Card>
                        <CardHeader className="py-2">
                          <CardTitle className="text-sm font-medium">R² Score</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <p className="text-xl font-bold">{predictionData.performance.r2.toFixed(4)}</p>
                          <p className="text-xs text-muted-foreground">Closer to 1 is better</p>
                        </CardContent>
                      </Card>

                      <Card>
                        <CardHeader className="py-2">
                          <CardTitle className="text-sm font-medium">Direction Accuracy</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <p className="text-xl font-bold">{(predictionData.performance.accuracy * 100).toFixed(1)}%</p>
                          <p className="text-xs text-muted-foreground">Higher is better</p>
                        </CardContent>
                      </Card>
                    </div>

                    <div className="bg-muted p-4 rounded-md">
                      <h3 className="text-sm font-medium mb-2">About These Metrics</h3>
                      <p className="text-sm text-muted-foreground">
                        These metrics indicate how well the model has performed on historical data.
                        The MSE and MAE measure the average magnitude of errors, while the R² score indicates
                        how well the model explains the variance in the data. Direction accuracy shows how often
                        the model correctly predicts price movement direction.
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-64">
                    <p className="text-muted-foreground">No performance metrics available</p>
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        {/* Sidebar information */}
        <Card>
          <CardHeader>
            <CardTitle>Prediction Insights</CardTitle>
            <CardDescription>Key factors influencing the forecast</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {isLoading ? (
              <div className="space-y-3">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-[90%]" />
                <Skeleton className="h-4 w-[80%]" />
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-[70%]" />
                <Skeleton className="h-10 w-full" />
              </div>
            ) : (
              <>
                <div>
                  <h3 className="font-medium mb-2">Market Sentiment</h3>
                  <div className="bg-muted p-3 rounded-md">
                    <p className="text-sm">
                      {predictionData && (
                        (predictionData.predictions["1h"] !== undefined && predictionData.predictions["1h"] > predictionData.current_price) ||
                        (predictionData.predictions["1d"] !== undefined && predictionData.predictions["1d"] > predictionData.current_price)
                      )
                        ? "The model suggests a bullish short-term outlook based on recent price action."
                        : "The model suggests a bearish short-term outlook based on recent price action."}
                    </p>
                  </div>
                </div>

                <div>
                  <h3 className="font-medium mb-2">Technical Factors</h3>
                  <ul className="space-y-1 text-sm font-light">
                    <li>• Trend direction</li>
                    <li>• Price momentum</li>
                    <li>• Moving averages</li>
                    <li>• Volume patterns</li>
                    <li>• Previous price action</li>
                  </ul>
                </div>

                <div className="pt-2">
                  <h3 className="font-medium mb-2">Forecast Confidence</h3>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary rounded-full"
                      style={{ width: predictionData ? `${predictionData.performance.accuracy * 100}%` : '0%' }}
                    ></div>
                  </div>
                  <p className="text-xs text-right mt-1 text-muted-foreground">
                    {predictionData ? `${(predictionData.performance.accuracy * 100).toFixed(1)}%` : 'N/A'}
                  </p>
                </div>

                <div className="pt-2">
                  <h3 className="font-medium mb-2">Model Information</h3>
                  <p className="text-sm text-muted-foreground">
                    This predictive model uses multiple regression algorithms and feature engineering to identify patterns
                    in historical price data. Forecasts are more reliable for shorter time periods and may not account for
                    unexpected market events.
                  </p>
                </div>
              </>
            )}
          </CardContent>
          <CardFooter>
            <Button variant="outline" className="w-full" onClick={resetModel}>
              <RefreshCcw className="mr-2 h-4 w-4" />
              Reset & Retrain Model
            </Button>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
};

export default PredictionPage;