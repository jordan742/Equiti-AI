import type { Regulation } from "./types";

export const REGULATIONS: Regulation[] = [
  {
    title: "Regulation Crowdfunding (Reg CF)",
    status: "Active",
    statusColor: "green",
    description: "Permits companies to raise up to $5M per 12-month period from non-accredited investors through SEC-registered funding portals. Sets disclosure requirements, investment limits, and ongoing reporting obligations.",
    citation: "Securities Act 4(a)(6) · 17 CFR Part 227",
    effectiveDate: "May 16, 2016 (amended Mar 15, 2021)",
  },
  {
    title: "Colorado AI Act",
    status: "Effective Jun 30, 2026",
    statusColor: "amber",
    description: "Requires developers and deployers of 'high-risk' AI systems to use reasonable care to protect consumers from known or reasonably foreseeable algorithmic discrimination. Financial scoring tools may fall under this regulation.",
    citation: "C.R.S. 6-1-1701 et seq.",
    effectiveDate: "June 30, 2026",
  },
  {
    title: "EU AI Act — High-Risk Systems",
    status: "Effective Aug 2, 2026",
    statusColor: "amber",
    description: "AI systems used in credit scoring, insurance, and investment decisions are classified as high-risk. Requires conformity assessments, transparency obligations, human oversight, and registration in EU database.",
    citation: "EU Regulation 2024/1689 · Annex III",
    effectiveDate: "August 2, 2026",
  },
  {
    title: "SEC AI-Washing Enforcement",
    status: "Active",
    statusColor: "red",
    description: "SEC actively pursues enforcement actions against firms making false or misleading claims about their AI capabilities. Investment platforms must accurately represent what AI does and does not do in their systems.",
    citation: "Exchange Act §10(b) · Rule 10b-5 · IA Act §206",
  },
  {
    title: "FINRA GenAI Oversight",
    status: "2026 Priority",
    statusColor: "amber",
    description: "FINRA has identified generative AI supervision as a top 2026 exam priority. Broker-dealers using AI for customer communications, recommendations, or analysis must have adequate supervisory systems.",
    citation: "FINRA Rule 3110 · Regulatory Notice 24-09",
  },
  {
    title: "Reg CF Resale Restrictions",
    status: "Active",
    statusColor: "green",
    description: "Securities purchased in Reg CF offerings are restricted for 12 months from the date of purchase. Transfers are limited to the issuer, accredited investors, family members, and in connection with registered offerings.",
    citation: "17 CFR 227.501",
  },
  {
    title: "Form C Annual Reporting",
    status: "Ongoing",
    statusColor: "blue",
    description: "Issuers that have sold securities under Reg CF must file annual reports (Form C-AR) within 120 days of fiscal year end, or terminate reporting obligations under specific conditions.",
    citation: "17 CFR 227.202",
  },
  {
    title: "California ADMT Regulations",
    status: "Effective Jan 1, 2027",
    statusColor: "blue",
    description: "Automated Decision-Making Technology regulations require opt-out rights for consumers subject to significant decisions made by automated systems, with pre-use notices and annual risk assessments.",
    citation: "CCPA Regulations § 7030 et seq.",
    effectiveDate: "January 1, 2027",
  },
];

export const INVESTOR_CHECKLIST = [
  "I understand I may lose my entire investment.",
  "I understand these securities are illiquid for at least 12 months.",
  "I have reviewed the company's Form C filing on SEC EDGAR.",
  "I understand my Reg CF annual investment limit.",
  "I have not exceeded my Reg CF investment limit across all platforms.",
  "I understand this platform is NOT a broker-dealer or investment adviser.",
  "I understand VisionScope scores are informational only, not recommendations.",
  "I have consulted or considered consulting a qualified financial adviser.",
  "I understand the company may fail and I may receive nothing.",
  "I understand there is no guaranteed secondary market for these securities.",
];
