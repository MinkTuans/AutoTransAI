import{Za as c,ia as y,y as T}from"./chunk-D3BHBSWL.js";import{c as a,e as g}from"./chunk-RLWRKBLA.js";import{f as d,sb as n}from"./chunk-ROW53IBC.js";import{a as p,g as x,i as r,n as i}from"./chunk-TSHWMJEM.js";r();i();r();i();var z=n.colors.legacy.spotWarning,D=n.colors.legacy.spotNegative,I=n.colors.legacy.spotNegative;var o=x(d(),1),C=a.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
`,N=g`
  0% {
    top: 15px;
    opacity: 0;
  };
  100% {
    top: 0px;
    opacity: 1;
  };
`,k=a.div`
  animation-name: ${e=>e.animateText?N:"none"};
  animation-duration: ${e=>e.animateText?".5s":"0s"};
  position: relative;
`,v=a(c).attrs(e=>({margin:e.margin??"20px auto 0 auto"}))`
  margin: ${e=>e.margin};
`,P=a(c).attrs(e=>({margin:e.margin??"15px 0px 0px 0px"}))`
  margin: ${e=>e.margin};
`,b=a.div`
  position: relative;
  left: 38px;
  bottom: 22px;
`;var w={large:30,medium:28,small:24},A={large:34,medium:34,small:29},W={large:18,medium:16,small:14},j=p(({className:e,icon:H,primaryText:m,secondaryText:s,headerStyle:t="medium",showWarning:R=!1,showError:S=!1,animateText:f=!1})=>{t=t??"medium";let E=w[t],u=A[t],M=W[t],L={large:22,medium:19,small:17}[t],l=t==="small"?"16px 0 0 0":void 0,O=S?I:n.colors.legacy.textDiminished;return(0,o.jsxs)(C,{className:e,children:[H??(0,o.jsx)(T,{}),R?(0,o.jsx)(b,{children:(0,o.jsx)(y,{})}):(0,o.jsx)(o.Fragment,{}),(0,o.jsxs)(k,{animateText:f,children:[m&&(0,o.jsx)(v,{margin:l,weight:500,size:E,lineHeight:u,maxWidth:"320px",children:m}),s&&(0,o.jsx)(P,{margin:l,wordBreak:"break-word",size:M,lineHeight:L,color:O,children:s})]})]})},"IconHeader");export{z as a,D as b,I as c,j as d};
//# sourceMappingURL=chunk-P43JCO4S.js.map
