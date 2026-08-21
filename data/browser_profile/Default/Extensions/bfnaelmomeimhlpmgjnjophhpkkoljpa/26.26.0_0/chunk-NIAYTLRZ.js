import{a as y,b as $,c as V,d as x}from"./chunk-GTBUZACE.js";import{W as H}from"./chunk-D3BHBSWL.js";import{c as L}from"./chunk-RLWRKBLA.js";import{$ as k}from"./chunk-IT2EKJZQ.js";import{Ua as S,e as I,f as g}from"./chunk-ROW53IBC.js";import{a as v,g as l,i as h,n as f}from"./chunk-TSHWMJEM.js";h();f();var R=l(I(),1);h();f();var E=l(I(),1);h();f();var P=l(I(),1);var B=l(g(),1),W=L.div`
  visibility: ${e=>e.isHidden?"hidden":"visible"};
  model-viewer {
    --poster-color: transparent;
    --progress-bar-color: transparent;
    --progress-mask: transparent;
    width: ${e=>e.width}px;
    height: ${e=>e.height}px;
  }
`,T=!1;function Z(){T||(T=!0,import("./model-viewer-P5RAWAP4.js"))}v(Z,"loadModelViewer");var _=v(({src:e,alt:o,autoRotate:r,autoPlay:t,cameraControls:i,loading:d,width:c=154,height:m=154,onLoad:n=S,onError:u=S,isHidden:C=!1})=>{Z();let p=(0,P.useRef)(null);return(0,P.useEffect)(()=>{let M=p.current;if(M)return M.addEventListener("load",n),M.addEventListener("error",u),()=>{M.removeEventListener("load",n),M.removeEventListener("error",u)}},[u,n,p]),(0,B.jsx)(W,{width:c,height:m,isHidden:C,children:(0,B.jsx)("model-viewer",{alt:o,loading:d??"eager","auto-rotate-delay":0,"auto-rotate":r||void 0,autoplay:t||void 0,"camera-controls":i||void 0,ref:p,src:e})})},"ModelViewer"),U=_;var s=l(g(),1),A=E.default.memo(e=>{let{uri:o,width:r,height:t,isCameraControlsEnabled:i}=e,[d,c]=(0,E.useState)(!0),[m,n]=(0,E.useState)(!1);return(0,s.jsxs)(s.Fragment,{children:[m?(0,s.jsx)(y,{children:(0,s.jsx)(H,{})}):(0,s.jsx)(y,{children:(0,s.jsx)(U,{src:o,autoRotate:!0,autoPlay:!0,cameraControls:i,onLoad:v(()=>{c(!1),n(!1)},"onLoad"),onError:v(()=>{c(!1),n(!0)},"onError"),width:r,height:t,isHidden:d})}),d?(0,s.jsx)(V,{showBadge:!1}):null]})});h();f();var w=l(I(),1);var a=l(g(),1),z={width:"100%",height:"100%",objectFit:"cover",borderRadius:"8px"},F=w.default.memo(e=>{let{uri:o,showSkeletonBadge:r=!1,autoPlay:t=!0,muted:i=!0,loop:d=!0,controls:c=!0}=e,[m,n]=(0,w.useState)("loading"),u=(0,w.useCallback)(()=>{n("success")},[]),C=(0,w.useCallback)(()=>{n("error")},[]),p=o!==null&&o.trim()!==""?o:null;return(0,a.jsxs)(a.Fragment,{children:[m==="error"||!p?(0,a.jsx)(y,{children:(0,a.jsx)($,{type:"video"})}):(0,a.jsx)(y,{children:(0,a.jsx)("video",{src:p,onLoadedData:u,onError:C,autoPlay:t,muted:i,loop:d,controls:c,playsInline:!0,style:z,children:(0,a.jsx)("track",{kind:"captions"})})}),m==="loading"&&p?(0,a.jsx)(V,{showBadge:r}):null]})});var b=l(g(),1),O=328,N=L.div`
  width: ${e=>e.width}px;
  height: ${e=>e.height}px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 8px;
  position: relative;
`,we=R.default.memo(({media:e,width:o=328,height:r=328})=>{let t=e?.type??"image",i=k(e,t,!0),d=k(e,"image",!1,"large"),c=t==="image",m=t==="video",n=t==="audio",u=t==="model",C=t==="other"||n,p=(0,R.useMemo)(()=>{if(i)return(0,b.jsx)(b.Fragment,{children:c?(0,b.jsx)(x,{width:O,height:O,uri:i,isZoomControlsEnabled:!0,showSkeletonBadge:!1}):m?(0,b.jsx)(F,{uri:i,width:o,height:r,showSkeletonBadge:!1}):u?(0,b.jsx)(A,{uri:i,width:o,height:r,isCameraControlsEnabled:!0}):C?(0,b.jsx)(x,{uri:d??"",width:o,height:r}):null})},[r,c,u,C,m,i,d,o]);return(0,b.jsx)(N,{width:o,height:r,children:p})});export{we as a};
//# sourceMappingURL=chunk-NIAYTLRZ.js.map
