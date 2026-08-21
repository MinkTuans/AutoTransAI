import{a as N}from"./chunk-DVKCIH7A.js";import{a as gt}from"./chunk-LO363DVC.js";import{b as we}from"./chunk-AFULND2K.js";import{b as St,c as Ct,d as Re}from"./chunk-VQSRXQ54.js";import{d as Q}from"./chunk-P43JCO4S.js";import{b as At}from"./chunk-CL5XSPPA.js";import{a as ut,m as lt,x as le}from"./chunk-WBIHZ7LK.js";import{b as st,c as _e}from"./chunk-OH3W2BRU.js";import{l as mt,m as ht}from"./chunk-EOII3ZM4.js";import{b as he}from"./chunk-2EQUCBKU.js";import{Za as U,pa as ft}from"./chunk-D3BHBSWL.js";import{c as s}from"./chunk-RLWRKBLA.js";import{a as me}from"./chunk-V6Q45TV4.js";import{g as it,h as Oe,i as dt,ia as pt,k as Pe}from"./chunk-44KDTK4M.js";import{Lg as Be,Se as ot,Td as et,Vf as at,j as J,m as Xe,n as Ze,o as Je,pb as Qe,q as P,qb as $,re as De,te as tt}from"./chunk-QPUEUZLS.js";import{A as Ge,Ja as rt,Ua as ct,bc as F,e as ce,f as M,ha as nt,sb as R,t as H}from"./chunk-ROW53IBC.js";import{a as n,g as b,i as S,n as C}from"./chunk-TSHWMJEM.js";S();C();var Ft={existingAccounts:{data:[],isFetched:!1,isError:!1},hardwareStepStack:[],hardwareStepSubStack:{},selectedChains:[],selectedChainsMap:new Map,chainImportStep:1,derivedAccountGroups:[],discoveredAccounts:[],activeAccountsFound:!1,selectedAccounts:{},onConnectHardwareAccounts:n(e=>Promise.resolve(),"onConnectHardwareAccounts"),onConnectHardwareDone:n(()=>{},"onConnectHardwareDone")},L=pt((e,o)=>({...Ft,pushStep:n(t=>{let r=o().hardwareStepStack;e({hardwareStepStack:r.concat(t)})},"pushStep"),popStep:n(()=>{let r=o().hardwareStepStack.length-1;if((o().hardwareStepSubStack[r]??[]).length)return e(Be(d=>{d.hardwareStepSubStack[r]=d.hardwareStepSubStack[r].slice(0,-1)}));e(Be(d=>{d.hardwareStepStack=d.hardwareStepStack.slice(0,-1)}))},"popStep"),pushSubStep:n(t=>{let c=o().hardwareStepStack.length-1,d=o().hardwareStepSubStack[c]??[];e(Be(x=>{x.hardwareStepSubStack[c]=d.concat([t])}))},"pushSubStep"),currentStep:n(()=>{let t=o().hardwareStepStack,r=o().hardwareStepSubStack,c=t.length>0?t.length-1:t.length;return r[c]?.length?Ge(r[c]):Ge(t)},"currentStep"),setExistingAccounts:n(t=>{e({existingAccounts:t})},"setExistingAccounts"),setSelectedChains:n((t,r)=>{e({selectedChains:t,selectedChainsMap:r})},"setSelectedChains"),setDecrementChainImportStep:n(()=>{let t=o().chainImportStep;e({chainImportStep:t-1})},"setDecrementChainImportStep"),setIncrementChainImportStep:n(()=>{let t=o().chainImportStep;e({chainImportStep:t+1})},"setIncrementChainImportStep"),setDerivedAccountGroups:n(t=>{e({derivedAccountGroups:t})},"setDerivedAccountGroups"),setDiscoveredAccounts:n((t,r)=>{e({discoveredAccounts:t,activeAccountsFound:r})},"setDiscoveredAccounts"),selectAccount:n(t=>{let c={...o().selectedAccounts};c[t]=!0,e({selectedAccounts:c})},"selectAccount"),deselectAccount:n(t=>{let c={...o().selectedAccounts};delete c[t],e({selectedAccounts:c})},"deselectAccount"),setSelectedAccounts:n(t=>{e({selectedAccounts:t})},"setSelectedAccounts"),setOnConnectHardwareAccounts:n(t=>{e({onConnectHardwareAccounts:t})},"setOnConnectHardwareAccounts"),setOnConnectHardwareDone:n(t=>{e({onConnectHardwareDone:t})},"setOnConnectHardwareDone")}));S();C();S();C();S();C();var wt=s.main`
  box-shadow: 0px 10px 20px rgba(0, 0, 0, 0.4);
  width: ${420}px;
  min-height: ${480}px;
  position: relative;
  overflow: hidden;
  background-color: ${R.colors.legacy.areaBase};
  border: 1px solid ${R.colors.legacy.borderBase};
  border-radius: 16px;
`;var Io=s(wt)`
  display: flex;
  flex-direction: column;
`,Do=s.div`
  display: flex;
  flex-direction: column;
  flex: 1;
  width: 100%;
  padding: 20px 20px;
`,ee=s.div`
  padding-top: 44px;
`,W=s.div`
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  flex: 1;
  width: 100%;
  overflow: auto;
`;S();C();var kt=b(ce(),1);S();C();var v=b(ce(),1);S();C();var se=b(ce(),1);S();C();var fe=b(ce(),1);var ae=b(M(),1),Ne=n(()=>{let{t:e}=H(),{discoveredAccounts:o,selectedAccounts:t,onConnectHardwareAccounts:r,onConnectHardwareDone:c}=L(),{mutateAsync:d}=it(),[x,w]=(0,fe.useState)(!1),g=(0,fe.useMemo)(()=>o.filter(l=>!!t[l.discoveryIdentifier]),[o,t]);return(0,fe.useEffect)(()=>{if(g.length){let l=[],a=new Set;for(let u of g){let{accounts:A,seedIndex:T,accountIndex:k}=u,E=[],D=[];for(let y of A)Xe(y.derivationPathType)?(D.push({pathType:y.derivationPathType,value:y.publicKey}),(!("amount"in y)||parseFloat(y.amount)!==0)&&a.add(y.chainType)):(Ze(y.derivationPathType)||Je(y.derivationPathType))&&E.push({pathType:y.derivationPathType,value:y.address});l.push({derivationIndex:T,addresses:E,publicKeys:D,accountIndex:k})}r({accounts:l}).then(()=>{a.size>0&&d({addressTypes:Array.from(a)})}).finally(()=>w(!0))}else w(!0)},[g,r,d]),(0,ae.jsxs)(W,{children:[(0,ae.jsx)(ee,{children:(0,ae.jsx)(Q,{icon:(0,ae.jsx)(N,{type:"success"}),primaryText:e("connectHardwareAccountsAddedInterpolated",{numOfAccounts:g.length}),headerStyle:"large",secondaryText:e("connectHardwareFinishSecondaryText")})}),(0,ae.jsx)(F,{onClick:c,background:"spot",disabled:!x,children:e("pastParticipleDone")})]})},"ConnectHardwareImportConfirmation");S();C();var Me=b(ce(),1);S();C();var ze=b(ce(),1);var h=b(M(),1),Wt=n((e,o,t)=>{switch(o){case"seed":return e("onboardingImportAccountsAccountName",{walletIndex:t});case"ledger":return e("onboardingImportAccountsLedgerAccountName",{walletIndex:t})}},"getAccountName"),$t=n(({account:e})=>{let{t:o}=H();return(0,h.jsxs)(Yt,{children:[(0,h.jsx)(zt,{children:(0,h.jsx)(me,{networkID:e.chain.id,size:40,borderColor:"elementBase"})}),(0,h.jsxs)(Ut,{children:[(0,h.jsxs)(jt,{children:[(0,h.jsx)(At,{networkID:e.chain.id,walletAddress:e.address,children:(0,h.jsx)(Le,{children:e.chain.name})}),(0,h.jsx)(Le,{children:ot(e.address,4)})]}),(0,h.jsxs)(Ee,{children:["amount"in e&&"chain"in e?(0,h.jsxs)(yt,{children:[nt(e.amount)," ",e.chain.symbol]}):null,"amount"in e&&e.lastActivityTimestamp?(0,h.jsx)(yt,{children:o("onboardingImportAccountsLastActive",{formattedTimestamp:rt(e.lastActivityTimestamp*1e3,!0)})}):null]})]})]})},"DiscoveredAccountCard"),bt=ze.default.memo(({accountType:e,accounts:o,checked:t,accountIndex:r,onPress:c})=>{let{t:d}=H(),x=r+1;return(0,h.jsxs)(xt,{children:[(0,h.jsxs)(Kt,{children:[(0,h.jsx)(Le,{children:Wt(d,e,x)}),(0,h.jsx)(we,{checked:t,onChange:c,"data-testid":"account-select-address-row-checkbox"})]}),o.map((w,g)=>(0,h.jsx)($t,{account:w},`${w.address}-${g}`))]})}),on=ze.default.memo(({totalAccounts:e,selectedAccounts:o,onPress:t})=>{let{t:r}=H();return(0,h.jsx)(xt,{children:(0,h.jsxs)(Vt,{children:[(0,h.jsx)(Le,{children:r("onboardingSelectAccountsNoOfAccountsSelected",{numOfAccounts:o})})," ",(0,h.jsxs)(qt,{children:[r("onboardingSelectAccountSelectAllText")," ",(0,h.jsx)(we,{checked:o===e,onChange:t,"data-testid":"account-select-all-checkbox"})]})]})})}),xt=s.div`
  margin-bottom: 24px;
  width: 100%;
`,zt=s.div`
  flex-shrink: 0;
  margin-right: 10px;
`,Ut=s.div`
  display: flex;
  flex-direction: column;
  width: 100%;
`,Ee=s.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  width: 100%;
`,jt=s(Ee)`
  margin-bottom: 2px;
