import{c as I}from"./chunk-2EQUCBKU.js";import{Za as l,aa as C,u as h,x as b}from"./chunk-D3BHBSWL.js";import{c as n}from"./chunk-RLWRKBLA.js";import{e as B,f as m,sb as r,t as f}from"./chunk-ROW53IBC.js";import{a as i,g,i as a,n as s}from"./chunk-TSHWMJEM.js";a();s();var e=g(B());var P=n.div`
  width: 94px;
  height: 94px;
  margin: auto;
  position: relative;
  border-radius: ${t=>t.borderRadius};
  background: ${t=>t.background};
`,L=n.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
`,F=n.div`
  @keyframes rotate {
    0% {
      transform: rotateZ(0deg);
    }
    100% {
      transform: rotateZ(360deg);
    }
  }
  animation: rotate 0.5s linear infinite;
  position: absolute;
  margin: 0 auto;
  width: 94px;
  height: 94px;
  border-radius: 100%;
  box-shadow: 0 0 0 7px rgba(from ${r.colors.legacy.spotWarning} r g b / 10%);
  & > svg {
    position: absolute;
    bottom: -8px;
    right: -9px;
  }
`,x=i(({children:t,color:c=r.colors.brand.yellowMoon})=>e.createElement(P,null,e.createElement(F,null,e.createElement("svg",{width:38,height:60,viewBox:"0 0 38 60",fill:"none",xmlns:"http://www.w3.org/2000/svg"},e.createElement("path",{fillRule:"evenodd",clipRule:"evenodd",d:"M31.897 5.75301C33.5532 5.70601 34.9339 7.01051 34.9809 8.6667C35.2548 18.3187 32.5493 27.8208 27.2322 35.8808C21.9151 43.9408 14.2446 50.1676 5.26377 53.7144C3.72274 54.323 1.98013 53.5671 1.37153 52.0261C0.762941 50.485 1.51883 48.7424 3.05986 48.1338C10.8942 45.0398 17.5855 39.6079 22.2238 32.5769C26.8621 25.5458 29.2223 17.2567 28.9833 8.8369C28.9363 7.18071 30.2408 5.80001 31.897 5.75301Z",fill:c}))),t&&e.createElement(L,null,t)),"IconLoading");a();s();var o=g(m(),1),oo=i(({icon:t,title:c,onClose:S,iconSize:R="normal",showButton:u=!0,buttonText:y,children:k,onIgnore:T,ignoreText:p})=>{let{t:z}=f(),d=R==="large"?44:32,$=y||z("commandClose");return(0,o.jsxs)(D,{children:[(0,o.jsxs)("section",{children:[t==="loading"?(0,o.jsx)(x,{children:(0,o.jsx)(C,{width:d})}):t==="error"?(0,o.jsx)(M,{iconSize:d}):(0,o.jsx)(N,{iconSize:d}),(0,o.jsx)(Z,{children:c}),k]}),p!==void 0&&(0,o.jsx)(A,{onClick:T,children:p}),(0,o.jsx)(j,{hasMarginBottom:!u,children:u?(0,o.jsx)(I,{onClick:S,children:$}):(0,o.jsx)(o.Fragment,{children:"\xA0"})})]})},"TransactionStatusDetail"),M=i(({iconSize:t})=>(0,o.jsx)(v,{borderRadius:"100%",background:`rgba(from ${r.colors.legacy.spotNegative} r g b / 10%)`,children:(0,o.jsx)(w,{children:(0,o.jsx)(h,{width:t})})}),"ErrorIcon"),N=i(({iconSize:t})=>(0,o.jsx)(v,{borderRadius:"100%",background:`rgba(from ${r.colors.legacy.spotPositive} r g b / 10%)`,children:(0,o.jsx)(w,{children:(0,o.jsx)(b,{width:t,fill:r.colors.legacy.spotPositive})})}),"IconSuccess"),D=n.section`
  display: grid;
  grid-template-rows: 1fr auto;
  height: 100%;
  & > section:first-child {
    display: grid;
    gap: 8.5px;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    margin: auto;
  }
`,Z=n(l).attrs({size:28,lineHeight:33.89,weight:500})`
  word-wrap: break-word;
  overflow: hidden;
  margin-top: 15px;
`,v=n.div`
  width: 94px;
  height: 94px;
  margin: auto;
  position: relative;
  border-radius: ${t=>t.borderRadius};
  background: ${t=>t.background};
`,w=n.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
`,j=n.div`
  margin-bottom: ${t=>t.hasMarginBottom&&"60px"};
  width: 100%;
`,A=n(l)`
  margin: auto;
  font-size: 14px;
  padding-bottom: 35px;
  color: ${r.colors.legacy.textDiminished};
  font-weight: 500;
  &:hover {
    color: ${r.colors.legacy.spotNegative};
  }
`;export{x as a,oo as b};
//# sourceMappingURL=chunk-C4LSQOYZ.js.map
