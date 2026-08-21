import{a as N,c as F,d as G,g as I}from"./chunk-BD3X2VAW.js";import{a as x}from"./chunk-SPDMWR4Q.js";import"./chunk-DVKCIH7A.js";import{a as D}from"./chunk-LO363DVC.js";import"./chunk-63ST3ZAN.js";import"./chunk-CLUQU7WM.js";import"./chunk-AFULND2K.js";import"./chunk-MRYXFGDC.js";import"./chunk-ACMEWKV4.js";import"./chunk-G5EJHLNE.js";import"./chunk-5FRW4UO4.js";import"./chunk-K3AOJOH2.js";import"./chunk-T5DSHPMV.js";import"./chunk-FFDTKKDT.js";import"./chunk-A4FRP5S3.js";import{a as L}from"./chunk-6P6J5E4Q.js";import"./chunk-5M6YSMA7.js";import"./chunk-7FPALEDT.js";import"./chunk-VQSRXQ54.js";import"./chunk-P43JCO4S.js";import"./chunk-FUOWEUPT.js";import"./chunk-PA2NRDYY.js";import"./chunk-CL5XSPPA.js";import"./chunk-K7GHDVLN.js";import"./chunk-5NHH6Z66.js";import"./chunk-6HGM4SLG.js";import"./chunk-V53E4MU6.js";import{a as C}from"./chunk-6N3EJFJR.js";import"./chunk-CCMUSPWN.js";import"./chunk-O33ZUXR5.js";import"./chunk-WBIHZ7LK.js";import"./chunk-EVDRYYXH.js";import"./chunk-WF3LOBWM.js";import"./chunk-N54X2CUO.js";import"./chunk-VRM2NWAU.js";import"./chunk-OH3W2BRU.js";import"./chunk-GHSB2TGN.js";import"./chunk-EOII3ZM4.js";import"./chunk-RMMVJ6R3.js";import"./chunk-4AQPJCXC.js";import"./chunk-FMMOYV2U.js";import"./chunk-C4LSQOYZ.js";import"./chunk-4VICHEHO.js";import"./chunk-2EQUCBKU.js";import{q as _}from"./chunk-D3BHBSWL.js";import{c as s}from"./chunk-RLWRKBLA.js";import{a as y}from"./chunk-QQJPKFTO.js";import"./chunk-HRSMUG5A.js";import"./chunk-M3TVHC7T.js";import"./chunk-KS7AKYDM.js";import"./chunk-IT2EKJZQ.js";import"./chunk-R6A7JGWU.js";import"./chunk-RKVM6QQ3.js";import"./chunk-6SLFKWVX.js";import"./chunk-OY47TOHT.js";import"./chunk-G2YN7S6F.js";import"./chunk-V6Q45TV4.js";import"./chunk-S47GYCJH.js";import"./chunk-UPPQC44E.js";import"./chunk-OJPBMZQC.js";import"./chunk-3VGVYQIC.js";import"./chunk-CYENH7PC.js";import{A as O,s as $}from"./chunk-44KDTK4M.js";import"./chunk-3SRDKZHE.js";import"./chunk-2TCOJUYX.js";import"./chunk-3CHZKZ7J.js";import"./chunk-QPUEUZLS.js";import"./chunk-TWVSBOL5.js";import{$b as T,C as E,U as P,Xb as R,e as z,f as u,sb as e}from"./chunk-ROW53IBC.js";import"./chunk-TPWF5M5V.js";import"./chunk-PPRUN2KR.js";import"./chunk-U7OZEJ4F.js";import"./chunk-ZRGHR2IN.js";import{a as g,g as l,i as n,n as i}from"./chunk-TSHWMJEM.js";n();i();var f=l(z(),1);n();i();n();i();var M=s(C)`
  cursor: pointer;
  width: 24px;
  height: 24px;
  transition: background-color 200ms ease;
  background-color: ${t=>t.$isExpanded?e.colors.legacy.black:e.colors.legacy.elementAccent} !important;
  :hover {
    background-color: ${e.colors.legacy.gray};
    svg {
      fill: white;
    }
  }
  svg {
    fill: ${t=>t.$isExpanded?"white":e.colors.legacy.textDiminished};
    transition: fill 200ms ease;
    position: relative;
    ${t=>t.top?`top: ${t.top}px;`:""}
    ${t=>t.right?`right: ${t.right}px;`:""}
  }
`;var o=l(u(),1),K=s(L).attrs({justify:"space-between"})`
  background-color: ${e.colors.legacy.areaBase};
  padding: 10px 16px;
  border-bottom: 1px solid ${e.colors.legacy.borderDiminished};
  height: 46px;
  opacity: ${t=>t.opacity??"1"};
`,Q=s.div`
  display: flex;
  margin-left: 10px;
  > * {
    margin-right: 10px;
  }
`,W=s.div`
  width: 24px;
  height: 24px;
`,X=g(({onBackClick:t,totalSteps:c,currentStepIndex:d,isHidden:m,showBackButtonOnFirstStep:r,showBackButton:S=!0})=>(0,o.jsxs)(K,{opacity:m?0:1,children:[S&&(r||d!==0)?(0,o.jsx)(M,{right:1,onClick:t,children:(0,o.jsx)(_,{})}):(0,o.jsx)(W,{}),(0,o.jsx)(Q,{children:E(c).map(p=>{let h=p<=d?e.colors.legacy.spotBase:e.colors.legacy.elementAccent;return(0,o.jsx)(C,{diameter:12,color:h},p)})}),(0,o.jsx)(W,{})]}),"StepHeader");n();i();var a=l(u(),1),Z=g(()=>{let{mutateAsync:t}=O(),{hardwareStepStack:c,pushStep:d,popStep:m,currentStep:r,setOnConnectHardwareAccounts:S,setOnConnectHardwareDone:b,setExistingAccounts:p}=N(),{data:h=[],isFetched:H,isError:v}=$(),w=P(c,(k,q)=>k?.length===q.length),J=c.length>(w??[]).length,B=w?.length===0,U={initial:{x:B?0:J?150:-150,opacity:B?1:0},animate:{x:0,opacity:1},exit:{opacity:0},transition:{duration:.2}},V=(0,f.useCallback)(()=>{r()?.props.preventBack||(r()?.props.onBackCallback&&r()?.props.onBackCallback?.(),m())},[r,m]);return D(()=>{S(async k=>{await t(k),await y.set(x,!await y.get(x))}),b(()=>self.close()),d((0,a.jsx)(I,{}))},c.length===0),(0,f.useEffect)(()=>{p({data:h,isFetched:H,isError:v})},[h,H,v,p]),(0,a.jsxs)(F,{children:[(0,a.jsx)(X,{totalSteps:3,onBackClick:V,showBackButton:!r()?.props.preventBack,currentStepIndex:c.length-1}),(0,a.jsx)(R,{mode:"wait",children:(0,a.jsx)(T.div,{style:{display:"flex",flexGrow:1},...U,children:(0,a.jsx)(G,{children:r()})},`${c.length}_${w?.length}`)})]})},"SettingsConnectHardware"),Tt=Z;export{Tt as default};
//# sourceMappingURL=SettingsConnectHardware-SMYX5IJ5.js.map
