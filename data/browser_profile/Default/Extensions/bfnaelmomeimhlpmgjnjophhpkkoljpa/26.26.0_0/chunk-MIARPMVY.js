import{c as d}from"./chunk-RLWRKBLA.js";import{e as B,f as r,sb as t,t as c}from"./chunk-ROW53IBC.js";import{g as l,i as g,n as a}from"./chunk-TSHWMJEM.js";g();a();var n=l(B(),1);var o=l(r(),1),S=d.div`
  position: relative;
  width: ${e=>`${e.width}px`};
  height: ${e=>`${e.height}px`};
  opacity: ${e=>e.disabled?e.disabledToggleOpacity:1};

  input[type="checkbox"] {
    width: ${e=>`${e.width}px`};
    height: ${e=>`${e.height}px`};
    margin: 0;
    &:hover {
      cursor: pointer;
    }
  }

  label {
    width: ${e=>`${e.width}px`};
    height: ${e=>`${e.height}px`};
    background: ${e=>e.disabled?e.disabledBackgroundColor:e.inactiveBackgroundColor};
    border-radius: ${e=>`${(e.height||0)/2}px`};
    cursor: pointer;
    text-indent: -9999px;
    display: block;
    position: absolute;
    top: 0;
    left: 0;
    pointer-events: none;
  }

  label:after {
    content: "";
    position: absolute;
    top: ${e=>`${((e.height||0)-(e.toggleHeight||0))/2}px`};
    left: ${e=>`${((e.width||0)-(e.toggleWidth||0)*2)/2}px`};
    width: ${e=>`${e.toggleWidth}px`};
    height: ${e=>`${e.toggleHeight}px`};
    background: ${e=>e.inactiveToggleColor};
    border-radius: 100px;
    transition: 0.3s;
  }

  input:checked + label {
    background: ${e=>e.disabled?e.disabledBackgroundColor:e.activeBackgroundColor};
    &:after {
      background: ${e=>e.disabled?e.disabledToggleColor:e.activeToggleColor};
    }
  }

  input:checked + label:after {
    left: calc(100% - ${e=>`${((e.width||0)-(e.toggleWidth||0)*2)/2}px`});
    transform: translateX(-100%);
  }

  label:active:after {
    width: 14px;
    background: ${t.colors.legacy.textBase};
  }
`,R=n.default.memo(({id:e,width:h=34,height:s=20,toggleWidth:b=14,toggleHeight:u=14,activeBackgroundColor:p=t.colors.legacy.spotBase,activeToggleColor:$=t.colors.legacy.textBase,inactiveBackgroundColor:k=t.colors.legacy.areaAccent,inactiveToggleColor:x=t.colors.legacy.borderAccent,disabledBackgroundColor:C=t.colors.legacy.spotBase,disabledToggleColor:T=t.colors.legacy.textBase,disabledToggleOpacity:w=.4,checked:v=!1,disabled:i=!1,onChange:m,label:y})=>{let{t:f}=c();return(0,o.jsxs)(S,{width:h,height:s,toggleWidth:b,toggleHeight:u,activeBackgroundColor:p,inactiveBackgroundColor:k,disabledBackgroundColor:C,activeToggleColor:$,inactiveToggleColor:x,disabledToggleColor:T,disabledToggleOpacity:w,disabled:i,children:[(0,o.jsx)("input",{type:"checkbox","aria-label":y??"checkbox",id:e,checked:i||v,onChange:m,disabled:i,"data-testid":e}),(0,o.jsx)("label",{htmlFor:e,children:f("switchToggle")})]})});export{R as a};
//# sourceMappingURL=chunk-MIARPMVY.js.map
