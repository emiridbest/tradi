import type { NextApiRequest, NextApiResponse } from 'next';


export interface AnalyzeParams {
  symbol: string;
  timeframe: string;
  interval: string;
  signals?: {
    price: number[];
    short_mavg: number[];
    long_mavg: number[];
    positions: number[];
  };
}

export interface ChatParams {
  message: string;
  session_id: string;
}

export interface ClearParams {
  session_id: string;
}
export  async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  const { symbol, timeframe } = req.query;
  
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/stock-data?symbol=${symbol}&timeframe=${timeframe}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch stock data');
    }
    
    const data = await response.json();
    return res.status(200).json(data);
  } catch (error) {
    console.error('API error:', error);
    return res.status(500).json({ error: 'Failed to fetch stock data' });
  }
}// API handlers for the backend
const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

export const stock = async (params: AnalyzeParams) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/stock-data`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });
    
    if (!response.ok) {
      throw new Error(`Error ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};


export const analyze = async (params: AnalyzeParams) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chart-analysis`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });
    
    if (!response.ok) {
      throw new Error(`Error ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

export const predict = async (params: AnalyzeParams) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });
    
    if (!response.ok) {
      throw new Error(`Error ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

export const chat = async (params: ChatParams) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });
    
    if (!response.ok) {
      throw new Error(`Error ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

export const clear = async (params: ClearParams) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/clear?session_id=${params.session_id}`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error(`Error ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

export const reset = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/reset-model`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error(`Error ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

