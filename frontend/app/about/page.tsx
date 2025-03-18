export default function AboutPage() {
    return (
      <main className="container mx-auto py-6">
        <h1 className="text-3xl font-bold mb-6">About Tradi</h1>
        
        <div className="prose prose-stone max-w-none">
          <p>
            Tradi is an AI-powered trading analysis platform designed to help traders make informed decisions.
            By combining technical analysis with artificial intelligence, Tradi provides insights, predictions,
            and recommendations for trading strategies.
          </p>
          
          <h2>Key Features</h2>
          <ul>
            <li>Real-time technical analysis with multiple indicators</li>
            <li>AI-powered trading insights and recommendations</li>
            <li>Price prediction using machine learning models</li>
            <li>Interactive charts with customizable timeframes</li>
            <li>Conversational interface for exploring market data</li>
          </ul>
          
          <h2>Technology Stack</h2>
          <p>
            Tradi is built using modern technologies including Next.js, React, TypeScript, 
            Flask, Pandas, and various AI/ML libraries. The platform leverages advanced
            algorithms to analyze market data and generate predictions.
          </p>
          
          <h2>About the Team</h2>
          <p>
            Tradi was developed by a team of financial experts and software engineers
            passionate about making advanced trading analysis accessible to everyone.
          </p>
        </div>
      </main>
    );
  }