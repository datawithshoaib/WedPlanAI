import type { Metadata } from "next";
import { Cormorant_Garamond, Inter } from "next/font/google";

import { HealthProvider } from "@/components/health-provider";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { Toaster } from "@/components/ui/sonner";
import "./globals.css";

const sans = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const serif = Cormorant_Garamond({
  variable: "--font-cormorant",
  weight: ["500", "600", "700"],
  style: ["normal", "italic"],
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: {
    default: "WedPlannerAI — Multi-Agent Wedding Planner",
    template: "%s · WedPlannerAI",
  },
  description:
    "Describe your wedding brief and let a team of research agents build a client-ready planning strategy with budget, timeline, and tradeoffs.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${sans.variable} ${serif.variable} h-full antialiased`}>
      <body className="flex min-h-full flex-col">
        <HealthProvider>
          <SiteHeader />
          <main className="hero-glow flex-1">{children}</main>
          <SiteFooter />
          <Toaster richColors position="top-center" />
        </HealthProvider>
      </body>
    </html>
  );
}
