import{a as w,b as Y,c as g}from"./chunk-IJQ4KOXN.js";import{a as G}from"./chunk-6NA7ELBO.js";import{H as W,m as _}from"./chunk-ACMEWKV4.js";import{o as F}from"./chunk-T5DSHPMV.js";import{e as H,l as M}from"./chunk-FUOWEUPT.js";import{a as K}from"./chunk-CCMUSPWN.js";import{a as E}from"./chunk-4VICHEHO.js";import{Ya as J,Za as L}from"./chunk-D3BHBSWL.js";import{c as n}from"./chunk-RLWRKBLA.js";import{A as B,Ia as q}from"./chunk-R6A7JGWU.js";import{b as z}from"./chunk-G2YN7S6F.js";import{Se as I}from"./chunk-QPUEUZLS.js";import{Hb as b,Qb as N,Rb as R,bc as O,cd as V,e as fo,f as k,jb as U,qb as s,sb as u,t as D}from"./chunk-ROW53IBC.js";import{a as d,g as f,i as x,n as T}from"./chunk-TSHWMJEM.js";x();T();var h=f(fo(),1);x();T();var r=f(k(),1),wo=n.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  width: 100%;
  height: 83px;
  padding: 16px;
`,go=n.div`
  margin-left: 12px;
  width: 100%;