`,Vt=s(Ee)`
  background: ${R.colors.legacy.elementBase};
  margin-bottom: 1px;
  padding: 12px 10px 12px 14px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: space-between;
`,qt=s.div`
  display: flex;
  align-items: center;
  gap: 10px;
`,Kt=s(Ee)`
  background: ${R.colors.legacy.elementBase};
  margin-bottom: 1px;
  padding: 12px 16px 12px 14px;
  border-top-left-radius: 6px;
  border-top-right-radius: 6px;

  & > span {
    margin-right: 0;
  }
`,Yt=s.div`
  background: ${R.colors.legacy.elementBase};
  margin-top: 1px;
  padding: 17px 16px 17px 14px;
  width: 100%;
  display: flex;
  align-items: center;

  &:last-of-type {
    border-bottom-left-radius: 6px;
    border-bottom-right-radius: 6px;
  }
`,Le=s(U).attrs({size:16,lineHeight:19,weight:600})``,yt=s(U).attrs({size:14,lineHeight:17,weight:400,color:R.colors.legacy.textDiminished})``;var j=b(M(),1),Tt=n(({activeAccounts:e})=>{let{t:o}=H(),{selectedAccounts:t,selectAccount:r,deselectAccount:c,pushSubStep:d}=L(),x=(0,Me.useMemo)(()=>Object.values(t).filter(l=>!!l).length===0,[t]),w=(0,Me.useCallback)(()=>{d((0,j.jsx)(Ne,{preventBack:!0}))},[d]);return(0,j.jsxs)(W,{children:[(0,j.jsxs)("div",{style:{marginBottom:15},children:[(0,j.jsxs)("div",{style:{display:"flex",flexDirection:"column",alignItems:"center",marginBottom:30},children:[(0,j.jsx)(U,{weight:500,size:30,lineHeight:34,maxWidth:"320px",children:o("connectHardwareSelectAccounts")}),(0,j.jsx)(Xt,{wordBreak:"break-word",size:18,lineHeight:22,color:R.colors.legacy.textDiminished,children:o("connectHardwareChooseAccountsToConnect")})]}),(0,j.jsx)("div",{style:{maxHeight:420,overflowY:"scroll"},children:e.map(({accounts:g,discoveryIdentifier:l,accountIndex:a})=>{let _=!!t[l];return(0,j.jsx)(bt,{accountType:"ledger",accounts:g,accountIndex:a,checked:_,onPress:n(()=>{_?c(l):r(l)},"onPress")},l)})})]}),(0,j.jsx)(F,{onClick:w,background:"spot",disabled:x,children:o("commandContinue")})]})},"ConnectHardwareSelectAccounts"),Xt=s(U)`
  margin-top: 15px;
