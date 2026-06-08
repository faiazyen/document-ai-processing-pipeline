import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Document AI Processing Pipeline by MaverickIQ",
  description:
    "Portfolio-grade invoice extraction, validation, and fallback processing for B2B merchandise documents.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full bg-background text-foreground">{children}</body>
    </html>
  );
}
