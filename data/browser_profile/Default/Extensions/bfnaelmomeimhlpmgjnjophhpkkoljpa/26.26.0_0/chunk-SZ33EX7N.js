import{a as w}from"./chunk-6NA7ELBO.js";import{b as N}from"./chunk-5FRW4UO4.js";import{o as B}from"./chunk-T5DSHPMV.js";import{I as $,r as P}from"./chunk-D3BHBSWL.js";import{c as r}from"./chunk-RLWRKBLA.js";import{$ as z}from"./chunk-OY47TOHT.js";import{b as L}from"./chunk-S47GYCJH.js";import{pa as I}from"./chunk-3VGVYQIC.js";import{Se as S,v as T}from"./chunk-QPUEUZLS.js";import{Hb as v,Pa as k,Qb as V,Rb as R,cd as D,e as W,f as C,sb as s}from"./chunk-ROW53IBC.js";import{a as l,g as b,i as x,n as f}from"./chunk-TSHWMJEM.js";x();f();x();f();var h={header:"_14rx5di1 _14rx5di0 _48j31a5b _48j31a3o _48j31a6y _48j31a21 _48j31a1ke _48j31a1nl _48j31a1mq _48j31aky _48j31a2gb _48j31as5 _48j31ax8",summaryContainer:"_14rx5di2 _48j31a1c3"};x();f();var _=b(W(),1),u=b(C(),1),j=_.default.memo(({address:e,networkID:o,showConcise:a})=>{let{getExistingAccount:m,getKnownAddressLabel:n}=I(),{data:y}=z(e,o),c=y?.address;if(!e)return null;let i=m(e),p=n(e,o),g=i?i.name:p;return c?(0,u.jsxs)(R,{children:[e," ",(0,u.jsxs)(R,{color:"textDiminished",children:["(",S(c,4),")"]})]}):g?(0,u.jsxs)(R,{children:[g," ",(0,u.jsxs)(R,{color:"textDiminished",children:["(",S(e,4),")"]})]}):(0,u.jsx)(R,{children:a?S(e,4):e})});var t=b(C(),1);function E(e){if(!e){let a=parseInt(s.radiusBase.replace("px",""),10);return{borderTopLeftRadius:a,borderTopRightRadius:a,borderBottomRightRadius:a,borderBottomLeftRadius:a}}let o=e.split(" ").map(a=>a.replace("px","")).map(a=>parseInt(a,10));return o.length===1?{borderTopLeftRadius:o[0],borderTopRightRadius:o[0],borderBottomRightRadius:o[0],borderBottomLeftRadius:o[0]}:o.length===2?{borderTopLeftRadius:o[0],borderTopRightRadius:o[1],borderBottomRightRadius:o[0],borderBottomLeftRadius:o[1]}:{borderTopLeftRadius:o[0],borderTopRightRadius:o[1],borderBottomRightRadius:o[2],borderBottomLeftRadius:o[3]}}l(E,"explodeBorderRadius");var H=r.div`
  display: flex;
  flex-direction: column;
  border-bottom: 1px solid ${s.colors.legacy.areaBase};
  border-bottom-width: ${e=>e.border?1:0}px;
  padding: ${e=>e.padding?e.padding:14}px;
  cursor: ${e=>e.onClick?"pointer":"default"};
`,F=r.div`
  padding-top: 3px;
`,G=r.div`
  display: flex;
  justify-content: space-between;
  font-size: ${e=>e.fontSize?e.fontSize:14}px;
`,M=r.div`
  display: flex;
  justify-content: space-between;
`,U=r.div`
  text-align: left;
  flex: 1;
`,q=r.div`
  text-align: right;
  flex: 1;
`,K=r.div`
  display: flex;
  align-items: center;
  ${e=>e.truncate?"flex: 1; min-width: 0; justify-content:end;":""}
`,J=r.div`
  padding-left: 8px;
  color: ${s.colors.legacy.textDiminished};
`,O=l(({children:e,showArrow:o})=>(0,t.jsxs)(K,{truncate:!o,children:[e,o&&(0,t.jsx)(J,{children:(0,t.jsx)(P,{height:12})})]}),"Value"),d=r.span`
  color: ${e=>e.color||"white"};
  text-align: ${e=>e.align||"left"};
  font-weight: ${e=>e.weight||400};
  overflow-wrap: break-word;
  ${e=>e.margin?"margin: "+e.margin+";":""};
  ${e=>e.size?"font-size: "+e.size+"px;":""}
  ${e=>e.truncate?"white-space: nowrap; text-overflow: ellipsis; overflow:hidden; width: 100%;"+(e.size?"line-height: "+e.size*1.2+"px;":"line-height: 17px;"):""}
`,Q=r.a.attrs({target:"_blank",rel:"noopener noreferrer"})`
  color: ${s.colors.legacy.spotBase};
  text-decoration: none;
  cursor: pointer;
`,X=r.div`
  text-align: center;
  width: 100%;
`,Y=l(({children:e,label:o,tooltipContent:a,fontSize:m})=>(0,t.jsxs)(t.Fragment,{children:[(0,t.jsx)(w,{tooltipAlignment:"topLeft",iconSize:12,lineHeight:17,fontSize:m,fontWeight:500,info:a?(0,t.jsx)(B,{children:a}):null,children:o}),e]}),"InfoRow"),Z=l(e=>{L.capture("activityItemDetailLinkClicked",{data:{hostname:k(e)}})},"captureLinkClickAnalytics"),ee=l(e=>"designSystemOptIn"in e&&e.designSystemOptIn===!0?(0,t.jsx)(te,{...e}):(0,t.jsx)(oe,{...e}),"Summary"),te=l(({header:e,rows:o,borderRadius:a})=>{let m=E(a);return(0,t.jsx)(V,{...m,children:(0,t.jsxs)(v,{className:h.summaryContainer,children:[e?(0,t.jsx)("div",{className:h.header,children:e}):null,(0,t.jsx)(D,{rows:o.map(n=>({...n.onPress?{onClick:n.onPress}:{},topLeft:n.tooltipContent?{component:l(()=>(0,t.jsx)(w,{textColor:s.colors.legacy.textDiminished,iconColor:s.colors.legacy.textDiminished,tooltipAlignment:"topLeft",iconSize:12,lineHeight:17,fontSize:14,fontWeight:500,info:(0,t.jsx)(B,{children:n.tooltipContent}),children:n.label}),"component")}:{text:n.label,color:"textDiminished"},topRight:{text:n.value,color:"textBase"}}))})]})})},"SummaryDesignSystem"),oe=l(({header:e,rows:o,borderRadius:a,padding:m,fontSize:n,networkID:y})=>{let c=E(a);return(0,t.jsx)(V,{...c,children:(0,t.jsxs)(v,{className:h.summaryContainer,children:[" ",e?(0,t.jsx)("div",{className:h.header,children:e}):null,o.map((i,p)=>{if(i.value===void 0)return null;let g=i.onClick?{role:"button"}:void 0;return(0,t.jsxs)(H,{border:o.length-1!==p,padding:m,onClick:i.onClick,...g,children:[(0,t.jsx)(G,{fontSize:n,children:typeof i.value=="string"?i.type==="link"?(0,t.jsx)(X,{children:(0,t.jsx)(Q,{href:i.value,onClick:()=>Z(i.value),children:i.label})}):(0,t.jsx)(Y,{label:i.label,tooltipContent:i.tooltipContent,fontSize:n,children:(0,t.jsx)(O,{showArrow:!!i.onClick,children:i.type==="address"?(0,t.jsx)(j,{address:i.value,networkID:y??T.Mainnet}):(0,t.jsx)(d,{color:i.color,weight:500,align:"right",truncate:!i.onClick,children:i.value})})}):(0,t.jsxs)(t.Fragment,{children:[(0,t.jsx)(d,{color:s.colors.legacy.textDiminished,size:n,children:i.label}),(0,t.jsx)(O,{showArrow:!!i.onClick,children:i.value})]})},i.label),(0,t.jsxs)(M,{children:[i.leftSubtext?(0,t.jsx)(U,{children:(0,t.jsx)(F,{children:(0,t.jsx)(d,{color:i.leftSubtextColor||s.colors.legacy.textDiminished,size:13,children:i.leftSubtext})})}):null,i.rightSubtext?(0,t.jsx)(q,{children:(0,t.jsx)(F,{children:(0,t.jsx)(d,{color:i.rightSubtextColor||s.colors.legacy.textDiminished,size:13,children:i.rightSubtext})})}):null]})]},`summary-row-${p}`)})]})})},"SummaryLegacy"),ut=l(({name:e,imageURL:o})=>(0,t.jsxs)("div",{style:{display:"flex",flexDirection:"row",alignItems:"center"},children:[(0,t.jsx)(N,{iconUrl:o,width:16}),(0,t.jsx)(d,{margin:"0 0 0 5px",weight:500,children:e})]}),"ActivityProvider"),ie=r.div`
  height: 100%;
  overflow: scroll;
  margin-top: -16px;
  padding-top: 16px;
  padding-bottom: 64px;
`,re=r.div`
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
`,ae=r.div`
  margin-top: 10px;
  margin-bottom: 10px;
`,ne=r.div`
  margin-top: 10px;
  margin-bottom: 20px;
`,se=r.div`
  margin-bottom: 10px;
`,le=r.div`
  position: relative;
  width: 100%;
  text-align: center;
  margin: 10px 0 10px 0;
`,de=r(d)`
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
  max-width: 100%;
`,me=r.div`
  background-color: ${s.colors.legacy.spotWarning};
  width: 100%;
  margin-top: 24px;
  margin-bottom: 14px;
  border-radius: 9px;
  padding: 16px;
  gap: 8px;
  display: flex;
  align-items: flex-start;
  align-self: stretch;
`,ce=r.div`
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
`,pt=l(({title:e,primaryText:o,secondaryText:a,image:m,sections:n,leftButton:y,warning:c})=>(0,t.jsxs)(ie,{children:[(0,t.jsxs)(re,{children:[(0,t.jsxs)(le,{children:[y||!1,(0,t.jsx)(d,{weight:500,size:22,children:e})]}),(0,t.jsx)(ae,{children:m}),o.value&&(0,t.jsx)(de,{weight:600,size:34,color:o.color,align:"center",margin:"10px 0 10px 0",children:o.value}),a.value&&(0,t.jsx)(d,{size:16,color:s.colors.legacy.textDiminished,margin:"0 0 10px 0",children:a.value}),c&&(0,t.jsxs)(me,{children:[(0,t.jsx)(ce,{children:(0,t.jsx)($,{})}),(0,t.jsx)(d,{size:14,color:s.colors.legacy.areaBase,margin:"3px 0px 3px 8px",children:c})]})]}),n.map(({title:i,rows:p},g)=>(0,t.jsxs)(ne,{children:[i&&(0,t.jsx)(se,{children:(0,t.jsx)(d,{size:14,weight:500,color:s.colors.legacy.textDiminished,children:i})}),(0,t.jsx)(ee,{rows:p})]},`summary-item-${g}`))]}),"Details");export{ee as a,ut as b,pt as c};
//# sourceMappingURL=chunk-SZ33EX7N.js.map
