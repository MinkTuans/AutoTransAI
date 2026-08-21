import{a as f,c as m}from"./chunk-IJQ4KOXN.js";import{a as F}from"./chunk-DVKCIH7A.js";import"./chunk-6NA7ELBO.js";import{F as w,Y as R}from"./chunk-ACMEWKV4.js";import"./chunk-G5EJHLNE.js";import"./chunk-5FRW4UO4.js";import"./chunk-K3AOJOH2.js";import"./chunk-T5DSHPMV.js";import"./chunk-FFDTKKDT.js";import"./chunk-A4FRP5S3.js";import"./chunk-6P6J5E4Q.js";import"./chunk-5M6YSMA7.js";import"./chunk-7FPALEDT.js";import"./chunk-VQSRXQ54.js";import"./chunk-P43JCO4S.js";import"./chunk-FUOWEUPT.js";import"./chunk-PA2NRDYY.js";import"./chunk-CL5XSPPA.js";import"./chunk-K7GHDVLN.js";import"./chunk-5NHH6Z66.js";import"./chunk-6HGM4SLG.js";import"./chunk-V53E4MU6.js";import"./chunk-6N3EJFJR.js";import"./chunk-CCMUSPWN.js";import"./chunk-WBIHZ7LK.js";import"./chunk-EVDRYYXH.js";import"./chunk-WF3LOBWM.js";import"./chunk-N54X2CUO.js";import"./chunk-VRM2NWAU.js";import"./chunk-EOII3ZM4.js";import"./chunk-RMMVJ6R3.js";import"./chunk-4AQPJCXC.js";import"./chunk-FMMOYV2U.js";import"./chunk-C4LSQOYZ.js";import"./chunk-4VICHEHO.js";import{c as T,d as b}from"./chunk-2EQUCBKU.js";import{Za as s}from"./chunk-D3BHBSWL.js";import{c as t}from"./chunk-RLWRKBLA.js";import"./chunk-HRSMUG5A.js";import"./chunk-M3TVHC7T.js";import"./chunk-KS7AKYDM.js";import"./chunk-IT2EKJZQ.js";import"./chunk-R6A7JGWU.js";import"./chunk-RKVM6QQ3.js";import"./chunk-6SLFKWVX.js";import"./chunk-OY47TOHT.js";import"./chunk-G2YN7S6F.js";import"./chunk-V6Q45TV4.js";import"./chunk-S47GYCJH.js";import"./chunk-UPPQC44E.js";import"./chunk-OJPBMZQC.js";import"./chunk-3VGVYQIC.js";import"./chunk-CYENH7PC.js";import"./chunk-44KDTK4M.js";import"./chunk-3SRDKZHE.js";import"./chunk-2TCOJUYX.js";import"./chunk-3CHZKZ7J.js";import{Nb as B,qb as l,xb as x}from"./chunk-QPUEUZLS.js";import"./chunk-TWVSBOL5.js";import{Hb as I,e as M,f as h,sb as a,t as C}from"./chunk-ROW53IBC.js";import"./chunk-TPWF5M5V.js";import"./chunk-PPRUN2KR.js";import"./chunk-U7OZEJ4F.js";import"./chunk-ZRGHR2IN.js";import{a as d,g as c,i as y,n as g}from"./chunk-TSHWMJEM.js";y();g();var k=c(M(),1);var n=c(h(),1),E=t.div`
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  overflow-y: scroll;
`,N=t.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 90px;
`,S=t(s).attrs({size:28,weight:500,color:a.colors.legacy.textBase})`
  margin: 16px;
`,V=t(s).attrs({size:14,weight:400,lineHeight:17,color:a.colors.legacy.textDiminished})`
  max-width: 275px;

  span {
    color: white;
  }
`,$=d(({networkId:o,token:r})=>{let{t:e}=C(),{handleHideModalVisibility:p}=R(),u=(0,k.useCallback)(()=>{p("insufficientBalance")},[p]),v=o&&x(B(l.getChainID(o))),{canBuy:P,openBuy:D}=w({caip19:v||"",context:"modal",analyticsEvent:"fiatOnrampFromInsufficientBalance",entryPoint:"insufficientBalance"}),i=o?l.getTokenSymbol(o):e("tokens");return(0,n.jsxs)(E,{children:[(0,n.jsx)("div",{children:(0,n.jsxs)(N,{children:[(0,n.jsx)(F,{type:"failure",backgroundWidth:75}),(0,n.jsx)(S,{children:e("insufficientBalancePrimaryText",{tokenSymbol:i})}),(0,n.jsx)(V,{children:e("insufficientBalanceSecondaryText",{tokenSymbol:i})}),r?(0,n.jsxs)(I,{borderRadius:8,gap:1,marginTop:32,width:"100%",children:[(0,n.jsx)(f,{label:e("insufficientBalanceRemaining"),children:(0,n.jsx)(m,{color:a.colors.legacy.spotNegative,children:`${r.balance} ${i}`})}),(0,n.jsx)(f,{label:e("insufficientBalanceRequired"),children:(0,n.jsx)(m,{children:`${r.required} ${i}`})})]}):null]})}),P?(0,n.jsx)(b,{primaryText:e("buyAssetInterpolated",{tokenSymbol:i}),onPrimaryClicked:D,secondaryText:e("commandCancel"),onSecondaryClicked:u}):(0,n.jsx)(T,{onClick:u,children:e("commandCancel")})]})},"InsufficientBalance"),X=$;export{$ as InsufficientBalance,X as default};
//# sourceMappingURL=InsufficientBalance-DGPZ7LHI.js.map