`;var Z=b(M(),1),vt=n(()=>{let{t:e}=H(),{discoveredAccounts:o,activeAccountsFound:t,setSelectedAccounts:r,pushSubStep:c}=L(),d=(0,se.useMemo)(()=>{let g;if(t){let l=o.filter(a=>a.status==="undiscovered"||a.isSelectedByDefault);g=e(l.length===1?"connectHardwareFoundAccountsWithActivitySingular":"connectHardwareFoundAccountsWithActivity",{numOfAccounts:l.length})}else g=e("connectHardwareFoundSomeAccounts");return g},[t,e,o]),x=(0,se.useCallback)(()=>{c((0,Z.jsx)(Tt,{activeAccounts:o}))},[c,o]),w=(0,se.useCallback)(()=>{c((0,Z.jsx)(Ne,{preventBack:!0}))},[c]);return(0,se.useEffect)(()=>{let g=o.reduce((l,a,_)=>((a.status==="discovered"&&a.isSelectedByDefault||_===0)&&(l[a.discoveryIdentifier]=!0),l),{});r(g)},[o,r,t,e]),(0,Z.jsxs)(W,{children:[(0,Z.jsx)(Zt,{children:(0,Z.jsx)(Q,{icon:(0,Z.jsx)(N,{type:"success"}),primaryText:e("connectHardwareConnectAccounts"),headerStyle:"large",secondaryText:d})}),(0,Z.jsx)(Jt,{background:"spot",onClick:x,children:e("connectHardwareSelectAccounts")}),(0,Z.jsx)(F,{onClick:w,background:"spot",children:e("commandContinue")})]})},"ConnectHardwareImportAccounts"),Zt=s(ee)`
  margin-bottom: 35px;
