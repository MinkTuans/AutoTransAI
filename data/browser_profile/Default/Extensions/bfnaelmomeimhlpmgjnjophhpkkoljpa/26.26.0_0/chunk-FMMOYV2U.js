import{b as d}from"./chunk-C4LSQOYZ.js";import{M as s,Za as D}from"./chunk-D3BHBSWL.js";import{c as i}from"./chunk-RLWRKBLA.js";import{b as k,c as B}from"./chunk-HRSMUG5A.js";import{tb as C}from"./chunk-OY47TOHT.js";import{a as m}from"./chunk-G2YN7S6F.js";import{b as w}from"./chunk-S47GYCJH.js";import{e as F,f as y,sb as t,t as T}from"./chunk-ROW53IBC.js";import{m as c}from"./chunk-PPRUN2KR.js";import{a as e,g as f,i as b,n as E}from"./chunk-TSHWMJEM.js";b();E();var g=f(F(),1);var r=f(y(),1),P="Unknown Error",S="Looks like you ran into an unknown error. Please close Phantom and try again.",H="Close",h=i(D).attrs({wordBreak:"break-word",color:t.colors.legacy.textDiminished,size:16,lineHeight:20.8,maxWidth:"400px"})``,x=i.a.attrs({target:"_blank",rel:"noopener noreferrer"})`
  display: flex;
  align-items: center;
  margin: 0 auto;
  color: ${t.colors.legacy.spotBase};
  text-decoration: none;
  cursor: pointer;
  svg {
    fill: ${t.colors.legacy.spotBase};
    margin-right: 5px;
  }
`,R=e(o=>(0,r.jsx)(m,{fallback:a=>a instanceof C?(0,r.jsx)(A,{}):o.fallback,children:o.children}),"ErrorBoundaryWithDefaultFallback"),A=e(()=>{let{t:o}=T(),a=e(()=>{w.capture("walletScreenErrorBoundaryClosed"),self.close()},"onClose");return(0,r.jsx)(L,{children:(0,r.jsxs)(d,{icon:"error",title:o("transactionsDisabledTitle"),buttonText:o("commandClose"),onClose:a,children:[(0,r.jsx)(h,{margin:"0 0 5px 0",children:o("transactionsDisabledMessage")}),(0,r.jsxs)(x,{href:c,onClick:a,children:[(0,r.jsx)(s,{}),"Help & Support"]})]})})},"WalletScreenErrorFallback"),L=i.main`
  width: ${k}px;
  height: ${B}px;
  padding: 15px;
`,Q=e(({title:o=P,message:a=S,buttonText:l=H,onReset:n=e(()=>self.close(),"onReset"),children:p})=>{let u=(0,g.useMemo)(()=>(0,r.jsx)(N,{children:(0,r.jsxs)(d,{icon:"error",title:o,buttonText:l,onClose:n,children:[(0,r.jsx)(h,{margin:"0 0 5px 0",children:a}),(0,r.jsxs)(x,{href:c,onClick:n,children:[(0,r.jsx)(s,{}),"Help & Support"]})]})}),[o,a,l,n]);return(0,r.jsx)(R,{fallback:u,children:p})},"PopupAndNotificationErrorBoundary"),N=i.main`
  min-width: ${k}px;
  height: 100vh;
  padding: 15px;
  width: 100vw;
`,V=e(({title:o=P,message:a="Looks like you ran into an unknown error. Please refresh the page and try again.",buttonText:l="Refresh",onReset:n=e(()=>self.location.reload(),"onReset"),children:p})=>{let u=(0,g.useMemo)(()=>(0,r.jsx)(_,{children:(0,r.jsxs)(d,{icon:"error",title:o,buttonText:l,onClose:n,children:[(0,r.jsx)(h,{margin:"0 0 5px 0",children:a}),(0,r.jsxs)(x,{href:c,onClick:n,children:[(0,r.jsx)(s,{}),"Help & Support"]})]})}),[o,a,l,n]);return(0,r.jsx)(R,{fallback:u,children:p})},"OnboardingAndConnectHardwareErrorBoundary"),_=i.main`
  box-shadow: 0px 10px 20px rgba(0, 0, 0, 0.3);
  width: 400px;
  height: 450px;
  background-color: ${t.colors.legacy.areaBase};
  border: 1px solid ${t.colors.legacy.borderDiminished};
  border-radius: 8px;
  position: relative;
  overflow: hidden;
  padding: 20px;
`;export{R as a,Q as b,V as c};
//# sourceMappingURL=chunk-FMMOYV2U.js.map
