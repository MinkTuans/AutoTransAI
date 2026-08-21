import{c as N}from"./chunk-D3BHBSWL.js";import{b as c,c as m}from"./chunk-RLWRKBLA.js";import{$b as w,Xb as $,f,sb as o}from"./chunk-ROW53IBC.js";import{a as l,g as u,i as y,n as h}from"./chunk-TSHWMJEM.js";y();h();var i=u(f(),1),z=l(({width:e=44,trackColor:a=o.colors.legacy.areaAccent,spinnerColor:n=o.colors.legacy.spotBase})=>(0,i.jsxs)("svg",{width:e,height:e,viewBox:"0 0 26 26",children:[(0,i.jsx)("g",{children:(0,i.jsx)("path",{fillRule:"evenodd",clipRule:"evenodd",d:"M13 23.413c5.751 0 10.413-4.662 10.413-10.413S18.751 2.587 13 2.587 2.587 7.249 2.587 13 7.249 23.413 13 23.413zm0 2.315c7.03 0 12.727-5.699 12.727-12.728S20.03.273 13 .273C5.97.273.273 5.97.273 13 .273 20.03 5.97 25.728 13 25.728z",fill:a})}),(0,i.jsx)("g",{children:(0,i.jsx)("path",{fillRule:"evenodd",clipRule:"evenodd",d:"M16.382 24.125a1.157 1.157 0 01.623-1.513 10.412 10.412 0 005.607-13.617 1.157 1.157 0 112.136-.89 12.726 12.726 0 01-6.853 16.643 1.157 1.157 0 01-1.513-.623z",fill:n})})]}),"LoaderSvg"),A=m.div`
  position: ${e=>e.position};
  height: ${e=>e.diameter}px;
  width: ${e=>e.diameter}px;
  animation: rotate 0.5s linear infinite;
  @keyframes rotate {
    100% {
      transform: rotate(360deg);
    }
  }
`,B=l(({diameter:e=44,color:a,trackColor:n,position:s})=>(0,i.jsx)(A,{diameter:e,position:s,children:(0,i.jsx)(z,{width:e,spinnerColor:a,trackColor:n})}),"Spinner"),I=m.div`
  display: flex;
  align-items: center;
  justify-content: center;
`,E=l(()=>(0,i.jsx)(I,{children:(0,i.jsx)(B,{})}),"SpinnerIcon");y();h();var r=u(f(),1),R=m.button`
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  padding: ${e=>e.paddingY}px 0px;
  width: ${e=>e.width};
  height: ${e=>e.height};
  border-radius: ${e=>e.borderRadius};
  font-size: ${e=>e.fontSize}px;
  font-weight: ${e=>e.fontWeight};
  line-height: ${e=>e.lineHeight}px;
  color: ${o.colors.legacy.textBase};
  pointer-events: auto;
  border: none;
  outline-color: transparent;
  outline-style: none;
  cursor: ${e=>e.disabled?"auto":"pointer"};
  &:disabled {
    opacity: 0.4;
  }
  ${e=>e.noWrap&&c`
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    `}
  ${e=>e.theme==="primary"?c`
          background: ${o.colors.legacy.spotBase};
          color: ${o.colors.legacy.areaBase};
          &:hover:enabled {
            background: ${o.colors.legacy.spotAccent};
          }
        `:e.theme==="warning"?c`
            background: ${o.colors.legacy.spotNegative};
            color: ${o.colors.legacy.areaBase};
            &:hover:enabled {
              background: ${o.colors.legacy.spotNegative};
            }
          `:e.theme==="dark"?c`
              background: ${o.colors.legacy.areaAccent};
            `:e.theme==="metamask"?c`
                /* metamask brand color */
                background: #f5841f;
                &:hover:enabled {
                  /* metamask brand color */
                  background: #d0701a;
                }
              `:e.theme==="link"?c`
                  background: transparent;
                  color: ${o.colors.legacy.spotBase};
                  justify-content: flex-start;
                  &:hover:enabled {
                    color: ${o.colors.legacy.spotBase};
                  }
                `:e.theme==="text"?c`
                    background: transparent;
                    padding-left: 4px;
                    padding-right: 4px;
                    justify-content: flex-start;
                    &:hover:enabled {
                      background: ${o.colors.legacy.gray};
                    }
                  `:c`
                    background: ${o.colors.legacy.elementAccent};
                    &:hover:enabled {
                      background: ${o.colors.legacy.gray};
                    }
                  `}
`,x=l(({children:e,loading:a,to:n,onClick:s,fontSize:d=16,fontWeight:t=600,lineHeight:p=19,paddingY:k=14,width:v="100%",borderRadius:b="16px",theme:P="default",type:S="button",noWrap:g=!0,...H})=>{let C={fontSize:d,fontWeight:t,lineHeight:p,paddingY:k,width:v,borderRadius:b,theme:P,type:S,noWrap:g,...H};return n?(0,r.jsx)(M,{loading:a,to:n,...C,children:e}):(0,r.jsx)(R,{...C,onClick:s,children:a?(0,r.jsx)(B,{diameter:24,position:"absolute"}):e})},"Button");var M=l(({children:e,loading:a,to:n,...s})=>{let d=N();if(!n)throw new Error("ButtonWithNavigation requires a 'to' prop");return(0,r.jsx)(R,{...s,onClick:()=>d(n),children:a?(0,r.jsx)(B,{diameter:24,position:"absolute"}):e})},"NavButton"),T=m.div`
  display: flex;
  flex-direction: ${e=>e.vertical?"column-reverse":"row"};
  width: 100%;
  gap: 10px;
`;var D={fontSize:14,lineHeight:17,paddingY:10},V=l(({className:e,primaryText:a,secondaryText:n,onPrimaryClicked:s,onPrimaryHover:d,onSecondaryClicked:t,primaryTheme:p="primary",secondaryTheme:k="default",primaryDisabled:v=!1,primaryLoading:b,secondaryDisabled:P,buttonPairStyle:S="normal"})=>{let g=S==="normal"?{}:D;return(0,r.jsxs)(T,{className:e,children:[(0,r.jsx)(x,{theme:k,onClick:t,disabled:P,...g,"data-testid":"secondary-button",children:n}),(0,r.jsx)(x,{type:"submit",theme:p,disabled:v,loading:b,onClick:s,onMouseEnter:d,...g,"data-testid":"primary-button",children:a})]})},"ButtonPair");var X=l(({buttons:e,buttonStyle:a,className:n,vertical:s})=>{let d=a==="small"?D:{};return(0,r.jsx)(T,{className:n,vertical:s,children:(0,r.jsx)($,{children:e.map((t,p)=>typeof t.hideButton>"u"?(0,r.jsx)(x,{type:t.type??"button",theme:t.theme,onClick:t.onClick,disabled:t.disabled,loading:t.loading,className:t.className,"data-testid":t.testID,...d,children:t.text},t.key??(typeof t.text=="string"&&t.text?t.text:p)):t.hideButton?null:(0,r.jsx)(w.div,{initial:{opacity:0,scale:.8,width:0},exit:{opacity:0,width:0},animate:{height:"auto",opacity:1,scale:1,width:"100%"},transition:{ease:"easeInOut",duration:.3},children:(0,r.jsx)(x,{type:t.type??"button",theme:t.theme,onClick:t.onClick,disabled:t.disabled,loading:t.loading,className:t.className,"data-testid":t.testID,...d,children:t.text})},t.key??(typeof t.text=="string"&&t.text?t.text:p)))})})},"ButtonGroup");export{B as a,E as b,x as c,V as d,X as e};
//# sourceMappingURL=chunk-2EQUCBKU.js.map