`,Jt=s(F)`
  margin-bottom: 10px;
`;var f=b(M(),1),Qt=19,eo=n(e=>{let o=new Set;for(let t of e)for(let{address:r}of t.addresses)o.add(r);return o},"getExistingAddressesSet"),ye=n(()=>{let{chainImportStep:e,setIncrementChainImportStep:o,selectedChains:t,selectedChainsMap:r,pushStep:c,pushSubStep:d,setDiscoveredAccounts:x,setDerivedAccountGroups:w,derivedAccountGroups:g}=L(),l=(0,v.useRef)(g),{t:a,i18n:_}=H(),u=e-1,A=t[u],{data:T=[],isFetched:k,isError:E}=L(p=>p.existingAccounts),[D,y]=(0,v.useState)(!1),B=(0,v.useMemo)(()=>{let p=[],m=r.get(A)||{};for(let[z,oe]of Object.entries(m))oe&&p.push(z);return[p[0]]},[A,r]),{chainNameTextOr:te,chainNameTextAnd:ie}=(0,v.useMemo)(()=>{let p=B.map(oe=>$.getChainName(le.get(oe).ledgerAppOverride??oe)),m=new Intl.ListFormat(_.resolvedLanguage,{style:"long",type:"disjunction"}),z=new Intl.ListFormat(_.resolvedLanguage,{style:"long",type:"conjunction"});return{chainNameTextOr:m.format(p),chainNameTextAnd:z.format(p)}},[B,_]),be=(0,v.useMemo)(()=>B.map(p=>{let m=le.get(p).ledgerAppOverride??p;return(0,f.jsx)(me,{networkID:m,size:72,borderColor:"areaBase"},$.getMainnetNetworkID(le.get(m).ledgerAppOverride??m))}),[B]);(0,v.useEffect)(()=>{let p=L.subscribe(m=>l.current=m.derivedAccountGroups);return()=>p()},[]);let V=(0,v.useMemo)(()=>{let p=[];switch(A){case P.Solana:{p.push({pathType:J.Bip44RootSolana});break}case P.EVM:{p.push({pathType:J.Bip44RootEthereum});break}case P.BitcoinTaproot:case P.BitcoinNativeSegwit:case P.BitcoinNestedSegwit:case P.BitcoinLegacy:case P.Sui:break}for(let m=0;m<Qt;++m)switch(A){case P.Solana:{p.push({index:m,pathType:J.Bip44ChangeSolana}),p.push({index:m,pathType:J.Bip44Solana});break}case P.EVM:{p.push({index:m,pathType:J.Bip44Ethereum}),p.push({index:m,pathType:J.Bip44EthereumSecondary});break}case P.BitcoinTaproot:case P.BitcoinNativeSegwit:case P.BitcoinNestedSegwit:case P.BitcoinLegacy:{p.push({index:m,pathType:J.BitcoinTaproot},{index:m,pathType:J.BitcoinNativeSegwit});break}case P.Sui:throw new Qe("connect hardware")}return p},[A]),[xe,Te]=(0,v.useState)(!0),{data:de=ut}=Ct(xe,!0),{data:[It]}=et(["kill-ledger-xpub-derivation"]),{data:ne,error:Ue,fetchStatus:Dt,refetch:je}=St(de,V,!0,!It),Bt=Dt==="fetching",Fe=!de.isConnected&&de.status!=="reconnecting",[Ot,Pt]=(0,v.useState)(!1),{data:ve,refetch:Ve}=Re(Ot,!0);(0,v.useEffect)(()=>{Fe&&Te(!1)},[Fe]),(0,v.useEffect)(()=>{ve?.type==="granted"&&(Te(!0),Pt(!1))},[ve]);let qe=dt(),Ke=(0,v.useCallback)(async()=>{if(ne&&Object.keys(ne).length){let p=[...l.current],m=0;for(let z of Object.values(ne)){let Ae={accounts:{...(p[m]??{accounts:{}}).accounts},derivationIndex:V[m].index},He=$.getChainIDs(z.addressType).filter(ke=>qe.includes(ke));for(let ke of He){let Se=$.getNetworkIDs(ke);for(let ue of Se)B.includes(ue)&&(Ae.accounts[`${ue}-${z.address}`]={chainType:z.addressType,chainId:ue,address:z.address,publicKey:z.publicKey,pathParams:V[m]})}p[m]=Ae,m++}if(w(p),k&&t.length===e){y(!0);let z=eo(T),oe=p.reduce((i,O)=>{let Ce=!1;for(let Ie of Object.values(O.accounts))Ce=Ce||z.has(Ie.address);return Ce||i.push(O),i},[]),Ae=[],He=[];for(let i=0;i<oe.length;i+=_e.extension){let O=oe.slice(i,i+_e.extension).map(Ce=>Object.entries(Ce.accounts).reduce((Ie,[Et,Mt])=>(Ie[Et]={account:Mt},Ie),{}));He.push(O)}for(let i of He)Ae.push(st(i));let Se=(await Promise.all(Ae)).flat().map(i=>{switch(i.status){case"discovered":return{...i,accounts:i.accounts.filter(O=>O.hasAccountActivity||De(O.derivationPathType))};case"undiscovered":return{...i,accounts:i.accounts.filter(O=>De(O.derivationPathType))}}}).filter(i=>i.accounts.length>0).map(i=>{let O=at();return{...i,discoveryIdentifier:O}}),ue=Se.filter(i=>i.status==="undiscovered"||i.isSelectedByDefault),Rt=Se.filter(i=>!(i.status==="undiscovered"||i.isSelectedByDefault)).slice(0,2),Ye=ue.length>0,Nt=T.filter(i=>i.type===tt.Ledger).length,Lt=(Ye?[...ue,...Rt]:Se.filter(i=>!i.accounts.some(O=>!De(O.derivationPathType))).slice(0,3)).map((i,O)=>({...i,accountIndex:Nt+O}));x(Lt,Ye),c((0,f.jsx)(vt,{preventBack:!0}))}}},[ne,w,k,t.length,e,V,qe,B,T,x,c]);(0,v.useEffect)(()=>{ne&&Object.keys(ne).length===V.length&&(Ke(),t.length!==e&&(o(),d((0,f.jsx)(ye,{preventBack:!0}))))},[ne,V,c,d,e,t,Ke,o]);let q,K,Y,re,pe=n(()=>{},"onClick");return E?(q=(0,f.jsx)(N,{type:"failure"}),K=a("connectHardwareErrorLedgerGeneric"),Y=a("connectHardwareErrorLedgerPhantomLocked"),pe=n(async()=>{let p=await mt();p.id!==void 0&&ht(p.id)},"onClick"),re=a("commandClose")):ve&&ve.type!=="granted"?(q=(0,f.jsx)(N,{type:"warning"}),K=a("connectHardwarePermissionDeniedPrimary"),Y=a("connectHardwarePermissionDeniedSecondary"),re=a("homeErrorButtonText"),pe=Ve):Fe?(q=(0,f.jsx)(N,{type:"warning"}),K=a("connectHardwarePermissionUnableToConnect"),Y=a("connectHardwarePermissionUnableToConnectDescription"),re=a("commandConnect"),pe=Ve):Ue instanceof lt?(q=(0,f.jsx)(N,{type:"failure"}),K=a("connectHardwareErrorLedgerLocked"),Y=a("connectHardwareErrorLedgerLockedDescription"),re=a("homeErrorButtonText"),pe=je):Ue?(q=(0,f.jsx)(N,{type:"failure"}),K=a("connectHardwareErrorLedgerGeneric"),Y=a("connectHardwareErrorLedgerGenericDescription"),re=a("homeErrorButtonText"),pe=je):de.status=="reconnecting"?(q=(0,f.jsx)(N,{defaultIcon:(0,f.jsx)(he,{}),type:"default"}),K=a("connectHardwareConnecting"),Y=a("connectHardwareConnectingDescription")):D?(q=(0,f.jsx)(N,{defaultIcon:(0,f.jsx)(he,{}),type:"default"}),K=a("connectHardwareDiscoveringAccounts"),Y=a("connectHardwareDiscoveringAccountsDescription")):Bt?(q=(0,f.jsx)(N,{defaultIcon:(0,f.jsx)(he,{}),type:"default"}),K=a("connectHardwareConnectingAccounts"),Y=a("connectHardwareFindingAccountsWithActivity",{chainName:ie})):(q=(0,f.jsx)(oo,{children:be}),K=a("connectHardwareMobileOpenAppSingleChain",{chainName:te}),Y=a("connectHardwareOpenAppDescription")),(0,f.jsxs)(W,{children:[(0,f.jsx)(ee,{children:(0,f.jsx)(Q,{icon:q,primaryText:K,headerStyle:"large",secondaryText:Y})}),re?(0,f.jsx)(F,{onClick:pe,background:"spot",children:re}):(0,f.jsx)(to,{children:(0,f.jsx)(U,{color:R.colors.legacy.textDiminished,size:14,children:a("connectHardwareAccountsStepOfSteps",{stepNum:e,totalSteps:t.length})})})]})},"ConnectHardwareOpenApp"),to=s.div`
  align-self: center;
  background-color: ${R.colors.legacy.borderDiminished};
  border-radius: 80px;
  padding: 8px 16px;
  max-width: 150px;
