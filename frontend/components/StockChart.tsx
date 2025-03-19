import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';


export interface StockData {
  dates: string[];
  price: number[];
  short_mavg: number[];
  long_mavg: number[];
  positions: number[];
}


interface StockChartProps {
  data: StockData;
}

const StockChart: React.FC<StockChartProps> = ({ data }) => {
  // Transform the array data into the format expected by recharts
  console.log(data);
  const chartData = data.dates.map((date, index) => {
    // Create buy/sell points based on positions
    const position = data.positions?.[index] || 0;
    let buyPoint = null;
    let sellPoint = null;

    if (position === 1) {
      buyPoint = data.price[index];
    } else if (position === -1) {
      sellPoint = data.price[index];
    }
    console.log(position);
    return {
      date,
      price: data.price[index],
      short_mavg: data.short_mavg?.[index] || null,
      long_mavg: data.long_mavg?.[index] || null,
      buyPoint,
      sellPoint
    };
  });
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart
        data={chartData}
        margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 12 }}
          tickFormatter={(date) => {
            const d = new Date(date);
            return `${d.getMonth() + 1}/${d.getDate()}`;
          }}
          minTickGap={30}
        />
        <YAxis
          domain={['auto', 'auto']}
          tick={{ fontSize: 12 }}
          tickFormatter={(value) => `$${value.toFixed(0)}`}
        />
        
        <Tooltip
          formatter={(value: any) => [`$${Number(value).toFixed(2)}`, undefined]}
          labelFormatter={(label) => new Date(label).toLocaleDateString()}
        />
        <Legend />

        {/* Main price line */}
        <Line
          type="monotone"
          dataKey="price"
          stroke="#2563eb"
          name="Price"
          dot={false}
          strokeWidth={2}
          activeDot={{ r: 6, strokeWidth: 0 }}
        />

        {/* Moving averages */}
        <Line
          type="monotone"
          dataKey="short_mavg"
          stroke="#22c55e"
          name="Short MA"
          dot={false}
          strokeDasharray="5 5"
          strokeWidth={1.5}
        />
        <Line
          type="monotone"
          dataKey="long_mavg"
          stroke="#ef4444"
          name="Long MA"
          dot={false}
          strokeDasharray="5 5"
          strokeWidth={1.5}
        />

        {/* Buy points */}
        <Line
          type="monotone"
          dataKey="buyPoint"
          stroke="#16a34a"
          name="Buy Signal"
          dot={{ r: 6, strokeWidth: 2, fill: "white" }}
          activeDot={{ r: 8 }}
        />

        {/* Sell points */}
        <Line
          type="monotone"
          dataKey="sellPoint"
          stroke="#dc2626"
          name="Sell Signal"
          dot={{ r: 6, strokeWidth: 2, fill: "white" }}
          activeDot={{ r: 8 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default StockChart;