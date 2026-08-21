import{a as x,b as G}from"./chunk-366FMGKO.js";import{a as $}from"./chunk-Z3TIOBSF.js";import{d as W}from"./chunk-CL5XSPPA.js";import{c as E}from"./chunk-K7GHDVLN.js";import{a as Q}from"./chunk-6HGM4SLG.js";import{g as S,h as z}from"./chunk-V53E4MU6.js";import{c as I}from"./chunk-2EQUCBKU.js";import{Za as g,t as H}from"./chunk-D3BHBSWL.js";import{c as i}from"./chunk-RLWRKBLA.js";import{b as D}from"./chunk-G2YN7S6F.js";import{a as h}from"./chunk-V6Q45TV4.js";import{Se as v,ie as b,qb as f,tg as B}from"./chunk-QPUEUZLS.js";import{Wb as P,e as w,f as l,qb as N,sb as r,t as R}from"./chunk-ROW53IBC.js";import{a as A,g as t,i as c,n as m}from"./chunk-TSHWMJEM.js";c();m();var C=t(w(),1);var y=t(l(),1),ae=C.default.memo(({chainAddress:s,onQRPress:n})=>{let{networkID:d,address:o}=s,{buttonText:a,copied:u,copy:T}=x(o),F=v(o,4),U=B(s.networkID),j=(0,C.useCallback)(q=>{q?.stopPropagation(),T()},[T]);return(0,y.jsx)(P,{copied:u,copiedText:a,formattedAddress:F,networkBadge:(0,y.jsx)(W,{networkID:d,address:o}),networkLogo:(0,y.jsx)(h,{networkID:d,size:40}),networkName:U,onCopyPress:j,onQRPress:n})});c();m();var O=t(G(),1),_=t(w(),1);c();m();var k=t(w(),1);var p=t(l(),1),K=i.div`
  width: 100%;
`,Y=i(E)`
  background: ${r.colors.legacy.areaAccent};
  border: 1px solid ${r.colors.legacy.borderDiminished};
  border-radius: 6px 6px 0 0;
  border-bottom: none;
  margin: 0;
  padding: 16px 22px;
  font-size: 16px;
  font-weight: 500;
  line-height: 21px;
  text-align: center;
  resize: none;
  overflow: hidden;
`,Z=i.button`
  display: flex;
  justify-content: center;
  align-items: center;
  background: ${r.colors.legacy.areaAccent};
  border: 1px solid ${r.colors.legacy.borderDiminished};
  border-radius: 0 0 6px 6px;
  border-top: none;
  height: 40px;
  width: 100%;
  padding: 0;
  cursor: pointer;

  &:hover {
    background: ${r.colors.brand.black};
  }
`,J=i(g).attrs({size:16,weight:600,lineHeight:16})`
  margin-left: 6px;
`,M=A(({value:s})=>{let{buttonText:n,copy:d}=x(s),o=(0,k.useRef)(null);return(0,k.useEffect)(()=>{A(()=>{if(o&&o.current){let u=o.current.scrollHeight;o.current.style.height=u+"px"}},"autoSizeTextArea")()},[]),(0,p.jsxs)(K,{children:[(0,p.jsx)(Y,{ref:o,readOnly:!0,value:s}),(0,p.jsxs)(Z,{onClick:d,children:[(0,p.jsx)(H,{}),(0,p.jsx)(J,{children:n})]})]})},"CopyArea");var e=t(l(),1),V=48,Qe=_.default.memo(({address:s,networkID:n,headerType:d,onCloseClick:o})=>{let{t:a}=R();return(0,e.jsxs)(e.Fragment,{children:[(0,e.jsx)(d==="page"?S:z,{children:a("depositAddress")}),(0,e.jsxs)($,{children:[(0,e.jsx)(Q,{align:"center",justify:"center",id:"column",children:(0,e.jsxs)(ee,{id:"QRCodeWrapper",children:[(0,e.jsx)(X,{value:s,size:160,level:"Q",id:"styledqrcode"}),(0,e.jsx)("div",{className:N({position:"absolute"}),children:(0,e.jsx)(h,{networkID:n,size:V,borderColor:"areaBase"})})]})}),(0,e.jsx)(g,{size:16,lineHeight:22,weight:600,margin:"16px 0 8px",children:a("depositAddressChainInterpolated",{chain:f.getNetworkName(n)})}),(0,e.jsx)(M,{value:s}),(0,e.jsxs)(g,{size:14,color:r.colors.legacy.textDiminished,lineHeight:20,margin:"16px 0",children:[(0,e.jsxs)(D,{i18nKey:"depositAssetQRCodeInterpolated",values:{network:f.getNetworkName(n)},children:["Use to receive tokens on the ",f.getNetworkName(n)," network only."]}),f.isBitcoinNetworkID(n)?(0,e.jsxs)(e.Fragment,{children:[" ",(0,e.jsx)(oe,{href:b,target:"_blank",rel:"noopener noreferrer",children:a("commandLearnMore2")})]}):null]})]}),(0,e.jsx)(I,{onClick:o,children:a("commandClose")})]})}),X=i(O.default)`
  padding: 8px;
  background: ${r.colors.legacy.white};
  border-radius: 6px;
  position: relative;
`,ee=i.div`
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
`,oe=i.a`
  color: ${r.colors.legacy.spotBase};
  text-decoration: none;
  font-weight: 500;
`;export{ae as a,M as b,Qe as c};
//# sourceMappingURL=chunk-227AXUGX.js.map
