import{e as O}from"./chunk-FFIY7B6A.js";import{Y as h}from"./chunk-ACMEWKV4.js";import"./chunk-G5EJHLNE.js";import"./chunk-5FRW4UO4.js";import"./chunk-K3AOJOH2.js";import"./chunk-T5DSHPMV.js";import"./chunk-FFDTKKDT.js";import"./chunk-A4FRP5S3.js";import"./chunk-6P6J5E4Q.js";import"./chunk-5M6YSMA7.js";import"./chunk-7FPALEDT.js";import"./chunk-VQSRXQ54.js";import"./chunk-P43JCO4S.js";import"./chunk-FUOWEUPT.js";import"./chunk-PA2NRDYY.js";import"./chunk-CL5XSPPA.js";import"./chunk-K7GHDVLN.js";import"./chunk-5NHH6Z66.js";import"./chunk-6HGM4SLG.js";import"./chunk-V53E4MU6.js";import"./chunk-6N3EJFJR.js";import"./chunk-CCMUSPWN.js";import"./chunk-WBIHZ7LK.js";import"./chunk-EVDRYYXH.js";import"./chunk-WF3LOBWM.js";import"./chunk-N54X2CUO.js";import"./chunk-VRM2NWAU.js";import"./chunk-GHSB2TGN.js";import"./chunk-EOII3ZM4.js";import"./chunk-RMMVJ6R3.js";import"./chunk-4AQPJCXC.js";import"./chunk-FMMOYV2U.js";import"./chunk-C4LSQOYZ.js";import"./chunk-4VICHEHO.js";import{d as x}from"./chunk-2EQUCBKU.js";import{$ as C,Za as l}from"./chunk-D3BHBSWL.js";import{c as r}from"./chunk-RLWRKBLA.js";import"./chunk-HRSMUG5A.js";import"./chunk-M3TVHC7T.js";import"./chunk-KS7AKYDM.js";import"./chunk-IT2EKJZQ.js";import"./chunk-R6A7JGWU.js";import"./chunk-RKVM6QQ3.js";import{F as g,gb as v}from"./chunk-6SLFKWVX.js";import"./chunk-OY47TOHT.js";import{b as w}from"./chunk-G2YN7S6F.js";import"./chunk-V6Q45TV4.js";import"./chunk-S47GYCJH.js";import"./chunk-UPPQC44E.js";import"./chunk-OJPBMZQC.js";import"./chunk-3VGVYQIC.js";import"./chunk-CYENH7PC.js";import"./chunk-44KDTK4M.js";import"./chunk-3SRDKZHE.js";import"./chunk-2TCOJUYX.js";import"./chunk-3CHZKZ7J.js";import"./chunk-QPUEUZLS.js";import"./chunk-TWVSBOL5.js";import{e as b,f as y,sb as i,t as T}from"./chunk-ROW53IBC.js";import"./chunk-TPWF5M5V.js";import{o as S,p as u}from"./chunk-PPRUN2KR.js";import"./chunk-U7OZEJ4F.js";import"./chunk-ZRGHR2IN.js";import{a as t,g as s,i as d,n as f}from"./chunk-TSHWMJEM.js";d();f();var a=s(b(),1);var e=s(y(),1),P=r.div`
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: center;
  height: 100%;
  width: 100%;
  overflow-y: scroll;
  padding: 16px;
`,A=r.div`
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  margin-top: -20px;
`,B=r(l).attrs({size:28,weight:500,color:i.colors.legacy.textBase})`
  margin-top: 24px;
`,M=r(l).attrs({size:16,weight:500,color:i.colors.legacy.textDiminished})`
  padding: 0px 5px;
  margin-top: 9px;
  span {
    color: ${i.colors.legacy.textBase};
  }
  label {
    color: ${i.colors.legacy.spotBase};
    cursor: pointer;
  }
`,F=r.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  height: fit-content;
`,L=r.div`
  margin-top: auto;
  width: 100%;
`,_=t(()=>{let{t:n}=T(),{mutateAsync:c}=O(),{handleHideModalVisibility:o,handleShowModalVisibility:m}=h(),k=(0,a.useCallback)(()=>{m("swapConfirmation",void 0,{event:"showSwapModal",payload:{data:{uiContext:g.SwapConfirmation}}}),o("swapTermsOfService")},[m,o]),p=v({goToConfirmation:k});return{onAgreeClick:(0,a.useCallback)(()=>{c(!0),p()},[c,p]),onCancelClick:t(()=>{o("swapTermsOfService")},"onCancelClick"),t:n}},"useSwapTermsOfServiceProps"),R=t(()=>{self.open(S,"_blank")},"handleTermsClick"),V=t(()=>{self.open(u,"_blank")},"handleFeesClick"),E=a.default.memo(({onAgreeClick:n,onCancelClick:c,t:o})=>(0,e.jsxs)(P,{children:[(0,e.jsx)(A,{children:(0,e.jsxs)(F,{children:[(0,e.jsx)(C,{}),(0,e.jsx)(B,{children:o("termsOfServicePrimaryText")}),(0,e.jsx)(M,{children:(0,e.jsxs)(w,{i18nKey:"termsOfServiceDiscliamerFeesEnabledInterpolated",children:["We have revised our Terms of Service. By clicking ",(0,e.jsx)("span",{children:'"I Agree"'})," you agree to our new",(0,e.jsx)("label",{onClick:R,children:"Terms of Service"}),".",(0,e.jsx)("br",{}),(0,e.jsx)("br",{}),"Our new Terms of Service include a new ",(0,e.jsx)("label",{onClick:V,children:"fee structure"})," for certain products."]})})]})}),(0,e.jsx)(L,{children:(0,e.jsx)(x,{primaryText:o("termsOfServiceActionButtonAgree"),secondaryText:o("commandCancel"),onPrimaryClicked:n,onSecondaryClicked:c})})]})),H=t(()=>{let n=_();return(0,e.jsx)(E,{...n})},"SwapTermsOfServicePage"),Z=H;export{H as SwapTermsOfServicePage,Z as default};
//# sourceMappingURL=SwapTermsOfServicePage-UK5DDQGT.js.map
