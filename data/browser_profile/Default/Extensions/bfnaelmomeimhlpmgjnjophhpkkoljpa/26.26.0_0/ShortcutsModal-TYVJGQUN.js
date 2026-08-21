import{a as A,c as B}from"./chunk-TVMERHEX.js";import{a as V}from"./chunk-GO2OCDS6.js";import{c as G}from"./chunk-2EQUCBKU.js";import{Aa as L,Ba as T,Ca as v,Da as C,Ea as M,Fa as P,Ga as b,Ha as D,Ia as R,Ja as W,Ka as l,La as F,Za as O,ta as S,ua as f,va as h,wa as x,xa as k,ya as y,za as w}from"./chunk-D3BHBSWL.js";import{c as o}from"./chunk-RLWRKBLA.js";import{b as g}from"./chunk-S47GYCJH.js";import"./chunk-UPPQC44E.js";import"./chunk-OJPBMZQC.js";import"./chunk-3VGVYQIC.js";import"./chunk-CYENH7PC.js";import"./chunk-44KDTK4M.js";import"./chunk-3CHZKZ7J.js";import"./chunk-QPUEUZLS.js";import"./chunk-TWVSBOL5.js";import{e as E,f as p,sb as d,t as I}from"./chunk-ROW53IBC.js";import"./chunk-TPWF5M5V.js";import"./chunk-PPRUN2KR.js";import"./chunk-U7OZEJ4F.js";import"./chunk-ZRGHR2IN.js";import{a as i,g as c,i as s,n as a}from"./chunk-TSHWMJEM.js";s();a();var z=c(E(),1);s();a();var U=c(p(),1),Y={[V]:l,vote:T,"vote-2":v,stake:C,"stake-2":M,view:P,chat:b,tip:D,mint:R,"mint-2":W,"generic-link":l,"generic-add":F,discord:S,twitter:f,"twitter-2":h,x:h,instagram:x,telegram:k,leaderboard:L,gaming:y,"gaming-2":w};function N({icon:r,...n}){let m=Y[r];return(0,U.jsx)(m,{...n})}i(N,"ShortcutsIcon");var t=c(p(),1),_=o.div`
  width: 100%;
  display: flex;
  flex-direction: column;
  margin-top: -16px; // compensate for generic screen margins
`,q=o.footer`
  margin-top: auto;
  flex-shrink: 0;
  min-height: 16px;
`,J=o.div`
  overflow: scroll;
`,K=o.ul`
  flex: 1;
  max-height: 350px;
  padding-top: 16px; // compensate for the override of the generic screen margins
`,Q=o.li``,X=o.div`
  display: flex;
  align-items: center;
  padding: 6px 12px;
`,Z=o(O).attrs(r=>({margin:r.margin??"12px 0px"}))`
  text-align: left;
`;function $({shortcuts:r,...n}){let{t:m}=I(),u=(0,z.useMemo)(()=>n.hostname.includes("//")?new URL(n.hostname).hostname:n.hostname,[n.hostname]);return(0,t.jsxs)(_,{children:[(0,t.jsx)(J,{children:(0,t.jsx)(K,{children:r.map(e=>(0,t.jsx)(Q,{children:(0,t.jsxs)(G,{type:"button",onClick:()=>{g.capture("walletShortcutsLinkOpenClick",A(n,e)),self.open(e.uri)},theme:"text",paddingY:6,children:[(0,t.jsx)(X,{children:(0,t.jsx)(N,{icon:B(e.uri,e.icon)})}),e.label]})},e.uri))})}),(0,t.jsx)(q,{children:u&&(0,t.jsx)(Z,{color:d.colors.legacy.textDiminished,size:14,lineHeight:17,children:m("shortcutsWarningDescription",{url:u})})})]})}i($,"ShortcutsModal");var It=$;export{$ as ShortcutsModal,It as default};
//# sourceMappingURL=ShortcutsModal-TYVJGQUN.js.map
