import type{Company}from"./types";
export function score(c:Company):number{
  let s=0;
  const run=c.cash/c.burn;if(run>18)s+=25;else if(run>12)s+=20;else if(run>6)s+=14;else if(run>3)s+=7;else s+=2;
  const g=c.growth;if(g>80)s+=25;else if(g>50)s+=20;else if(g>25)s+=14;else if(g>0)s+=7;else s+=1;
  const dr=c.xbrl.assets>0?c.debt/c.xbrl.assets:1;if(dr<.15)s+=15;else if(dr<.3)s+=11;else if(dr<.5)s+=6;else s+=2;
  const cov=c.burn>0?c.revenue/c.burn:0;if(cov>1)s+=20;else if(cov>.5)s+=15;else if(cov>.2)s+=9;else if(cov>.05)s+=4;else s+=1;
  const cr=c.xbrl.liabilities>0?c.xbrl.assets/c.xbrl.liabilities:10;if(cr>3)s+=15;else if(cr>2)s+=12;else if(cr>1)s+=8;else s+=2;
  return Math.min(100,Math.max(0,s));
}
export type Label="STRONG"|"MODERATE"|"CAUTION"|"HIGH RISK";
export function label(s:number):Label{if(s>=75)return"STRONG";if(s>=55)return"MODERATE";if(s>=35)return"CAUTION";return"HIGH RISK";}
export function scoreColor(s:number):string{if(s>=75)return"#00d4aa";if(s>=55)return"#2e6cf6";if(s>=35)return"#ffb830";return"#ff4757";}
