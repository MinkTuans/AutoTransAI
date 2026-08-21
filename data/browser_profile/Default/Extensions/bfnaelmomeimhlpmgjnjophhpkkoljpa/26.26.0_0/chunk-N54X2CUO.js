import{c as nt}from"./chunk-VRM2NWAU.js";import{b as tt,c as K}from"./chunk-RLWRKBLA.js";import{Oc as Wn,e as l,f as et,lc as _n,sb as Y}from"./chunk-ROW53IBC.js";import{a as o,g as c,i as E,n as R}from"./chunk-TSHWMJEM.js";E();R();E();R();E();R();var y=c(l(),1);E();R();var _=c(l(),1);E();R();var $=c(l(),1);E();R();var ot=c(l(),1),at=c(l(),1),oe=c(l(),1),ct=c(l(),1),Bn=c(l(),1),ye=c(l(),1),st=c(l(),1),lt=c(l(),1),ae=c(l(),1),ue=c(l(),1),Hn=c(l(),1),pt=c(l(),1),Ce=c(l(),1),mt=c(l(),1),ht=c(l(),1);function rt(){return!!(typeof self<"u"&&self.document&&self.document.createElement)}o(rt,"canUseDOM");function Fn(t){return!!(t&&{}.toString.call(t)=="[object Function]")}o(Fn,"isFunction");function Un(t,e){if(t!=null)if(Fn(t))t(e);else try{t.current=e}catch{throw new Error(`Cannot assign value "${e}" to ref "${t}"`)}}o(Un,"assignRef");function ut(...t){return(0,at.useCallback)(e=>{for(let n of t)Un(n,e)},t)}o(ut,"useComposedRefs");function it(t){return rt()?t?t.ownerDocument:document:null}o(it,"getOwnerDocument");function ft(){let[,t]=(0,ae.useState)(Object.create(null));return(0,ae.useCallback)(()=>{t(Object.create(null))},[])}o(ft,"useForceUpdate");var dt=rt()?ue.useLayoutEffect:ue.useEffect;var wt=c(_n(),1);var jn=o(({children:t,type:e="reach-portal",containerRef:n})=>{let r=$.useRef(null),a=$.useRef(null),i=ft();return $.useEffect(()=>{n!=null&&(typeof n!="object"||!("current"in n)?console.warn("@reach/portal: Invalid value passed to the `containerRef` of a `Portal`. The portal will be appended to the document body, but if you want to attach it to another DOM node you must pass a valid React ref object to `containerRef`."):n.current==null&&console.warn("@reach/portal: A ref was passed to the `containerRef` prop of a `Portal`, but no DOM node was attached to it. Be sure to pass the ref to a DOM component.\n\nIf you are forwarding the ref from another component, be sure to use the React.forwardRef API. See https://reactjs.org/docs/forwarding-refs.html."))},[n]),dt(()=>{if(!r.current)return;let u=r.current.ownerDocument,s=n?.current||u.body;return a.current=u?.createElement(e),s.appendChild(a.current),i(),()=>{a.current&&s&&s.removeChild(a.current)}},[e,i,n]),a.current?(0,wt.createPortal)(t,a.current):$.createElement("span",{ref:r})},"PortalImpl"),xe=o(({unstable_skipInitialRender:t,...e})=>{let[n,r]=$.useState(!1);return $.useEffect(()=>{t&&r(!0)},[t]),t&&!n?null:$.createElement(jn,{...e})},"Portal");xe.displayName="Portal";E();R();var A=c(l(),1);E();R();var Xn=["bottom","height","left","right","top","width"],Yn=o(function(e,n){return e===void 0&&(e={}),n===void 0&&(n={}),Xn.some(function(r){return e[r]!==n[r]})},"rectChanged"),H=new Map,gt,Kn=o(function t(){var e=[];H.forEach(function(n,r){var a=r.getBoundingClientRect();Yn(a,n.rect)&&(n.rect=a,e.push(n))}),e.forEach(function(n){n.callbacks.forEach(function(r){return r(n.rect)})}),gt=self.requestAnimationFrame(t)},"run");function zn(t,e){return{observe:o(function(){var r=H.size===0;H.has(t)?H.get(t).callbacks.push(e):H.set(t,{rect:void 0,hasRectChanged:!1,callbacks:[e]}),r&&Kn()},"observe"),unobserve:o(function(){var r=H.get(t);if(r){var a=r.callbacks.indexOf(e);a>=0&&r.callbacks.splice(a,1),r.callbacks.length||H.delete(t),H.size||cancelAnimationFrame(gt)}},"unobserve")}}o(zn,"observeRect");var bt=zn;E();R();var vt=c(l(),1),qn=c(l(),1),ie=c(l(),1),Et=c(l(),1),Qn=c(l(),1),De=c(l(),1),Rt=c(l(),1),yt=c(l(),1),Ct=c(l(),1),ce=c(l(),1),Gn=c(l(),1),xt=c(l(),1),ke=c(l(),1),St=c(l(),1),It=c(l(),1);function Vn(){return!!(typeof self<"u"&&self.document&&self.document.createElement)}o(Vn,"canUseDOM");function Se(t){return typeof t=="boolean"}o(Se,"isBoolean");function Ie(t){return!!(t&&{}.toString.call(t)=="[object Function]")}o(Ie,"isFunction");var se=Vn()?ce.useLayoutEffect:ce.useEffect;var Zn=o(({onChange:t,observe:e=!0,children:n})=>{let r=A.useRef(null),a=le(r,{observe:e,onChange:t});return n({ref:r,rect:a})},"Rect");Zn.displayName="Rect";function le(t,e,n){let r,a;Se(e)?r=e:(r=e?.observe??!0,a=e?.onChange),Ie(n)&&(a=n),A.useEffect(()=>{Se(e)&&console.warn("Passing `observe` as the second argument to `useRect` is deprecated and will be removed in a future version of Reach UI. Instead, you can pass an object of options with an `observe` property as the second argument (`useRect(ref, { observe })`).\nSee https://reach.tech/rect#userect-observe")},[e]),A.useEffect(()=>{Ie(n)&&console.warn("Passing `onChange` as the third argument to `useRect` is deprecated and will be removed in a future version of Reach UI. Instead, you can pass an object of options with an `onChange` property as the second argument (`useRect(ref, { onChange })`).\nSee https://reach.tech/rect#userect-onchange")},[n]);let[i,u]=A.useState(t.current),s=A.useRef(!1),w=A.useRef(!1),[b,p]=A.useState(null),m=A.useRef(a);return se(()=>{m.current=a,t.current!==i&&u(t.current)}),se(()=>{i&&!s.current&&(s.current=!0,p(i.getBoundingClientRect()))},[i]),se(()=>{if(!r)return;let v=i;if(w.current||(w.current=!0,v=t.current),!v){console.warn("You need to place the ref");return}let h=bt(v,C=>{m.current?.(C),p(C)});return h.observe(),()=>{h.unobserve()}},[r,i,t]),b}o(le,"useRect");E();R();var Jn=["input","select","textarea","a[href]","button","[tabindex]:not(slot)","audio[controls]","video[controls]",'[contenteditable]:not([contenteditable="false"])',"details>summary:first-of-type","details"],Te=Jn.join(","),Tt=typeof Element>"u",q=Tt?function(){}:Element.prototype.matches||Element.prototype.msMatchesSelector||Element.prototype.webkitMatchesSelector,Pe=!Tt&&Element.prototype.getRootNode?function(t){return t.getRootNode()}:function(t){return t.ownerDocument},er=o(function(e,n,r){var a=Array.prototype.slice.apply(e.querySelectorAll(Te));return n&&q.call(e,Te)&&a.unshift(e),a=a.filter(r),a},"getCandidates"),tr=o(function t(e,n,r){for(var a=[],i=Array.from(e);i.length;){var u=i.shift();if(u.tagName==="SLOT"){var s=u.assignedElements(),w=s.length?s:u.children,b=t(w,!0,r);r.flatten?a.push.apply(a,b):a.push({scope:u,candidates:b})}else{var p=q.call(u,Te);p&&r.filter(u)&&(n||!e.includes(u))&&a.push(u);var m=u.shadowRoot||typeof r.getShadowRoot=="function"&&r.getShadowRoot(u),v=!r.shadowRootFilter||r.shadowRootFilter(u);if(m&&v){var h=t(m===!0?u.children:m.children,!0,r);r.flatten?a.push.apply(a,h):a.push({scope:u,candidates:h})}else i.unshift.apply(i,u.children)}}return a},"getCandidatesIteratively"),Pt=o(function(e,n){return e.tabIndex<0&&(n||/^(AUDIO|VIDEO|DETAILS)$/.test(e.tagName)||e.isContentEditable)&&isNaN(parseInt(e.getAttribute("tabindex"),10))?0:e.tabIndex},"getTabindex"),nr=o(function(e,n){return e.tabIndex===n.tabIndex?e.documentOrder-n.documentOrder:e.tabIndex-n.tabIndex},"sortOrderedTabbables"),Lt=o(function(e){return e.tagName==="INPUT"},"isInput"),rr=o(function(e){return Lt(e)&&e.type==="hidden"},"isHiddenInput"),or=o(function(e){var n=e.tagName==="DETAILS"&&Array.prototype.slice.apply(e.children).some(function(r){return r.tagName==="SUMMARY"});return n},"isDetailsWithSummary"),ar=o(function(e,n){for(var r=0;r<e.length;r++)if(e[r].checked&&e[r].form===n)return e[r]},"getCheckedRadio"),ur=o(function(e){if(!e.name)return!0;var n=e.form||Pe(e),r=o(function(s){return n.querySelectorAll('input[type="radio"][name="'+s+'"]')},"queryRadios"),a;if(typeof self<"u"&&typeof self.CSS<"u"&&typeof self.CSS.escape=="function")a=r(self.CSS.escape(e.name));else try{a=r(e.name)}catch(u){return console.error("Looks like you have a radio button with a name attribute containing invalid CSS selector characters and need the CSS.escape polyfill: %s",u.message),!1}var i=ar(a,e.form);return!i||i===e},"isTabbableRadio"),ir=o(function(e){return Lt(e)&&e.type==="radio"},"isRadio"),cr=o(function(e){return ir(e)&&!ur(e)},"isNonTabbableRadio"),Dt=o(function(e){var n=e.getBoundingClientRect(),r=n.width,a=n.height;return r===0&&a===0},"isZeroArea"),sr=o(function(e,n){var r=n.displayCheck,a=n.getShadowRoot;if(getComputedStyle(e).visibility==="hidden")return!0;var i=q.call(e,"details>summary:first-of-type"),u=i?e.parentElement:e;if(q.call(u,"details:not([open]) *"))return!0;var s=Pe(e).host,w=s?.ownerDocument.contains(s)||e.ownerDocument.contains(e);if(!r||r==="full"){if(typeof a=="function"){for(var b=e;e;){var p=e.parentElement,m=Pe(e);if(p&&!p.shadowRoot&&a(p)===!0)return Dt(e);e.assignedSlot?e=e.assignedSlot:!p&&m!==e.ownerDocument?e=m.host:e=p}e=b}if(w)return!e.getClientRects().length}else if(r==="non-zero-area")return Dt(e);return!1},"isHidden"),lr=o(function(e){if(/^(INPUT|BUTTON|SELECT|TEXTAREA)$/.test(e.tagName))for(var n=e.parentElement;n;){if(n.tagName==="FIELDSET"&&n.disabled){for(var r=0;r<n.children.length;r++){var a=n.children.item(r);if(a.tagName==="LEGEND")return q.call(n,"fieldset[disabled] *")?!0:!a.contains(e)}return!0}n=n.parentElement}return!1},"isDisabledFromFieldset"),fr=o(function(e,n){return!(n.disabled||rr(n)||sr(n,e)||or(n)||lr(n))},"isNodeMatchingSelectorFocusable"),kt=o(function(e,n){return!(cr(n)||Pt(n)<0||!fr(e,n))},"isNodeMatchingSelectorTabbable"),dr=o(function(e){var n=parseInt(e.getAttribute("tabindex"),10);return!!(isNaN(n)||n>=0)},"isValidShadowRootTabbable"),pr=o(function t(e){var n=[],r=[];return e.forEach(function(a,i){var u=!!a.scope,s=u?a.scope:a,w=Pt(s,u),b=u?t(a.candidates):s;w===0?u?n.push.apply(n,b):n.push(s):r.push({documentOrder:i,tabIndex:w,item:a,isScope:u,content:b})}),r.sort(nr).reduce(function(a,i){return i.isScope?a.push.apply(a,i.content):a.push(i.content),a},[]).concat(n)},"sortByOrder"),W=o(function(e,n){n=n||{};var r;return n.getShadowRoot?r=tr([e],n.includeContainer,{filter:kt.bind(null,n),flatten:!1,getShadowRoot:n.getShadowRoot,shadowRootFilter:dr}):r=er(e,n.includeContainer,kt.bind(null,n)),pr(r)},"tabbable");var Q=_.forwardRef(o(function({unstable_skipInitialPortalRender:e,...n},r){return _.createElement(xe,{unstable_skipInitialRender:e},_.createElement(Mt,{ref:r,...n}))},"Popover2"));Q.displayName="Popover";var Mt=_.forwardRef(o(function({as:e="div",targetRef:n,position:r=wr,unstable_observableRefs:a=[],...i},u){let s=_.useRef(null),w=le(s,{observe:!i.hidden}),b=le(n,{observe:!0}),p=ut(s,u);return br(n,s),_.createElement(e,{"data-reach-popover":"",ref:p,...i,style:{position:"absolute",...mr(r,b,w,...a),...i.style}})},"PopoverImpl2"));Mt.displayName="PopoverImpl";function mr(t,e,n,...r){return n?t(e,n,...r.map(a=>a.current)):{visibility:"hidden"}}o(mr,"getStyles");function hr(t,e,n){return{top:n?`${t.top-e.height+self.pageYOffset}px`:`${t.top+t.height+self.pageYOffset}px`}}o(hr,"getTopPosition");var wr=o((t,e)=>{if(!t||!e)return{};let{directionRight:n,directionUp:r}=gr(t,e);return{left:n?`${t.right-e.width+self.pageXOffset}px`:`${t.left+self.pageXOffset}px`,...hr(t,e,r)}},"positionDefault");function gr(t,e,n=0,r=0){let a={top:t.top-e.height<0,right:self.innerWidth<t.left+e.width-n,bottom:self.innerHeight<t.bottom+e.height-r,left:t.left+t.width-e.width<0},i=a.right&&!a.left,u=a.left&&!a.right,s=a.bottom&&!a.top,w=a.top&&!a.bottom;return{directionRight:i,directionLeft:u,directionUp:s,directionDown:w}}o(gr,"getCollisions");function br(t,e){let n=it(t.current);function r(f){f.key==="Tab"&&e.current&&W(e.current).length===0||(f.key==="Tab"&&f.shiftKey?b(f)?p(f):m(f)?v(f):C(f)&&k():f.key==="Tab"&&(i()?u(f):s()?w(f):h(f)&&k()))}o(r,"handleKeyDown"),_.useEffect(()=>(n.addEventListener("keydown",r),()=>{n.removeEventListener("keydown",r)}),[]);function a(){let f=W(n),d=f&&t.current?f.indexOf(t.current):-1,T=f&&f[d+1];return e.current&&e.current.contains(T||null)?!1:T}o(a,"getElementAfterTrigger");function i(){return t.current?t.current===n.activeElement:!1}o(i,"tabbedFromTriggerToPopover");function u(f){let d=e.current&&W(e.current);d&&d[0]&&(f.preventDefault(),d[0].focus())}o(u,"focusFirstPopoverTabbable");function s(){if(e.current?e.current.contains(n.activeElement||null):!1){let d=e.current&&W(e.current);return!!(d&&d[d.length-1]===n.activeElement)}return!1}o(s,"tabbedOutOfPopover");function w(f){let d=a();d&&(f.preventDefault(),d.focus())}o(w,"focusTabbableAfterTrigger");function b(f){if(!f.shiftKey)return;let d=a();return f.target===d}o(b,"shiftTabbedFromElementAfterTrigger");function p(f){let d=e.current&&W(e.current),T=d&&d[d.length-1];T&&(f.preventDefault(),T.focus())}o(p,"focusLastTabbableInPopover");function m(f){let d=e.current&&W(e.current);return d?d.length===0?!1:f.target===d[0]:!1}o(m,"shiftTabbedOutOfPopover");function v(f){f.preventDefault(),t.current?.focus()}o(v,"focusTriggerRef");function h(f){let d=e.current?W(n).filter(T=>!e.current.contains(T)):null;return d?f.target===d[d.length-1]:!1}o(h,"tabbedToBrowserChrome");function C(f){return f.target===W(n)[0]}o(C,"shiftTabbedToBrowserChrome");let x=[];function k(){let f=e.current&&W(e.current);f&&(f.forEach(d=>{x.push([d,d.tabIndex]),d.tabIndex=-1}),n.addEventListener("focusin",S))}o(k,"disableTabbablesInPopover");function S(){n.removeEventListener("focusin",S),x.forEach(([f,d])=>{f.tabIndex=d})}o(S,"enableTabbablesInPopover")}o(br,"useSimulateTabNavigationForReactTree");E();R();var g=c(l(),1);E();R();var z=c(l(),1);E();R();var Ot=c(l(),1),$t=c(l(),1),j=c(l(),1),Wt=c(l(),1),Er=c(l(),1),Ne=c(l(),1),Ft=c(l(),1),Ut=c(l(),1),fe=c(l(),1),de=c(l(),1),Rr=c(l(),1),me=c(l(),1),Oe=c(l(),1),we=c(l(),1),jt=c(l(),1);function Nt(){return!!(typeof self<"u"&&self.document&&self.document.createElement)}o(Nt,"canUseDOM");function M(t,e){return n=>{if(t&&t(n),!n.defaultPrevented)return e(n)}}o(M,"composeEventHandlers");function Le(t){return!!(t&&{}.toString.call(t)=="[object Function]")}o(Le,"isFunction");function At(t){return typeof t=="string"}o(At,"isString");function vr(t,e){if(t!=null)if(Le(t))t(e);else try{t.current=e}catch{throw new Error(`Cannot assign value "${e}" to ref "${t}"`)}}o(vr,"assignRef");function G(...t){return(0,$t.useCallback)(e=>{for(let n of t)vr(n,e)},t)}o(G,"useComposedRefs");function Z(t){return Nt()?t?t.ownerDocument:document:null}o(Z,"getOwnerDocument");function _t(t,e){let n=j.createContext(e);function r(i){let{children:u,...s}=i,w=j.useMemo(()=>s,Object.values(s));return j.createElement(n.Provider,{value:w},u)}o(r,"Provider");function a(i){let u=j.useContext(n);if(u)return u;if(e)return e;throw Error(`${i} must be rendered inside of a ${t} component.`)}return o(a,"useContext2"),n.displayName=`${t}Context`,r.displayName=`${t}Provider`,[r,a]}o(_t,"createContext2");function J(t){return"which"in t?t.which===3:"button"in t?t.button===2:!1}o(J,"isRightClick");function ee(...t){return t.filter(e=>e!=null).join("--")}o(ee,"makeId");function Me(){}o(Me,"noop");function Bt(){let[,t]=(0,fe.useState)(Object.create(null));return(0,fe.useCallback)(()=>{t(Object.create(null))},[])}o(Bt,"useForceUpdate");var pe=Nt()?de.useLayoutEffect:de.useEffect;function he(t){let e=(0,me.useRef)(null);return(0,me.useEffect)(()=>{e.current=t},[t]),e.current}o(he,"usePrevious");function Ht(t,e){let[n,r]=(0,we.useState)(e),a=(0,we.useCallback)(i=>{t.current=i,r(i)},[]);return[n,a]}o(Ht,"useStatefulRefValue");var $e=!1,yr=0;function Xt(){return++yr}o(Xt,"genId");var Yt=z.useId;function Kt(t){if(Yt!==void 0){let a=Yt();return t??a}let e=t??($e?Xt():null),[n,r]=z.useState(e);return pe(()=>{n===null&&r(Xt())},[]),z.useEffect(()=>{$e===!1&&($e=!0)},[]),t??n??void 0}o(Kt,"useId");E();R();var N=c(l(),1);function Vt(t,e={}){let r=N.createContext({descendants:[],registerDescendant:o(()=>Me,"registerDescendant"),...e});return r.displayName=t,r}o(Vt,"createDescendantContext");function qt(t,e,n){let r=Bt(),{registerDescendant:a,descendants:i}=N.useContext(e),u=n??i.findIndex(s=>s.element===t.element);return pe(()=>(t.element||r(),a({...t,index:u})),[t,r,u,a,...Object.values(t)]),u}o(qt,"useDescendant");function Qt(){return N.useState([])}o(Qt,"useDescendantsInit");function Gt(t){return N.useContext(t).descendants}o(Gt,"useDescendants");function Zt({context:t,children:e,items:n,set:r}){let a=N.useCallback(({element:i,index:u,...s})=>i?(r(w=>{if(u!=null&&u!==-1)return zt(w,{element:i,index:u,...s},u);if(w.length===0)return[{...s,element:i,index:0}];if(w.find(m=>m.element===i))return console.warn(`[reach-ui]: \`useDescendant\` was called with an element that was already registered.

If you are using the \`@reach/descendants\` package directly, make sure to only register descendants once. Registering a descendant more than once will lead to bugs in your app.

If you are using another \`reach-ui\` package, this is probably our bug!

To report a bug, open a new issue:

  https://github.com/reach/reach-ui/issues/new?assignees=&labels=&template=Bug_report.md

IMPORTANT: this check will only run in the development build, so if you see this warning please be aware that your app may crash when deployed.`),xr(w);let b=Cr(w,i),p;return b===-1?p=[...w,{...s,element:i,index:w.length}]:p=zt(w,{...s,element:i,index:b},b),p}),()=>{i&&r(w=>w.filter(b=>i!==b.element))}):Me,[]);return N.createElement(t.Provider,{value:N.useMemo(()=>({descendants:n,registerDescendant:a}),[n,a])},e)}o(Zt,"DescendantProvider");function Jt(t,e){let{descendants:n}=N.useContext(t),{callback:r,currentIndex:a,filter:i,key:u="index",orientation:s="vertical",rotate:w=!0,rtl:b=!1}=e;return o(function(m){if(!["ArrowDown","ArrowUp","ArrowLeft","ArrowRight","PageUp","PageDown","Home","End"].includes(m.key))return;let v=a??-1,h=i?n.filter(i):n;if(!h.length)return;let C=h.findIndex(d=>d.index===a);function x(){return v===f().index?w?S():h[C]:h[(C+1)%h.length]}o(x,"getNextOption");function k(){return v===S().index?w?f():h[C]:h[(C-1+h.length)%h.length]}o(k,"getPreviousOption");function S(){return h[0]}o(S,"getFirstOption");function f(){return h[h.length-1]}switch(o(f,"getLastOption"),m.key){case"ArrowDown":if(s==="vertical"||s==="both"){m.preventDefault();let D=x();r(u==="option"?D:D[u])}break;case"ArrowUp":if(s==="vertical"||s==="both"){m.preventDefault();let D=k();r(u==="option"?D:D[u])}break;case"ArrowLeft":if(s==="horizontal"||s==="both"){m.preventDefault();let D=(b?x:k)();r(u==="option"?D:D[u])}break;case"ArrowRight":if(s==="horizontal"||s==="both"){m.preventDefault();let D=(b?k:x)();r(u==="option"?D:D[u])}break;case"PageUp":m.preventDefault();let d=(m.ctrlKey?k:S)();r(u==="option"?d:d[u]);break;case"Home":m.preventDefault();let T=S();r(u==="option"?T:T[u]);break;case"PageDown":m.preventDefault();let F=(m.ctrlKey?x:f)();r(u==="option"?F:F[u]);break;case"End":m.preventDefault();let O=f();r(u==="option"?O:O[u]);break}},"handleKeyDown")}o(Jt,"useDescendantKeyDown");function en(t,e){return!!(e.compareDocumentPosition(t)&Node.DOCUMENT_POSITION_PRECEDING)}o(en,"isElementPreceding");function Cr(t,e){if(!e||!t.length)return-1;let n=t.length;for(;n--;){let r=t[n].element;if(r&&en(r,e))return n+1}return-1}o(Cr,"findDOMIndex");function zt(t,e,n){return n==null||!(n in t)?[...t,e]:[...t.slice(0,n),e,...t.slice(n)]}o(zt,"insertAt");function xr(t){return t.sort((e,n)=>!e.element||!n.element?0:en(e.element,n.element)?-1:1).map((e,n)=>({...e,index:n}))}o(xr,"updateIndices");var tn="CLEAR_SELECTION_INDEX",Fe="CLICK_MENU_ITEM",te="CLOSE_MENU",Sr="OPEN_MENU_AT_FIRST_ITEM",Ae="OPEN_MENU_AT_INDEX",nn="OPEN_MENU_CLEARED",_e="SEARCH_FOR_ITEM",X="SELECT_ITEM_AT_INDEX",We="SET_BUTTON_ID",be=Vt("DropdownDescendantContext"),[Ir,V]=_t("Dropdown"),Dr={triggerId:null,isExpanded:!1,typeaheadQuery:"",selectionIndex:-1},Ue=o(({id:t,children:e})=>{let n=g.useRef(null),r=g.useRef(null),a=g.useRef(null),[i,u]=Qt(),s=Kt(t),w=t||ee("menu",s),b=ee("menu-button",w),[p,m]=g.useReducer(Or,{...Dr,triggerId:b}),v=g.useRef(!1),h=g.useRef([]),C=g.useRef(!1),x=g.useRef({x:0,y:0});return g.useEffect(()=>{p.isExpanded?(self.__REACH_DISABLE_TOOLTIPS=!0,self.requestAnimationFrame(()=>{ge(r.current)})):self.__REACH_DISABLE_TOOLTIPS=!1},[p.isExpanded]),g.createElement(Zt,{context:be,items:i,set:u},g.createElement(Ir,{dispatch:m,dropdownId:w,dropdownRef:r,mouseDownStartPosRef:x,popoverRef:a,readyToSelect:C,selectCallbacks:h,state:p,triggerClickedRef:v,triggerRef:n},Le(e)?e({isExpanded:p.isExpanded,isOpen:p.isExpanded}):e))},"DropdownProvider_");Ue.displayName="DropdownProvider";function Be({onKeyDown:t,onMouseDown:e,id:n,ref:r,...a}){let{dispatch:i,dropdownId:u,mouseDownStartPosRef:s,triggerClickedRef:w,triggerRef:b,state:{triggerId:p,isExpanded:m}}=V("useDropdownTrigger"),v=G(b,r),h=on(),C=g.useMemo(()=>h.findIndex(S=>!S.disabled),[h]);g.useEffect(()=>{n!=null&&n!==p&&i({type:We,payload:n})},[p,i,n]),g.useEffect(()=>{n==null&&i({type:We,payload:ee("menu-button",u)})},[u,i,n]);function x(S){switch(S.key){case"ArrowDown":case"ArrowUp":S.preventDefault(),i({type:Ae,payload:{index:C}});break;case"Enter":case" ":i({type:Ae,payload:{index:C}});break;default:break}}o(x,"handleKeyDown");function k(S){J(S.nativeEvent)||(s.current={x:S.clientX,y:S.clientY},m||(w.current=!0),i(m?{type:te}:{type:nn}))}return o(k,"handleMouseDown"),{data:{isExpanded:m,controls:u},props:{...a,ref:v,id:p||void 0,onKeyDown:M(t,x),onMouseDown:M(e,k),type:"button"}}}o(Be,"useDropdownTrigger");var kr=g.forwardRef(({as:t="button",...e},n)=>{let{props:r}=Be({...e,ref:n});return g.createElement(t,{"data-reach-dropdown-trigger":"",...r})});kr.displayName="DropdownTrigger";function He({index:t,isLink:e=!1,onClick:n,onDragStart:r,onMouseDown:a,onMouseEnter:i,onMouseLeave:u,onMouseMove:s,onMouseUp:w,onSelect:b,disabled:p,onFocus:m,valueText:v,ref:h,...C}){let{dispatch:x,dropdownRef:k,mouseDownStartPosRef:S,readyToSelect:f,selectCallbacks:d,triggerRef:T,state:{selectionIndex:F,isExpanded:O}}=V("useDropdownItem"),D=g.useRef(null),[Re,yn]=g.useState(v||""),Cn=g.useCallback(I=>{!v&&I?.textContent&&yn(I.textContent)},[v]),ne=g.useRef(!1),[Ze,xn]=Ht(D,null),Sn=g.useMemo(()=>({element:Ze,key:Re,disabled:p,isLink:e}),[p,Ze,e,Re]),U=qt(Sn,be,t),re=U===F&&!p,In=G(h,xn,Cn);d.current[U]=b;function Je(){ge(T.current),b&&b(),x({type:Fe})}o(Je,"select");function Dn(I){J(I.nativeEvent)||e&&(p?I.preventDefault():Je())}o(Dn,"handleClick");function kn(I){e&&I.preventDefault()}o(kn,"handleDragStart");function Tn(I){J(I.nativeEvent)||(e?ne.current=!0:I.preventDefault())}o(Tn,"handleMouseDown");function Pn(I){let B=Z(k.current);!re&&U!=null&&!p&&(k?.current&&k.current!==B.activeElement&&D.current!==B.activeElement&&k.current.focus(),x({type:X,payload:{index:U}}))}o(Pn,"handleMouseEnter");function Ln(I){x({type:tn})}o(Ln,"handleMouseLeave");function Mn(I){if(!f.current){let B=8,$n=Math.abs(I.clientX-S.current.x),An=Math.abs(I.clientY-S.current.y);($n>B||An>B)&&(f.current=!0)}!re&&U!=null&&!p&&x({type:X,payload:{index:U,dropdownRef:k}})}o(Mn,"handleMouseMove");function Nn(){f.current=!0,!re&&U!=null&&!p&&x({type:X,payload:{index:U}})}o(Nn,"handleFocus");function On(I){if(!J(I.nativeEvent)){if(!f.current){f.current=!0;return}e?ne.current?ne.current=!1:D.current&&D.current.click():p||Je()}}return o(On,"handleMouseUp"),g.useEffect(()=>{if(O){let I=self.setTimeout(()=>{f.current=!0},400);return()=>{self.clearTimeout(I)}}else f.current=!1},[O,f]),g.useEffect(()=>{let I=Z(D.current);return I.addEventListener("mouseup",B),()=>{I.removeEventListener("mouseup",B)};function B(){ne.current=!1}o(B,"listener")},[]),{data:{disabled:p},props:{id:rn(U),tabIndex:-1,...C,ref:In,"data-disabled":p?"":void 0,"data-selected":re?"":void 0,"data-valuetext":Re,onClick:M(n,Dn),onDragStart:M(r,kn),onMouseDown:M(a,Tn),onMouseEnter:M(i,Pn),onMouseLeave:M(u,Ln),onMouseMove:M(s,Mn),onFocus:M(m,Nn),onMouseUp:M(w,On)}}}o(He,"useDropdownItem");var Tr=g.forwardRef(({as:t="div",...e},n)=>{let{props:r}=He({...e,ref:n});return g.createElement(t,{"data-reach-dropdown-item":"",...r})});Tr.displayName="DropdownItem";function je({id:t,onKeyDown:e,ref:n,...r}){let{dispatch:a,triggerRef:i,dropdownRef:u,selectCallbacks:s,dropdownId:w,state:{isExpanded:b,triggerId:p,selectionIndex:m,typeaheadQuery:v}}=V("useDropdownItems"),h=on(),C=G(u,n);g.useEffect(()=>{let d=Mr(h,v);v&&d!=null&&a({type:X,payload:{index:d,dropdownRef:u}});let T=self.setTimeout(()=>v&&a({type:_e,payload:""}),1e3);return()=>self.clearTimeout(T)},[a,h,v,u]);let x=he(h.length),k=he(h[m]),S=he(m);g.useEffect(()=>{m>h.length-1?a({type:X,payload:{index:h.length-1,dropdownRef:u}}):x!==h.length&&m>-1&&k&&S===m&&h[m]!==k&&a({type:X,payload:{index:h.findIndex(d=>d.key===k?.key),dropdownRef:u}})},[u,a,h,x,k,S,m]);let f=M(o(function(T){let{key:F}=T;if(b)switch(F){case"Enter":case" ":let O=h.find(D=>D.index===m);O&&!O.disabled&&(T.preventDefault(),O.isLink&&O.element?O.element.click():(ge(i.current),s.current[O.index]&&s.current[O.index](),a({type:Fe})));break;case"Escape":ge(i.current),a({type:te});break;case"Tab":T.preventDefault();break;default:if(At(F)&&F.length===1){let D=v+F.toLowerCase();a({type:_e,payload:D})}break}},"handleKeyDown2"),Jt(be,{currentIndex:m,orientation:"vertical",rotate:!1,filter:o(d=>!d.disabled,"filter"),callback:o(d=>{a({type:X,payload:{index:d,dropdownRef:u}})},"callback"),key:"index"}));return{data:{activeDescendant:rn(m)||void 0,triggerId:p},props:{tabIndex:-1,...r,ref:C,id:w,onKeyDown:M(e,f)}}}o(je,"useDropdownItems");var Pr=g.forwardRef(({as:t="div",...e},n)=>{let{props:r}=je({...e,ref:n});return g.createElement(t,{"data-reach-dropdown-items":"",...r})});Pr.displayName="DropdownItems";function Xe({onBlur:t,portal:e=!0,position:n,ref:r,...a}){let{triggerRef:i,triggerClickedRef:u,dispatch:s,dropdownRef:w,popoverRef:b,state:{isExpanded:p}}=V("useDropdownPopover"),m=G(b,r);return g.useEffect(()=>{if(!p)return;let v=Z(b.current);function h(C){u.current?u.current=!1:Nr(b.current,C.target)||s({type:te})}return o(h,"listener"),v.addEventListener("mousedown",h),()=>{v.removeEventListener("mousedown",h)}},[u,i,s,w,b,p]),{data:{portal:e,position:n,targetRef:i,isExpanded:p},props:{ref:m,hidden:!p,onBlur:M(t,v=>{v.currentTarget.contains(v.relatedTarget)||s({type:te})}),...a}}}o(Xe,"useDropdownPopover");var Lr=g.forwardRef(({as:t="div",...e},n)=>{let{data:{portal:r,targetRef:a,position:i},props:u}=Xe({...e,ref:n}),s={"data-reach-dropdown-popover":""};return r?g.createElement(Q,{...u,...s,as:t,targetRef:a,position:i,unstable_skipInitialPortalRender:!0}):g.createElement(t,{...u,...s})});Lr.displayName="DropdownPopover";function Mr(t,e=""){if(!e)return null;let n=t.find(r=>r.disabled?!1:r.element?.dataset?.valuetext?.toLowerCase().startsWith(e));return n?t.indexOf(n):null}o(Mr,"findItemFromTypeahead");function rn(t){let{dropdownId:e}=V("useItemId");return t!=null&&t>-1?ee(`option-${t}`,e):void 0}o(rn,"useItemId");function ge(t){t&&t.focus()}o(ge,"focus");function Nr(t,e){return!!(t&&t.contains(e))}o(Nr,"popoverContainsEventTarget");function Or(t,e={}){switch(e.type){case Fe:return{...t,isExpanded:!1,selectionIndex:-1};case te:return{...t,isExpanded:!1,selectionIndex:-1};case Sr:return{...t,isExpanded:!0,selectionIndex:0};case Ae:return{...t,isExpanded:!0,selectionIndex:e.payload.index};case nn:return{...t,isExpanded:!0,selectionIndex:-1};case X:{let{dropdownRef:n={current:null}}=e.payload;if(e.payload.index>=0&&e.payload.index!==t.selectionIndex){if(n.current){let r=Z(n.current);n.current!==r?.activeElement&&n.current.focus()}return{...t,selectionIndex:e.payload.max!=null?Math.min(Math.max(e.payload.index,0),e.payload.max):Math.max(e.payload.index,0)}}return t}case tn:return{...t,selectionIndex:-1};case We:return{...t,triggerId:e.payload};case _e:return typeof e.payload<"u"?{...t,typeaheadQuery:e.payload}:t;default:return t}}o(Or,"reducer");function on(){return Gt(be)}o(on,"useDropdownDescendants");E();R();var an=c(l(),1),Ar=c(l(),1),ve=c(l(),1),un=c(l(),1),_r=c(l(),1),Ye=c(l(),1),sn=c(l(),1),ln=c(l(),1),fn=c(l(),1),Ee=c(l(),1),Wr=c(l(),1),dn=c(l(),1),Ke=c(l(),1),pn=c(l(),1),mn=c(l(),1);function $r(){return!!(typeof self<"u"&&self.document&&self.document.createElement)}o($r,"canUseDOM");function cn(){}o(cn,"noop");var qo=$r()?Ee.useLayoutEffect:Ee.useEffect;var hn=c(Wn(),1);var ze=y.forwardRef(({as:t=y.Fragment,id:e,children:n,...r},a)=>{let u=y.useMemo(()=>{try{return(0,hn.isFragment)(y.createElement(t,null))}catch{return!1}},[t])?{}:{ref:a,id:e,"data-reach-menu":"",...r};return y.createElement(t,{...u},y.createElement(Ue,{id:e,children:n}))});ze.displayName="Menu";var Ve=y.forwardRef(({as:t="button",...e},n)=>{let{data:{isExpanded:r,controls:a},props:i}=Be({...e,ref:n});return y.createElement(t,{"aria-expanded":r?!0:void 0,"aria-haspopup":!0,"aria-controls":a,...i,"data-reach-menu-button":""})});Ve.displayName="MenuButton";var qe=y.forwardRef(({as:t="div",...e},n)=>{let{data:{disabled:r},props:a}=He({...e,ref:n});return y.createElement(t,{role:"menuitem",...a,"aria-disabled":r||void 0,"data-reach-menu-item":""})});qe.displayName="MenuItemImpl";var Qe=y.forwardRef(({as:t="div",...e},n)=>y.createElement(qe,{...e,ref:n,as:t}));Qe.displayName="MenuItem";var wn=y.forwardRef(({as:t="div",...e},n)=>{let{data:{activeDescendant:r,triggerId:a},props:i}=je({...e,ref:n});return y.createElement(t,{"aria-activedescendant":r,"aria-labelledby":a||void 0,role:"menu",...i,"data-reach-menu-items":""})});wn.displayName="MenuItems";var Fr=y.forwardRef(({as:t="a",component:e,onSelect:n,...r},a)=>(y.useEffect(()=>{e&&console.warn("[@reach/menu-button]: Please use the `as` prop instead of `component`")},[e]),y.createElement(qe,{...r,ref:a,"data-reach-menu-link":"",as:t,isLink:!0,onSelect:n||cn})));Fr.displayName="MenuLink";var Ge=y.forwardRef(({portal:t=!0,...e},n)=>y.createElement(gn,{portal:t},y.createElement(wn,{...e,ref:n,"data-reach-menu-list":""})));Ge.displayName="MenuList";var gn=y.forwardRef(({as:t="div",...e},n)=>{let{data:{portal:r,targetRef:a,position:i},props:u}=Xe({...e,ref:n}),s={"data-reach-menu-popover":""};return r?y.createElement(Q,{...u,...s,as:t,targetRef:a,position:i,unstable_skipInitialPortalRender:!0}):y.createElement(t,{...u,...s})});gn.displayName="MenuPopover";var En=c(l(),1);var P=c(et(),1),bn=K(Ge)`
  box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
  background: ${Y.colors.legacy.areaAccent};
  border-radius: 6px;
  padding: 10px 17px;
  margin-top: 4px;
  width: ${t=>t.width};

  /* this is needed for the dropdown to correctly overlay on our settings popups */
  z-index: 999;
  position: relative;
`,vn=K.div`
  overflow: scroll;
  max-height: ${t=>t.maxHeight};
`,Rn=K(Qe)`
  font-size: 16px;
  padding: 7px 0px;
  display: flex;
  color: ${t=>t.variant==="warning"?Y.colors.legacy.spotNegative:Y.colors.legacy.textBase};
  justify-content: space-between;
  ${t=>{let e=t.variant==="warning"?Y.colors.legacy.spotNegative:Y.colors.legacy.spotBase;return tt`
      &[data-selected] {
        background: inherit;
        color: ${e};
        p {
          color: ${e};
        }
      }
    `}}
`,Ur=K(Rn)`
  padding: 0;
`,Br=K.div`
  width: 100%;
  margin: 6px 0px;
  border-bottom: 1px solid ${Y.colors.legacy.borderDiminished};
`,ga=o(({icon:t,items:e,sections:n,onIconClick:r,className:a,children:i,dropdownWidth:u="250px",noDropdownItemPadding:s=!1,disableIconBackground:w=!1})=>{let b="330px",p=(0,En.useMemo)(()=>s?Ur:Rn,[s]);return(0,P.jsx)(ze,{children:({isExpanded:m})=>(0,P.jsxs)(P.Fragment,{children:[(0,P.jsx)(Ve,{as:"span",className:a,onClick:r,children:t?w?t:(0,P.jsx)(nt,{isActive:e&&m,children:t}):i}),n?(0,P.jsx)(bn,{width:u,children:(0,P.jsx)(vn,{maxHeight:b,children:n.map((v,h)=>v.data.length?(0,P.jsxs)("div",{children:[v.data.map((C,x)=>(0,P.jsx)(p,{"data-testid":`dropdown-section-${h}-item-${x}`,onSelect:C.onClick,variant:C.variant,children:C.label},C.key)),h!==n.length-1?(0,P.jsx)(Br,{}):null]},v.key):null)})}):null,e?(0,P.jsx)(bn,{width:u,children:(0,P.jsx)(vn,{maxHeight:b,children:e.map((v,h)=>(0,P.jsx)(p,{"data-testid":`dropdown-item-${h}`,onSelect:v.onClick,variant:v.variant,children:v.label},v.key))})}):null]})})},"Dropdown");export{bt as a,ga as b};
/*! Bundled license information:

@reach/utils/dist/reach-utils.mjs:
  (**
    * @reach/utils v0.18.0
    *
    * Copyright (c) 2018-2022, React Training LLC
    *
    * This source code is licensed under the MIT license found in the
    * LICENSE.md file in the root directory of this source tree.
    *
    * @license MIT
    *)

@reach/portal/dist/reach-portal.mjs:
  (**
    * @reach/portal v0.18.0
    *
    * Copyright (c) 2018-2022, React Training LLC
    *
    * This source code is licensed under the MIT license found in the
    * LICENSE.md file in the root directory of this source tree.
    *
    * @license MIT
    *)

@reach/utils/dist/reach-utils.mjs:
  (**
    * @reach/utils v0.18.0
    *
    * Copyright (c) 2018-2022, React Training LLC
    *
    * This source code is licensed under the MIT license found in the
    * LICENSE.md file in the root directory of this source tree.
    *
    * @license MIT
    *)

@reach/rect/dist/reach-rect.mjs:
  (**
    * @reach/rect v0.18.0
    *
    * Copyright (c) 2018-2022, React Training LLC
    *
    * This source code is licensed under the MIT license found in the
    * LICENSE.md file in the root directory of this source tree.
    *
    * @license MIT
    *)

tabbable/dist/index.esm.js:
  (*!
  * tabbable 5.3.3
  * @license MIT, https://github.com/focus-trap/tabbable/blob/master/LICENSE
  *)

@reach/popover/dist/reach-popover.mjs:
  (**
    * @reach/popover v0.18.0
    *
    * Copyright (c) 2018-2022, React Training LLC
    *
    * This source code is licensed under the MIT license found in the
    * LICENSE.md file in the root directory of this source tree.
    *
    * @license MIT
    *)

@reach/utils/dist/reach-utils.mjs:
  (**
    * @reach/utils v0.18.0
    *
    * Copyright (c) 2018-2022, React Training LLC
    *
    * This source code is licensed under the MIT license found in the
    * LICENSE.md file in the root directory of this source tree.
    *
    * @license MIT
    *)

@reach/auto-id/dist/reach-auto-id.mjs:
  (**
    * @reach/auto-id v0.18.0
    *
    * Copyright (c) 2018-2022, React Training LLC
    *
    * This source code is licensed under the MIT license found in the
    * LICENSE.md file in the root directory of this source tree.
    *
    * @license MIT
    *)

@reach/descendants/dist/reach-descendants.mjs:
  (**
    * @reach/descendants v0.18.0
    *
    * Copyright (c) 2018-2022, React Training LLC
    *
    * This source code is licensed under the MIT license found in the
    * LICENSE.md file in the root directory of this source tree.
    *
    * @license MIT
    *)

@reach/dropdown/dist/reach-dropdown.mjs:
  (**
    * @reach/dropdown v0.18.0
    *
    * Copyright (c) 2018-2022, React Training LLC
    *
    * This source code is licensed under the MIT license found in the
    * LICENSE.md file in the root directory of this source tree.
    *
    * @license MIT
    *)

@reach/utils/dist/reach-utils.mjs:
  (**
    * @reach/utils v0.18.0
    *
    * Copyright (c) 2018-2022, React Training LLC
    *
    * This source code is licensed under the MIT license found in the
    * LICENSE.md file in the root directory of this source tree.
    *
    * @license MIT
    *)

@reach/menu-button/dist/reach-menu-button.mjs:
  (**
    * @reach/menu-button v0.18.0
    *
    * Copyright (c) 2018-2022, React Training LLC
    *
    * This source code is licensed under the MIT license found in the
    * LICENSE.md file in the root directory of this source tree.
    *
    * @license MIT
    *)
*/
//# sourceMappingURL=chunk-N54X2CUO.js.map
