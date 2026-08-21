import{s as z}from"./chunk-T5DSHPMV.js";import{F as M,G as L,W as S}from"./chunk-D3BHBSWL.js";import{c as h}from"./chunk-RLWRKBLA.js";import{e as I,f as d,sb as s}from"./chunk-ROW53IBC.js";import{g as n,i as l,n as a}from"./chunk-TSHWMJEM.js";l();a();var k=h.div`
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  overflow: hidden;
  background-color: ${e=>e.isPurple?s.colors.brand.midnight:s.colors.legacy.elementBase};
  background-image: ${e=>e.previewImage?`url(${e.previewImage})`:void 0};
  background-repeat: no-repeat;
  background-size: cover;
  background-position: center;
`;l();a();var E=n(I(),1);var p=n(d(),1),P=E.default.memo(({type:e,width:r=48,fill:m=s.colors.legacy.borderBase})=>{switch(e){case"video":return(0,p.jsx)(L,{width:r,height:r,fill:m});case"audio":return(0,p.jsx)(M,{width:r,height:r,fill:m});case"image":case"other":default:return(0,p.jsx)(S,{width:r,height:r,fill:m})}});l();a();var o=n(I(),1);l();a();var x=n(I(),1);var v=n(d(),1),O=x.default.memo(({showBadge:e=!0})=>(0,v.jsx)(z,{aspectRatio:1,width:"100%",height:"100%",backgroundColor:s.colors.legacy.elementBase,align:"flex-end",borderRadius:"6px",padding:"15px",children:e?(0,v.jsx)(z,{width:"100px",height:"10px",borderRadius:"6px",backgroundColor:s.colors.legacy.borderDiminished}):null}));var t=n(d(),1),U=3,V=h.img`
  transition: transform 0.5s ease;
  object-fit: cover;
  width: 100%;
  height: 100%;
  overflow: hidden;
  transform: ${e=>e.zoomState==="zoomedIn"?`scale(${U})`:"scale(1)"};
  cursor: ${e=>{if(e.isZoomControlsEnabled){if(e.zoomState==="zoomedIn")return"zoom-out";if(e.zoomState==="zoomedOut")return"zoom-in"}else return"inherit"}};
`,ge=o.default.memo(e=>{let{uri:r,showSkeletonBadge:m=!1,isZoomControlsEnabled:c=!1}=e,[w,f]=(0,o.useState)("loading"),[u,C]=(0,o.useState)("zoomedOut"),g=(0,o.useRef)(null),b=(0,o.useCallback)(i=>{let H=i.nativeEvent.layerX,X=i.nativeEvent.layerY,Y=i.currentTarget.offsetWidth,D=i.currentTarget.offsetHeight,F=H/Y*100,N=X/D*100;g.current&&(g.current.style.transformOrigin=`${F}% ${N}%`)},[]),R=(0,o.useCallback)(i=>{c&&(C(u==="zoomedIn"?"zoomedOut":"zoomedIn"),b(i))},[b,u,C,c]),T=(0,o.useCallback)(i=>{u==="zoomedOut"||!c||b(i)},[b,u,c]),$=(0,o.useCallback)(()=>{c&&(g.current&&(g.current.style.transformOrigin="center"),C("zoomedOut"))},[c]),B=(0,o.useMemo)(()=>r!==null&&r.trim()!==""?r:null,[r]),Z=(0,o.useCallback)(()=>{f("success")},[f]),A=(0,o.useCallback)(()=>{f("error")},[f]);return(0,t.jsxs)(t.Fragment,{children:[w==="error"?(0,t.jsx)(k,{children:(0,t.jsx)(P,{type:"image"})}):(0,t.jsx)(k,{children:(0,t.jsx)(V,{ref:g,onMouseMove:T,onMouseLeave:$,onClick:R,src:B??"",onLoad:Z,onError:A,zoomState:u,isZoomControlsEnabled:c})}),w==="loading"?(0,t.jsx)(O,{showBadge:m}):null]})});export{k as a,P as b,O as c,ge as d};
//# sourceMappingURL=chunk-GTBUZACE.js.map