`,oo=s.div`
  display: flex;
  align-items: center;

  & > *:not(:last-child) {
    margin-right: -12.5px;
  }
`;S();C();var ge=b(ce(),1);var G=b(M(),1),Ht=n(()=>{let{t:e}=H(),{pushSubStep:o,selectedChains:t,setSelectedChains:r,selectedChainsMap:c}=L(),d=Pe(),x=(0,ge.useMemo)(()=>d.filter(u=>le.get(u).isLedgerEnabled),[d]),w=Oe(),g=(0,ge.useCallback)(u=>{let A=new Map(c),T=$.getAddressTypes(u);for(let E of T){let D=c.get(E),y=D?.[u];A.set(E,{...D,[u]:!y})}let k=w.filter(E=>{let D=A.get(E)||{};return Object.values(D).reduce((B,te)=>te?++B:B,0)>0});r(k,A)},[w,r,c]),l=n(()=>{o((0,G.jsx)(ye,{preventBack:!0}))},"onPressContinue");gt(()=>{let u=new Map;for(let A of w)u.set(A,{});for(let A of x){let T=$.getAddressTypes(A);for(let k of T){let E=u.get(k);u.set(k,{...E,[A]:!1})}}r(t,u)},w.length>0&&x.length>0);let a=(0,ge.useMemo)(()=>x.map(u=>{let A=$.getAddressTypes(u),T=!1;for(let k of A)T=c.get(k)?.[u]||T;return(0,G.jsx)(no,{icon:(0,G.jsx)(me,{networkID:u,size:40}),networkID:u,onPressChain:g,isChecked:T},u)}),[x,c,g]),_=(0,ge.useMemo)(()=>{let u=0;for(let A of c.values())u+=Object.values(A).reduce((T,k)=>k?++T:T,0);return u===0},[c]);return(0,G.jsxs)(W,{children:[(0,G.jsx)(U,{weight:500,size:28,lineHeight:34,children:e("connectHardwareSelectChains")}),(0,G.jsx)(ao,{children:a}),(0,G.jsx)(F,{onClick:l,background:"spot",disabled:_,children:e("commandContinue")})]})},"ConnectHardwareSelectChains"),no=n(({networkID:e,icon:o,onPressChain:t,isChecked:r})=>(0,G.jsxs)(ro,{onClick:n(()=>{t(e)},"onClickCheckbox"),children:[(0,G.jsxs)(so,{children:[(0,G.jsx)(co,{children:o}),(0,G.jsx)(U,{size:16,weight:600,children:$.getNetworkName(e)})]}),(0,G.jsx)(we,{checked:r})]}),"SelectChainRow"),ro=s.div`
  align-items: center;
  background-color: ${R.colors.legacy.elementBase};
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  padding: 16px 24px 16px 12px;

  > span {
    margin-right: 0px;
  }
