import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VisionScope | Institutional Startup Intelligence",
  description: "Bloomberg Terminal-style analytics platform democratizing startup investing for retail investors.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen" style={{ background: "#060a13" }}>
        {children}
      </body>
    </html>
  );
}
