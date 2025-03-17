"use client";

import Navbar from '@/components/Navbar';
import Analyze from '@/components/Analyze';
import { Toaster } from 'sonner';

export default function AnalyzePage() {
  return (
    <>
      <Navbar />
      <main className="container mx-auto py-6">
        <Analyze />
      </main>
      <Toaster />
    </>
  );
}