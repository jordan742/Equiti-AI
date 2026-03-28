export interface Company {
  id:string; name:string; sector:string; stage:string; platform:string; location:string;
  status:"Live"|"Closed"; security:"SAFE"|"Preferred Equity"; pricePerShare:number;
  raised:number; target:number; valuationCap:number; investors:number;
  cash:number; burn:number; revenue:number; growth:number; margin:number; debt:number;
  quarterlyRevenue:number[]; quarterlyBurn:number[]; quarterlyCash:number[];
  quarterlyCustomers:number[]; quarterLabels:string[];
  xbrl:{assets:number;liabilities:number;equity:number;revenueTTM:number;netIncome:number;};
  risks:string[]; useOfProceeds:Record<string,number>;
  ai:{verdict:string;conviction:"HIGH"|"MODERATE"|"LOW";risk:number;plainEnglish:string;summary:string;bull:string;bear:string;};
  market:{ask:number;bid:number;vol:number;trades:number;};
}
