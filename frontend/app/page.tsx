import Link from 'next/link';
import { ArrowRight, ChartLine, Brain, Zap, TrendingUp, BarChart4 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';

export default function HomePage() {
  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <section className="relative bg-gradient-vibrant py-24 overflow-hidden">
        <div className="container mx-auto px-4 relative z-10">
          <div className="flex flex-col items-center text-center max-w-4xl mx-auto">
            <h1 className="text-5xl font-bold tracking-tight sm:text-6xl md:text-7xl mb-6 text-gradient-vibrant">
              Smart Trading Analysis
            </h1>

            <p className="mt-4 text-xl text-white max-w-3xl">
              Get real-time insights, technical analysis, and price predictions
              to make smarter, data-driven trading decisions.
            </p>

            <div className="mt-10 flex flex-wrap justify-center gap-4">
              <Button size="lg" className="btn-gradient rounded-full px-8 h-12 font-medium">
                <Link href="/analyze" className="flex items-center">
                  Start Analyzing <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              <Button variant="outline" size="lg" className="card-glass text-white rounded-full px-8 h-12 font-medium">
                <Link href="/predict">
                  View Predictions
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-background">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4">Powerful Trading Tools</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Everything you need to analyze markets, identify opportunities, and make informed decisions
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <Card className="border bg-card/50 backdrop-blur-sm transition-all duration-300 hover:shadow-md hover:border-primary/20">
              <CardHeader>
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <ChartLine className="h-6 w-6 text-primary" />
                </div>
                <CardTitle className="text-xl">Technical Analysis</CardTitle>
                <CardDescription className="text-muted-foreground">
                  Advanced indicators and signals
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p>Get comprehensive technical analysis with moving averages, trend indicators, and buy/sell signals to identify optimal entry and exit points.</p>
              </CardContent>
              <CardFooter>
                <Link href="/analyze" className="text-primary hover:text-primary/80 inline-flex items-center font-medium">
                  Analyze Charts <ArrowRight className="ml-1 h-4 w-4" />
                </Link>
              </CardFooter>
            </Card>

            <Card className="border bg-card/50 backdrop-blur-sm transition-all duration-300 hover:shadow-md hover:border-primary/20">
              <CardHeader>
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <Brain className="h-6 w-6 text-primary" />
                </div>
                <CardTitle className="text-xl">AI Insights</CardTitle>
                <CardDescription className="text-muted-foreground">
                  Intelligent market interpretations
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p>Our AI analyzes patterns, trends, market sentiment, and news to provide actionable trading insights with contextual reasoning.</p>
              </CardContent>
              <CardFooter>
                <Link href="/analyze" className="text-primary hover:text-primary/80 inline-flex items-center font-medium">
                  Get Insights <ArrowRight className="ml-1 h-4 w-4" />
                </Link>
              </CardFooter>
            </Card>

            <Card className="border bg-card/50 backdrop-blur-sm transition-all duration-300 hover:shadow-md hover:border-primary/20">
              <CardHeader>
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <Zap className="h-6 w-6 text-primary" />
                </div>
                <CardTitle className="text-xl">Price Predictions</CardTitle>
                <CardDescription className="text-muted-foreground">
                  ML-powered forecasting
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p>See where prices might go next with machine learning prediction models trained on historical patterns and current market conditions.</p>
              </CardContent>
              <CardFooter>
                <Link href="/predictions" className="text-primary hover:text-primary/80 inline-flex items-center font-medium">
                  View Predictions <ArrowRight className="ml-1 h-4 w-4" />
                </Link>
              </CardFooter>
            </Card>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-muted/30">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div className="flex flex-col items-center text-center">
              <div className="mb-2">
                <BarChart4 className="h-10 w-10 text-primary/80" />
              </div>
              <div className="mt-2">
                <div className="text-3xl font-bold">1000+</div>
                <div className="text-sm text-muted-foreground">Stocks Analyzed</div>
              </div>
            </div>

            <div className="flex flex-col items-center text-center">
              <div className="mb-2">
                <TrendingUp className="h-10 w-10 text-primary/80" />
              </div>
              <div className="mt-2">
                <div className="text-3xl font-bold">96%</div>
                <div className="text-sm text-muted-foreground">Analysis Accuracy</div>
              </div>
            </div>

            <div className="flex flex-col items-center text-center">
              <div className="mb-2">
                <Brain className="h-10 w-10 text-primary/80" />
              </div>
              <div className="mt-2">
                <div className="text-3xl font-bold">50+</div>
                <div className="text-sm text-muted-foreground">AI Models</div>
              </div>
            </div>

            <div className="flex flex-col items-center text-center">
              <div className="mb-2">
                <Zap className="h-10 w-10 text-primary/80" />
              </div>
              <div className="mt-2">
                <div className="text-3xl font-bold">24/7</div>
                <div className="text-sm text-muted-foreground">Market Monitoring</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-background">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl font-bold mb-6">Ready to elevate your trading strategy?</h2>
            <p className="text-lg text-muted-foreground mb-8">
              Start using our powerful AI-powered trading analysis platform today and make better-informed decisions.
            </p>
            <Button size="lg" className="rounded-full px-8 h-12 font-medium">
              <Link href="/analyze">Get Started For Free</Link>
            </Button>
          </div>
        </div>
      </section>
    </main>
  );
}
