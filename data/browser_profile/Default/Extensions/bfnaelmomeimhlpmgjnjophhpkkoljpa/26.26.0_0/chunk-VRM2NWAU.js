import{b as e,c}from"./chunk-RLWRKBLA.js";import{sb as r}from"./chunk-ROW53IBC.js";import{i as n,n as t}from"./chunk-TSHWMJEM.js";n();t();var i=5,a=c.div`
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  :hover {
    svg {
      fill: white;
    }
  }
  svg {
    fill: ${r.colors.legacy.textDiminished};
    transition: fill 200ms ease;
  }
  padding: ${i}px;
  margin: -${i}px;
  ${o=>o.isActive&&e`
      svg {
        fill: white;
      }
    `}
`,p=c(a).attrs(o=>({diameter:o.diameter??28}))`
  height: ${o=>o.diameter}px;
  min-width: ${o=>o.diameter}px;
  transition: background-color 200ms ease;
  border-radius: 50%;
  background-color: ${o=>o.backgroundColor||""};

  :hover {
    background-color: ${r.colors.legacy.areaAccent};
  }
  ${o=>o.isActive&&e`
      background-color: ${r.colors.legacy.areaAccent};
    `}
`;export{i as a,a as b,p as c};
//# sourceMappingURL=chunk-VRM2NWAU.js.map
