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
import { PredictionData } from './PredictionPage';

interface PredictionChartProps {
  data: PredictionData;
}

const PredictionChart: React.FC<PredictionChartProps> = ({ data }) => {
  const [showConfidenceInterval, setShowConfidenceInterval] = useState(true);
  
  // Check if we're using hourly or daily predictions
  const isHourly = data.predictions && ("1h" in data.predictions);
  
  // Create chart data for display
  const createChartData = () => {
    // Start with the current time/price point
    const now = new Date();
    const chartData = [
      {
        date: now.toISOString(),
        label: 'Now',
        historical: data.current_price as number | null,
        predicted: null as number | null,
        upper: null as number | null,
        lower: null as number | null
      }
    ];
    
    // Add prediction points based on whether we're using hourly or daily intervals
    if (isHourly) {
      // 1 hour prediction
      if (data.predictions["1h"] !== undefined) {
        const date = new Date(now);
        date.setHours(date.getHours() + 1);
        chartData.push({
          date: date.toISOString(),
          label: '1h',
          historical: null,
          predicted: data.predictions["1h"],
          upper: data.predictions["1h"] * 1.05,
          lower: data.predictions["1h"] * 0.95
        });
      }
      
      // 4 hour prediction
      if (data.predictions["4h"] !== undefined) {
        const date = new Date(now);
        date.setHours(date.getHours() + 4);
        chartData.push({
          date: date.toISOString(),
          label: '4h',
          historical: null,
          predicted: data.predictions["4h"],
          upper: data.predictions["4h"] * 1.08,
          lower: data.predictions["4h"] * 0.92
        });
      }
      
      // 8 hour prediction
      if (data.predictions["8h"] !== undefined) {
        const date = new Date(now);
        date.setHours(date.getHours() + 8);
        chartData.push({
          date: date.toISOString(),
          label: '8h',
          historical: null,
          predicted: data.predictions["8h"],
          upper: data.predictions["8h"] * 1.12,
          lower: data.predictions["8h"] * 0.88
        });
      }
      
      // 24 hour prediction
      if (data.predictions["24h"] !== undefined) {
        const date = new Date(now);
        date.setHours(date.getHours() + 24);
        chartData.push({
          date: date.toISOString(),
          label: '24h',
          historical: null,
          predicted: data.predictions["24h"],
          upper: data.predictions["24h"] * 1.15,
          lower: data.predictions["24h"] * 0.85
        });
      }
    } else {
      // 1 day prediction
      if (data.predictions["1d"] !== undefined) {
        const date = new Date(now);
        date.setDate(date.getDate() + 1);
        chartData.push({
          date: date.toISOString(),
          label: '1d',
          historical: null,
          predicted: data.predictions["1d"],
          upper: data.predictions["1d"] * 1.05,
          lower: data.predictions["1d"] * 0.95
        });
      }
      
      // 7 day prediction
      if (data.predictions["7d"] !== undefined) {
        const date = new Date(now);
        date.setDate(date.getDate() + 7);
        chartData.push({
          date: date.toISOString(),
          label: '7d',
          historical: null,
          predicted: data.predictions["7d"],
          upper: data.predictions["7d"] * 1.10,
          lower: data.predictions["7d"] * 0.90
        });
      }
      
      // 30 day prediction
      if (data.predictions["30d"] !== undefined) {
        const date = new Date(now);
        date.setDate(date.getDate() + 30);
        chartData.push({
          date: date.toISOString(),
          label: '30d',
          historical: null,
          predicted: data.predictions["30d"],
          upper: data.predictions["30d"] * 1.15,
          lower: data.predictions["30d"] * 0.85
        });
      }
      
      // 90 day prediction
      if (data.predictions["90d"] !== undefined) {
        const date = new Date(now);
        date.setDate(date.getDate() + 90);
        chartData.push({
          date: date.toISOString(),
          label: '90d',
          historical: null,
          predicted: data.predictions["90d"],
          upper: data.predictions["90d"] * 1.20,
          lower: data.predictions["90d"] * 0.80
        });
      }
    }
    
    return chartData;
  };
  
  // Generate the chart data
  const chartData = createChartData();

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
                dataKey="label"
                minTickGap={20}
              />
              <YAxis
                domain={['auto', 'auto']}
                tickFormatter={(value) => `$${value.toFixed(2)}`}
              />
              <Tooltip 
                formatter={(value, name) => {
                  if (value === null) return ['-', name];
                  return [`$${Number(value).toFixed(2)}`, name];
                }}
                labelFormatter={(label) => {
                  return label === 'Now' ? 'Current Price' : `Forecast: ${label}`;
                }}
              />
              <Legend />

              {/* Historical line */}
              <Line
                type="monotone"
                dataKey="historical"
                name="Historical"
                stroke="#2563eb"
                strokeWidth={2}
                dot={{ r: 4, strokeWidth: 2 }}
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
                dot={{ r: 4, strokeWidth: 2 }}
                activeDot={{ r: 7 }}
                connectNulls
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
                  connectNulls
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
                  connectNulls
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