import{m as W,t as K}from"./chunk-KJE7OXHO.js";import{L as E,Y as U}from"./chunk-ACMEWKV4.js";import{b as M,d as V}from"./chunk-V53E4MU6.js";import{c as B}from"./chunk-VRM2NWAU.js";import{b as D}from"./chunk-EOII3ZM4.js";import{Z as _,_ as O,c as H}from"./chunk-D3BHBSWL.js";import{b as x,c as a}from"./chunk-RLWRKBLA.js";import{c as i,na as N}from"./chunk-R6A7JGWU.js";import{e as L,f as y,sb as A}from"./chunk-ROW53IBC.js";import{a as c,g as d,i as u,n as g}from"./chunk-TSHWMJEM.js";u();g();var e=d(L());u();g();var f=d(y(),1),X=5,I=5,b=2,J=I+2*b,$=14,Q=$+2*b,j=I+2*b,Y=a.div`
  display: flex;
  justify-content: ${t=>t.shouldCenter?"center":"flex-start"};
  align-items: center;
  position: relative;
  overflow: hidden;
  width: ${t=>(t.maxVisible-1)*J+Q}px;
`,Z=a.div`
  align-items: center;
  display: flex;
  ${t=>t.shouldShift&&x`
      transform: translateX(calc(-${j}px * ${t.shiftAmount}));
      transition: transform 0.3s ease-in-out;
    `}
`,R=a.div`
  align-items: center;
  background-color: ${A.colors.legacy.textDiminished};
  border-radius: 95px;
  display: flex;
  height: ${X}px;
  justify-content: center;
  margin: 0 ${b}px;
  min-width: ${I}px;
  transition: all 0.3s ease-in-out;
  ${t=>t.isActive&&x`
      min-width: ${$}px;
    `}
  ${t=>t.isSmall&&x`
      min-width: 3px;
      margin: 0 ${b}px;
      height: 3px;
    `}
`,tt=a.div`
  width: ${$}px;
  height: ${X}px;
  border-radius: 95px;
  position: absolute;
  margin: 0 ${b}px;
  background-color: ${A.colors.legacy.spotBase};
  transition: transform 0.3s ease-in-out;
  ${t=>t.position&&x`
      transform: translateX(${t.position*j}px);
    `}
`,et=c(({numOfItems:t,currentIndex:o,maxVisible:r=5})=>{let n=t>r?o>r-3:!1,s=n?o-(r-3):0;return(0,f.jsx)(Y,{shouldCenter:r>t,maxVisible:r,children:(0,f.jsxs)(Z,{shouldShift:n,shiftAmount:s,children:[Array.from({length:t}).map((k,m)=>{let p=(m===o-2||m===o+2)&&n;return(0,f.jsx)(R,{isActive:o===m,isSmall:p},`pagination-dot-${m}`)}),(0,f.jsx)(tt,{position:o})]})})},"PaginationDots"),G=et;var nt=a.div`
  height: 0;
  transition: height 0.2s ease-in-out;
  width: 100%;
  ${t=>t.animate?`height: ${t.shouldCollapse?t.itemHeight+26:t.itemHeight+46}px`:""}
`,it=a.div`
  transition: transform 0.5s ease;
  width: 100%;
`,q=a(B)``,z=a.div`
  visibility: ${t=>t.isVisible?"visible":"hidden"};
`,ot=a.div`
  align-items: center;
  display: flex;
  justify-content: space-between;
`,at=a.ul`
  align-items: center;
  display: flex;
  margin-bottom: 8px;
  transition: transform 0.5s ease;
  transform: ${t=>`translateX(${t.currentIndex*-100}%)`};
`,rt=a.li`
  align-items: center;
  display: flex;
  flex: 0 0 100%;
  padding: ${t=>t.isActive?"0":t.isNext||t.isPrevious?"0 6px":"0"};
  height: ${t=>t.isActive?t.itemHeight:.9*t.itemHeight}px; /* 0.9 is taken from parallaxAdjacentItemScale from the carousel on mobile */
`,Ct=c(({items:t,onIndexChange:o,itemHeight:r})=>{let[n,s]=(0,e.useState)(0),k=(0,e.useCallback)(()=>{s(l=>l+1)},[]),m=(0,e.useCallback)(()=>{s(l=>l-1)},[]),p=n<t.length-1,v=n>0;(0,e.useEffect)(()=>{!t.length||n>t.length-1||o(n)},[t,o,n]),(0,e.useEffect)(()=>{t.length>0&&n>=t.length&&s(t.length-1)},[n,t]);let C=t.length<=1;return e.default.createElement(nt,{animate:t.length>0,shouldCollapse:C,itemHeight:r},e.default.createElement(it,null,e.default.createElement(at,{currentIndex:n},t.map((l,h)=>e.default.createElement(rt,{key:l.key,isActive:n===h,isNext:n+1===h,isPrevious:n-1===h,itemHeight:r},l.node))),!C&&e.default.createElement(ot,null,e.default.createElement(z,{isVisible:v},e.default.createElement(q,{onClick:m},e.default.createElement(_,null))),e.default.createElement(G,{numOfItems:t.length,currentIndex:n,maxVisible:5}),e.default.createElement(z,{isVisible:p},e.default.createElement(q,{onClick:k},e.default.createElement(O,null))))))},"Carousel");u();g();var S=d(L(),1);u();g();var F=c(t=>{if(t===i.SettingsSecurityAndPrivacy)return K;if(t===i.SettingsCurrency)return W},"getSanityComponentMapping");var P=d(y(),1),st=S.default.lazy(()=>import("./FungibleDetailPage-VMZHSFN3.js")),Wt=c(()=>{let{showSettingsMenu:t}=V(),{handleShowModalVisibility:o}=U(),{pushDetailView:r}=M(),n=N(),s=H();return(0,S.useCallback)((k,m)=>{let{destinationType:p,url:v,caip19:C,tokenCategoryId:l,tokenCategoryName:h}=m;switch(p){case i.ExternalLink:D({url:v});break;case i.Buy:o("onramp");break;case i.Collectibles:s("/",{state:{defaultTab:"collectibles",nonce:Date.now()}});break;case i.Explore:s("/explore");break;case i.TokenCategory:{if(!l||!h)return;r((0,P.jsx)(E,{category:{id:l,name:h}}));break}case i.Swapper:s("/swap");break;case i.SettingsClaimUsername:o("quickClaimUsername");break;case i.SettingsImportSeedPhrase:D({url:"onboarding.html?append=true"});break;case i.ConnectHardwareWallet:D({url:"connect_hardware.html"});break;case i.ConvertToJito:o(n?"mintPSOLUKInfo":"mintPSOLInfo",{presentNext:!0});break;case i.Token:{if(!C)return;r((0,P.jsx)(st,{caip19:C,title:void 0,entryPoint:"actionBanner"}));break}default:{let w=F(p);if(!w)return;t(k,(0,P.jsx)(w,{}))}}},[s,t,o,r,n])},"useDeepLink");export{Wt as a,Ct as b};
//# sourceMappingURL=chunk-RSUD4MBN.js.map
