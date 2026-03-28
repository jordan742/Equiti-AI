export function fm(n:number,compact=false):string{
  if(compact){if(Math.abs(n)>=1_000_000)return`$${(n/1_000_000).toFixed(1)}M`;if(Math.abs(n)>=1_000)return`$${(n/1_000).toFixed(0)}K`;return`$${n.toFixed(0)}`;}
  return new Intl.NumberFormat("en-US",{style:"currency",currency:"USD",maximumFractionDigits:0}).format(n);
}
export function pct(n:number,d=1):string{return`${n>=0?"+":""}${n.toFixed(d)}%`;}
export function months(cash:number,burn:number):string{const m=cash/burn;if(m<2)return`${(m*4.33).toFixed(0)} wks`;return`${m.toFixed(1)} mo`;}
