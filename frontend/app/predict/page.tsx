"use client";

import PredictionPage from "@/components/PredictionPage";
import { Toaster } from 'sonner';

export default function PredictionsPage() {
  return (
    <main className="container mx-auto py-6">
      <PredictionPage />
      <Toaster />
    </main>
  );
}