import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VisionScope — Reg CF Investment Intelligence",
  description: "Bloomberg Terminal-style analytics for startup equity investments. Educational use only.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen" style={{ background: "#0a0e17" }}>
        {children}
      </body>
    </html>
  );
}
