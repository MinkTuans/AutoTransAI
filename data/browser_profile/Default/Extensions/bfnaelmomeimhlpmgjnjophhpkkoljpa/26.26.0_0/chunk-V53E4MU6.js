import{b as W}from"./chunk-N54X2CUO.js";import{c as T}from"./chunk-VRM2NWAU.js";import{L as v,X as O,Z as R,Za as P}from"./chunk-D3BHBSWL.js";import{c as u}from"./chunk-RLWRKBLA.js";import{d as I}from"./chunk-HRSMUG5A.js";import{M as L}from"./chunk-44KDTK4M.js";import{Lg as C}from"./chunk-QPUEUZLS.js";import{$b as N,A as M,Rc as X,U as A,Ua as w,Xb as B,e as b,f as V,sb as D}from"./chunk-ROW53IBC.js";import{a as l,g as m,i as f,n as h}from"./chunk-TSHWMJEM.js";f();h();var $=m(X(),1);var n=m(b(),1);var x=m(V(),1),F=(0,n.createContext)({pushDetailViewCallback:l(()=>w,"pushDetailViewCallback"),pushDetailView:w,popDetailView:w,resetDetailView:w,detailViewStackLength:0}),j=u(N.div)`
  position: relative;
  height: 100%;
  display: flex;
  flex-direction: column;
  max-height: ${e=>e.theme?.detailViewMaxHeight??"100%"};
  min-height: ${e=>e.theme?.detailViewMinHeight??"initial"};
`,me=n.default.memo(({children:e,shouldResetOnAccountChange:t,shouldPushDetailView:i})=>{let{detailViewStack:a,setDetailViewStack:c,pushDetailView:r,popDetailView:s,resetDetailView:d,pushDetailViewCallback:p}=J(),{data:g}=L();(0,n.useEffect)(()=>{t&&c([])},[g,c,t]),(0,n.useEffect)(()=>{i&&r(e)},[e,i,r]);let _=(0,n.useMemo)(()=>({pushDetailView:r,popDetailView:s,resetDetailView:d,pushDetailViewCallback:p,detailViewStackLength:a.length}),[r,s,d,p,a.length]);return(0,x.jsx)(F.Provider,{value:_,children:(0,x.jsx)(K,{stack:a,children:e})})}),G=navigator.webdriver?0:500,J=l(()=>{let[e,t]=(0,n.useState)([]),i=(0,n.useMemo)(()=>(0,$.default)(s=>{t(d=>C(d,p=>{p.push(s)}))},G,{leading:!0,trailing:!1}),[t]),a=(0,n.useCallback)(()=>{t(s=>C(s,d=>{d.pop()}))},[t]),c=(0,n.useCallback)(s=>()=>{i(s)},[i]),r=(0,n.useCallback)(()=>()=>{t([])},[t]);return(0,n.useMemo)(()=>({detailViewStack:e,setDetailViewStack:t,pushDetailView:i,popDetailView:a,resetDetailView:r,pushDetailViewCallback:c}),[e,a,i,r,c])},"useDetailViewStack"),q=.15,K=l(({children:e,stack:t})=>{let i=A(t,(p,g)=>p?.length===g.length),a=M(t),c=t.length>(i??[]).length,r=i===void 0;return(0,x.jsx)(B,{mode:"wait",children:(0,x.jsx)(j,{initial:{x:r?0:c?10:-10,opacity:r?1:0},animate:{x:0,opacity:1},exit:{opacity:0},transition:{duration:q},ref:Q,children:a||e},`${t.length}_${i?.length}`)})},"DetailViewsController"),k=l(()=>{let e=(0,n.useContext)(F);if(!e)throw new Error("Missing detail view context");return e},"useDetailViews"),Q=l(e=>{e&&e.parentElement&&(e.parentElement.scrollTop=0)},"resetScroll");f();h();var S=m(b(),1);var Y=(0,S.createContext)({isOpen:!1,showSettingsMenu:w,hideSettingsMenu:w}),z=l(()=>(0,S.useContext)(Y),"useSettingsMenu");f();h();var y=m(b(),1);var o=m(V(),1),Z=u.section`
  z-index: 1;
  background-color: ${D.colors.legacy.areaBase};
  padding: 10px 16px;
  display: flex;
  flex-shrink: 0;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid ${D.colors.legacy.elementBase};
  height: ${I}px;
  width: 100%;
`,ee=u(P).attrs(e=>({size:16,weight:500,lineHeight:25,maxWidth:e.maxWidth??"280px",noWrap:e.noWrap??!0}))``,te=u.div`
  display: flex;
  flex-shrink: 0;
  justify-content: center;
  align-items: center;
  padding-bottom: 17px;
  position: relative;
  width: 100%;
`,U=u(W)`
  position: absolute;
  right: 0;
`,H=u(T)`
  position: absolute;
  left: 0;
`,Be=l(({children:e,items:t,sections:i,icon:a,shouldWrap:c,onIconClick:r,onLeftButtonClick:s,useCloseButton:d})=>{let p=ne({withCloseButton:d??!1,onLeftButtonClick:s}),g=i&&i.length>0||t&&t.length>0;return(0,o.jsxs)(te,{children:[p,(0,o.jsx)(P,{weight:500,size:22,noWrap:!c,maxWidth:"280px",children:e}),g||r?(0,o.jsx)(U,{sections:i,items:t,icon:a||(0,o.jsx)(O,{}),onIconClick:r}):(0,o.jsx)("div",{})]})},"PageHeader"),ie=u(Z)`
  position: relative;
  border-bottom: none;

  &:after {
    content: "";
    position: absolute;
    bottom: 0;
    left: -20px;
    width: calc(100% + 40px);
    border-bottom: 1px solid ${D.colors.legacy.borderDiminished};
  }
`,oe=u.div`
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
`,Ne=l(({children:e,sections:t,items:i,icon:a,shouldWrap:c,onIconClick:r,onLeftButtonClick:s,disableIconBackground:d})=>{let p=ae(s),g=t&&t.length>0||i&&i.length>0;return(0,o.jsxs)(ie,{children:[p,(0,o.jsx)(oe,{children:typeof e=="string"?(0,o.jsx)(ee,{noWrap:!c,children:e}):e}),g||r?(0,o.jsx)(U,{sections:t,items:i,icon:a,onIconClick:r,disableIconBackground:d}):(0,o.jsx)("div",{})]})},"SettingsHeader"),ne=l(({withCloseButton:e,onLeftButtonClick:t})=>{let{popDetailView:i,detailViewStackLength:a}=k();return(0,y.useMemo)(()=>a===0?(0,o.jsx)("div",{}):(0,o.jsx)(H,{onClick:()=>{t?.(),i()},"data-testid":"header--back",children:e?(0,o.jsx)(v,{}):(0,o.jsx)(R,{})}),[e,a,t,i])},"usePageHeaderLeftButton"),ae=l(e=>{let{hideSettingsMenu:t}=z(),{popDetailView:i,detailViewStackLength:a}=k();return(0,y.useMemo)(()=>a>0?(0,o.jsx)(H,{onClick:()=>{i()},"data-testid":"header--back",children:(0,o.jsx)(R,{})}):(0,o.jsx)(H,{"data-testid":"settings-menu-close-button",onClick:e??t,children:(0,o.jsx)(v,{})}),[a,t,e,i])},"useSettingsHeaderLeftButton");export{me as a,k as b,Y as c,z as d,Z as e,ee as f,Be as g,Ne as h,ae as i};
//# sourceMappingURL=chunk-V53E4MU6.js.map
