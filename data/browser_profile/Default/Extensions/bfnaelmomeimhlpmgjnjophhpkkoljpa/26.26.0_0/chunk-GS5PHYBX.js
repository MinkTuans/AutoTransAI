import{a as h}from"./chunk-DVKCIH7A.js";import{f as k}from"./chunk-VQSRXQ54.js";import{c as b}from"./chunk-2EQUCBKU.js";import{M as T,Za as l}from"./chunk-D3BHBSWL.js";import{b as y,c as i}from"./chunk-RLWRKBLA.js";import{$b as d,Xb as m,f as x,sb as n,t as C}from"./chunk-ROW53IBC.js";import{a as r,g as w,i as S,n as f}from"./chunk-TSHWMJEM.js";S();f();var t=w(x(),1),B=i.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  width: 100%;
  padding: ${o=>o.addScreenPadding?"16px":"0"};
`,A=i.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex-grow: 1;
`,D=i.div`
  width: 100%;
  > * {
    margin-top: 10px;
  }
  padding: 16px;
`,R=i.div`
  display: flex;
  justify-content: flex-end;
  position: absolute;
  width: 100%;
  padding: 16px;
`,$=i.div`
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
`,X=i.div`
  position: relative;
`,Y=i.div`
  position: absolute;
  top: 0;
  height: 100%;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  svg {
    fill: ${n.colors.legacy.spotPositive};
  }
`,N=i(l).attrs({size:28,weight:500,color:n.colors.legacy.textBase})`
  margin-top: 24px;
  margin-left: 12px;
  margin-right: 12px;
`,v=i(l).attrs({size:16,weight:400,color:n.colors.legacy.textDiminished})`
  margin-top: 9px;
  margin-left: 12px;
  margin-right: 12px;
  span {
    color: ${n.colors.legacy.textDiminished};
    font-weight: bold;
  }
`,I=i(l).attrs({size:16,weight:500,color:n.colors.legacy.spotBase})`
  margin-top: 18px;
  text-decoration: none;
  ${o=>o.opacity!==0&&y`
      &:hover {
        cursor: pointer;
        color: ${n.colors.legacy.spotAccent};
      }
    `}
`,E=r(({description:o,header:a,icon:s,onClose:e,title:c,txLink:p,isClosable:g,disclaimer:P})=>{let{t:u}=C(),L=r(()=>{p&&self.open(p)},"onViewTransactionClick");return(0,t.jsxs)(B,{children:[a,(0,t.jsxs)(A,{children:[(0,t.jsx)(m,{mode:"wait",initial:!0,children:(0,t.jsx)(d.div,{initial:{opacity:0},animate:{opacity:1},exit:{opacity:0},transition:{duration:.2},children:s},c)}),(0,t.jsx)(N,{children:c}),(0,t.jsx)(v,{children:o}),p&&(0,t.jsx)(m,{mode:"wait",initial:!1,children:(0,t.jsx)(d.div,{initial:{opacity:0,y:16},animate:{opacity:1,y:0},exit:{opacity:0},transition:{duration:.2},children:(0,t.jsx)(I,{opacity:1,onClick:L,children:u("swapTxConfirmationViewTransaction")})},p)})]}),g&&e?(0,t.jsxs)(D,{children:[(0,t.jsx)(v,{children:P}),g&&e?(0,t.jsx)(b,{onClick:e,children:u("commandClose")}):null]}):null]})},"SwapStatus");var Z=r(({ledgerAction:o,numberOfTransactions:a,cancel:s,ledgerApp:e})=>(0,t.jsx)(B,{addScreenPadding:!0,children:(0,t.jsx)(k,{ledgerAction:o,numberOfTransactions:a,cancel:s,ledgerApp:e})}),"SwapStatusLedger");var F=r(o=>self.open(o,"_blank"),"openSupportLink"),tt=r(({txErrorTitle:o,txErrorMessage:a,txErrorHelpButtonLink:s,txLink:e,onClose:c})=>(0,t.jsx)(E,{header:(0,t.jsx)(R,{children:(0,t.jsx)($,{onClick:()=>F(s),children:(0,t.jsx)(T,{fill:"white"})})}),icon:(0,t.jsx)(h,{type:"failure"}),description:a,onClose:c,title:o,txLink:e,isClosable:!0}),"SwapStatusError");export{Z as a,tt as b};
//# sourceMappingURL=chunk-GS5PHYBX.js.map
