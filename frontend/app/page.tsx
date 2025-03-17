"use client";

import Navbar from '@/components/Navbar';
import Analyze from '@/components/Analyze';
import { Toaster } from 'sonner';
import ChatInterface from '@/components/ChatInterface';

interface AnalyzeProps {
  messages: any[];
  onSendMessage: (message: string) => Promise<void>;
  sessionId: string | null;
}

export default function AnalyzePage() {
  return (
    <>
      <Navbar />
      <main className="container mx-auto py-6">
        <Analyze
        />
        <ChatInterface />
      </main>
      <Toaster />
    </>
  );
}