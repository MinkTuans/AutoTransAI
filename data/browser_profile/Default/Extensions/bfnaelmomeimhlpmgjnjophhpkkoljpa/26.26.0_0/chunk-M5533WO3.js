import{a as k}from"./chunk-63ST3ZAN.js";import{f as B}from"./chunk-EOII3ZM4.js";import{c as r}from"./chunk-RLWRKBLA.js";import{a as w,b as q}from"./chunk-KS7AKYDM.js";import{a as $}from"./chunk-CYENH7PC.js";import{Ua as y,e as I,sb as p,ya as v}from"./chunk-ROW53IBC.js";import{a as s,g as R,i as c,n as u}from"./chunk-TSHWMJEM.js";c();u();var o=R(I()),m=R($());var A={isConnected:!1,lastMessage:null,postMessage:y},L=o.default.createContext(A);function D(){let[e,i]=(0,o.useState)(null),[l,d]=(0,o.useState)(null),{isSidebarOpen:f}=k(),x=s(n=>{let t=q(n);!t||typeof t.url!="string"||!t.url||!t.req||typeof t.req.method!="string"||!t.req.method||d({...t,url:v(t.url.toString())})},"onMessage");(0,o.useEffect)(()=>{let n;return s(async()=>{if(f){let g=s(a=>{a.name==="popup/sidepanel"&&(i(a),a.onMessage.addListener(x),a.onDisconnect.addListener(()=>{i(null),d(null)}))},"onConnect");m.default.runtime.onConnect.addListener(g)}else{let a=`notification/${(await B()).id}`;n=m.default.runtime.connect({name:a}),i(n),n.onMessage.addListener(x),n.onDisconnect.addListener(()=>{self.close(),i(null),d(null)})}},"init")(),()=>{n?.disconnect()}},[f]);let M=(0,o.useCallback)(n=>{e&&e.postMessage(w(n))},[e]);return[!!e,l,M]}s(D,"useRemotePortConnection");function h(){let e=(0,o.useContext)(L);if(!e)throw new Error("Missing background connection context");return e}s(h,"useBackgroundConnection");function O(){let{lastMessage:e}=h();return e}s(O,"useIncomingBackgroundRequest");function F(){let e=O(),{postMessage:i}=h();return(0,o.useCallback)(l=>{if(e){if(e.req.id!==l.id)throw new Error(`Request id: ${e.req.id} does not match response id: ${l.id}`);i(l)}else throw new Error("No request received from the background yet")},[e,i])}s(F,"usePostOutgoingBackgroundResponse");c();u();c();u();var C=r.div`
  ${e=>!e.plain&&`
    box-shadow: ${e.theme?.footer?.boxShadow??"0px -6px 10px rgba(0, 0, 0, 0.1)"};
    background-color: ${p.colors.legacy.areaBase};
    border-top: ${`1px solid ${p.colors.legacy.elementBase}`};
  `}
`;var Y=r.div`
  flex: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;

  > * {
    margin-top: 27px;
  }
`,Z=r.div`
  flex: 1;
  overflow: auto;
  padding: 0px 16px;
`,ee=r.div`
  position: fixed;
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  left: 0;
  bottom: 0;
  background: ${p.colors.legacy.areaBase};
`,oe=r(C)`
  flex: none;
  padding: 14px 20px;
`,ne=r.div`
  padding: 20px;
  height: 100%;
`;export{C as a,L as b,D as c,O as d,F as e,Y as f,Z as g,ee as h,oe as i,ne as j};
//# sourceMappingURL=chunk-M5533WO3.js.map