`,co=s.div`
  margin-right: 12px;
`,ao=s.div`
  margin-top: 20px;
`,so=s.div`
  display: flex;
  align-items: center;
`;var I=b(M(),1),io=n(()=>{let{t:e}=H(),{pushStep:o,setSelectedChains:t}=L(),r=Pe(),c=Oe(),{data:d,isFetching:x,refetch:w}=Re(!0,!0),{buttonDisabled:g,defaultIcon:l,primaryText:a,secondaryText:_,buttonText:u,iconType:A,onClick:T}=(0,kt.useMemo)(()=>{let k=!1,E=(0,I.jsx)(he,{}),D,y,B,te="default",ie=ct;if(x)D=e("connectHardwareSearching"),y=e("connectHardwareMakeSureConnected"),B=e("commandContinue"),k=!0;else if(d?.type==="granted"){let be=d.transport.deviceModel?.productName??"Ledger";te="success",D=e("connectHardwarePairSuccessPrimary",{productName:be}),y=e("connectHardwarePairSuccessSecondary",{productName:be}),B=e("commandContinue"),ie=n(()=>{if(c.length===1){let V=new Map;V.set(c[0],{});for(let xe of r){let Te=$.getAddressTypes(xe);for(let de of Te)V.set(de,{[xe]:!0})}t(c,V),o((0,I.jsx)(ye,{preventBack:!0}))}else o((0,I.jsx)(Ht,{onBackCallback:()=>{t([],new Map)}}))},"onClick")}else d?.type==="denied"?(te="failure",D=e("connectHardwarePermissionDeniedPrimary"),y=e("connectHardwarePermissionDeniedSecondary"),B=e("commandTryAgain"),ie=w):(!d||d.type==="unable-to-connect")&&(te="failure",D=e("connectHardwarePermissionUnableToConnect"),y=e("connectHardwareWaitingForApplicationSecondaryText"),B=e("commandTryAgain"),ie=w);return{buttonDisabled:k,defaultIcon:E,primaryText:D,secondaryText:y,buttonText:B,iconType:te,onClick:ie}},[r,c,d,o,w,x,t,e]);return(0,I.jsxs)(W,{children:[(0,I.jsx)(ee,{children:(0,I.jsx)(Q,{icon:(0,I.jsx)(N,{defaultIcon:l,type:A}),primaryText:a,headerStyle:"large",secondaryText:_})}),(0,I.jsx)(F,{onClick:T,background:"spot",disabled:g,children:u})]})},"ConnectHardwareSearchForWallet"),Wr=n(()=>{let{t:e}=H(),{pushSubStep:o}=L(),t=n(()=>o((0,I.jsx)(io,{})),"onPressConnect");return(0,I.jsxs)(W,{children:[(0,I.jsx)(ee,{children:(0,I.jsx)(Q,{icon:(0,I.jsx)(ft,{}),primaryText:e("connectHardwareLedger"),headerStyle:"large",secondaryText:e("connectHardwareStartConnection"),animateText:!0})}),(0,I.jsx)(F,{onClick:t,background:"spot",children:e("commandConnect")})]})},"ConnectHardware");export{L as a,wt as b,Io as c,Do as d,bt as e,on as f,Wr as g};
//# sourceMappingURL=chunk-BD3X2VAW.js.map
