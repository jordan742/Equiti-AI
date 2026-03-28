"use client";
import { useState } from "react";
import TopBar from "./components/nav/TopBar";
import TabNav from "./components/nav/TabNav";
import MarketTicker from "./components/nav/MarketTicker";
import ScreenerView from "./components/screener/ScreenerView";
import PortfolioView from "./components/portfolio/PortfolioView";
import MarketplaceView from "./components/marketplace/MarketplaceView";
import ComplianceView from "./components/compliance/ComplianceView";
import GuardrailView from "./components/guardrail/GuardrailView";
import DisclaimerFooter from "./components/shared/DisclaimerFooter";

const TABS = ["SCREENER", "PORTFOLIO", "MARKETPLACE", "COMPLIANCE", "GUARDRAIL"] as const;
type Tab = typeof TABS[number];

export default function Home() {
  const [activeTab, setActiveTab] = useState<Tab>("SCREENER");

  return (
    <div className="min-h-screen flex flex-col" style={{ background: "#060a13" }}>
      <TopBar />
      <TabNav tabs={[...TABS]} active={activeTab} onChange={(t) => setActiveTab(t as Tab)} />
      <MarketTicker />

      <main className="flex-1 px-4 py-4 max-w-screen-2xl mx-auto w-full">
        {activeTab === "SCREENER"     && <ScreenerView />}
        {activeTab === "PORTFOLIO"    && <PortfolioView />}
        {activeTab === "MARKETPLACE"  && <MarketplaceView />}
        {activeTab === "COMPLIANCE"   && <ComplianceView />}
        {activeTab === "GUARDRAIL"    && <GuardrailView />}
      </main>

      <DisclaimerFooter />
    </div>
  );
}
