export interface Company {
  id: string;
  name: string;
  sector: string;
  stage: string;
  platform: string;
  status: "Live" | "Closed";
  raised: number;
  target: number;
  valuationCap: number;
  pricePerShare: number;
  securityType: "SAFE" | "Preferred Equity";
  investors: number;
  cashOnHand: number;
  monthlyBurn: number;
  revenue: number;         // MRR
  revenueGrowthPct: number;
  grossMarginPct: number;
  totalDebt: number;
  employees: number;
  location: string;
  ceo: string;
  cto: string;
  description: string;
  filingDate: string;
  formType: string;
  cik: string;
  quarterlyRevenue: number[];
  quarterlyBurn: number[];
  quarterlyCash: number[];
  quarterLabels: string[];
  xbrl: {
    totalAssets: number;
    currentAssets: number;
    cash: number;
    accountsReceivable: number;
    totalLiabilities: number;
    currentLiabilities: number;
    stockholdersEquity: number;
    revenue: number;
    cogs: number;
    operatingExpenses: number;
    netIncome: number;
  };
  riskFactors: string[];
  useOfProceeds: Record<string, number>;
  aiAnalysis: {
    verdict: string;
    conviction: "HIGH" | "MODERATE" | "LOW";
    riskLevel: number;
    plainEnglish: string;
    summary: string;
    bullCase: string;
    bearCase: string;
  };
  market: {
    askPrice: number;
    bidPrice: number;
    volume24h: number;
    trades24h: number;
  };
}

export interface PortfolioPosition {
  ticker: string;
  companyName: string;
  shares: number;
  avgCost: number;
  currentPrice: number;
  totalInvested: number;
  isLocked: boolean;
}

export interface Regulation {
  title: string;
  status: string;
  statusColor: "green" | "amber" | "red" | "blue";
  description: string;
  citation: string;
  effectiveDate?: string;
}

export type ScoreLabel = "STRONG" | "MODERATE" | "CAUTION" | "HIGH RISK";
