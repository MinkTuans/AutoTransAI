import{a as D}from"./chunk-CCMUSPWN.js";import{c as A}from"./chunk-VRM2NWAU.js";import{c as v}from"./chunk-2EQUCBKU.js";import{L as k,Za as C}from"./chunk-D3BHBSWL.js";import{c as e}from"./chunk-RLWRKBLA.js";import{ff as g}from"./chunk-3SRDKZHE.js";import"./chunk-2TCOJUYX.js";import"./chunk-3CHZKZ7J.js";import"./chunk-QPUEUZLS.js";import"./chunk-TWVSBOL5.js";import{Hb as w,cd as b,e as I,f as T,sb as c,t as y}from"./chunk-ROW53IBC.js";import"./chunk-TPWF5M5V.js";import"./chunk-PPRUN2KR.js";import"./chunk-U7OZEJ4F.js";import"./chunk-ZRGHR2IN.js";import{a,g as u,i as f,n as h}from"./chunk-TSHWMJEM.js";f();h();var F=u(I(),1);var o=u(T(),1),H=16,R=e.div`
  width: 100%;
  display: flex;
  flex-direction: column;
  margin-bottom: 16px;
  height: 100%;
`,B=e.div`
  overflow: scroll;
`,M=e.div`
  margin: 45px 16px 16px 16px;
  padding-top: 16px;
`,$=e(A)`
  left: ${H}px;
  position: absolute;
`,z=e.div`
  align-items: center;
  background: ${c.colors.legacy.areaBase};
  border-bottom: 1px solid ${c.colors.legacy.borderDiminished};
  display: flex;
  height: 46px;
  padding: ${H}px;
  position: absolute;
  width: 100%;
  top: 0;
  left: 0;
`,P=e.div`
  display: flex;
  flex: 1;
  justify-content: center;
`,G=e.footer`
  margin-top: auto;
  flex-shrink: 0;
  min-height: 16px;
`,N=e(C).attrs(r=>({margin:r.margin??"12px 0px"}))`
  text-align: left;
`,W=e(C).attrs({size:16,weight:500,lineHeight:25})``;function L(r){let{actions:i,shortcuts:p,trackAction:n,onClose:s}=r;return(0,F.useMemo)(()=>{let m=i.more.map(t=>{let d=g(t.type),l=t.isDestructive?"spotNegative":"textBase";return{start:(0,o.jsx)(d,{size:18,type:t.type,color:l}),topLeft:{text:t.text,color:l},onClick:a(()=>{n(t),s(),t.onClick(t.type)},"onClick")}}),x=p?.map(t=>{let d=g(t.type),l=t.isDestructive?"spotNegative":"textBase";return{start:(0,o.jsx)(d,{size:18,color:l}),topLeft:{text:t.text,color:l},onClick:a(()=>{n(t),s(),t.onClick(t.type)},"onClick")}})??[];return[{rows:m},{rows:x}]},[i,s,p,n])}a(L,"useConvertActionsToRows");function S(r){let{t:i}=y(),{headerText:p,hostname:n,shortcuts:s}=r,m=L(r);return(0,o.jsx)(R,{children:(0,o.jsxs)(B,{children:[(0,o.jsxs)(z,{onClick:r.onClose,children:[(0,o.jsx)($,{children:(0,o.jsx)(k,{})}),(0,o.jsx)(P,{children:(0,o.jsx)(W,{children:p})})]}),(0,o.jsxs)(M,{children:[(0,o.jsx)(w,{gap:"section",children:m.map((x,t)=>(0,o.jsx)(b,{rows:x.rows},`group-${t}`))}),(0,o.jsx)(G,{children:n&&s&&s.length>0&&(0,o.jsx)(N,{color:c.colors.legacy.textDiminished,size:14,lineHeight:17,children:i("shortcutsWarningDescription",{url:n})})})]}),(0,o.jsx)(D,{removeFooterExpansion:!0,children:(0,o.jsx)(v,{onClick:r.onClose,children:i("commandClose")})})]})})}a(S,"CTAModal");var Z=S;export{S as CTAModal,Z as default};
//# sourceMappingURL=Modal-4TSCC2FW.js.map
