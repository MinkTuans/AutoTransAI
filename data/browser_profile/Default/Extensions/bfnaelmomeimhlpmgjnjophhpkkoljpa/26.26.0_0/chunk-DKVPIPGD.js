import{a as $,c as Y,d as Z}from"./chunk-5FRW4UO4.js";import{b as Q}from"./chunk-FFDTKKDT.js";import{a as J,d as X}from"./chunk-7FPALEDT.js";import{g as x}from"./chunk-V53E4MU6.js";import{a as K,d as q}from"./chunk-2EQUCBKU.js";import{Za as a}from"./chunk-D3BHBSWL.js";import{c as i}from"./chunk-RLWRKBLA.js";import{K as _,X as G,aa as R,da as W,w as H,x as O}from"./chunk-R6A7JGWU.js";import{E as N,S as F,Va as U,ub as z}from"./chunk-OY47TOHT.js";import{b as I}from"./chunk-G2YN7S6F.js";import{ea as D}from"./chunk-44KDTK4M.js";import{La as f,Ma as E,Nb as L,Oa as Tt,Se as B,q as w,t as P}from"./chunk-QPUEUZLS.js";import{c as V,e as ht,f as M,sb as n,t as S}from"./chunk-ROW53IBC.js";import{a as s,g,i as b,n as k}from"./chunk-TSHWMJEM.js";b();k();var p=g(ht(),1);var t=g(M(),1),vt=s(r=>{let{t:e}=S(),{voteAccountPubkey:c}=r,{showStakeAccountCreateAndDelegateStatusModal:et,closeAllModals:ot}=Q(),at=s(()=>{r.onClose(),ot()},"onCloseTxStatusView"),{data:nt}=D(w.Solana),{data:it}=U(),rt=it?.totalQuantityString??"";H(nt,z.STAKE_FUNGIBLE);let{cluster:st,connection:y}=F(),l=G(),lt=L(P.Solana),{data:ct}=N({query:{data:lt}}),mt=ct?.usd,o=(0,p.useMemo)(()=>l.results?.find(At=>At.voteAccountPubkey===c),[l.results,c]),dt=o?.info?.name??o?.info?.keybaseUsername??B(c),ut=X(y),[m,C]=(0,p.useState)(""),d=V(m),A=W(y).data??0,T=f(J+A),h=R({balance:rt,cluster:st,rentExemptionMinimum:f(A)}),pt=s(()=>C(h.toString()),"onSetMax"),gt=d.isLessThan(T),ft=d.isGreaterThan(h),St=d.isFinite(),u=m&&gt?e("validatorViewAmountSOLRequiredToStakeInterpolated",{amount:T}):m&&ft?e("validatorViewInsufficientBalance"):"",xt=ut.isPending,v=St&&!u&&!xt,yt=s(()=>{et({lamports:E(d).toNumber(),votePubkey:c,usdPerSol:mt,onClose:at,validatorName:dt})},"onSubmit"),Ct=o?.totalApy?_(o.totalApy):null;return(0,t.jsx)(bt,{children:l.isPending?(0,t.jsx)(K,{}):l.isError||!o?(0,t.jsxs)(t.Fragment,{children:[(0,t.jsx)(x,{children:e("validatorViewPrimaryText")}),(0,t.jsx)(j,{children:(0,t.jsxs)(a,{size:16,color:n.colors.legacy.textDiminished,lineHeight:20,children:[e("validatorViewErrorFetching")," ",l.error?.message??""]})})]}):(0,t.jsxs)(t.Fragment,{children:[(0,t.jsx)(x,{children:e("validatorViewPrimaryText")}),(0,t.jsxs)(j,{children:[(0,t.jsx)(a,{size:16,color:n.colors.legacy.textDiminished,lineHeight:20,margin:"0 0 20px 0",children:(0,t.jsxs)(I,{i18nKey:"validatorViewDescriptionInterpolated",children:["Choose how much SOL you\u2019d like to ",(0,t.jsx)("br",{}),"stake with this validator. ",(0,t.jsx)(tt,{href:O,children:"Learn more"})]})}),(0,t.jsx)($,{value:m,symbol:"SOL",alignSymbol:"right",buttonText:e("maxInputMax"),width:47,warning:!!u,onSetTarget:pt,onUserInput:C}),(0,t.jsx)(wt,{children:(0,t.jsx)(a,{color:u?n.colors.legacy.spotNegative:"transparent",size:16,textAlign:"left",children:u})}),(0,t.jsx)(Vt,{onEdit:r.onClose}),(0,t.jsx)(Y,{identifier:o.voteAccountPubkey,name:o.info?.name,keybaseUsername:o.info?.keybaseUsername,iconUrl:o.info?.iconUrl,website:o.info?.website,data:[{label:e("validatorCardEstimatedApy"),value:(0,t.jsxs)(a,{textAlign:"right",weight:500,size:14,noWrap:!0,children:[Ct,"%"]})},{label:e("validatorCardCommission"),value:(0,t.jsxs)(a,{textAlign:"right",weight:500,size:14,noWrap:!0,children:[o.commission,"%"]})},{label:e("validatorCardTotalStake"),value:(0,t.jsx)(a,{textAlign:"right",weight:500,size:14,noWrap:!0,children:(0,t.jsx)(Z,{children:o.activatedStake})})}]})]}),(0,t.jsx)(kt,{children:(0,t.jsx)(q,{primaryText:e("validatorViewActionButtonStake"),secondaryText:e("commandClose"),onPrimaryClicked:yt,onSecondaryClicked:r.onClose,primaryTheme:v?"primary":"default",primaryDisabled:!v})})]})})},"StakeAmountPage"),ae=vt,bt=i.div`
  display: grid;
  grid-template-rows: 42px auto 47px;
  height: 100%;
`,j=i.div`
  display: flex;
  flex-direction: column;
  align-items: center;
`,tt=i.a.attrs({target:"_blank",rel:"noopener noreferrer"})`
  color: ${n.colors.legacy.spotBase};
  text-decoration: none;
  cursor: pointer;
`,kt=i.section`
  display: flex;
  gap: 15px;
`,wt=i.div`
  width: 100%;
`,Pt=i(a)`
  width: 100%;
  margin-top: 15px;
  > a {
    color: ${n.colors.legacy.spotBase};
    cursor: pointer;
  }
`,Vt=s(r=>{let{t:e}=S();return(0,t.jsxs)(Pt,{size:16,color:n.colors.legacy.textDiminished,lineHeight:20,textAlign:"left",children:[e("validatorViewValidator")," \u2022 ",(0,t.jsx)(tt,{onClick:r.onEdit,children:e("commandEdit")})]})},"ValidatorSectionLabel");export{vt as a,ae as b};
//# sourceMappingURL=chunk-DKVPIPGD.js.map
