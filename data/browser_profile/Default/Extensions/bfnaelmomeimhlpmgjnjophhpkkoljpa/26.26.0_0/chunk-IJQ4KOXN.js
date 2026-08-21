import{a as k}from"./chunk-6NA7ELBO.js";import{o as R,p as h,s as b}from"./chunk-T5DSHPMV.js";import{Za as u}from"./chunk-D3BHBSWL.js";import{b as x,c as r}from"./chunk-RLWRKBLA.js";import{Rb as m,f,sb as t}from"./chunk-ROW53IBC.js";import{a as i,g as p,i as d,n as g}from"./chunk-TSHWMJEM.js";d();g();var e=p(f(),1),v=r.div`
  display: flex;
  height: 49px;
  padding: 0 16px;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  &:last-of-type {
    margin-bottom: 0;
  }
  background-color: ${o=>o.customBackground??t.colors.legacy.elementBase};
  ${o=>o.onClick?x`
          :hover {
            background-color: ${t.colors.legacy.elementAccent};
          }
          cursor: pointer;
        `:""}
`,L=r.div`
  display: flex;
  flex-direction: row;
  align-items: center;
`,N=r.div`
  display: flex;
  flex-direction: column;
  gap: 2px;
`,W=r.div`
  display: flex;
  margin: 2px 4px 0 0;
`,B=r(u).attrs(o=>({color:o.color||t.colors.legacy.textDiminished,size:14,lineHeight:17,weight:400,noWrap:!0,paddingLeft:8}))`
  cursor: ${o=>o.onClick?"pointer":"default"};
  text-decoration: none;
`,A=i(({children:o,icon:n,fontWeight:c,label:y,lineHeight:T,customBackground:C,color:w,tooltipContent:l,isLoading:a=!1,error:s,onClick:I})=>(0,e.jsxs)(v,{customBackground:C,onClick:a?void 0:I,children:[(0,e.jsxs)(N,{children:[(0,e.jsxs)(L,{children:[n?(0,e.jsx)(W,{children:n}):null,(0,e.jsx)(k,{tooltipAlignment:"topLeft",iconSize:12,lineHeight:T??17,fontWeight:c??400,info:l?(0,e.jsx)(P,{tooltipContent:l}):null,textColor:w||t.colors.legacy.textBase,children:y})]}),s?(0,e.jsx)(m,{color:"spotNegative",font:"textSm",children:s}):null]}),a?(0,e.jsx)(b,{width:"75px",height:"15px",borderRadius:"50px",backgroundColor:t.colors.legacy.borderDiminished}):o]}),"InfoRow"),P=i(({tooltipContent:o})=>(0,e.jsx)(h,{children:typeof o=="string"?(0,e.jsx)(R,{children:o}):o}),"InfoTooltip"),j=i(({children:o,color:n,onClick:c})=>(0,e.jsx)(B,{onClick:c,color:n||t.colors.legacy.textDiminished,children:o||"-"}),"Value");export{A as a,P as b,j as c};
//# sourceMappingURL=chunk-IJQ4KOXN.js.map