`,xo=n(L).attrs({size:14,weight:400,color:u.colors.legacy.textDiminished,textAlign:"left"})``,To=n.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`,ko=n(L).attrs({size:28,lineHeight:32,weight:600,color:u.colors.legacy.textBase,textAlign:"left"})`
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
`,v=d(({title:e,network:a,tokenType:l,symbol:m,logoUri:p,tokenAddress:y,amount:i,amountUsd:t})=>(0,r.jsxs)(wo,{children:[(0,r.jsx)(M,{image:{type:"fungible",src:p,fallback:m||y},size:44,tokenType:l,chainMeta:a}),(0,r.jsxs)(go,{children:[(0,r.jsxs)(To,{children:[(0,r.jsx)(xo,{children:e}),(0,r.jsx)(H,{value:t,font:"textSm",color:"textDiminished"})]}),(0,r.jsx)(ko,{children:i})]})]}),"AssetRow");var o=f(k(),1),c={screen:s({overflow:"auto"}),body:s({display:"flex",flexDirection:"column",justifyContent:"space-between"}),content:s({display:"flex",flexDirection:"column",width:"100%"}),assets:s({width:"100%"}),line:s({backgroundColor:"areaBase",width:"100%",height:1}),button:s({width:"100%",height:48})},S=n(J).attrs({color:E.grayLight,size:14})`
  text-align: left;
  line-height: normal;
  max-width: 100%;
  margin: 16px 0;
`,bo=n.a.attrs({target:"_blank",rel:"noopener noreferrer"})`
  color: ${e=>e.theme.purple};
  text-decoration: none;
  cursor: pointer;
`,ho=d(({isJitoSOL:e,feeFootnoteText:a,feeFootnoteDescriptionText:l,feeFootnoteTooltipText:m,showUKDisclaimer:p})=>e?(0,o.jsx)(S,{children:(0,o.jsxs)(z,{i18nKey:"liquidStakeReviewConversionFootnote",children:["When you stake Solana tokens in exchange for JitoSOL you'll receive a slightly lesser amount of JitoSOL.",(0,o.jsx)(bo,{href:B,children:"Learn more"})]})}):p?(0,o.jsx)(W,{disclaimers:[],showUKDisclaimer:!0,showPastPerformanceInline:!0,marginTop:16,onPastPerformancePress:void 0,onDisclosuresPress:void 0,onFeeDisclaimerPress:void 0}):(0,o.jsxs)(o.Fragment,{children:[(0,o.jsx)(S,{children:(0,o.jsx)(G,{tooltipAlignment:"topLeft",iconSize:12,lineHeight:17,fontWeight:400,info:(0,o.jsx)(Y,{tooltipContent:(0,o.jsx)(F,{children:m})}),textColor:u.colors.legacy.textDiminished,children:a})}),(0,o.jsx)(S,{children:l})]}),"ConversionFootnote"),yo=d(({children:e})=>(0,o.jsx)(b,{direction:"row",width:"100%",gap:8,paddingRight:4,children:e}),"DelayDisclaimer"),Ro=d(({durationUntilEpochEnds:e})=>{let{t:a}=D(),l=(0,h.useMemo)(()=>[{topLeft:{component:yo,text:(0,o.jsx)(o.Fragment,{children:(0,o.jsx)(R,{children:a("convertToPSOLDelayDisclaimer",{durationUntilEpochEnds:e})})}),truncate:void 0,style:{wordWrap:"break-word",whiteSpace:"normal"},before:(0,o.jsx)(U,{size:18,style:{alignSelf:"flex-start",marginTop:2}})}}],[a,e]);return(0,o.jsx)(V,{rows:l})},"DepositStakeFootnote"),jo=h.default.memo(({process:e,headerTitle:a,onBack:l,openExternalLink:m,onPrimaryButtonPress:p,canSubmit:y,payAsset:i,receiveAsset:t,account:$,providerName:j,apy:A,networkFee:Q,isLoading:C,networkFeeErrorMsg:X,isJitoSOL:Z,strings:oo,showUKDisclaimer:P,durationUntilEpochEnds:eo})=>{let{accountLabelText:to,providerLabelText:io,apyLabelText:no,apyLabelTextTooltip:ro,networkFeeLabelText:ao,primaryButtonText:lo,feeFootnoteText:so,feeFootnoteDescriptionText:mo,feeFootnoteTooltipText:co}=oo,po=[t?(0,o.jsx)(w,{label:to,children:(0,o.jsx)(g,{children:(0,o.jsx)(R,{font:"textMd",children:I($,4)})})},"account-row"):null,(0,o.jsx)(w,{label:io,children:(0,o.jsx)(g,{children:j})},"provider-row"),(0,o.jsx)(w,{label:no,tooltipContent:(0,o.jsx)(F,{children:ro}),children:(0,o.jsx)(g,{children:A})},"apy-row"),(0,o.jsx)(w,{label:ao,isLoading:C,error:X,children:(0,o.jsx)(g,{children:Q})},"network-fee-row")];return(0,o.jsxs)("div",{className:c.screen,children:[(0,o.jsx)(_,{leftButton:{type:"back",onClick:l},titleSize:"regular",children:a}),(0,o.jsxs)("div",{className:c.body,children:[m&&P?(0,o.jsx)(b,{marginBottom:"base",children:(0,o.jsx)(q,{paddingTop:8,navigateToExternalLink:m})}):null,(0,o.jsxs)("div",{className:c.content,children:[(0,o.jsx)(N,{borderRadius:6,children:(0,o.jsxs)("div",{className:c.assets,children:[i?(0,o.jsx)(v,{title:i.title,amount:i.amount+" "+i.symbol,amountUsd:i.amountUsd,logoUri:i.logoUri,symbol:i.symbol,tokenType:i.tokenType,tokenAddress:i.tokenAddress,network:i.network}):null,(0,o.jsx)("div",{className:c.line}),t?(0,o.jsx)(v,{title:t.title,amount:t.amount+" "+t.symbol,amountUsd:t.amountUsd,logoUri:t.logoUri,symbol:t.symbol,tokenType:t.tokenType,tokenAddress:t.tokenAddress,network:t.network}):null]})}),(0,o.jsx)(b,{marginY:"base",borderRadius:8,gap:1,overflow:"hidden",children:po}),e==="mint"?(0,o.jsx)(ho,{isJitoSOL:Z,feeFootnoteText:so,feeFootnoteDescriptionText:mo,feeFootnoteTooltipText:co,showUKDisclaimer:P}):e==="convertDelayed"?(0,o.jsx)(Ro,{durationUntilEpochEnds:eo}):null]}),(0,o.jsx)(K,{children:(0,o.jsx)(O,{className:c.button,background:"spot",disabled:!y||C,onClick:p,children:lo})})]})]})});export{jo as a};
//# sourceMappingURL=chunk-LI6DJGU2.js.map
