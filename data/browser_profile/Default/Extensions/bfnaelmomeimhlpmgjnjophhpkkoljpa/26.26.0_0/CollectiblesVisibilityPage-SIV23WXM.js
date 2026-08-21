import{a as Z}from"./chunk-WHSGVNLC.js";import{a as U}from"./chunk-MIARPMVY.js";import{a as G}from"./chunk-WUAZEUZV.js";import{b as $,d as F}from"./chunk-GTBUZACE.js";import{Y as K}from"./chunk-ACMEWKV4.js";import{k as B}from"./chunk-G5EJHLNE.js";import"./chunk-5FRW4UO4.js";import"./chunk-K3AOJOH2.js";import"./chunk-T5DSHPMV.js";import"./chunk-FFDTKKDT.js";import"./chunk-A4FRP5S3.js";import{a as R}from"./chunk-6P6J5E4Q.js";import"./chunk-5M6YSMA7.js";import"./chunk-7FPALEDT.js";import"./chunk-VQSRXQ54.js";import"./chunk-P43JCO4S.js";import"./chunk-FUOWEUPT.js";import"./chunk-PA2NRDYY.js";import"./chunk-CL5XSPPA.js";import{g as Q}from"./chunk-K7GHDVLN.js";import"./chunk-5NHH6Z66.js";import{a as O}from"./chunk-6HGM4SLG.js";import"./chunk-V53E4MU6.js";import"./chunk-6N3EJFJR.js";import{a as V}from"./chunk-CCMUSPWN.js";import"./chunk-WBIHZ7LK.js";import"./chunk-EVDRYYXH.js";import"./chunk-WF3LOBWM.js";import"./chunk-N54X2CUO.js";import"./chunk-VRM2NWAU.js";import"./chunk-EOII3ZM4.js";import"./chunk-RMMVJ6R3.js";import"./chunk-4AQPJCXC.js";import"./chunk-FMMOYV2U.js";import"./chunk-C4LSQOYZ.js";import"./chunk-4VICHEHO.js";import{c as z}from"./chunk-2EQUCBKU.js";import{Za as H,w as D}from"./chunk-D3BHBSWL.js";import{c as s}from"./chunk-RLWRKBLA.js";import"./chunk-HRSMUG5A.js";import"./chunk-M3TVHC7T.js";import"./chunk-KS7AKYDM.js";import{$ as A,X as E,ca as _,da as N}from"./chunk-IT2EKJZQ.js";import"./chunk-R6A7JGWU.js";import"./chunk-RKVM6QQ3.js";import"./chunk-6SLFKWVX.js";import"./chunk-OY47TOHT.js";import"./chunk-G2YN7S6F.js";import"./chunk-V6Q45TV4.js";import"./chunk-S47GYCJH.js";import"./chunk-UPPQC44E.js";import"./chunk-OJPBMZQC.js";import"./chunk-3VGVYQIC.js";import"./chunk-CYENH7PC.js";import{F as v}from"./chunk-44KDTK4M.js";import"./chunk-3SRDKZHE.js";import"./chunk-2TCOJUYX.js";import"./chunk-3CHZKZ7J.js";import{Fd as W}from"./chunk-QPUEUZLS.js";import"./chunk-TWVSBOL5.js";import{Fc as P,e as M,f as b,qb as L,sb as w,t as h,zc as k}from"./chunk-ROW53IBC.js";import"./chunk-TPWF5M5V.js";import"./chunk-PPRUN2KR.js";import"./chunk-U7OZEJ4F.js";import"./chunk-ZRGHR2IN.js";import{a as I,g as p,i as f,n as C}from"./chunk-TSHWMJEM.js";f();C();var n=p(M(),1);f();C();var X=p(M(),1);var o=p(b(),1),j=L({marginLeft:4}),ee=s(R).attrs({align:"center",padding:"10px"})`
  background-color: ${w.colors.legacy.elementBase};
  border-radius: 6px;
  height: 74px;
  margin: 4px 0;
`,te=s.div`
  display: flex;
  align-items: center;
`,oe=s(O)`
  flex: 1;
  min-width: 0;
  text-align: left;
  align-items: normal;
`,ie=s(H).attrs({size:16,weight:600,lineHeight:19,noWrap:!0,maxWidth:"175px",textAlign:"left"})``,ne=s(H).attrs({color:w.colors.legacy.textDiminished,size:14,lineHeight:17,noWrap:!0})`
  text-align: left;
  margin-top: 5px;
`,le=s.div`
  width: 55px;
  min-width: 55px;
  max-width: 55px;
  height: 55px;
  min-height: 55px;
  max-height: 55px;
  aspect-ratio: 1;
  margin-right: 10px;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
`,q=X.default.memo(e=>{let{t:l}=h(),{collection:i,unknownItem:c,isHidden:a,isSpam:r,onToggleHidden:g}=e,{name:d,id:u}=i,m=_(i),y=N(i),S=A(m?.media,"image",!1,"small"),x=d||m?.name||c;return(0,o.jsxs)(ee,{children:[(0,o.jsx)(le,{children:r&&a?(0,o.jsx)(Z,{width:32}):S?(0,o.jsx)(F,{uri:S}):(0,o.jsx)($,{type:"image",width:42})}),(0,o.jsx)(R,{children:(0,o.jsxs)(oe,{children:[(0,o.jsxs)(te,{children:[(0,o.jsx)(ie,{children:x}),r?(0,o.jsx)(D,{className:j,fill:w.colors.legacy.spotWarning,height:16,width:16}):null]}),(0,o.jsx)(ne,{children:l("collectiblesSearchNrOfItems",{nrOfItems:y})})]})}),(0,o.jsx)(U,{id:u,label:`${d} visible`,checked:!a,onChange:T=>{g(T.target.checked?"show":"hide")}})]})});var t=p(b(),1),se=74,ae=10,re=se+ae,me=20,ce=s.div`
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
`,de=s.div`
  position: relative;
  width: 100%;
`,pe=I(()=>{let{handleHideModalVisibility:e}=K(),{data:l,isPending:i}=v(),{viewState:c,viewStateLoading:a}=E({account:l}),r=(0,n.useCallback)(()=>e("collectiblesVisibility"),[e]),g=(0,n.useMemo)(()=>({...c,handleCloseModal:r}),[r,c]),d=(0,n.useMemo)(()=>i||a,[i,a]);return{data:g,loading:d}},"useProps"),ge=n.default.memo(e=>{let{t:l}=h(),i=(0,n.useRef)(null);return(0,n.useEffect)(()=>{setTimeout(()=>i.current?.focus(),200)},[]),(0,t.jsxs)(t.Fragment,{children:[(0,t.jsx)(de,{children:(0,t.jsx)(Q,{ref:i,tabIndex:0,placeholder:l("assetListSearch"),maxLength:W,onChange:e.handleSearch,value:e.searchQuery,name:"Search collectibles"})}),(0,t.jsx)(B,{children:(0,t.jsx)(k,{children:({height:c,width:a})=>(0,t.jsx)(P,{style:{padding:`${me}px 0`},scrollToIndex:e.searchQuery!==e.debouncedSearchQuery?0:void 0,height:c,width:a,rowCount:e.listItems.length,rowHeight:re,rowRenderer:r=>(0,t.jsx)(he,{...r,data:e.listItems,unknownItem:l("assetListUnknownToken"),getIsHidden:e.getIsHidden,getIsSpam:e.getIsSpam,getSpamStatus:e.getSpamStatus,onToggleHidden:e.onToggleHidden})})})})]})}),he=I(e=>{let{index:l,data:i,style:c,unknownItem:a,getIsHidden:r,getIsSpam:g,getSpamStatus:d,onToggleHidden:u}=e,m=i[l],y=r(m),S=g(m),x=d(m),T=(0,n.useCallback)(J=>u({item:m,status:J}),[u,m]);return(0,t.jsx)("div",{style:c,children:(0,t.jsx)(q,{collection:m,unknownItem:a,isHidden:y,isSpam:S,spamStatus:x,onToggleHidden:T})})},"ResultRowWrapper"),ue=I(()=>{let{data:e,loading:l}=pe(),{t:i}=h();return(0,t.jsxs)(ce,{children:[l?(0,t.jsx)(G,{}):(0,t.jsx)(ge,{...e}),(0,t.jsx)(V,{children:(0,t.jsx)(z,{onClick:e.handleCloseModal,children:i("commandClose")})})]})},"CollectiblesVisibilityPage"),Ue=ue;export{ue as CollectiblesVisibilityPage,Ue as default};
//# sourceMappingURL=CollectiblesVisibilityPage-SIV23WXM.js.map
