import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    ReferenceLine,
  } from 'recharts';
  import { useState } from 'react';
  import { Card, CardContent } from '@/components/ui/card';
  import { Toggle } from '@/components/ui/toggle';
  
  interface PredictionData {
    symbol: string;
    current_price: number;
    predictions: {
      next_day: number;
      three_day: number;
      week: number;
      month: number;
    };
    performance?: {
      mse: number;
      mae: number;
      r2: number;
      accuracy: number;
    };
    dates?: string[];
    historical?: number[];
    predicted?: number[];
  }
  
  interface PredictionChartProps {
    data: PredictionData;
  }
  
  const PredictionChart: React.FC<PredictionChartProps> = ({ data }) => {
    const [showConfidenceInterval, setShowConfidenceInterval] = useState(true);
    
    let chartData = [];
    
    if (data.dates && data.historical && data.predicted) {
      chartData = data.dates.map((date, i) => ({
        date,
        historical: data.historical?.[i] || null,
        predicted: data.predicted?.[i] || null,
        upper: data.predicted?.[i] ? data.predicted[i] * 1.05 : null,
        lower: data.predicted?.[i] ? data.predicted[i] * 0.95 : null,
      }));
    } else {
      // Create synthetic data for visualization
      const currentDate = new Date();
      const historicalDates = Array.from({ length: 30 }, (_, i) => {
        const date = new Date();
        date.setDate(currentDate.getDate() - (30 - i));
        return date.toISOString().split('T')[0];
      });
      
      const startPrice = data.current_price * 0.9;
      const volatility = data.current_price * 0.01;
      let currentHistoricalPrice = startPrice;
      const historicalPrices: any[] = [];
      
      for (let i = 0; i < 30; i++) {
        historicalPrices.push(currentHistoricalPrice);
        const randomChange = (Math.random() - 0.45) * volatility;
        currentHistoricalPrice = currentHistoricalPrice + randomChange;
      }
      
      // Create future dates for predictions
      const futureDates = [
        new Date(currentDate.setDate(currentDate.getDate() + 1)).toISOString().split('T')[0],
        new Date(currentDate.setDate(currentDate.getDate() + 2)).toISOString().split('T')[0],
        new Date(currentDate.setDate(currentDate.getDate() + 4)).toISOString().split('T')[0],
        new Date(currentDate.setDate(currentDate.getDate() + 23)).toISOString().split('T')[0],
      ];
      
      // Build the chart data
      chartData = [
        ...historicalDates.map((date, i) => ({
          date,
          historical: historicalPrices[i],
          predicted: null,
          upper: null,
          lower: null,
        })),
        {
          date: futureDates[0],
          historical: null,
          predicted: data.predictions.next_day,
          upper: data.predictions.next_day * 1.05,
          lower: data.predictions.next_day * 0.95,
        },
        {
          date: futureDates[1],
          historical: null,
          predicted: data.predictions.three_day,
          upper: data.predictions.three_day * 1.05,
          lower: data.predictions.three_day * 0.95,
        },
        {
          date: futureDates[2],
          historical: null,
          predicted: data.predictions.week,
          upper: data.predictions.week * 1.07,
          lower: data.predictions.week * 0.93,
        },
        {
          date: futureDates[3],
          historical: null,
          predicted: data.predictions.month,
          upper: data.predictions.month * 1.15,
          lower: data.predictions.month * 0.85,
        },
      ];
    }
    
    const formatDate = (dateStr: string) => {
      const date = new Date(dateStr);
      return `${date.getMonth() + 1}/${date.getDate()}`;
    };
    
    // Format tooltip values
    const formatY = (value: number) => {
      return `$${value.toFixed(2)}`;
    };
  
    return (
      <Card>
        <CardContent className="pt-4">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-sm font-medium">{data.symbol} Historical & Forecast</h3>
            <Toggle
              pressed={showConfidenceInterval}
              onPressedChange={setShowConfidenceInterval}
              size="sm"
              variant="outline"
            >
              Show Confidence Intervals
            </Toggle>
          </div>
          <div className="h-[400px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={chartData}
                margin={{
                  top: 10,
                  right: 30,
                  left: 20,
                  bottom: 5,
                }}
              >
                <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                <XAxis 
                  dataKey="date" 
                  tickFormatter={formatDate}
                  minTickGap={20}
                />
                <YAxis 
                  domain={['auto', 'auto']} 
                  tickFormatter={formatY}
                />
                <Tooltip 
                  formatter={(value) => [`$${parseFloat(value as string).toFixed(2)}`, 'Price']}
                  labelFormatter={(label) => new Date(label).toLocaleDateString()}
                />
                <Legend />
                
                {/* Historical line */}
                <Line
                  type="monotone"
                  dataKey="historical"
                  name="Historical"
                  stroke="#2563eb"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 6 }}
                />
                
                {/* Prediction line */}
                <Line
                  type="monotone"
                  dataKey="predicted"
                  name="Prediction"
                  stroke="#16a34a"
                  strokeWidth={2.5}
                  strokeDasharray="5 5"
                  activeDot={{ r: 7 }}
                />
                
                {/* Confidence interval - upper bound */}
                {showConfidenceInterval && (
                  <Line
                    type="monotone"
                    dataKey="upper"
                    name="Upper Bound"
                    stroke="#22c55e"
                    strokeWidth={1}
                    dot={false}
                    activeDot={false}
                    opacity={0.5}
                  />
                )}
                
                {/* Confidence interval - lower bound */}
                {showConfidenceInterval && (
                  <Line
                    type="monotone"
                    dataKey="lower"
                    name="Lower Bound"
                    stroke="#22c55e"
                    strokeWidth={1}
                    dot={false}
                    activeDot={false}
                    opacity={0.5}
                  />
                )}
                
                {/* Reference line for current price */}
                <ReferenceLine
                  y={data.current_price}
                  stroke="#dc2626"
                  strokeDasharray="3 3"
                  opacity={0.7}
                  label={{
                    value: 'Current',
                    position: 'insideBottomLeft',
                    style: { fill: '#dc2626', fontSize: 12 }
                  }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <p className="text-xs text-muted-foreground text-center mt-2">
            Predictions shown with increased uncertainty over longer time periods.
            Past performance is not indicative of future results.
          </p>
        </CardContent>
      </Card>
    );
  };
  
  export default PredictionChart;