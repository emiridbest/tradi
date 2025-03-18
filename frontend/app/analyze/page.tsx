"use client";

import Analyze from "@/components/Analyze";
import { Toaster } from 'sonner';

export default function AnalyzePage() {
  return (
    <main className="container mx-auto py-6">
      <Analyze />
      <Toaster />
    </main>
  );
}