import{h as P}from"./chunk-V53E4MU6.js";import{Za as m}from"./chunk-D3BHBSWL.js";import{c as i}from"./chunk-RLWRKBLA.js";import{W as y}from"./chunk-OY47TOHT.js";import{bc as T,e as H,f as x,sb as n,t as u}from"./chunk-ROW53IBC.js";import{a as p,g,i as S,n as f}from"./chunk-TSHWMJEM.js";S();f();var d=g(H(),1);var t=g(x(),1),b=i.div`
  padding-top: 16px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: ${e=>e.settingsContainerHeight??"100%"};
`,B=i.div``,A=i.div`
  border-radius: 6px;
  overflow: hidden;
  padding-bottom: 32px;
`,D=i.div`
  display: flex;
  background-color: ${e=>e.selected?n.colors.legacy.spotBase:n.colors.legacy.elementBase};
  padding: 16px;
  align-items: center;
  cursor: pointer;

  & + & {
    border-top: 1px solid ${n.colors.legacy.areaBase};
  }
`,U=i.div`
  display: flex;
  flex-direction: column;
  flex-grow: 1;
`,I=p(({selected:e,title:o,description:r,onClick:a})=>(0,t.jsx)(D,{onClick:a,selected:e,children:(0,t.jsxs)(U,{children:[(0,t.jsx)(m,{margin:"0 0 7px",lineHeight:16,textAlign:"left",weight:500,size:16,color:e?n.colors.legacy.areaBase:n.colors.legacy.textBase,children:o}),(0,t.jsx)(m,{textAlign:"left",weight:500,size:12,lineHeight:12,color:e?n.colors.legacy.elementBase:n.colors.legacy.textDiminished,children:r||(0,t.jsx)("span",{children:"\xA0"})})]})}),"Preset"),R=p(({onSelectTransactionSpeed:e,selectedTransactionSpeed:o,networkID:r,transactionUnitAmount:a,closeModal:c,settingsContainerHeight:s})=>{let{t:l}=u(),{presets:h,transactionSpeed:C}=y(r,o,a),k=(0,d.useCallback)(()=>{e(C),c()},[c,C,e]),v=l("settingsTransactions"),w=l("commandSave");return{headerText:v,primaryText:w,onPress:k,presetViewStates:h,settingsContainerHeight:s}},"useProps"),E=p(e=>{let o=R(e);return(0,t.jsx)(V,{...o})},"TransactionSettings"),V=d.default.memo(({headerText:e,primaryText:o,onPress:r,settingsContainerHeight:a,presetViewStates:c})=>(0,t.jsxs)(t.Fragment,{children:[(0,t.jsx)(B,{children:(0,t.jsx)(P,{children:e})}),(0,t.jsxs)(b,{settingsContainerHeight:a,children:[(0,t.jsx)(A,{children:c.map((s,l)=>(0,t.jsx)(I,{onClick:s.onClick,title:s.title,description:s.description,selected:s.selected},l))}),(0,t.jsx)(T,{background:"spot",onClick:r,children:o})]})]}));export{E as a};
//# sourceMappingURL=chunk-XSLI3QHK.js.map
