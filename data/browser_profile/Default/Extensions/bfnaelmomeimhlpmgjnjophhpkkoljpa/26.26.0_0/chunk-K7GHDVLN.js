import{a as P}from"./chunk-2EQUCBKU.js";import{D as C,ma as S}from"./chunk-D3BHBSWL.js";import{b,c as n}from"./chunk-RLWRKBLA.js";import{e as H,f as W,sb as r}from"./chunk-ROW53IBC.js";import{a as u,g as h,i as m,n as f}from"./chunk-TSHWMJEM.js";m();f();var s=h(H(),1);var t=h(W(),1),d=b`
  width: 100%;
  padding: ${e=>e.padding||"14px"};
  background: ${e=>e.backgroundColor||r.colors.legacy.areaAccent};
  border-width: ${e=>e.borderWidth||"1px"};
  border-style: solid;
  border-color: ${e=>e.warning?r.colors.legacy.spotNegative:r.colors.legacy.borderDiminished};
  border-radius: ${e=>e.borderRadius||"6px"};
  color: white;
  font-size: ${e=>e.fontSize||"16px"};
  line-height: 19px;

  &::placeholder {
    color: ${e=>e.placeholderColor||r.colors.legacy.textIncidental};
  }

  &:focus {
    outline: 0;
  }

  ::selection {
    background: ${r.colors.legacy.spotBase};
  }

  ::-moz-selection {
    background: ${r.colors.legacy.spotBase};
  }
`,N=b`
  &::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }

  &::-webkit-outer-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }

  &[type="number"] {
    -moz-appearance: textfield;
  }
`,g=u(e=>{let p=(0,s.forwardRef)(({warningMessage:o,...a},c)=>(0,t.jsxs)(F,{children:[(0,t.jsx)(e,{...a,ref:c}),o&&(0,t.jsx)(V,{children:o})]})),l=(0,s.forwardRef)(({label:o,...a},c)=>(0,t.jsx)(B,{label:o,children:(0,t.jsx)(e,{...a,ref:c})})),i=e;return i.WithWarning=p,i.WithLabel=l,i},"withVariants"),F=n.div`
  width: 100%;
`,x=n.input`
  ${d}
  ${N}
`,V=n.div`
  color: ${r.colors.legacy.spotNegative};
  font-size: 16px;
  line-height: 1.2;
  margin-top: 10px;
  text-align: left;
`,B=n.div`
  position: relative;
  &:after {
    ${e=>e.label?`content: "${e.label}"`:""};
    color: ${r.colors.legacy.textIncidental};
    position: absolute;
    right: 20px;
    bottom: 17px;
    font-size: 16px;
  }
`,te=g(x),K=n.textarea`
  ${d}
  resize: none;
  padding: 25px;
  line-height: 150%;
  word-spacing: 10px;
  text-align: left;
  white-space: normal;
  &:placeholder-shown {
    word-spacing: 3px;
  }
`,D=n.textarea`
  ${d}
  height: 68px;
  text-align: start;
  resize: none;
`,q=n.textarea`
  ${d}
  height: 68px;
  text-align: start;
  resize: none;
`,O=n.textarea`
  ${d}
  overflow: auto;
  height: 50px;
  text-align: start;
`,ne=g(K),re=g(D),oe=g(q),ae=g(O),U=n(x)`
  padding-left: 43px;
  padding-right: 43px;
`,G=n.div`
  width: 100%;
  position: relative;
`,J=n.div`
  position: absolute;
  top: 16px;
  left: 15px;
`,Q=n.div`
  position: absolute;
  top: 16px;
  right: 15px;
  cursor: pointer;
`,ie=(0,s.forwardRef)((e,p)=>{let{showClearIcon:l,onClear:i,showLoadingIcon:o=!1,...a}=e;return(0,t.jsxs)(G,{children:[(0,t.jsx)(J,{children:o?(0,t.jsx)(P,{diameter:17}):(0,t.jsx)(C,{})}),(0,t.jsx)(U,{...a,ref:p,type:"text"}),l&&(0,t.jsx)(Q,{onClick:i,children:(0,t.jsx)(S,{})})]})}),X=n(x)`
  border: ${({border:e})=>e||"inherit"};
  color: ${({color:e})=>e||"inherit"};

  &:disabled {
    cursor: not-allowed;
  }
`,se=s.default.memo(u(function({value:p,placeholder:l,fontSize:i="16px",required:o,warning:a,minLength:c=1,maxLength:w=79,decimalLimit:v=9,border:T,borderRadius:$,disabled:L,"aria-labelledby":R,"aria-label":M,onKeyPress:k,onUserInput:z,name:A}){return(0,t.jsx)(X,{value:p,required:o,warning:a,border:T,borderRadius:$,color:a?r.colors.legacy.spotNegative:r.colors.legacy.textBase,type:"text",inputMode:"decimal",pattern:`^\\d*(\\.\\d{0,${v}})?$`,autoComplete:"off",autoCorrect:"off",spellCheck:"false",fontSize:i,placeholder:l,step:"any",minLength:c,maxLength:w,disabled:L,name:A,"aria-labelledby":R,"aria-label":M,onKeyPress:k,onInput:y=>{let I=y.target;if(!I.validity.valid)y.preventDefault();else{let E=I.value.replace(/,/g,".");z(E)}}})},"InnerInput"));export{g as a,te as b,ne as c,re as d,oe as e,ae as f,ie as g,se as h};
//# sourceMappingURL=chunk-K7GHDVLN.js.map
