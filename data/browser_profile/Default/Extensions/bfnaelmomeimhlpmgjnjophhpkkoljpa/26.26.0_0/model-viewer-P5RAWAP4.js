import{a as d,i as L,m as Buffer,n as P}from"./chunk-TSHWMJEM.js";L();P();L();P();L();P();L();P();L();P();var ty=d((o,e)=>e.kind==="method"&&e.descriptor&&!("value"in e.descriptor)?{...e,finisher(t){t.createProperty(e.key,o)}}:{kind:"field",key:Symbol(),placement:"own",descriptor:{},originalKey:e.key,initializer(){typeof e.initializer=="function"&&(this[e.key]=e.initializer.call(this))},finisher(t){t.createProperty(e.key,o)}},"i");function ye(o){return(e,t)=>t!==void 0?((n,i,s)=>{i.constructor.createProperty(s,n)})(o,e,t):ty(o,e)}d(ye,"e");L();P();L();P();L();P();L();P();L();P();L();P();L();P();var mh,FS=((mh=self.HTMLSlotElement)===null||mh===void 0?void 0:mh.prototype.assignedElements)!=null?(o,e)=>o.assignedElements(e):(o,e)=>o.assignedNodes(e).filter(t=>t.nodeType===Node.ELEMENT_NODE);L();P();L();P();var Mu="149";var ny=0,Ap=1,iy=2;var NA=1,sy=2,xo=3,fn=0,dt=1,Et=2;var ri=0,er=1,mp=2,gp=3,_p=4,ry=5,Ys=100,oy=101,ay=102,yp=103,xp=104,ly=200,cy=201,hy=202,uy=203,UA=204,QA=205,dy=206,fy=207,py=208,Ay=209,my=210,gy=0,_y=1,yy=2,Kh=3,xy=4,vy=5,Ey=6,wy=7,kA=0,My=1,by=2,qn=0,Iy=1,Cy=2,Sy=3,bu=4,Ty=5,GA=300,ir=301,sr=302,So=303,$h=304,zl=306,Pn=1e3,Lt=1001,vs=1002,ct=1003,rr=1004;var _s=1005;var Je=1006,Wo=1007;var wn=1008;var $t=1009,By=1010,Ry=1011,zA=1012,Dy=1013,gs=1014,Ut=1015,Pt=1016,Ly=1017,Py=1018,tr=1020,Fy=1021,lt=1023,Oy=1024,Ny=1025,ys=1026,or=1027,yr=1028,Uy=1029,xr=1030,Qy=1031,ky=1033,Eo=33776,gh=33777,_h=33778,wo=33779,dl=35840,vp=35841,fl=35842,Ep=35843,Iu=36196,pl=37492,Al=37496,ml=37808,wp=37809,Mp=37810,bp=37811,Ip=37812,Cp=37813,Sp=37814,Tp=37815,Bp=37816,Rp=37817,Dp=37818,Lp=37819,Pp=37820,Fp=37821,Mo=36492,Gy=36283,Op=36284,Np=36285,Up=36286,Cu=2200,qo=2201,Ko=2202,zi=2300,wi=2301,yh=2302,Js=2400,js=2401,gl=2402,Su=2500,zy=2501,VA=0,Vl=1,$o=2,ft=3e3,Se=3001,Vy=3200,Hy=3201,HA=0,Wy=1;var ii="srgb",To="srgb-linear";var xh=7680;var qy=519,Xh=35044;var Qp="300 es",Yh=1035,Mt=class{static{d(this,"EventDispatcher")}addEventListener(e,t){this._listeners===void 0&&(this._listeners={});let n=this._listeners;n[e]===void 0&&(n[e]=[]),n[e].indexOf(t)===-1&&n[e].push(t)}hasEventListener(e,t){if(this._listeners===void 0)return!1;let n=this._listeners;return n[e]!==void 0&&n[e].indexOf(t)!==-1}removeEventListener(e,t){if(this._listeners===void 0)return;let i=this._listeners[e];if(i!==void 0){let s=i.indexOf(t);s!==-1&&i.splice(s,1)}}dispatchEvent(e){if(this._listeners===void 0)return;let n=this._listeners[e.type];if(n!==void 0){e.target=this;let i=n.slice(0);for(let s=0,r=i.length;s<r;s++)i[s].call(this,e);e.target=null}}},qt=["00","01","02","03","04","05","06","07","08","09","0a","0b","0c","0d","0e","0f","10","11","12","13","14","15","16","17","18","19","1a","1b","1c","1d","1e","1f","20","21","22","23","24","25","26","27","28","29","2a","2b","2c","2d","2e","2f","30","31","32","33","34","35","36","37","38","39","3a","3b","3c","3d","3e","3f","40","41","42","43","44","45","46","47","48","49","4a","4b","4c","4d","4e","4f","50","51","52","53","54","55","56","57","58","59","5a","5b","5c","5d","5e","5f","60","61","62","63","64","65","66","67","68","69","6a","6b","6c","6d","6e","6f","70","71","72","73","74","75","76","77","78","79","7a","7b","7c","7d","7e","7f","80","81","82","83","84","85","86","87","88","89","8a","8b","8c","8d","8e","8f","90","91","92","93","94","95","96","97","98","99","9a","9b","9c","9d","9e","9f","a0","a1","a2","a3","a4","a5","a6","a7","a8","a9","aa","ab","ac","ad","ae","af","b0","b1","b2","b3","b4","b5","b6","b7","b8","b9","ba","bb","bc","bd","be","bf","c0","c1","c2","c3","c4","c5","c6","c7","c8","c9","ca","cb","cc","cd","ce","cf","d0","d1","d2","d3","d4","d5","d6","d7","d8","d9","da","db","dc","dd","de","df","e0","e1","e2","e3","e4","e5","e6","e7","e8","e9","ea","eb","ec","ed","ee","ef","f0","f1","f2","f3","f4","f5","f6","f7","f8","f9","fa","fb","fc","fd","fe","ff"],kp=1234567,bo=Math.PI/180,Bo=180/Math.PI;function Kn(){let o=Math.random()*4294967295|0,e=Math.random()*4294967295|0,t=Math.random()*4294967295|0,n=Math.random()*4294967295|0;return(qt[o&255]+qt[o>>8&255]+qt[o>>16&255]+qt[o>>24&255]+"-"+qt[e&255]+qt[e>>8&255]+"-"+qt[e>>16&15|64]+qt[e>>24&255]+"-"+qt[t&63|128]+qt[t>>8&255]+"-"+qt[t>>16&255]+qt[t>>24&255]+qt[n&255]+qt[n>>8&255]+qt[n>>16&255]+qt[n>>24&255]).toLowerCase()}d(Kn,"generateUUID");function Nt(o,e,t){return Math.max(e,Math.min(t,o))}d(Nt,"clamp");function Tu(o,e){return(o%e+e)%e}d(Tu,"euclideanModulo");function Ky(o,e,t,n,i){return n+(o-e)*(i-n)/(t-e)}d(Ky,"mapLinear");function $y(o,e,t){return o!==e?(t-o)/(e-o):0}d($y,"inverseLerp");function Io(o,e,t){return(1-t)*o+t*e}d(Io,"lerp");function Xy(o,e,t,n){return Io(o,e,1-Math.exp(-t*n))}d(Xy,"damp");function Yy(o,e=1){return e-Math.abs(Tu(o,e*2)-e)}d(Yy,"pingpong");function Jy(o,e,t){return o<=e?0:o>=t?1:(o=(o-e)/(t-e),o*o*(3-2*o))}d(Jy,"smoothstep");function jy(o,e,t){return o<=e?0:o>=t?1:(o=(o-e)/(t-e),o*o*o*(o*(o*6-15)+10))}d(jy,"smootherstep");function Zy(o,e){return o+Math.floor(Math.random()*(e-o+1))}d(Zy,"randInt");function ex(o,e){return o+Math.random()*(e-o)}d(ex,"randFloat");function tx(o){return o*(.5-Math.random())}d(tx,"randFloatSpread");function nx(o){o!==void 0&&(kp=o);let e=kp+=1831565813;return e=Math.imul(e^e>>>15,e|1),e^=e+Math.imul(e^e>>>7,e|61),((e^e>>>14)>>>0)/4294967296}d(nx,"seededRandom");function ix(o){return o*bo}d(ix,"degToRad");function sx(o){return o*Bo}d(sx,"radToDeg");function Jh(o){return(o&o-1)===0&&o!==0}d(Jh,"isPowerOfTwo");function WA(o){return Math.pow(2,Math.ceil(Math.log(o)/Math.LN2))}d(WA,"ceilPowerOfTwo");function _l(o){return Math.pow(2,Math.floor(Math.log(o)/Math.LN2))}d(_l,"floorPowerOfTwo");function rx(o,e,t,n,i){let s=Math.cos,r=Math.sin,a=s(t/2),l=r(t/2),c=s((e+n)/2),h=r((e+n)/2),u=s((e-n)/2),f=r((e-n)/2),p=s((n-e)/2),g=r((n-e)/2);switch(i){case"XYX":o.set(a*h,l*u,l*f,a*c);break;case"YZY":o.set(l*f,a*h,l*u,a*c);break;case"ZXZ":o.set(l*u,l*f,a*h,a*c);break;case"XZX":o.set(a*h,l*g,l*p,a*c);break;case"YXY":o.set(l*p,a*h,l*g,a*c);break;case"ZYZ":o.set(l*g,l*p,a*h,a*c);break;default:console.warn("THREE.MathUtils: .setQuaternionFromProperEuler() encountered an unknown order: "+i)}}d(rx,"setQuaternionFromProperEuler");function vi(o,e){switch(e.constructor){case Float32Array:return o;case Uint16Array:return o/65535;case Uint8Array:return o/255;case Int16Array:return Math.max(o/32767,-1);case Int8Array:return Math.max(o/127,-1);default:throw new Error("Invalid component type.")}}d(vi,"denormalize");function tt(o,e){switch(e.constructor){case Float32Array:return o;case Uint16Array:return Math.round(o*65535);case Uint8Array:return Math.round(o*255);case Int16Array:return Math.round(o*32767);case Int8Array:return Math.round(o*127);default:throw new Error("Invalid component type.")}}d(tt,"normalize");var vr=Object.freeze({__proto__:null,DEG2RAD:bo,RAD2DEG:Bo,ceilPowerOfTwo:WA,clamp:Nt,damp:Xy,degToRad:ix,denormalize:vi,euclideanModulo:Tu,floorPowerOfTwo:_l,generateUUID:Kn,inverseLerp:$y,isPowerOfTwo:Jh,lerp:Io,mapLinear:Ky,normalize:tt,pingpong:Yy,radToDeg:sx,randFloat:ex,randFloatSpread:tx,randInt:Zy,seededRandom:nx,setQuaternionFromProperEuler:rx,smootherstep:jy,smoothstep:Jy}),Be=class o{static{d(this,"Vector2")}constructor(e=0,t=0){o.prototype.isVector2=!0,this.x=e,this.y=t}get width(){return this.x}set width(e){this.x=e}get height(){return this.y}set height(e){this.y=e}set(e,t){return this.x=e,this.y=t,this}setScalar(e){return this.x=e,this.y=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y)}copy(e){return this.x=e.x,this.y=e.y,this}add(e){return this.x+=e.x,this.y+=e.y,this}addScalar(e){return this.x+=e,this.y+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this}subScalar(e){return this.x-=e,this.y-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this}multiply(e){return this.x*=e.x,this.y*=e.y,this}multiplyScalar(e){return this.x*=e,this.y*=e,this}divide(e){return this.x/=e.x,this.y/=e.y,this}divideScalar(e){return this.multiplyScalar(1/e)}applyMatrix3(e){let t=this.x,n=this.y,i=e.elements;return this.x=i[0]*t+i[3]*n+i[6],this.y=i[1]*t+i[4]*n+i[7],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this}clampLength(e,t){let n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this}roundToZero(){return this.x=this.x<0?Math.ceil(this.x):Math.floor(this.x),this.y=this.y<0?Math.ceil(this.y):Math.floor(this.y),this}negate(){return this.x=-this.x,this.y=-this.y,this}dot(e){return this.x*e.x+this.y*e.y}cross(e){return this.x*e.y-this.y*e.x}lengthSq(){return this.x*this.x+this.y*this.y}length(){return Math.sqrt(this.x*this.x+this.y*this.y)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)}normalize(){return this.divideScalar(this.length()||1)}angle(){return Math.atan2(-this.y,-this.x)+Math.PI}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){let t=this.x-e.x,n=this.y-e.y;return t*t+n*n}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this}equals(e){return e.x===this.x&&e.y===this.y}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this}rotateAround(e,t){let n=Math.cos(t),i=Math.sin(t),s=this.x-e.x,r=this.y-e.y;return this.x=s*n-r*i+e.x,this.y=s*i+r*n+e.y,this}random(){return this.x=Math.random(),this.y=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y}},wt=class o{static{d(this,"Matrix3")}constructor(){o.prototype.isMatrix3=!0,this.elements=[1,0,0,0,1,0,0,0,1]}set(e,t,n,i,s,r,a,l,c){let h=this.elements;return h[0]=e,h[1]=i,h[2]=a,h[3]=t,h[4]=s,h[5]=l,h[6]=n,h[7]=r,h[8]=c,this}identity(){return this.set(1,0,0,0,1,0,0,0,1),this}copy(e){let t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],this}extractBasis(e,t,n){return e.setFromMatrix3Column(this,0),t.setFromMatrix3Column(this,1),n.setFromMatrix3Column(this,2),this}setFromMatrix4(e){let t=e.elements;return this.set(t[0],t[4],t[8],t[1],t[5],t[9],t[2],t[6],t[10]),this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){let n=e.elements,i=t.elements,s=this.elements,r=n[0],a=n[3],l=n[6],c=n[1],h=n[4],u=n[7],f=n[2],p=n[5],g=n[8],A=i[0],m=i[3],_=i[6],E=i[1],x=i[4],y=i[7],w=i[2],I=i[5],S=i[8];return s[0]=r*A+a*E+l*w,s[3]=r*m+a*x+l*I,s[6]=r*_+a*y+l*S,s[1]=c*A+h*E+u*w,s[4]=c*m+h*x+u*I,s[7]=c*_+h*y+u*S,s[2]=f*A+p*E+g*w,s[5]=f*m+p*x+g*I,s[8]=f*_+p*y+g*S,this}multiplyScalar(e){let t=this.elements;return t[0]*=e,t[3]*=e,t[6]*=e,t[1]*=e,t[4]*=e,t[7]*=e,t[2]*=e,t[5]*=e,t[8]*=e,this}determinant(){let e=this.elements,t=e[0],n=e[1],i=e[2],s=e[3],r=e[4],a=e[5],l=e[6],c=e[7],h=e[8];return t*r*h-t*a*c-n*s*h+n*a*l+i*s*c-i*r*l}invert(){let e=this.elements,t=e[0],n=e[1],i=e[2],s=e[3],r=e[4],a=e[5],l=e[6],c=e[7],h=e[8],u=h*r-a*c,f=a*l-h*s,p=c*s-r*l,g=t*u+n*f+i*p;if(g===0)return this.set(0,0,0,0,0,0,0,0,0);let A=1/g;return e[0]=u*A,e[1]=(i*c-h*n)*A,e[2]=(a*n-i*r)*A,e[3]=f*A,e[4]=(h*t-i*l)*A,e[5]=(i*s-a*t)*A,e[6]=p*A,e[7]=(n*l-c*t)*A,e[8]=(r*t-n*s)*A,this}transpose(){let e,t=this.elements;return e=t[1],t[1]=t[3],t[3]=e,e=t[2],t[2]=t[6],t[6]=e,e=t[5],t[5]=t[7],t[7]=e,this}getNormalMatrix(e){return this.setFromMatrix4(e).invert().transpose()}transposeIntoArray(e){let t=this.elements;return e[0]=t[0],e[1]=t[3],e[2]=t[6],e[3]=t[1],e[4]=t[4],e[5]=t[7],e[6]=t[2],e[7]=t[5],e[8]=t[8],this}setUvTransform(e,t,n,i,s,r,a){let l=Math.cos(s),c=Math.sin(s);return this.set(n*l,n*c,-n*(l*r+c*a)+r+e,-i*c,i*l,-i*(-c*r+l*a)+a+t,0,0,1),this}scale(e,t){return this.premultiply(vh.makeScale(e,t)),this}rotate(e){return this.premultiply(vh.makeRotation(-e)),this}translate(e,t){return this.premultiply(vh.makeTranslation(e,t)),this}makeTranslation(e,t){return this.set(1,0,e,0,1,t,0,0,1),this}makeRotation(e){let t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,n,t,0,0,0,1),this}makeScale(e,t){return this.set(e,0,0,0,t,0,0,0,1),this}equals(e){let t=this.elements,n=e.elements;for(let i=0;i<9;i++)if(t[i]!==n[i])return!1;return!0}fromArray(e,t=0){for(let n=0;n<9;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){let n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e}clone(){return new this.constructor().fromArray(this.elements)}},vh=new wt;function qA(o){for(let e=o.length-1;e>=0;--e)if(o[e]>=65535)return!0;return!1}d(qA,"arrayNeedsUint32");function Ro(o){return document.createElementNS("http://www.w3.org/1999/xhtml",o)}d(Ro,"createElementNS");function xs(o){return o<.04045?o*.0773993808:Math.pow(o*.9478672986+.0521327014,2.4)}d(xs,"SRGBToLinear");function ul(o){return o<.0031308?o*12.92:1.055*Math.pow(o,.41666)-.055}d(ul,"LinearToSRGB");var Eh={[ii]:{[To]:xs},[To]:{[ii]:ul}},en={legacyMode:!0,get workingColorSpace(){return To},set workingColorSpace(o){console.warn("THREE.ColorManagement: .workingColorSpace is readonly.")},convert:d(function(o,e,t){if(this.legacyMode||e===t||!e||!t)return o;if(Eh[e]&&Eh[e][t]!==void 0){let n=Eh[e][t];return o.r=n(o.r),o.g=n(o.g),o.b=n(o.b),o}throw new Error("Unsupported color space conversion.")},"convert"),fromWorkingColorSpace:d(function(o,e){return this.convert(o,this.workingColorSpace,e)},"fromWorkingColorSpace"),toWorkingColorSpace:d(function(o,e){return this.convert(o,e,this.workingColorSpace)},"toWorkingColorSpace")},KA={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074},vt={r:0,g:0,b:0},Vn={h:0,s:0,l:0},za={h:0,s:0,l:0};function wh(o,e,t){return t<0&&(t+=1),t>1&&(t-=1),t<1/6?o+(e-o)*6*t:t<1/2?e:t<2/3?o+(e-o)*6*(2/3-t):o}d(wh,"hue2rgb");function Va(o,e){return e.r=o.r,e.g=o.g,e.b=o.b,e}d(Va,"toComponents");var Me=class{static{d(this,"Color")}constructor(e,t,n){return this.isColor=!0,this.r=1,this.g=1,this.b=1,t===void 0&&n===void 0?this.set(e):this.setRGB(e,t,n)}set(e){return e&&e.isColor?this.copy(e):typeof e=="number"?this.setHex(e):typeof e=="string"&&this.setStyle(e),this}setScalar(e){return this.r=e,this.g=e,this.b=e,this}setHex(e,t=ii){return e=Math.floor(e),this.r=(e>>16&255)/255,this.g=(e>>8&255)/255,this.b=(e&255)/255,en.toWorkingColorSpace(this,t),this}setRGB(e,t,n,i=en.workingColorSpace){return this.r=e,this.g=t,this.b=n,en.toWorkingColorSpace(this,i),this}setHSL(e,t,n,i=en.workingColorSpace){if(e=Tu(e,1),t=Nt(t,0,1),n=Nt(n,0,1),t===0)this.r=this.g=this.b=n;else{let s=n<=.5?n*(1+t):n+t-n*t,r=2*n-s;this.r=wh(r,s,e+1/3),this.g=wh(r,s,e),this.b=wh(r,s,e-1/3)}return en.toWorkingColorSpace(this,i),this}setStyle(e,t=ii){function n(s){s!==void 0&&parseFloat(s)<1&&console.warn("THREE.Color: Alpha component of "+e+" will be ignored.")}d(n,"handleAlpha");let i;if(i=/^((?:rgb|hsl)a?)\(([^\)]*)\)/.exec(e)){let s,r=i[1],a=i[2];switch(r){case"rgb":case"rgba":if(s=/^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(a))return this.r=Math.min(255,parseInt(s[1],10))/255,this.g=Math.min(255,parseInt(s[2],10))/255,this.b=Math.min(255,parseInt(s[3],10))/255,en.toWorkingColorSpace(this,t),n(s[4]),this;if(s=/^\s*(\d+)\%\s*,\s*(\d+)\%\s*,\s*(\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(a))return this.r=Math.min(100,parseInt(s[1],10))/100,this.g=Math.min(100,parseInt(s[2],10))/100,this.b=Math.min(100,parseInt(s[3],10))/100,en.toWorkingColorSpace(this,t),n(s[4]),this;break;case"hsl":case"hsla":if(s=/^\s*(\d*\.?\d+)\s*,\s*(\d*\.?\d+)\%\s*,\s*(\d*\.?\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(a)){let l=parseFloat(s[1])/360,c=parseFloat(s[2])/100,h=parseFloat(s[3])/100;return n(s[4]),this.setHSL(l,c,h,t)}break}}else if(i=/^\#([A-Fa-f\d]+)$/.exec(e)){let s=i[1],r=s.length;if(r===3)return this.r=parseInt(s.charAt(0)+s.charAt(0),16)/255,this.g=parseInt(s.charAt(1)+s.charAt(1),16)/255,this.b=parseInt(s.charAt(2)+s.charAt(2),16)/255,en.toWorkingColorSpace(this,t),this;if(r===6)return this.r=parseInt(s.charAt(0)+s.charAt(1),16)/255,this.g=parseInt(s.charAt(2)+s.charAt(3),16)/255,this.b=parseInt(s.charAt(4)+s.charAt(5),16)/255,en.toWorkingColorSpace(this,t),this}return e&&e.length>0?this.setColorName(e,t):this}setColorName(e,t=ii){let n=KA[e.toLowerCase()];return n!==void 0?this.setHex(n,t):console.warn("THREE.Color: Unknown color "+e),this}clone(){return new this.constructor(this.r,this.g,this.b)}copy(e){return this.r=e.r,this.g=e.g,this.b=e.b,this}copySRGBToLinear(e){return this.r=xs(e.r),this.g=xs(e.g),this.b=xs(e.b),this}copyLinearToSRGB(e){return this.r=ul(e.r),this.g=ul(e.g),this.b=ul(e.b),this}convertSRGBToLinear(){return this.copySRGBToLinear(this),this}convertLinearToSRGB(){return this.copyLinearToSRGB(this),this}getHex(e=ii){return en.fromWorkingColorSpace(Va(this,vt),e),Nt(vt.r*255,0,255)<<16^Nt(vt.g*255,0,255)<<8^Nt(vt.b*255,0,255)<<0}getHexString(e=ii){return("000000"+this.getHex(e).toString(16)).slice(-6)}getHSL(e,t=en.workingColorSpace){en.fromWorkingColorSpace(Va(this,vt),t);let n=vt.r,i=vt.g,s=vt.b,r=Math.max(n,i,s),a=Math.min(n,i,s),l,c,h=(a+r)/2;if(a===r)l=0,c=0;else{let u=r-a;switch(c=h<=.5?u/(r+a):u/(2-r-a),r){case n:l=(i-s)/u+(i<s?6:0);break;case i:l=(s-n)/u+2;break;case s:l=(n-i)/u+4;break}l/=6}return e.h=l,e.s=c,e.l=h,e}getRGB(e,t=en.workingColorSpace){return en.fromWorkingColorSpace(Va(this,vt),t),e.r=vt.r,e.g=vt.g,e.b=vt.b,e}getStyle(e=ii){return en.fromWorkingColorSpace(Va(this,vt),e),e!==ii?`color(${e} ${vt.r} ${vt.g} ${vt.b})`:`rgb(${vt.r*255|0},${vt.g*255|0},${vt.b*255|0})`}offsetHSL(e,t,n){return this.getHSL(Vn),Vn.h+=e,Vn.s+=t,Vn.l+=n,this.setHSL(Vn.h,Vn.s,Vn.l),this}add(e){return this.r+=e.r,this.g+=e.g,this.b+=e.b,this}addColors(e,t){return this.r=e.r+t.r,this.g=e.g+t.g,this.b=e.b+t.b,this}addScalar(e){return this.r+=e,this.g+=e,this.b+=e,this}sub(e){return this.r=Math.max(0,this.r-e.r),this.g=Math.max(0,this.g-e.g),this.b=Math.max(0,this.b-e.b),this}multiply(e){return this.r*=e.r,this.g*=e.g,this.b*=e.b,this}multiplyScalar(e){return this.r*=e,this.g*=e,this.b*=e,this}lerp(e,t){return this.r+=(e.r-this.r)*t,this.g+=(e.g-this.g)*t,this.b+=(e.b-this.b)*t,this}lerpColors(e,t,n){return this.r=e.r+(t.r-e.r)*n,this.g=e.g+(t.g-e.g)*n,this.b=e.b+(t.b-e.b)*n,this}lerpHSL(e,t){this.getHSL(Vn),e.getHSL(za);let n=Io(Vn.h,za.h,t),i=Io(Vn.s,za.s,t),s=Io(Vn.l,za.l,t);return this.setHSL(n,i,s),this}equals(e){return e.r===this.r&&e.g===this.g&&e.b===this.b}fromArray(e,t=0){return this.r=e[t],this.g=e[t+1],this.b=e[t+2],this}toArray(e=[],t=0){return e[t]=this.r,e[t+1]=this.g,e[t+2]=this.b,e}fromBufferAttribute(e,t){return this.r=e.getX(t),this.g=e.getY(t),this.b=e.getZ(t),this}toJSON(){return this.getHex()}*[Symbol.iterator](){yield this.r,yield this.g,yield this.b}};Me.NAMES=KA;var Os,yl=class{static{d(this,"ImageUtils")}static getDataURL(e){if(/^data:/i.test(e.src)||typeof HTMLCanvasElement>"u")return e.src;let t;if(e instanceof HTMLCanvasElement)t=e;else{Os===void 0&&(Os=Ro("canvas")),Os.width=e.width,Os.height=e.height;let n=Os.getContext("2d");e instanceof ImageData?n.putImageData(e,0,0):n.drawImage(e,0,0,e.width,e.height),t=Os}return t.width>2048||t.height>2048?(console.warn("THREE.ImageUtils.getDataURL: Image converted to jpg for performance reasons",e),t.toDataURL("image/jpeg",.6)):t.toDataURL("image/png")}static sRGBToLinear(e){if(typeof HTMLImageElement<"u"&&e instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&e instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&e instanceof ImageBitmap){let t=Ro("canvas");t.width=e.width,t.height=e.height;let n=t.getContext("2d");n.drawImage(e,0,0,e.width,e.height);let i=n.getImageData(0,0,e.width,e.height),s=i.data;for(let r=0;r<s.length;r++)s[r]=xs(s[r]/255)*255;return n.putImageData(i,0,0),t}else if(e.data){let t=e.data.slice(0);for(let n=0;n<t.length;n++)t instanceof Uint8Array||t instanceof Uint8ClampedArray?t[n]=Math.floor(xs(t[n]/255)*255):t[n]=xs(t[n]);return{data:t,width:e.width,height:e.height}}else return console.warn("THREE.ImageUtils.sRGBToLinear(): Unsupported image type. No color space conversion applied."),e}},ar=class{static{d(this,"Source")}constructor(e=null){this.isSource=!0,this.uuid=Kn(),this.data=e,this.version=0}set needsUpdate(e){e===!0&&this.version++}toJSON(e){let t=e===void 0||typeof e=="string";if(!t&&e.images[this.uuid]!==void 0)return e.images[this.uuid];let n={uuid:this.uuid,url:""},i=this.data;if(i!==null){let s;if(Array.isArray(i)){s=[];for(let r=0,a=i.length;r<a;r++)i[r].isDataTexture?s.push(Mh(i[r].image)):s.push(Mh(i[r]))}else s=Mh(i);n.url=s}return t||(e.images[this.uuid]=n),n}};function Mh(o){return typeof HTMLImageElement<"u"&&o instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&o instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&o instanceof ImageBitmap?yl.getDataURL(o):o.data?{data:Array.from(o.data),width:o.width,height:o.height,type:o.data.constructor.name}:(console.warn("THREE.Texture: Unable to serialize Texture."),{})}d(Mh,"serializeImage");var ox=0,st=class o extends Mt{static{d(this,"Texture")}constructor(e=o.DEFAULT_IMAGE,t=o.DEFAULT_MAPPING,n=Lt,i=Lt,s=Je,r=wn,a=lt,l=$t,c=o.DEFAULT_ANISOTROPY,h=ft){super(),this.isTexture=!0,Object.defineProperty(this,"id",{value:ox++}),this.uuid=Kn(),this.name="",this.source=new ar(e),this.mipmaps=[],this.mapping=t,this.wrapS=n,this.wrapT=i,this.magFilter=s,this.minFilter=r,this.anisotropy=c,this.format=a,this.internalFormat=null,this.type=l,this.offset=new Be(0,0),this.repeat=new Be(1,1),this.center=new Be(0,0),this.rotation=0,this.matrixAutoUpdate=!0,this.matrix=new wt,this.generateMipmaps=!0,this.premultiplyAlpha=!1,this.flipY=!0,this.unpackAlignment=4,this.encoding=h,this.userData={},this.version=0,this.onUpdate=null,this.isRenderTargetTexture=!1,this.needsPMREMUpdate=!1}get image(){return this.source.data}set image(e){this.source.data=e}updateMatrix(){this.matrix.setUvTransform(this.offset.x,this.offset.y,this.repeat.x,this.repeat.y,this.rotation,this.center.x,this.center.y)}clone(){return new this.constructor().copy(this)}copy(e){return this.name=e.name,this.source=e.source,this.mipmaps=e.mipmaps.slice(0),this.mapping=e.mapping,this.wrapS=e.wrapS,this.wrapT=e.wrapT,this.magFilter=e.magFilter,this.minFilter=e.minFilter,this.anisotropy=e.anisotropy,this.format=e.format,this.internalFormat=e.internalFormat,this.type=e.type,this.offset.copy(e.offset),this.repeat.copy(e.repeat),this.center.copy(e.center),this.rotation=e.rotation,this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrix.copy(e.matrix),this.generateMipmaps=e.generateMipmaps,this.premultiplyAlpha=e.premultiplyAlpha,this.flipY=e.flipY,this.unpackAlignment=e.unpackAlignment,this.encoding=e.encoding,this.userData=JSON.parse(JSON.stringify(e.userData)),this.needsUpdate=!0,this}toJSON(e){let t=e===void 0||typeof e=="string";if(!t&&e.textures[this.uuid]!==void 0)return e.textures[this.uuid];let n={metadata:{version:4.5,type:"Texture",generator:"Texture.toJSON"},uuid:this.uuid,name:this.name,image:this.source.toJSON(e).uuid,mapping:this.mapping,repeat:[this.repeat.x,this.repeat.y],offset:[this.offset.x,this.offset.y],center:[this.center.x,this.center.y],rotation:this.rotation,wrap:[this.wrapS,this.wrapT],format:this.format,type:this.type,encoding:this.encoding,minFilter:this.minFilter,magFilter:this.magFilter,anisotropy:this.anisotropy,flipY:this.flipY,generateMipmaps:this.generateMipmaps,premultiplyAlpha:this.premultiplyAlpha,unpackAlignment:this.unpackAlignment};return Object.keys(this.userData).length>0&&(n.userData=this.userData),t||(e.textures[this.uuid]=n),n}dispose(){this.dispatchEvent({type:"dispose"})}transformUv(e){if(this.mapping!==GA)return e;if(e.applyMatrix3(this.matrix),e.x<0||e.x>1)switch(this.wrapS){case Pn:e.x=e.x-Math.floor(e.x);break;case Lt:e.x=e.x<0?0:1;break;case vs:Math.abs(Math.floor(e.x)%2)===1?e.x=Math.ceil(e.x)-e.x:e.x=e.x-Math.floor(e.x);break}if(e.y<0||e.y>1)switch(this.wrapT){case Pn:e.y=e.y-Math.floor(e.y);break;case Lt:e.y=e.y<0?0:1;break;case vs:Math.abs(Math.floor(e.y)%2)===1?e.y=Math.ceil(e.y)-e.y:e.y=e.y-Math.floor(e.y);break}return this.flipY&&(e.y=1-e.y),e}set needsUpdate(e){e===!0&&(this.version++,this.source.needsUpdate=!0)}};st.DEFAULT_IMAGE=null;st.DEFAULT_MAPPING=GA;st.DEFAULT_ANISOTROPY=1;var nt=class o{static{d(this,"Vector4")}constructor(e=0,t=0,n=0,i=1){o.prototype.isVector4=!0,this.x=e,this.y=t,this.z=n,this.w=i}get width(){return this.z}set width(e){this.z=e}get height(){return this.w}set height(e){this.w=e}set(e,t,n,i){return this.x=e,this.y=t,this.z=n,this.w=i,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this.w=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setW(e){return this.w=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;case 3:this.w=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;case 3:return this.w;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z,this.w)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this.w=e.w!==void 0?e.w:1,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this.w+=e.w,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this.w+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this.w=e.w+t.w,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this.w+=e.w*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this.w-=e.w,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this.w-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this.w=e.w-t.w,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this.w*=e.w,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this.w*=e,this}applyMatrix4(e){let t=this.x,n=this.y,i=this.z,s=this.w,r=e.elements;return this.x=r[0]*t+r[4]*n+r[8]*i+r[12]*s,this.y=r[1]*t+r[5]*n+r[9]*i+r[13]*s,this.z=r[2]*t+r[6]*n+r[10]*i+r[14]*s,this.w=r[3]*t+r[7]*n+r[11]*i+r[15]*s,this}divideScalar(e){return this.multiplyScalar(1/e)}setAxisAngleFromQuaternion(e){this.w=2*Math.acos(e.w);let t=Math.sqrt(1-e.w*e.w);return t<1e-4?(this.x=1,this.y=0,this.z=0):(this.x=e.x/t,this.y=e.y/t,this.z=e.z/t),this}setAxisAngleFromRotationMatrix(e){let t,n,i,s,l=e.elements,c=l[0],h=l[4],u=l[8],f=l[1],p=l[5],g=l[9],A=l[2],m=l[6],_=l[10];if(Math.abs(h-f)<.01&&Math.abs(u-A)<.01&&Math.abs(g-m)<.01){if(Math.abs(h+f)<.1&&Math.abs(u+A)<.1&&Math.abs(g+m)<.1&&Math.abs(c+p+_-3)<.1)return this.set(1,0,0,0),this;t=Math.PI;let x=(c+1)/2,y=(p+1)/2,w=(_+1)/2,I=(h+f)/4,S=(u+A)/4,v=(g+m)/4;return x>y&&x>w?x<.01?(n=0,i=.707106781,s=.707106781):(n=Math.sqrt(x),i=I/n,s=S/n):y>w?y<.01?(n=.707106781,i=0,s=.707106781):(i=Math.sqrt(y),n=I/i,s=v/i):w<.01?(n=.707106781,i=.707106781,s=0):(s=Math.sqrt(w),n=S/s,i=v/s),this.set(n,i,s,t),this}let E=Math.sqrt((m-g)*(m-g)+(u-A)*(u-A)+(f-h)*(f-h));return Math.abs(E)<.001&&(E=1),this.x=(m-g)/E,this.y=(u-A)/E,this.z=(f-h)/E,this.w=Math.acos((c+p+_-1)/2),this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this.w=Math.min(this.w,e.w),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this.w=Math.max(this.w,e.w),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this.w=Math.max(e.w,Math.min(t.w,this.w)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this.w=Math.max(e,Math.min(t,this.w)),this}clampLength(e,t){let n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this.w=Math.floor(this.w),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this.w=Math.ceil(this.w),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this.w=Math.round(this.w),this}roundToZero(){return this.x=this.x<0?Math.ceil(this.x):Math.floor(this.x),this.y=this.y<0?Math.ceil(this.y):Math.floor(this.y),this.z=this.z<0?Math.ceil(this.z):Math.floor(this.z),this.w=this.w<0?Math.ceil(this.w):Math.floor(this.w),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this.w=-this.w,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z+this.w*e.w}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)+Math.abs(this.w)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this.w+=(e.w-this.w)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this.w=e.w+(t.w-e.w)*n,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z&&e.w===this.w}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this.w=e[t+3],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e[t+3]=this.w,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this.w=e.getW(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this.w=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z,yield this.w}},Xt=class extends Mt{static{d(this,"WebGLRenderTarget")}constructor(e=1,t=1,n={}){super(),this.isWebGLRenderTarget=!0,this.width=e,this.height=t,this.depth=1,this.scissor=new nt(0,0,e,t),this.scissorTest=!1,this.viewport=new nt(0,0,e,t);let i={width:e,height:t,depth:1};this.texture=new st(i,n.mapping,n.wrapS,n.wrapT,n.magFilter,n.minFilter,n.format,n.type,n.anisotropy,n.encoding),this.texture.isRenderTargetTexture=!0,this.texture.flipY=!1,this.texture.generateMipmaps=n.generateMipmaps!==void 0?n.generateMipmaps:!1,this.texture.internalFormat=n.internalFormat!==void 0?n.internalFormat:null,this.texture.minFilter=n.minFilter!==void 0?n.minFilter:Je,this.depthBuffer=n.depthBuffer!==void 0?n.depthBuffer:!0,this.stencilBuffer=n.stencilBuffer!==void 0?n.stencilBuffer:!1,this.depthTexture=n.depthTexture!==void 0?n.depthTexture:null,this.samples=n.samples!==void 0?n.samples:0}setSize(e,t,n=1){(this.width!==e||this.height!==t||this.depth!==n)&&(this.width=e,this.height=t,this.depth=n,this.texture.image.width=e,this.texture.image.height=t,this.texture.image.depth=n,this.dispose()),this.viewport.set(0,0,e,t),this.scissor.set(0,0,e,t)}clone(){return new this.constructor().copy(this)}copy(e){this.width=e.width,this.height=e.height,this.depth=e.depth,this.viewport.copy(e.viewport),this.texture=e.texture.clone(),this.texture.isRenderTargetTexture=!0;let t=Object.assign({},e.texture.image);return this.texture.source=new ar(t),this.depthBuffer=e.depthBuffer,this.stencilBuffer=e.stencilBuffer,e.depthTexture!==null&&(this.depthTexture=e.depthTexture.clone()),this.samples=e.samples,this}dispose(){this.dispatchEvent({type:"dispose"})}},xl=class extends st{static{d(this,"DataArrayTexture")}constructor(e=null,t=1,n=1,i=1){super(null),this.isDataArrayTexture=!0,this.image={data:e,width:t,height:n,depth:i},this.magFilter=ct,this.minFilter=ct,this.wrapR=Lt,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}};var Do=class extends st{static{d(this,"Data3DTexture")}constructor(e=null,t=1,n=1,i=1){super(null),this.isData3DTexture=!0,this.image={data:e,width:t,height:n,depth:i},this.magFilter=ct,this.minFilter=ct,this.wrapR=Lt,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}};var Kt=class{static{d(this,"Quaternion")}constructor(e=0,t=0,n=0,i=1){this.isQuaternion=!0,this._x=e,this._y=t,this._z=n,this._w=i}static slerpFlat(e,t,n,i,s,r,a){let l=n[i+0],c=n[i+1],h=n[i+2],u=n[i+3],f=s[r+0],p=s[r+1],g=s[r+2],A=s[r+3];if(a===0){e[t+0]=l,e[t+1]=c,e[t+2]=h,e[t+3]=u;return}if(a===1){e[t+0]=f,e[t+1]=p,e[t+2]=g,e[t+3]=A;return}if(u!==A||l!==f||c!==p||h!==g){let m=1-a,_=l*f+c*p+h*g+u*A,E=_>=0?1:-1,x=1-_*_;if(x>Number.EPSILON){let w=Math.sqrt(x),I=Math.atan2(w,_*E);m=Math.sin(m*I)/w,a=Math.sin(a*I)/w}let y=a*E;if(l=l*m+f*y,c=c*m+p*y,h=h*m+g*y,u=u*m+A*y,m===1-a){let w=1/Math.sqrt(l*l+c*c+h*h+u*u);l*=w,c*=w,h*=w,u*=w}}e[t]=l,e[t+1]=c,e[t+2]=h,e[t+3]=u}static multiplyQuaternionsFlat(e,t,n,i,s,r){let a=n[i],l=n[i+1],c=n[i+2],h=n[i+3],u=s[r],f=s[r+1],p=s[r+2],g=s[r+3];return e[t]=a*g+h*u+l*p-c*f,e[t+1]=l*g+h*f+c*u-a*p,e[t+2]=c*g+h*p+a*f-l*u,e[t+3]=h*g-a*u-l*f-c*p,e}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get w(){return this._w}set w(e){this._w=e,this._onChangeCallback()}set(e,t,n,i){return this._x=e,this._y=t,this._z=n,this._w=i,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._w)}copy(e){return this._x=e.x,this._y=e.y,this._z=e.z,this._w=e.w,this._onChangeCallback(),this}setFromEuler(e,t){let n=e._x,i=e._y,s=e._z,r=e._order,a=Math.cos,l=Math.sin,c=a(n/2),h=a(i/2),u=a(s/2),f=l(n/2),p=l(i/2),g=l(s/2);switch(r){case"XYZ":this._x=f*h*u+c*p*g,this._y=c*p*u-f*h*g,this._z=c*h*g+f*p*u,this._w=c*h*u-f*p*g;break;case"YXZ":this._x=f*h*u+c*p*g,this._y=c*p*u-f*h*g,this._z=c*h*g-f*p*u,this._w=c*h*u+f*p*g;break;case"ZXY":this._x=f*h*u-c*p*g,this._y=c*p*u+f*h*g,this._z=c*h*g+f*p*u,this._w=c*h*u-f*p*g;break;case"ZYX":this._x=f*h*u-c*p*g,this._y=c*p*u+f*h*g,this._z=c*h*g-f*p*u,this._w=c*h*u+f*p*g;break;case"YZX":this._x=f*h*u+c*p*g,this._y=c*p*u+f*h*g,this._z=c*h*g-f*p*u,this._w=c*h*u-f*p*g;break;case"XZY":this._x=f*h*u-c*p*g,this._y=c*p*u-f*h*g,this._z=c*h*g+f*p*u,this._w=c*h*u+f*p*g;break;default:console.warn("THREE.Quaternion: .setFromEuler() encountered an unknown order: "+r)}return t!==!1&&this._onChangeCallback(),this}setFromAxisAngle(e,t){let n=t/2,i=Math.sin(n);return this._x=e.x*i,this._y=e.y*i,this._z=e.z*i,this._w=Math.cos(n),this._onChangeCallback(),this}setFromRotationMatrix(e){let t=e.elements,n=t[0],i=t[4],s=t[8],r=t[1],a=t[5],l=t[9],c=t[2],h=t[6],u=t[10],f=n+a+u;if(f>0){let p=.5/Math.sqrt(f+1);this._w=.25/p,this._x=(h-l)*p,this._y=(s-c)*p,this._z=(r-i)*p}else if(n>a&&n>u){let p=2*Math.sqrt(1+n-a-u);this._w=(h-l)/p,this._x=.25*p,this._y=(i+r)/p,this._z=(s+c)/p}else if(a>u){let p=2*Math.sqrt(1+a-n-u);this._w=(s-c)/p,this._x=(i+r)/p,this._y=.25*p,this._z=(l+h)/p}else{let p=2*Math.sqrt(1+u-n-a);this._w=(r-i)/p,this._x=(s+c)/p,this._y=(l+h)/p,this._z=.25*p}return this._onChangeCallback(),this}setFromUnitVectors(e,t){let n=e.dot(t)+1;return n<Number.EPSILON?(n=0,Math.abs(e.x)>Math.abs(e.z)?(this._x=-e.y,this._y=e.x,this._z=0,this._w=n):(this._x=0,this._y=-e.z,this._z=e.y,this._w=n)):(this._x=e.y*t.z-e.z*t.y,this._y=e.z*t.x-e.x*t.z,this._z=e.x*t.y-e.y*t.x,this._w=n),this.normalize()}angleTo(e){return 2*Math.acos(Math.abs(Nt(this.dot(e),-1,1)))}rotateTowards(e,t){let n=this.angleTo(e);if(n===0)return this;let i=Math.min(1,t/n);return this.slerp(e,i),this}identity(){return this.set(0,0,0,1)}invert(){return this.conjugate()}conjugate(){return this._x*=-1,this._y*=-1,this._z*=-1,this._onChangeCallback(),this}dot(e){return this._x*e._x+this._y*e._y+this._z*e._z+this._w*e._w}lengthSq(){return this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w}length(){return Math.sqrt(this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w)}normalize(){let e=this.length();return e===0?(this._x=0,this._y=0,this._z=0,this._w=1):(e=1/e,this._x=this._x*e,this._y=this._y*e,this._z=this._z*e,this._w=this._w*e),this._onChangeCallback(),this}multiply(e){return this.multiplyQuaternions(this,e)}premultiply(e){return this.multiplyQuaternions(e,this)}multiplyQuaternions(e,t){let n=e._x,i=e._y,s=e._z,r=e._w,a=t._x,l=t._y,c=t._z,h=t._w;return this._x=n*h+r*a+i*c-s*l,this._y=i*h+r*l+s*a-n*c,this._z=s*h+r*c+n*l-i*a,this._w=r*h-n*a-i*l-s*c,this._onChangeCallback(),this}slerp(e,t){if(t===0)return this;if(t===1)return this.copy(e);let n=this._x,i=this._y,s=this._z,r=this._w,a=r*e._w+n*e._x+i*e._y+s*e._z;if(a<0?(this._w=-e._w,this._x=-e._x,this._y=-e._y,this._z=-e._z,a=-a):this.copy(e),a>=1)return this._w=r,this._x=n,this._y=i,this._z=s,this;let l=1-a*a;if(l<=Number.EPSILON){let p=1-t;return this._w=p*r+t*this._w,this._x=p*n+t*this._x,this._y=p*i+t*this._y,this._z=p*s+t*this._z,this.normalize(),this._onChangeCallback(),this}let c=Math.sqrt(l),h=Math.atan2(c,a),u=Math.sin((1-t)*h)/c,f=Math.sin(t*h)/c;return this._w=r*u+this._w*f,this._x=n*u+this._x*f,this._y=i*u+this._y*f,this._z=s*u+this._z*f,this._onChangeCallback(),this}slerpQuaternions(e,t,n){return this.copy(e).slerp(t,n)}random(){let e=Math.random(),t=Math.sqrt(1-e),n=Math.sqrt(e),i=2*Math.PI*Math.random(),s=2*Math.PI*Math.random();return this.set(t*Math.cos(i),n*Math.sin(s),n*Math.cos(s),t*Math.sin(i))}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._w===this._w}fromArray(e,t=0){return this._x=e[t],this._y=e[t+1],this._z=e[t+2],this._w=e[t+3],this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._w,e}fromBufferAttribute(e,t){return this._x=e.getX(t),this._y=e.getY(t),this._z=e.getZ(t),this._w=e.getW(t),this}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._w}},B=class o{static{d(this,"Vector3")}constructor(e=0,t=0,n=0){o.prototype.isVector3=!0,this.x=e,this.y=t,this.z=n}set(e,t,n){return n===void 0&&(n=this.z),this.x=e,this.y=t,this.z=n,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this}multiplyVectors(e,t){return this.x=e.x*t.x,this.y=e.y*t.y,this.z=e.z*t.z,this}applyEuler(e){return this.applyQuaternion(Gp.setFromEuler(e))}applyAxisAngle(e,t){return this.applyQuaternion(Gp.setFromAxisAngle(e,t))}applyMatrix3(e){let t=this.x,n=this.y,i=this.z,s=e.elements;return this.x=s[0]*t+s[3]*n+s[6]*i,this.y=s[1]*t+s[4]*n+s[7]*i,this.z=s[2]*t+s[5]*n+s[8]*i,this}applyNormalMatrix(e){return this.applyMatrix3(e).normalize()}applyMatrix4(e){let t=this.x,n=this.y,i=this.z,s=e.elements,r=1/(s[3]*t+s[7]*n+s[11]*i+s[15]);return this.x=(s[0]*t+s[4]*n+s[8]*i+s[12])*r,this.y=(s[1]*t+s[5]*n+s[9]*i+s[13])*r,this.z=(s[2]*t+s[6]*n+s[10]*i+s[14])*r,this}applyQuaternion(e){let t=this.x,n=this.y,i=this.z,s=e.x,r=e.y,a=e.z,l=e.w,c=l*t+r*i-a*n,h=l*n+a*t-s*i,u=l*i+s*n-r*t,f=-s*t-r*n-a*i;return this.x=c*l+f*-s+h*-a-u*-r,this.y=h*l+f*-r+u*-s-c*-a,this.z=u*l+f*-a+c*-r-h*-s,this}project(e){return this.applyMatrix4(e.matrixWorldInverse).applyMatrix4(e.projectionMatrix)}unproject(e){return this.applyMatrix4(e.projectionMatrixInverse).applyMatrix4(e.matrixWorld)}transformDirection(e){let t=this.x,n=this.y,i=this.z,s=e.elements;return this.x=s[0]*t+s[4]*n+s[8]*i,this.y=s[1]*t+s[5]*n+s[9]*i,this.z=s[2]*t+s[6]*n+s[10]*i,this.normalize()}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this}divideScalar(e){return this.multiplyScalar(1/e)}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this}clampLength(e,t){let n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this}roundToZero(){return this.x=this.x<0?Math.ceil(this.x):Math.floor(this.x),this.y=this.y<0?Math.ceil(this.y):Math.floor(this.y),this.z=this.z<0?Math.ceil(this.z):Math.floor(this.z),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this}cross(e){return this.crossVectors(this,e)}crossVectors(e,t){let n=e.x,i=e.y,s=e.z,r=t.x,a=t.y,l=t.z;return this.x=i*l-s*a,this.y=s*r-n*l,this.z=n*a-i*r,this}projectOnVector(e){let t=e.lengthSq();if(t===0)return this.set(0,0,0);let n=e.dot(this)/t;return this.copy(e).multiplyScalar(n)}projectOnPlane(e){return bh.copy(this).projectOnVector(e),this.sub(bh)}reflect(e){return this.sub(bh.copy(e).multiplyScalar(2*this.dot(e)))}angleTo(e){let t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;let n=this.dot(e)/t;return Math.acos(Nt(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){let t=this.x-e.x,n=this.y-e.y,i=this.z-e.z;return t*t+n*n+i*i}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)+Math.abs(this.z-e.z)}setFromSpherical(e){return this.setFromSphericalCoords(e.radius,e.phi,e.theta)}setFromSphericalCoords(e,t,n){let i=Math.sin(t)*e;return this.x=i*Math.sin(n),this.y=Math.cos(t)*e,this.z=i*Math.cos(n),this}setFromCylindrical(e){return this.setFromCylindricalCoords(e.radius,e.theta,e.y)}setFromCylindricalCoords(e,t,n){return this.x=e*Math.sin(t),this.y=n,this.z=e*Math.cos(t),this}setFromMatrixPosition(e){let t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this}setFromMatrixScale(e){let t=this.setFromMatrixColumn(e,0).length(),n=this.setFromMatrixColumn(e,1).length(),i=this.setFromMatrixColumn(e,2).length();return this.x=t,this.y=n,this.z=i,this}setFromMatrixColumn(e,t){return this.fromArray(e.elements,t*4)}setFromMatrix3Column(e,t){return this.fromArray(e.elements,t*3)}setFromEuler(e){return this.x=e._x,this.y=e._y,this.z=e._z,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this}randomDirection(){let e=(Math.random()-.5)*2,t=Math.random()*Math.PI*2,n=Math.sqrt(1-e**2);return this.x=n*Math.cos(t),this.y=n*Math.sin(t),this.z=e,this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z}},bh=new B,Gp=new Kt,Qt=class{static{d(this,"Box3")}constructor(e=new B(1/0,1/0,1/0),t=new B(-1/0,-1/0,-1/0)){this.isBox3=!0,this.min=e,this.max=t}set(e,t){return this.min.copy(e),this.max.copy(t),this}setFromArray(e){let t=1/0,n=1/0,i=1/0,s=-1/0,r=-1/0,a=-1/0;for(let l=0,c=e.length;l<c;l+=3){let h=e[l],u=e[l+1],f=e[l+2];h<t&&(t=h),u<n&&(n=u),f<i&&(i=f),h>s&&(s=h),u>r&&(r=u),f>a&&(a=f)}return this.min.set(t,n,i),this.max.set(s,r,a),this}setFromBufferAttribute(e){let t=1/0,n=1/0,i=1/0,s=-1/0,r=-1/0,a=-1/0;for(let l=0,c=e.count;l<c;l++){let h=e.getX(l),u=e.getY(l),f=e.getZ(l);h<t&&(t=h),u<n&&(n=u),f<i&&(i=f),h>s&&(s=h),u>r&&(r=u),f>a&&(a=f)}return this.min.set(t,n,i),this.max.set(s,r,a),this}setFromPoints(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t++)this.expandByPoint(e[t]);return this}setFromCenterAndSize(e,t){let n=ds.copy(t).multiplyScalar(.5);return this.min.copy(e).sub(n),this.max.copy(e).add(n),this}setFromObject(e,t=!1){return this.makeEmpty(),this.expandByObject(e,t)}clone(){return new this.constructor().copy(this)}copy(e){return this.min.copy(e.min),this.max.copy(e.max),this}makeEmpty(){return this.min.x=this.min.y=this.min.z=1/0,this.max.x=this.max.y=this.max.z=-1/0,this}isEmpty(){return this.max.x<this.min.x||this.max.y<this.min.y||this.max.z<this.min.z}getCenter(e){return this.isEmpty()?e.set(0,0,0):e.addVectors(this.min,this.max).multiplyScalar(.5)}getSize(e){return this.isEmpty()?e.set(0,0,0):e.subVectors(this.max,this.min)}expandByPoint(e){return this.min.min(e),this.max.max(e),this}expandByVector(e){return this.min.sub(e),this.max.add(e),this}expandByScalar(e){return this.min.addScalar(-e),this.max.addScalar(e),this}expandByObject(e,t=!1){e.updateWorldMatrix(!1,!1);let n=e.geometry;if(n!==void 0)if(t&&n.attributes!=null&&n.attributes.position!==void 0){let s=n.attributes.position;for(let r=0,a=s.count;r<a;r++)ds.fromBufferAttribute(s,r).applyMatrix4(e.matrixWorld),this.expandByPoint(ds)}else n.boundingBox===null&&n.computeBoundingBox(),Ih.copy(n.boundingBox),Ih.applyMatrix4(e.matrixWorld),this.union(Ih);let i=e.children;for(let s=0,r=i.length;s<r;s++)this.expandByObject(i[s],t);return this}containsPoint(e){return!(e.x<this.min.x||e.x>this.max.x||e.y<this.min.y||e.y>this.max.y||e.z<this.min.z||e.z>this.max.z)}containsBox(e){return this.min.x<=e.min.x&&e.max.x<=this.max.x&&this.min.y<=e.min.y&&e.max.y<=this.max.y&&this.min.z<=e.min.z&&e.max.z<=this.max.z}getParameter(e,t){return t.set((e.x-this.min.x)/(this.max.x-this.min.x),(e.y-this.min.y)/(this.max.y-this.min.y),(e.z-this.min.z)/(this.max.z-this.min.z))}intersectsBox(e){return!(e.max.x<this.min.x||e.min.x>this.max.x||e.max.y<this.min.y||e.min.y>this.max.y||e.max.z<this.min.z||e.min.z>this.max.z)}intersectsSphere(e){return this.clampPoint(e.center,ds),ds.distanceToSquared(e.center)<=e.radius*e.radius}intersectsPlane(e){let t,n;return e.normal.x>0?(t=e.normal.x*this.min.x,n=e.normal.x*this.max.x):(t=e.normal.x*this.max.x,n=e.normal.x*this.min.x),e.normal.y>0?(t+=e.normal.y*this.min.y,n+=e.normal.y*this.max.y):(t+=e.normal.y*this.max.y,n+=e.normal.y*this.min.y),e.normal.z>0?(t+=e.normal.z*this.min.z,n+=e.normal.z*this.max.z):(t+=e.normal.z*this.max.z,n+=e.normal.z*this.min.z),t<=-e.constant&&n>=-e.constant}intersectsTriangle(e){if(this.isEmpty())return!1;this.getCenter(ho),Ha.subVectors(this.max,ho),Ns.subVectors(e.a,ho),Us.subVectors(e.b,ho),Qs.subVectors(e.c,ho),Ni.subVectors(Us,Ns),Ui.subVectors(Qs,Us),fs.subVectors(Ns,Qs);let t=[0,-Ni.z,Ni.y,0,-Ui.z,Ui.y,0,-fs.z,fs.y,Ni.z,0,-Ni.x,Ui.z,0,-Ui.x,fs.z,0,-fs.x,-Ni.y,Ni.x,0,-Ui.y,Ui.x,0,-fs.y,fs.x,0];return!Ch(t,Ns,Us,Qs,Ha)||(t=[1,0,0,0,1,0,0,0,1],!Ch(t,Ns,Us,Qs,Ha))?!1:(Wa.crossVectors(Ni,Ui),t=[Wa.x,Wa.y,Wa.z],Ch(t,Ns,Us,Qs,Ha))}clampPoint(e,t){return t.copy(e).clamp(this.min,this.max)}distanceToPoint(e){return ds.copy(e).clamp(this.min,this.max).sub(e).length()}getBoundingSphere(e){return this.getCenter(e.center),e.radius=this.getSize(ds).length()*.5,e}intersect(e){return this.min.max(e.min),this.max.min(e.max),this.isEmpty()&&this.makeEmpty(),this}union(e){return this.min.min(e.min),this.max.max(e.max),this}applyMatrix4(e){return this.isEmpty()?this:(fi[0].set(this.min.x,this.min.y,this.min.z).applyMatrix4(e),fi[1].set(this.min.x,this.min.y,this.max.z).applyMatrix4(e),fi[2].set(this.min.x,this.max.y,this.min.z).applyMatrix4(e),fi[3].set(this.min.x,this.max.y,this.max.z).applyMatrix4(e),fi[4].set(this.max.x,this.min.y,this.min.z).applyMatrix4(e),fi[5].set(this.max.x,this.min.y,this.max.z).applyMatrix4(e),fi[6].set(this.max.x,this.max.y,this.min.z).applyMatrix4(e),fi[7].set(this.max.x,this.max.y,this.max.z).applyMatrix4(e),this.setFromPoints(fi),this)}translate(e){return this.min.add(e),this.max.add(e),this}equals(e){return e.min.equals(this.min)&&e.max.equals(this.max)}},fi=[new B,new B,new B,new B,new B,new B,new B,new B],ds=new B,Ih=new Qt,Ns=new B,Us=new B,Qs=new B,Ni=new B,Ui=new B,fs=new B,ho=new B,Ha=new B,Wa=new B,ps=new B;function Ch(o,e,t,n,i){for(let s=0,r=o.length-3;s<=r;s+=3){ps.fromArray(o,s);let a=i.x*Math.abs(ps.x)+i.y*Math.abs(ps.y)+i.z*Math.abs(ps.z),l=e.dot(ps),c=t.dot(ps),h=n.dot(ps);if(Math.max(-Math.max(l,c,h),Math.min(l,c,h))>a)return!1}return!0}d(Ch,"satForAxes");var ax=new Qt,uo=new B,Sh=new B,Mn=class{static{d(this,"Sphere")}constructor(e=new B,t=-1){this.center=e,this.radius=t}set(e,t){return this.center.copy(e),this.radius=t,this}setFromPoints(e,t){let n=this.center;t!==void 0?n.copy(t):ax.setFromPoints(e).getCenter(n);let i=0;for(let s=0,r=e.length;s<r;s++)i=Math.max(i,n.distanceToSquared(e[s]));return this.radius=Math.sqrt(i),this}copy(e){return this.center.copy(e.center),this.radius=e.radius,this}isEmpty(){return this.radius<0}makeEmpty(){return this.center.set(0,0,0),this.radius=-1,this}containsPoint(e){return e.distanceToSquared(this.center)<=this.radius*this.radius}distanceToPoint(e){return e.distanceTo(this.center)-this.radius}intersectsSphere(e){let t=this.radius+e.radius;return e.center.distanceToSquared(this.center)<=t*t}intersectsBox(e){return e.intersectsSphere(this)}intersectsPlane(e){return Math.abs(e.distanceToPoint(this.center))<=this.radius}clampPoint(e,t){let n=this.center.distanceToSquared(e);return t.copy(e),n>this.radius*this.radius&&(t.sub(this.center).normalize(),t.multiplyScalar(this.radius).add(this.center)),t}getBoundingBox(e){return this.isEmpty()?(e.makeEmpty(),e):(e.set(this.center,this.center),e.expandByScalar(this.radius),e)}applyMatrix4(e){return this.center.applyMatrix4(e),this.radius=this.radius*e.getMaxScaleOnAxis(),this}translate(e){return this.center.add(e),this}expandByPoint(e){if(this.isEmpty())return this.center.copy(e),this.radius=0,this;uo.subVectors(e,this.center);let t=uo.lengthSq();if(t>this.radius*this.radius){let n=Math.sqrt(t),i=(n-this.radius)*.5;this.center.addScaledVector(uo,i/n),this.radius+=i}return this}union(e){return e.isEmpty()?this:this.isEmpty()?(this.copy(e),this):(this.center.equals(e.center)===!0?this.radius=Math.max(this.radius,e.radius):(Sh.subVectors(e.center,this.center).setLength(e.radius),this.expandByPoint(uo.copy(e.center).add(Sh)),this.expandByPoint(uo.copy(e.center).sub(Sh))),this)}equals(e){return e.center.equals(this.center)&&e.radius===this.radius}clone(){return new this.constructor().copy(this)}},pi=new B,Th=new B,qa=new B,Qi=new B,Bh=new B,Ka=new B,Rh=new B,lr=class{static{d(this,"Ray")}constructor(e=new B,t=new B(0,0,-1)){this.origin=e,this.direction=t}set(e,t){return this.origin.copy(e),this.direction.copy(t),this}copy(e){return this.origin.copy(e.origin),this.direction.copy(e.direction),this}at(e,t){return t.copy(this.direction).multiplyScalar(e).add(this.origin)}lookAt(e){return this.direction.copy(e).sub(this.origin).normalize(),this}recast(e){return this.origin.copy(this.at(e,pi)),this}closestPointToPoint(e,t){t.subVectors(e,this.origin);let n=t.dot(this.direction);return n<0?t.copy(this.origin):t.copy(this.direction).multiplyScalar(n).add(this.origin)}distanceToPoint(e){return Math.sqrt(this.distanceSqToPoint(e))}distanceSqToPoint(e){let t=pi.subVectors(e,this.origin).dot(this.direction);return t<0?this.origin.distanceToSquared(e):(pi.copy(this.direction).multiplyScalar(t).add(this.origin),pi.distanceToSquared(e))}distanceSqToSegment(e,t,n,i){Th.copy(e).add(t).multiplyScalar(.5),qa.copy(t).sub(e).normalize(),Qi.copy(this.origin).sub(Th);let s=e.distanceTo(t)*.5,r=-this.direction.dot(qa),a=Qi.dot(this.direction),l=-Qi.dot(qa),c=Qi.lengthSq(),h=Math.abs(1-r*r),u,f,p,g;if(h>0)if(u=r*l-a,f=r*a-l,g=s*h,u>=0)if(f>=-g)if(f<=g){let A=1/h;u*=A,f*=A,p=u*(u+r*f+2*a)+f*(r*u+f+2*l)+c}else f=s,u=Math.max(0,-(r*f+a)),p=-u*u+f*(f+2*l)+c;else f=-s,u=Math.max(0,-(r*f+a)),p=-u*u+f*(f+2*l)+c;else f<=-g?(u=Math.max(0,-(-r*s+a)),f=u>0?-s:Math.min(Math.max(-s,-l),s),p=-u*u+f*(f+2*l)+c):f<=g?(u=0,f=Math.min(Math.max(-s,-l),s),p=f*(f+2*l)+c):(u=Math.max(0,-(r*s+a)),f=u>0?s:Math.min(Math.max(-s,-l),s),p=-u*u+f*(f+2*l)+c);else f=r>0?-s:s,u=Math.max(0,-(r*f+a)),p=-u*u+f*(f+2*l)+c;return n&&n.copy(this.direction).multiplyScalar(u).add(this.origin),i&&i.copy(qa).multiplyScalar(f).add(Th),p}intersectSphere(e,t){pi.subVectors(e.center,this.origin);let n=pi.dot(this.direction),i=pi.dot(pi)-n*n,s=e.radius*e.radius;if(i>s)return null;let r=Math.sqrt(s-i),a=n-r,l=n+r;return a<0&&l<0?null:a<0?this.at(l,t):this.at(a,t)}intersectsSphere(e){return this.distanceSqToPoint(e.center)<=e.radius*e.radius}distanceToPlane(e){let t=e.normal.dot(this.direction);if(t===0)return e.distanceToPoint(this.origin)===0?0:null;let n=-(this.origin.dot(e.normal)+e.constant)/t;return n>=0?n:null}intersectPlane(e,t){let n=this.distanceToPlane(e);return n===null?null:this.at(n,t)}intersectsPlane(e){let t=e.distanceToPoint(this.origin);return t===0||e.normal.dot(this.direction)*t<0}intersectBox(e,t){let n,i,s,r,a,l,c=1/this.direction.x,h=1/this.direction.y,u=1/this.direction.z,f=this.origin;return c>=0?(n=(e.min.x-f.x)*c,i=(e.max.x-f.x)*c):(n=(e.max.x-f.x)*c,i=(e.min.x-f.x)*c),h>=0?(s=(e.min.y-f.y)*h,r=(e.max.y-f.y)*h):(s=(e.max.y-f.y)*h,r=(e.min.y-f.y)*h),n>r||s>i||((s>n||isNaN(n))&&(n=s),(r<i||isNaN(i))&&(i=r),u>=0?(a=(e.min.z-f.z)*u,l=(e.max.z-f.z)*u):(a=(e.max.z-f.z)*u,l=(e.min.z-f.z)*u),n>l||a>i)||((a>n||n!==n)&&(n=a),(l<i||i!==i)&&(i=l),i<0)?null:this.at(n>=0?n:i,t)}intersectsBox(e){return this.intersectBox(e,pi)!==null}intersectTriangle(e,t,n,i,s){Bh.subVectors(t,e),Ka.subVectors(n,e),Rh.crossVectors(Bh,Ka);let r=this.direction.dot(Rh),a;if(r>0){if(i)return null;a=1}else if(r<0)a=-1,r=-r;else return null;Qi.subVectors(this.origin,e);let l=a*this.direction.dot(Ka.crossVectors(Qi,Ka));if(l<0)return null;let c=a*this.direction.dot(Bh.cross(Qi));if(c<0||l+c>r)return null;let h=-a*Qi.dot(Rh);return h<0?null:this.at(h/r,s)}applyMatrix4(e){return this.origin.applyMatrix4(e),this.direction.transformDirection(e),this}equals(e){return e.origin.equals(this.origin)&&e.direction.equals(this.direction)}clone(){return new this.constructor().copy(this)}},Ie=class o{static{d(this,"Matrix4")}constructor(){o.prototype.isMatrix4=!0,this.elements=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]}set(e,t,n,i,s,r,a,l,c,h,u,f,p,g,A,m){let _=this.elements;return _[0]=e,_[4]=t,_[8]=n,_[12]=i,_[1]=s,_[5]=r,_[9]=a,_[13]=l,_[2]=c,_[6]=h,_[10]=u,_[14]=f,_[3]=p,_[7]=g,_[11]=A,_[15]=m,this}identity(){return this.set(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1),this}clone(){return new o().fromArray(this.elements)}copy(e){let t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],t[9]=n[9],t[10]=n[10],t[11]=n[11],t[12]=n[12],t[13]=n[13],t[14]=n[14],t[15]=n[15],this}copyPosition(e){let t=this.elements,n=e.elements;return t[12]=n[12],t[13]=n[13],t[14]=n[14],this}setFromMatrix3(e){let t=e.elements;return this.set(t[0],t[3],t[6],0,t[1],t[4],t[7],0,t[2],t[5],t[8],0,0,0,0,1),this}extractBasis(e,t,n){return e.setFromMatrixColumn(this,0),t.setFromMatrixColumn(this,1),n.setFromMatrixColumn(this,2),this}makeBasis(e,t,n){return this.set(e.x,t.x,n.x,0,e.y,t.y,n.y,0,e.z,t.z,n.z,0,0,0,0,1),this}extractRotation(e){let t=this.elements,n=e.elements,i=1/ks.setFromMatrixColumn(e,0).length(),s=1/ks.setFromMatrixColumn(e,1).length(),r=1/ks.setFromMatrixColumn(e,2).length();return t[0]=n[0]*i,t[1]=n[1]*i,t[2]=n[2]*i,t[3]=0,t[4]=n[4]*s,t[5]=n[5]*s,t[6]=n[6]*s,t[7]=0,t[8]=n[8]*r,t[9]=n[9]*r,t[10]=n[10]*r,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromEuler(e){let t=this.elements,n=e.x,i=e.y,s=e.z,r=Math.cos(n),a=Math.sin(n),l=Math.cos(i),c=Math.sin(i),h=Math.cos(s),u=Math.sin(s);if(e.order==="XYZ"){let f=r*h,p=r*u,g=a*h,A=a*u;t[0]=l*h,t[4]=-l*u,t[8]=c,t[1]=p+g*c,t[5]=f-A*c,t[9]=-a*l,t[2]=A-f*c,t[6]=g+p*c,t[10]=r*l}else if(e.order==="YXZ"){let f=l*h,p=l*u,g=c*h,A=c*u;t[0]=f+A*a,t[4]=g*a-p,t[8]=r*c,t[1]=r*u,t[5]=r*h,t[9]=-a,t[2]=p*a-g,t[6]=A+f*a,t[10]=r*l}else if(e.order==="ZXY"){let f=l*h,p=l*u,g=c*h,A=c*u;t[0]=f-A*a,t[4]=-r*u,t[8]=g+p*a,t[1]=p+g*a,t[5]=r*h,t[9]=A-f*a,t[2]=-r*c,t[6]=a,t[10]=r*l}else if(e.order==="ZYX"){let f=r*h,p=r*u,g=a*h,A=a*u;t[0]=l*h,t[4]=g*c-p,t[8]=f*c+A,t[1]=l*u,t[5]=A*c+f,t[9]=p*c-g,t[2]=-c,t[6]=a*l,t[10]=r*l}else if(e.order==="YZX"){let f=r*l,p=r*c,g=a*l,A=a*c;t[0]=l*h,t[4]=A-f*u,t[8]=g*u+p,t[1]=u,t[5]=r*h,t[9]=-a*h,t[2]=-c*h,t[6]=p*u+g,t[10]=f-A*u}else if(e.order==="XZY"){let f=r*l,p=r*c,g=a*l,A=a*c;t[0]=l*h,t[4]=-u,t[8]=c*h,t[1]=f*u+A,t[5]=r*h,t[9]=p*u-g,t[2]=g*u-p,t[6]=a*h,t[10]=A*u+f}return t[3]=0,t[7]=0,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromQuaternion(e){return this.compose(lx,e,cx)}lookAt(e,t,n){let i=this.elements;return xn.subVectors(e,t),xn.lengthSq()===0&&(xn.z=1),xn.normalize(),ki.crossVectors(n,xn),ki.lengthSq()===0&&(Math.abs(n.z)===1?xn.x+=1e-4:xn.z+=1e-4,xn.normalize(),ki.crossVectors(n,xn)),ki.normalize(),$a.crossVectors(xn,ki),i[0]=ki.x,i[4]=$a.x,i[8]=xn.x,i[1]=ki.y,i[5]=$a.y,i[9]=xn.y,i[2]=ki.z,i[6]=$a.z,i[10]=xn.z,this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){let n=e.elements,i=t.elements,s=this.elements,r=n[0],a=n[4],l=n[8],c=n[12],h=n[1],u=n[5],f=n[9],p=n[13],g=n[2],A=n[6],m=n[10],_=n[14],E=n[3],x=n[7],y=n[11],w=n[15],I=i[0],S=i[4],v=i[8],b=i[12],R=i[1],N=i[5],z=i[9],O=i[13],D=i[2],Q=i[6],q=i[10],H=i[14],k=i[3],j=i[7],Z=i[11],fe=i[15];return s[0]=r*I+a*R+l*D+c*k,s[4]=r*S+a*N+l*Q+c*j,s[8]=r*v+a*z+l*q+c*Z,s[12]=r*b+a*O+l*H+c*fe,s[1]=h*I+u*R+f*D+p*k,s[5]=h*S+u*N+f*Q+p*j,s[9]=h*v+u*z+f*q+p*Z,s[13]=h*b+u*O+f*H+p*fe,s[2]=g*I+A*R+m*D+_*k,s[6]=g*S+A*N+m*Q+_*j,s[10]=g*v+A*z+m*q+_*Z,s[14]=g*b+A*O+m*H+_*fe,s[3]=E*I+x*R+y*D+w*k,s[7]=E*S+x*N+y*Q+w*j,s[11]=E*v+x*z+y*q+w*Z,s[15]=E*b+x*O+y*H+w*fe,this}multiplyScalar(e){let t=this.elements;return t[0]*=e,t[4]*=e,t[8]*=e,t[12]*=e,t[1]*=e,t[5]*=e,t[9]*=e,t[13]*=e,t[2]*=e,t[6]*=e,t[10]*=e,t[14]*=e,t[3]*=e,t[7]*=e,t[11]*=e,t[15]*=e,this}determinant(){let e=this.elements,t=e[0],n=e[4],i=e[8],s=e[12],r=e[1],a=e[5],l=e[9],c=e[13],h=e[2],u=e[6],f=e[10],p=e[14],g=e[3],A=e[7],m=e[11],_=e[15];return g*(+s*l*u-i*c*u-s*a*f+n*c*f+i*a*p-n*l*p)+A*(+t*l*p-t*c*f+s*r*f-i*r*p+i*c*h-s*l*h)+m*(+t*c*u-t*a*p-s*r*u+n*r*p+s*a*h-n*c*h)+_*(-i*a*h-t*l*u+t*a*f+i*r*u-n*r*f+n*l*h)}transpose(){let e=this.elements,t;return t=e[1],e[1]=e[4],e[4]=t,t=e[2],e[2]=e[8],e[8]=t,t=e[6],e[6]=e[9],e[9]=t,t=e[3],e[3]=e[12],e[12]=t,t=e[7],e[7]=e[13],e[13]=t,t=e[11],e[11]=e[14],e[14]=t,this}setPosition(e,t,n){let i=this.elements;return e.isVector3?(i[12]=e.x,i[13]=e.y,i[14]=e.z):(i[12]=e,i[13]=t,i[14]=n),this}invert(){let e=this.elements,t=e[0],n=e[1],i=e[2],s=e[3],r=e[4],a=e[5],l=e[6],c=e[7],h=e[8],u=e[9],f=e[10],p=e[11],g=e[12],A=e[13],m=e[14],_=e[15],E=u*m*c-A*f*c+A*l*p-a*m*p-u*l*_+a*f*_,x=g*f*c-h*m*c-g*l*p+r*m*p+h*l*_-r*f*_,y=h*A*c-g*u*c+g*a*p-r*A*p-h*a*_+r*u*_,w=g*u*l-h*A*l-g*a*f+r*A*f+h*a*m-r*u*m,I=t*E+n*x+i*y+s*w;if(I===0)return this.set(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);let S=1/I;return e[0]=E*S,e[1]=(A*f*s-u*m*s-A*i*p+n*m*p+u*i*_-n*f*_)*S,e[2]=(a*m*s-A*l*s+A*i*c-n*m*c-a*i*_+n*l*_)*S,e[3]=(u*l*s-a*f*s-u*i*c+n*f*c+a*i*p-n*l*p)*S,e[4]=x*S,e[5]=(h*m*s-g*f*s+g*i*p-t*m*p-h*i*_+t*f*_)*S,e[6]=(g*l*s-r*m*s-g*i*c+t*m*c+r*i*_-t*l*_)*S,e[7]=(r*f*s-h*l*s+h*i*c-t*f*c-r*i*p+t*l*p)*S,e[8]=y*S,e[9]=(g*u*s-h*A*s-g*n*p+t*A*p+h*n*_-t*u*_)*S,e[10]=(r*A*s-g*a*s+g*n*c-t*A*c-r*n*_+t*a*_)*S,e[11]=(h*a*s-r*u*s-h*n*c+t*u*c+r*n*p-t*a*p)*S,e[12]=w*S,e[13]=(h*A*i-g*u*i+g*n*f-t*A*f-h*n*m+t*u*m)*S,e[14]=(g*a*i-r*A*i-g*n*l+t*A*l+r*n*m-t*a*m)*S,e[15]=(r*u*i-h*a*i+h*n*l-t*u*l-r*n*f+t*a*f)*S,this}scale(e){let t=this.elements,n=e.x,i=e.y,s=e.z;return t[0]*=n,t[4]*=i,t[8]*=s,t[1]*=n,t[5]*=i,t[9]*=s,t[2]*=n,t[6]*=i,t[10]*=s,t[3]*=n,t[7]*=i,t[11]*=s,this}getMaxScaleOnAxis(){let e=this.elements,t=e[0]*e[0]+e[1]*e[1]+e[2]*e[2],n=e[4]*e[4]+e[5]*e[5]+e[6]*e[6],i=e[8]*e[8]+e[9]*e[9]+e[10]*e[10];return Math.sqrt(Math.max(t,n,i))}makeTranslation(e,t,n){return this.set(1,0,0,e,0,1,0,t,0,0,1,n,0,0,0,1),this}makeRotationX(e){let t=Math.cos(e),n=Math.sin(e);return this.set(1,0,0,0,0,t,-n,0,0,n,t,0,0,0,0,1),this}makeRotationY(e){let t=Math.cos(e),n=Math.sin(e);return this.set(t,0,n,0,0,1,0,0,-n,0,t,0,0,0,0,1),this}makeRotationZ(e){let t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,0,n,t,0,0,0,0,1,0,0,0,0,1),this}makeRotationAxis(e,t){let n=Math.cos(t),i=Math.sin(t),s=1-n,r=e.x,a=e.y,l=e.z,c=s*r,h=s*a;return this.set(c*r+n,c*a-i*l,c*l+i*a,0,c*a+i*l,h*a+n,h*l-i*r,0,c*l-i*a,h*l+i*r,s*l*l+n,0,0,0,0,1),this}makeScale(e,t,n){return this.set(e,0,0,0,0,t,0,0,0,0,n,0,0,0,0,1),this}makeShear(e,t,n,i,s,r){return this.set(1,n,s,0,e,1,r,0,t,i,1,0,0,0,0,1),this}compose(e,t,n){let i=this.elements,s=t._x,r=t._y,a=t._z,l=t._w,c=s+s,h=r+r,u=a+a,f=s*c,p=s*h,g=s*u,A=r*h,m=r*u,_=a*u,E=l*c,x=l*h,y=l*u,w=n.x,I=n.y,S=n.z;return i[0]=(1-(A+_))*w,i[1]=(p+y)*w,i[2]=(g-x)*w,i[3]=0,i[4]=(p-y)*I,i[5]=(1-(f+_))*I,i[6]=(m+E)*I,i[7]=0,i[8]=(g+x)*S,i[9]=(m-E)*S,i[10]=(1-(f+A))*S,i[11]=0,i[12]=e.x,i[13]=e.y,i[14]=e.z,i[15]=1,this}decompose(e,t,n){let i=this.elements,s=ks.set(i[0],i[1],i[2]).length(),r=ks.set(i[4],i[5],i[6]).length(),a=ks.set(i[8],i[9],i[10]).length();this.determinant()<0&&(s=-s),e.x=i[12],e.y=i[13],e.z=i[14],Hn.copy(this);let c=1/s,h=1/r,u=1/a;return Hn.elements[0]*=c,Hn.elements[1]*=c,Hn.elements[2]*=c,Hn.elements[4]*=h,Hn.elements[5]*=h,Hn.elements[6]*=h,Hn.elements[8]*=u,Hn.elements[9]*=u,Hn.elements[10]*=u,t.setFromRotationMatrix(Hn),n.x=s,n.y=r,n.z=a,this}makePerspective(e,t,n,i,s,r){let a=this.elements,l=2*s/(t-e),c=2*s/(n-i),h=(t+e)/(t-e),u=(n+i)/(n-i),f=-(r+s)/(r-s),p=-2*r*s/(r-s);return a[0]=l,a[4]=0,a[8]=h,a[12]=0,a[1]=0,a[5]=c,a[9]=u,a[13]=0,a[2]=0,a[6]=0,a[10]=f,a[14]=p,a[3]=0,a[7]=0,a[11]=-1,a[15]=0,this}makeOrthographic(e,t,n,i,s,r){let a=this.elements,l=1/(t-e),c=1/(n-i),h=1/(r-s),u=(t+e)*l,f=(n+i)*c,p=(r+s)*h;return a[0]=2*l,a[4]=0,a[8]=0,a[12]=-u,a[1]=0,a[5]=2*c,a[9]=0,a[13]=-f,a[2]=0,a[6]=0,a[10]=-2*h,a[14]=-p,a[3]=0,a[7]=0,a[11]=0,a[15]=1,this}equals(e){let t=this.elements,n=e.elements;for(let i=0;i<16;i++)if(t[i]!==n[i])return!1;return!0}fromArray(e,t=0){for(let n=0;n<16;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){let n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e[t+9]=n[9],e[t+10]=n[10],e[t+11]=n[11],e[t+12]=n[12],e[t+13]=n[13],e[t+14]=n[14],e[t+15]=n[15],e}},ks=new B,Hn=new Ie,lx=new B(0,0,0),cx=new B(1,1,1),ki=new B,$a=new B,xn=new B,zp=new Ie,Vp=new Kt,Vi=class o{static{d(this,"Euler")}constructor(e=0,t=0,n=0,i=o.DEFAULT_ORDER){this.isEuler=!0,this._x=e,this._y=t,this._z=n,this._order=i}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get order(){return this._order}set order(e){this._order=e,this._onChangeCallback()}set(e,t,n,i=this._order){return this._x=e,this._y=t,this._z=n,this._order=i,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._order)}copy(e){return this._x=e._x,this._y=e._y,this._z=e._z,this._order=e._order,this._onChangeCallback(),this}setFromRotationMatrix(e,t=this._order,n=!0){let i=e.elements,s=i[0],r=i[4],a=i[8],l=i[1],c=i[5],h=i[9],u=i[2],f=i[6],p=i[10];switch(t){case"XYZ":this._y=Math.asin(Nt(a,-1,1)),Math.abs(a)<.9999999?(this._x=Math.atan2(-h,p),this._z=Math.atan2(-r,s)):(this._x=Math.atan2(f,c),this._z=0);break;case"YXZ":this._x=Math.asin(-Nt(h,-1,1)),Math.abs(h)<.9999999?(this._y=Math.atan2(a,p),this._z=Math.atan2(l,c)):(this._y=Math.atan2(-u,s),this._z=0);break;case"ZXY":this._x=Math.asin(Nt(f,-1,1)),Math.abs(f)<.9999999?(this._y=Math.atan2(-u,p),this._z=Math.atan2(-r,c)):(this._y=0,this._z=Math.atan2(l,s));break;case"ZYX":this._y=Math.asin(-Nt(u,-1,1)),Math.abs(u)<.9999999?(this._x=Math.atan2(f,p),this._z=Math.atan2(l,s)):(this._x=0,this._z=Math.atan2(-r,c));break;case"YZX":this._z=Math.asin(Nt(l,-1,1)),Math.abs(l)<.9999999?(this._x=Math.atan2(-h,c),this._y=Math.atan2(-u,s)):(this._x=0,this._y=Math.atan2(a,p));break;case"XZY":this._z=Math.asin(-Nt(r,-1,1)),Math.abs(r)<.9999999?(this._x=Math.atan2(f,c),this._y=Math.atan2(a,s)):(this._x=Math.atan2(-h,p),this._y=0);break;default:console.warn("THREE.Euler: .setFromRotationMatrix() encountered an unknown order: "+t)}return this._order=t,n===!0&&this._onChangeCallback(),this}setFromQuaternion(e,t,n){return zp.makeRotationFromQuaternion(e),this.setFromRotationMatrix(zp,t,n)}setFromVector3(e,t=this._order){return this.set(e.x,e.y,e.z,t)}reorder(e){return Vp.setFromEuler(this),this.setFromQuaternion(Vp,e)}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._order===this._order}fromArray(e){return this._x=e[0],this._y=e[1],this._z=e[2],e[3]!==void 0&&(this._order=e[3]),this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._order,e}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._order}};Vi.DEFAULT_ORDER="XYZ";var Lo=class{static{d(this,"Layers")}constructor(){this.mask=1}set(e){this.mask=(1<<e|0)>>>0}enable(e){this.mask|=1<<e|0}enableAll(){this.mask=-1}toggle(e){this.mask^=1<<e|0}disable(e){this.mask&=~(1<<e|0)}disableAll(){this.mask=0}test(e){return(this.mask&e.mask)!==0}isEnabled(e){return(this.mask&(1<<e|0))!==0}},hx=0,Hp=new B,Gs=new Kt,Ai=new Ie,Xa=new B,fo=new B,ux=new B,dx=new Kt,Wp=new B(1,0,0),qp=new B(0,1,0),Kp=new B(0,0,1),fx={type:"added"},$p={type:"removed"},Ze=class o extends Mt{static{d(this,"Object3D")}constructor(){super(),this.isObject3D=!0,Object.defineProperty(this,"id",{value:hx++}),this.uuid=Kn(),this.name="",this.type="Object3D",this.parent=null,this.children=[],this.up=o.DEFAULT_UP.clone();let e=new B,t=new Vi,n=new Kt,i=new B(1,1,1);function s(){n.setFromEuler(t,!1)}d(s,"onRotationChange");function r(){t.setFromQuaternion(n,void 0,!1)}d(r,"onQuaternionChange"),t._onChange(s),n._onChange(r),Object.defineProperties(this,{position:{configurable:!0,enumerable:!0,value:e},rotation:{configurable:!0,enumerable:!0,value:t},quaternion:{configurable:!0,enumerable:!0,value:n},scale:{configurable:!0,enumerable:!0,value:i},modelViewMatrix:{value:new Ie},normalMatrix:{value:new wt}}),this.matrix=new Ie,this.matrixWorld=new Ie,this.matrixAutoUpdate=o.DEFAULT_MATRIX_AUTO_UPDATE,this.matrixWorldNeedsUpdate=!1,this.matrixWorldAutoUpdate=o.DEFAULT_MATRIX_WORLD_AUTO_UPDATE,this.layers=new Lo,this.visible=!0,this.castShadow=!1,this.receiveShadow=!1,this.frustumCulled=!0,this.renderOrder=0,this.animations=[],this.userData={}}onBeforeRender(){}onAfterRender(){}applyMatrix4(e){this.matrixAutoUpdate&&this.updateMatrix(),this.matrix.premultiply(e),this.matrix.decompose(this.position,this.quaternion,this.scale)}applyQuaternion(e){return this.quaternion.premultiply(e),this}setRotationFromAxisAngle(e,t){this.quaternion.setFromAxisAngle(e,t)}setRotationFromEuler(e){this.quaternion.setFromEuler(e,!0)}setRotationFromMatrix(e){this.quaternion.setFromRotationMatrix(e)}setRotationFromQuaternion(e){this.quaternion.copy(e)}rotateOnAxis(e,t){return Gs.setFromAxisAngle(e,t),this.quaternion.multiply(Gs),this}rotateOnWorldAxis(e,t){return Gs.setFromAxisAngle(e,t),this.quaternion.premultiply(Gs),this}rotateX(e){return this.rotateOnAxis(Wp,e)}rotateY(e){return this.rotateOnAxis(qp,e)}rotateZ(e){return this.rotateOnAxis(Kp,e)}translateOnAxis(e,t){return Hp.copy(e).applyQuaternion(this.quaternion),this.position.add(Hp.multiplyScalar(t)),this}translateX(e){return this.translateOnAxis(Wp,e)}translateY(e){return this.translateOnAxis(qp,e)}translateZ(e){return this.translateOnAxis(Kp,e)}localToWorld(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(this.matrixWorld)}worldToLocal(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(Ai.copy(this.matrixWorld).invert())}lookAt(e,t,n){e.isVector3?Xa.copy(e):Xa.set(e,t,n);let i=this.parent;this.updateWorldMatrix(!0,!1),fo.setFromMatrixPosition(this.matrixWorld),this.isCamera||this.isLight?Ai.lookAt(fo,Xa,this.up):Ai.lookAt(Xa,fo,this.up),this.quaternion.setFromRotationMatrix(Ai),i&&(Ai.extractRotation(i.matrixWorld),Gs.setFromRotationMatrix(Ai),this.quaternion.premultiply(Gs.invert()))}add(e){if(arguments.length>1){for(let t=0;t<arguments.length;t++)this.add(arguments[t]);return this}return e===this?(console.error("THREE.Object3D.add: object can't be added as a child of itself.",e),this):(e&&e.isObject3D?(e.parent!==null&&e.parent.remove(e),e.parent=this,this.children.push(e),e.dispatchEvent(fx)):console.error("THREE.Object3D.add: object not an instance of THREE.Object3D.",e),this)}remove(e){if(arguments.length>1){for(let n=0;n<arguments.length;n++)this.remove(arguments[n]);return this}let t=this.children.indexOf(e);return t!==-1&&(e.parent=null,this.children.splice(t,1),e.dispatchEvent($p)),this}removeFromParent(){let e=this.parent;return e!==null&&e.remove(this),this}clear(){for(let e=0;e<this.children.length;e++){let t=this.children[e];t.parent=null,t.dispatchEvent($p)}return this.children.length=0,this}attach(e){return this.updateWorldMatrix(!0,!1),Ai.copy(this.matrixWorld).invert(),e.parent!==null&&(e.parent.updateWorldMatrix(!0,!1),Ai.multiply(e.parent.matrixWorld)),e.applyMatrix4(Ai),this.add(e),e.updateWorldMatrix(!1,!0),this}getObjectById(e){return this.getObjectByProperty("id",e)}getObjectByName(e){return this.getObjectByProperty("name",e)}getObjectByProperty(e,t){if(this[e]===t)return this;for(let n=0,i=this.children.length;n<i;n++){let r=this.children[n].getObjectByProperty(e,t);if(r!==void 0)return r}}getObjectsByProperty(e,t){let n=[];this[e]===t&&n.push(this);for(let i=0,s=this.children.length;i<s;i++){let r=this.children[i].getObjectsByProperty(e,t);r.length>0&&(n=n.concat(r))}return n}getWorldPosition(e){return this.updateWorldMatrix(!0,!1),e.setFromMatrixPosition(this.matrixWorld)}getWorldQuaternion(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(fo,e,ux),e}getWorldScale(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(fo,dx,e),e}getWorldDirection(e){this.updateWorldMatrix(!0,!1);let t=this.matrixWorld.elements;return e.set(t[8],t[9],t[10]).normalize()}raycast(){}traverse(e){e(this);let t=this.children;for(let n=0,i=t.length;n<i;n++)t[n].traverse(e)}traverseVisible(e){if(this.visible===!1)return;e(this);let t=this.children;for(let n=0,i=t.length;n<i;n++)t[n].traverseVisible(e)}traverseAncestors(e){let t=this.parent;t!==null&&(e(t),t.traverseAncestors(e))}updateMatrix(){this.matrix.compose(this.position,this.quaternion,this.scale),this.matrixWorldNeedsUpdate=!0}updateMatrixWorld(e){this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||e)&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix),this.matrixWorldNeedsUpdate=!1,e=!0);let t=this.children;for(let n=0,i=t.length;n<i;n++){let s=t[n];(s.matrixWorldAutoUpdate===!0||e===!0)&&s.updateMatrixWorld(e)}}updateWorldMatrix(e,t){let n=this.parent;if(e===!0&&n!==null&&n.matrixWorldAutoUpdate===!0&&n.updateWorldMatrix(!0,!1),this.matrixAutoUpdate&&this.updateMatrix(),this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix),t===!0){let i=this.children;for(let s=0,r=i.length;s<r;s++){let a=i[s];a.matrixWorldAutoUpdate===!0&&a.updateWorldMatrix(!1,!0)}}}toJSON(e){let t=e===void 0||typeof e=="string",n={};t&&(e={geometries:{},materials:{},textures:{},images:{},shapes:{},skeletons:{},animations:{},nodes:{}},n.metadata={version:4.5,type:"Object",generator:"Object3D.toJSON"});let i={};i.uuid=this.uuid,i.type=this.type,this.name!==""&&(i.name=this.name),this.castShadow===!0&&(i.castShadow=!0),this.receiveShadow===!0&&(i.receiveShadow=!0),this.visible===!1&&(i.visible=!1),this.frustumCulled===!1&&(i.frustumCulled=!1),this.renderOrder!==0&&(i.renderOrder=this.renderOrder),Object.keys(this.userData).length>0&&(i.userData=this.userData),i.layers=this.layers.mask,i.matrix=this.matrix.toArray(),this.matrixAutoUpdate===!1&&(i.matrixAutoUpdate=!1),this.isInstancedMesh&&(i.type="InstancedMesh",i.count=this.count,i.instanceMatrix=this.instanceMatrix.toJSON(),this.instanceColor!==null&&(i.instanceColor=this.instanceColor.toJSON()));function s(a,l){return a[l.uuid]===void 0&&(a[l.uuid]=l.toJSON(e)),l.uuid}if(d(s,"serialize"),this.isScene)this.background&&(this.background.isColor?i.background=this.background.toJSON():this.background.isTexture&&(i.background=this.background.toJSON(e).uuid)),this.environment&&this.environment.isTexture&&this.environment.isRenderTargetTexture!==!0&&(i.environment=this.environment.toJSON(e).uuid);else if(this.isMesh||this.isLine||this.isPoints){i.geometry=s(e.geometries,this.geometry);let a=this.geometry.parameters;if(a!==void 0&&a.shapes!==void 0){let l=a.shapes;if(Array.isArray(l))for(let c=0,h=l.length;c<h;c++){let u=l[c];s(e.shapes,u)}else s(e.shapes,l)}}if(this.isSkinnedMesh&&(i.bindMode=this.bindMode,i.bindMatrix=this.bindMatrix.toArray(),this.skeleton!==void 0&&(s(e.skeletons,this.skeleton),i.skeleton=this.skeleton.uuid)),this.material!==void 0)if(Array.isArray(this.material)){let a=[];for(let l=0,c=this.material.length;l<c;l++)a.push(s(e.materials,this.material[l]));i.material=a}else i.material=s(e.materials,this.material);if(this.children.length>0){i.children=[];for(let a=0;a<this.children.length;a++)i.children.push(this.children[a].toJSON(e).object)}if(this.animations.length>0){i.animations=[];for(let a=0;a<this.animations.length;a++){let l=this.animations[a];i.animations.push(s(e.animations,l))}}if(t){let a=r(e.geometries),l=r(e.materials),c=r(e.textures),h=r(e.images),u=r(e.shapes),f=r(e.skeletons),p=r(e.animations),g=r(e.nodes);a.length>0&&(n.geometries=a),l.length>0&&(n.materials=l),c.length>0&&(n.textures=c),h.length>0&&(n.images=h),u.length>0&&(n.shapes=u),f.length>0&&(n.skeletons=f),p.length>0&&(n.animations=p),g.length>0&&(n.nodes=g)}return n.object=i,n;function r(a){let l=[];for(let c in a){let h=a[c];delete h.metadata,l.push(h)}return l}d(r,"extractFromCache")}clone(e){return new this.constructor().copy(this,e)}copy(e,t=!0){if(this.name=e.name,this.up.copy(e.up),this.position.copy(e.position),this.rotation.order=e.rotation.order,this.quaternion.copy(e.quaternion),this.scale.copy(e.scale),this.matrix.copy(e.matrix),this.matrixWorld.copy(e.matrixWorld),this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrixWorldNeedsUpdate=e.matrixWorldNeedsUpdate,this.matrixWorldAutoUpdate=e.matrixWorldAutoUpdate,this.layers.mask=e.layers.mask,this.visible=e.visible,this.castShadow=e.castShadow,this.receiveShadow=e.receiveShadow,this.frustumCulled=e.frustumCulled,this.renderOrder=e.renderOrder,this.userData=JSON.parse(JSON.stringify(e.userData)),t===!0)for(let n=0;n<e.children.length;n++){let i=e.children[n];this.add(i.clone())}return this}};Ze.DEFAULT_UP=new B(0,1,0);Ze.DEFAULT_MATRIX_AUTO_UPDATE=!0;Ze.DEFAULT_MATRIX_WORLD_AUTO_UPDATE=!0;var Wn=new B,mi=new B,Dh=new B,gi=new B,zs=new B,Vs=new B,Xp=new B,Lh=new B,Ph=new B,Fh=new B,Ei=class o{static{d(this,"Triangle")}constructor(e=new B,t=new B,n=new B){this.a=e,this.b=t,this.c=n}static getNormal(e,t,n,i){i.subVectors(n,t),Wn.subVectors(e,t),i.cross(Wn);let s=i.lengthSq();return s>0?i.multiplyScalar(1/Math.sqrt(s)):i.set(0,0,0)}static getBarycoord(e,t,n,i,s){Wn.subVectors(i,t),mi.subVectors(n,t),Dh.subVectors(e,t);let r=Wn.dot(Wn),a=Wn.dot(mi),l=Wn.dot(Dh),c=mi.dot(mi),h=mi.dot(Dh),u=r*c-a*a;if(u===0)return s.set(-2,-1,-1);let f=1/u,p=(c*l-a*h)*f,g=(r*h-a*l)*f;return s.set(1-p-g,g,p)}static containsPoint(e,t,n,i){return this.getBarycoord(e,t,n,i,gi),gi.x>=0&&gi.y>=0&&gi.x+gi.y<=1}static getUV(e,t,n,i,s,r,a,l){return this.getBarycoord(e,t,n,i,gi),l.set(0,0),l.addScaledVector(s,gi.x),l.addScaledVector(r,gi.y),l.addScaledVector(a,gi.z),l}static isFrontFacing(e,t,n,i){return Wn.subVectors(n,t),mi.subVectors(e,t),Wn.cross(mi).dot(i)<0}set(e,t,n){return this.a.copy(e),this.b.copy(t),this.c.copy(n),this}setFromPointsAndIndices(e,t,n,i){return this.a.copy(e[t]),this.b.copy(e[n]),this.c.copy(e[i]),this}setFromAttributeAndIndices(e,t,n,i){return this.a.fromBufferAttribute(e,t),this.b.fromBufferAttribute(e,n),this.c.fromBufferAttribute(e,i),this}clone(){return new this.constructor().copy(this)}copy(e){return this.a.copy(e.a),this.b.copy(e.b),this.c.copy(e.c),this}getArea(){return Wn.subVectors(this.c,this.b),mi.subVectors(this.a,this.b),Wn.cross(mi).length()*.5}getMidpoint(e){return e.addVectors(this.a,this.b).add(this.c).multiplyScalar(1/3)}getNormal(e){return o.getNormal(this.a,this.b,this.c,e)}getPlane(e){return e.setFromCoplanarPoints(this.a,this.b,this.c)}getBarycoord(e,t){return o.getBarycoord(e,this.a,this.b,this.c,t)}getUV(e,t,n,i,s){return o.getUV(e,this.a,this.b,this.c,t,n,i,s)}containsPoint(e){return o.containsPoint(e,this.a,this.b,this.c)}isFrontFacing(e){return o.isFrontFacing(this.a,this.b,this.c,e)}intersectsBox(e){return e.intersectsTriangle(this)}closestPointToPoint(e,t){let n=this.a,i=this.b,s=this.c,r,a;zs.subVectors(i,n),Vs.subVectors(s,n),Lh.subVectors(e,n);let l=zs.dot(Lh),c=Vs.dot(Lh);if(l<=0&&c<=0)return t.copy(n);Ph.subVectors(e,i);let h=zs.dot(Ph),u=Vs.dot(Ph);if(h>=0&&u<=h)return t.copy(i);let f=l*u-h*c;if(f<=0&&l>=0&&h<=0)return r=l/(l-h),t.copy(n).addScaledVector(zs,r);Fh.subVectors(e,s);let p=zs.dot(Fh),g=Vs.dot(Fh);if(g>=0&&p<=g)return t.copy(s);let A=p*c-l*g;if(A<=0&&c>=0&&g<=0)return a=c/(c-g),t.copy(n).addScaledVector(Vs,a);let m=h*g-p*u;if(m<=0&&u-h>=0&&p-g>=0)return Xp.subVectors(s,i),a=(u-h)/(u-h+(p-g)),t.copy(i).addScaledVector(Xp,a);let _=1/(m+A+f);return r=A*_,a=f*_,t.copy(n).addScaledVector(zs,r).addScaledVector(Vs,a)}equals(e){return e.a.equals(this.a)&&e.b.equals(this.b)&&e.c.equals(this.c)}},px=0,sn=class extends Mt{static{d(this,"Material")}constructor(){super(),this.isMaterial=!0,Object.defineProperty(this,"id",{value:px++}),this.uuid=Kn(),this.name="",this.type="Material",this.blending=er,this.side=fn,this.vertexColors=!1,this.opacity=1,this.transparent=!1,this.blendSrc=UA,this.blendDst=QA,this.blendEquation=Ys,this.blendSrcAlpha=null,this.blendDstAlpha=null,this.blendEquationAlpha=null,this.depthFunc=Kh,this.depthTest=!0,this.depthWrite=!0,this.stencilWriteMask=255,this.stencilFunc=qy,this.stencilRef=0,this.stencilFuncMask=255,this.stencilFail=xh,this.stencilZFail=xh,this.stencilZPass=xh,this.stencilWrite=!1,this.clippingPlanes=null,this.clipIntersection=!1,this.clipShadows=!1,this.shadowSide=null,this.colorWrite=!0,this.precision=null,this.polygonOffset=!1,this.polygonOffsetFactor=0,this.polygonOffsetUnits=0,this.dithering=!1,this.alphaToCoverage=!1,this.premultipliedAlpha=!1,this.forceSinglePass=!1,this.visible=!0,this.toneMapped=!0,this.userData={},this.version=0,this._alphaTest=0}get alphaTest(){return this._alphaTest}set alphaTest(e){this._alphaTest>0!=e>0&&this.version++,this._alphaTest=e}onBuild(){}onBeforeRender(){}onBeforeCompile(){}customProgramCacheKey(){return this.onBeforeCompile.toString()}setValues(e){if(e!==void 0)for(let t in e){let n=e[t];if(n===void 0){console.warn("THREE.Material: '"+t+"' parameter is undefined.");continue}let i=this[t];if(i===void 0){console.warn("THREE."+this.type+": '"+t+"' is not a property of this material.");continue}i&&i.isColor?i.set(n):i&&i.isVector3&&n&&n.isVector3?i.copy(n):this[t]=n}}toJSON(e){let t=e===void 0||typeof e=="string";t&&(e={textures:{},images:{}});let n={metadata:{version:4.5,type:"Material",generator:"Material.toJSON"}};n.uuid=this.uuid,n.type=this.type,this.name!==""&&(n.name=this.name),this.color&&this.color.isColor&&(n.color=this.color.getHex()),this.roughness!==void 0&&(n.roughness=this.roughness),this.metalness!==void 0&&(n.metalness=this.metalness),this.sheen!==void 0&&(n.sheen=this.sheen),this.sheenColor&&this.sheenColor.isColor&&(n.sheenColor=this.sheenColor.getHex()),this.sheenRoughness!==void 0&&(n.sheenRoughness=this.sheenRoughness),this.emissive&&this.emissive.isColor&&(n.emissive=this.emissive.getHex()),this.emissiveIntensity&&this.emissiveIntensity!==1&&(n.emissiveIntensity=this.emissiveIntensity),this.specular&&this.specular.isColor&&(n.specular=this.specular.getHex()),this.specularIntensity!==void 0&&(n.specularIntensity=this.specularIntensity),this.specularColor&&this.specularColor.isColor&&(n.specularColor=this.specularColor.getHex()),this.shininess!==void 0&&(n.shininess=this.shininess),this.clearcoat!==void 0&&(n.clearcoat=this.clearcoat),this.clearcoatRoughness!==void 0&&(n.clearcoatRoughness=this.clearcoatRoughness),this.clearcoatMap&&this.clearcoatMap.isTexture&&(n.clearcoatMap=this.clearcoatMap.toJSON(e).uuid),this.clearcoatRoughnessMap&&this.clearcoatRoughnessMap.isTexture&&(n.clearcoatRoughnessMap=this.clearcoatRoughnessMap.toJSON(e).uuid),this.clearcoatNormalMap&&this.clearcoatNormalMap.isTexture&&(n.clearcoatNormalMap=this.clearcoatNormalMap.toJSON(e).uuid,n.clearcoatNormalScale=this.clearcoatNormalScale.toArray()),this.iridescence!==void 0&&(n.iridescence=this.iridescence),this.iridescenceIOR!==void 0&&(n.iridescenceIOR=this.iridescenceIOR),this.iridescenceThicknessRange!==void 0&&(n.iridescenceThicknessRange=this.iridescenceThicknessRange),this.iridescenceMap&&this.iridescenceMap.isTexture&&(n.iridescenceMap=this.iridescenceMap.toJSON(e).uuid),this.iridescenceThicknessMap&&this.iridescenceThicknessMap.isTexture&&(n.iridescenceThicknessMap=this.iridescenceThicknessMap.toJSON(e).uuid),this.map&&this.map.isTexture&&(n.map=this.map.toJSON(e).uuid),this.matcap&&this.matcap.isTexture&&(n.matcap=this.matcap.toJSON(e).uuid),this.alphaMap&&this.alphaMap.isTexture&&(n.alphaMap=this.alphaMap.toJSON(e).uuid),this.lightMap&&this.lightMap.isTexture&&(n.lightMap=this.lightMap.toJSON(e).uuid,n.lightMapIntensity=this.lightMapIntensity),this.aoMap&&this.aoMap.isTexture&&(n.aoMap=this.aoMap.toJSON(e).uuid,n.aoMapIntensity=this.aoMapIntensity),this.bumpMap&&this.bumpMap.isTexture&&(n.bumpMap=this.bumpMap.toJSON(e).uuid,n.bumpScale=this.bumpScale),this.normalMap&&this.normalMap.isTexture&&(n.normalMap=this.normalMap.toJSON(e).uuid,n.normalMapType=this.normalMapType,n.normalScale=this.normalScale.toArray()),this.displacementMap&&this.displacementMap.isTexture&&(n.displacementMap=this.displacementMap.toJSON(e).uuid,n.displacementScale=this.displacementScale,n.displacementBias=this.displacementBias),this.roughnessMap&&this.roughnessMap.isTexture&&(n.roughnessMap=this.roughnessMap.toJSON(e).uuid),this.metalnessMap&&this.metalnessMap.isTexture&&(n.metalnessMap=this.metalnessMap.toJSON(e).uuid),this.emissiveMap&&this.emissiveMap.isTexture&&(n.emissiveMap=this.emissiveMap.toJSON(e).uuid),this.specularMap&&this.specularMap.isTexture&&(n.specularMap=this.specularMap.toJSON(e).uuid),this.specularIntensityMap&&this.specularIntensityMap.isTexture&&(n.specularIntensityMap=this.specularIntensityMap.toJSON(e).uuid),this.specularColorMap&&this.specularColorMap.isTexture&&(n.specularColorMap=this.specularColorMap.toJSON(e).uuid),this.envMap&&this.envMap.isTexture&&(n.envMap=this.envMap.toJSON(e).uuid,this.combine!==void 0&&(n.combine=this.combine)),this.envMapIntensity!==void 0&&(n.envMapIntensity=this.envMapIntensity),this.reflectivity!==void 0&&(n.reflectivity=this.reflectivity),this.refractionRatio!==void 0&&(n.refractionRatio=this.refractionRatio),this.gradientMap&&this.gradientMap.isTexture&&(n.gradientMap=this.gradientMap.toJSON(e).uuid),this.transmission!==void 0&&(n.transmission=this.transmission),this.transmissionMap&&this.transmissionMap.isTexture&&(n.transmissionMap=this.transmissionMap.toJSON(e).uuid),this.thickness!==void 0&&(n.thickness=this.thickness),this.thicknessMap&&this.thicknessMap.isTexture&&(n.thicknessMap=this.thicknessMap.toJSON(e).uuid),this.attenuationDistance!==void 0&&this.attenuationDistance!==1/0&&(n.attenuationDistance=this.attenuationDistance),this.attenuationColor!==void 0&&(n.attenuationColor=this.attenuationColor.getHex()),this.size!==void 0&&(n.size=this.size),this.shadowSide!==null&&(n.shadowSide=this.shadowSide),this.sizeAttenuation!==void 0&&(n.sizeAttenuation=this.sizeAttenuation),this.blending!==er&&(n.blending=this.blending),this.side!==fn&&(n.side=this.side),this.vertexColors&&(n.vertexColors=!0),this.opacity<1&&(n.opacity=this.opacity),this.transparent===!0&&(n.transparent=this.transparent),n.depthFunc=this.depthFunc,n.depthTest=this.depthTest,n.depthWrite=this.depthWrite,n.colorWrite=this.colorWrite,n.stencilWrite=this.stencilWrite,n.stencilWriteMask=this.stencilWriteMask,n.stencilFunc=this.stencilFunc,n.stencilRef=this.stencilRef,n.stencilFuncMask=this.stencilFuncMask,n.stencilFail=this.stencilFail,n.stencilZFail=this.stencilZFail,n.stencilZPass=this.stencilZPass,this.rotation!==void 0&&this.rotation!==0&&(n.rotation=this.rotation),this.polygonOffset===!0&&(n.polygonOffset=!0),this.polygonOffsetFactor!==0&&(n.polygonOffsetFactor=this.polygonOffsetFactor),this.polygonOffsetUnits!==0&&(n.polygonOffsetUnits=this.polygonOffsetUnits),this.linewidth!==void 0&&this.linewidth!==1&&(n.linewidth=this.linewidth),this.dashSize!==void 0&&(n.dashSize=this.dashSize),this.gapSize!==void 0&&(n.gapSize=this.gapSize),this.scale!==void 0&&(n.scale=this.scale),this.dithering===!0&&(n.dithering=!0),this.alphaTest>0&&(n.alphaTest=this.alphaTest),this.alphaToCoverage===!0&&(n.alphaToCoverage=this.alphaToCoverage),this.premultipliedAlpha===!0&&(n.premultipliedAlpha=this.premultipliedAlpha),this.forceSinglePass===!0&&(n.forceSinglePass=this.forceSinglePass),this.wireframe===!0&&(n.wireframe=this.wireframe),this.wireframeLinewidth>1&&(n.wireframeLinewidth=this.wireframeLinewidth),this.wireframeLinecap!=="round"&&(n.wireframeLinecap=this.wireframeLinecap),this.wireframeLinejoin!=="round"&&(n.wireframeLinejoin=this.wireframeLinejoin),this.flatShading===!0&&(n.flatShading=this.flatShading),this.visible===!1&&(n.visible=!1),this.toneMapped===!1&&(n.toneMapped=!1),this.fog===!1&&(n.fog=!1),Object.keys(this.userData).length>0&&(n.userData=this.userData);function i(s){let r=[];for(let a in s){let l=s[a];delete l.metadata,r.push(l)}return r}if(d(i,"extractFromCache"),t){let s=i(e.textures),r=i(e.images);s.length>0&&(n.textures=s),r.length>0&&(n.images=r)}return n}clone(){return new this.constructor().copy(this)}copy(e){this.name=e.name,this.blending=e.blending,this.side=e.side,this.vertexColors=e.vertexColors,this.opacity=e.opacity,this.transparent=e.transparent,this.blendSrc=e.blendSrc,this.blendDst=e.blendDst,this.blendEquation=e.blendEquation,this.blendSrcAlpha=e.blendSrcAlpha,this.blendDstAlpha=e.blendDstAlpha,this.blendEquationAlpha=e.blendEquationAlpha,this.depthFunc=e.depthFunc,this.depthTest=e.depthTest,this.depthWrite=e.depthWrite,this.stencilWriteMask=e.stencilWriteMask,this.stencilFunc=e.stencilFunc,this.stencilRef=e.stencilRef,this.stencilFuncMask=e.stencilFuncMask,this.stencilFail=e.stencilFail,this.stencilZFail=e.stencilZFail,this.stencilZPass=e.stencilZPass,this.stencilWrite=e.stencilWrite;let t=e.clippingPlanes,n=null;if(t!==null){let i=t.length;n=new Array(i);for(let s=0;s!==i;++s)n[s]=t[s].clone()}return this.clippingPlanes=n,this.clipIntersection=e.clipIntersection,this.clipShadows=e.clipShadows,this.shadowSide=e.shadowSide,this.colorWrite=e.colorWrite,this.precision=e.precision,this.polygonOffset=e.polygonOffset,this.polygonOffsetFactor=e.polygonOffsetFactor,this.polygonOffsetUnits=e.polygonOffsetUnits,this.dithering=e.dithering,this.alphaTest=e.alphaTest,this.alphaToCoverage=e.alphaToCoverage,this.premultipliedAlpha=e.premultipliedAlpha,this.forceSinglePass=e.forceSinglePass,this.visible=e.visible,this.toneMapped=e.toneMapped,this.userData=JSON.parse(JSON.stringify(e.userData)),this}dispose(){this.dispatchEvent({type:"dispose"})}set needsUpdate(e){e===!0&&this.version++}},Ft=class extends sn{static{d(this,"MeshBasicMaterial")}constructor(e){super(),this.isMeshBasicMaterial=!0,this.type="MeshBasicMaterial",this.color=new Me(16777215),this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.specularMap=null,this.alphaMap=null,this.envMap=null,this.combine=kA,this.reflectivity=1,this.refractionRatio=.98,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.specularMap=e.specularMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.combine=e.combine,this.reflectivity=e.reflectivity,this.refractionRatio=e.refractionRatio,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.fog=e.fog,this}},gt=new B,Ya=new Be,je=class{static{d(this,"BufferAttribute")}constructor(e,t,n=!1){if(Array.isArray(e))throw new TypeError("THREE.BufferAttribute: array should be a Typed Array.");this.isBufferAttribute=!0,this.name="",this.array=e,this.itemSize=t,this.count=e!==void 0?e.length/t:0,this.normalized=n,this.usage=Xh,this.updateRange={offset:0,count:-1},this.version=0}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}setUsage(e){return this.usage=e,this}copy(e){return this.name=e.name,this.array=new e.array.constructor(e.array),this.itemSize=e.itemSize,this.count=e.count,this.normalized=e.normalized,this.usage=e.usage,this}copyAt(e,t,n){e*=this.itemSize,n*=t.itemSize;for(let i=0,s=this.itemSize;i<s;i++)this.array[e+i]=t.array[n+i];return this}copyArray(e){return this.array.set(e),this}applyMatrix3(e){if(this.itemSize===2)for(let t=0,n=this.count;t<n;t++)Ya.fromBufferAttribute(this,t),Ya.applyMatrix3(e),this.setXY(t,Ya.x,Ya.y);else if(this.itemSize===3)for(let t=0,n=this.count;t<n;t++)gt.fromBufferAttribute(this,t),gt.applyMatrix3(e),this.setXYZ(t,gt.x,gt.y,gt.z);return this}applyMatrix4(e){for(let t=0,n=this.count;t<n;t++)gt.fromBufferAttribute(this,t),gt.applyMatrix4(e),this.setXYZ(t,gt.x,gt.y,gt.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)gt.fromBufferAttribute(this,t),gt.applyNormalMatrix(e),this.setXYZ(t,gt.x,gt.y,gt.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)gt.fromBufferAttribute(this,t),gt.transformDirection(e),this.setXYZ(t,gt.x,gt.y,gt.z);return this}set(e,t=0){return this.array.set(e,t),this}getX(e){let t=this.array[e*this.itemSize];return this.normalized&&(t=vi(t,this.array)),t}setX(e,t){return this.normalized&&(t=tt(t,this.array)),this.array[e*this.itemSize]=t,this}getY(e){let t=this.array[e*this.itemSize+1];return this.normalized&&(t=vi(t,this.array)),t}setY(e,t){return this.normalized&&(t=tt(t,this.array)),this.array[e*this.itemSize+1]=t,this}getZ(e){let t=this.array[e*this.itemSize+2];return this.normalized&&(t=vi(t,this.array)),t}setZ(e,t){return this.normalized&&(t=tt(t,this.array)),this.array[e*this.itemSize+2]=t,this}getW(e){let t=this.array[e*this.itemSize+3];return this.normalized&&(t=vi(t,this.array)),t}setW(e,t){return this.normalized&&(t=tt(t,this.array)),this.array[e*this.itemSize+3]=t,this}setXY(e,t,n){return e*=this.itemSize,this.normalized&&(t=tt(t,this.array),n=tt(n,this.array)),this.array[e+0]=t,this.array[e+1]=n,this}setXYZ(e,t,n,i){return e*=this.itemSize,this.normalized&&(t=tt(t,this.array),n=tt(n,this.array),i=tt(i,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=i,this}setXYZW(e,t,n,i,s){return e*=this.itemSize,this.normalized&&(t=tt(t,this.array),n=tt(n,this.array),i=tt(i,this.array),s=tt(s,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=i,this.array[e+3]=s,this}onUpload(e){return this.onUploadCallback=e,this}clone(){return new this.constructor(this.array,this.itemSize).copy(this)}toJSON(){let e={itemSize:this.itemSize,type:this.array.constructor.name,array:Array.from(this.array),normalized:this.normalized};return this.name!==""&&(e.name=this.name),this.usage!==Xh&&(e.usage=this.usage),(this.updateRange.offset!==0||this.updateRange.count!==-1)&&(e.updateRange=this.updateRange),e}copyColorsArray(){console.error("THREE.BufferAttribute: copyColorsArray() was removed in r144.")}copyVector2sArray(){console.error("THREE.BufferAttribute: copyVector2sArray() was removed in r144.")}copyVector3sArray(){console.error("THREE.BufferAttribute: copyVector3sArray() was removed in r144.")}copyVector4sArray(){console.error("THREE.BufferAttribute: copyVector4sArray() was removed in r144.")}};var vl=class extends je{static{d(this,"Uint16BufferAttribute")}constructor(e,t,n){super(new Uint16Array(e),t,n)}};var El=class extends je{static{d(this,"Uint32BufferAttribute")}constructor(e,t,n){super(new Uint32Array(e),t,n)}};var dn=class extends je{static{d(this,"Float32BufferAttribute")}constructor(e,t,n){super(new Float32Array(e),t,n)}};var Ax=0,Ln=new Ie,Oh=new Ze,Hs=new B,vn=new Qt,po=new Qt,Dt=new B,kt=class o extends Mt{static{d(this,"BufferGeometry")}constructor(){super(),this.isBufferGeometry=!0,Object.defineProperty(this,"id",{value:Ax++}),this.uuid=Kn(),this.name="",this.type="BufferGeometry",this.index=null,this.attributes={},this.morphAttributes={},this.morphTargetsRelative=!1,this.groups=[],this.boundingBox=null,this.boundingSphere=null,this.drawRange={start:0,count:1/0},this.userData={}}getIndex(){return this.index}setIndex(e){return Array.isArray(e)?this.index=new(qA(e)?El:vl)(e,1):this.index=e,this}getAttribute(e){return this.attributes[e]}setAttribute(e,t){return this.attributes[e]=t,this}deleteAttribute(e){return delete this.attributes[e],this}hasAttribute(e){return this.attributes[e]!==void 0}addGroup(e,t,n=0){this.groups.push({start:e,count:t,materialIndex:n})}clearGroups(){this.groups=[]}setDrawRange(e,t){this.drawRange.start=e,this.drawRange.count=t}applyMatrix4(e){let t=this.attributes.position;t!==void 0&&(t.applyMatrix4(e),t.needsUpdate=!0);let n=this.attributes.normal;if(n!==void 0){let s=new wt().getNormalMatrix(e);n.applyNormalMatrix(s),n.needsUpdate=!0}let i=this.attributes.tangent;return i!==void 0&&(i.transformDirection(e),i.needsUpdate=!0),this.boundingBox!==null&&this.computeBoundingBox(),this.boundingSphere!==null&&this.computeBoundingSphere(),this}applyQuaternion(e){return Ln.makeRotationFromQuaternion(e),this.applyMatrix4(Ln),this}rotateX(e){return Ln.makeRotationX(e),this.applyMatrix4(Ln),this}rotateY(e){return Ln.makeRotationY(e),this.applyMatrix4(Ln),this}rotateZ(e){return Ln.makeRotationZ(e),this.applyMatrix4(Ln),this}translate(e,t,n){return Ln.makeTranslation(e,t,n),this.applyMatrix4(Ln),this}scale(e,t,n){return Ln.makeScale(e,t,n),this.applyMatrix4(Ln),this}lookAt(e){return Oh.lookAt(e),Oh.updateMatrix(),this.applyMatrix4(Oh.matrix),this}center(){return this.computeBoundingBox(),this.boundingBox.getCenter(Hs).negate(),this.translate(Hs.x,Hs.y,Hs.z),this}setFromPoints(e){let t=[];for(let n=0,i=e.length;n<i;n++){let s=e[n];t.push(s.x,s.y,s.z||0)}return this.setAttribute("position",new dn(t,3)),this}computeBoundingBox(){this.boundingBox===null&&(this.boundingBox=new Qt);let e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error('THREE.BufferGeometry.computeBoundingBox(): GLBufferAttribute requires a manual bounding box. Alternatively set "mesh.frustumCulled" to "false".',this),this.boundingBox.set(new B(-1/0,-1/0,-1/0),new B(1/0,1/0,1/0));return}if(e!==void 0){if(this.boundingBox.setFromBufferAttribute(e),t)for(let n=0,i=t.length;n<i;n++){let s=t[n];vn.setFromBufferAttribute(s),this.morphTargetsRelative?(Dt.addVectors(this.boundingBox.min,vn.min),this.boundingBox.expandByPoint(Dt),Dt.addVectors(this.boundingBox.max,vn.max),this.boundingBox.expandByPoint(Dt)):(this.boundingBox.expandByPoint(vn.min),this.boundingBox.expandByPoint(vn.max))}}else this.boundingBox.makeEmpty();(isNaN(this.boundingBox.min.x)||isNaN(this.boundingBox.min.y)||isNaN(this.boundingBox.min.z))&&console.error('THREE.BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. The "position" attribute is likely to have NaN values.',this)}computeBoundingSphere(){this.boundingSphere===null&&(this.boundingSphere=new Mn);let e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error('THREE.BufferGeometry.computeBoundingSphere(): GLBufferAttribute requires a manual bounding sphere. Alternatively set "mesh.frustumCulled" to "false".',this),this.boundingSphere.set(new B,1/0);return}if(e){let n=this.boundingSphere.center;if(vn.setFromBufferAttribute(e),t)for(let s=0,r=t.length;s<r;s++){let a=t[s];po.setFromBufferAttribute(a),this.morphTargetsRelative?(Dt.addVectors(vn.min,po.min),vn.expandByPoint(Dt),Dt.addVectors(vn.max,po.max),vn.expandByPoint(Dt)):(vn.expandByPoint(po.min),vn.expandByPoint(po.max))}vn.getCenter(n);let i=0;for(let s=0,r=e.count;s<r;s++)Dt.fromBufferAttribute(e,s),i=Math.max(i,n.distanceToSquared(Dt));if(t)for(let s=0,r=t.length;s<r;s++){let a=t[s],l=this.morphTargetsRelative;for(let c=0,h=a.count;c<h;c++)Dt.fromBufferAttribute(a,c),l&&(Hs.fromBufferAttribute(e,c),Dt.add(Hs)),i=Math.max(i,n.distanceToSquared(Dt))}this.boundingSphere.radius=Math.sqrt(i),isNaN(this.boundingSphere.radius)&&console.error('THREE.BufferGeometry.computeBoundingSphere(): Computed radius is NaN. The "position" attribute is likely to have NaN values.',this)}}computeTangents(){let e=this.index,t=this.attributes;if(e===null||t.position===void 0||t.normal===void 0||t.uv===void 0){console.error("THREE.BufferGeometry: .computeTangents() failed. Missing required attributes (index, position, normal or uv)");return}let n=e.array,i=t.position.array,s=t.normal.array,r=t.uv.array,a=i.length/3;this.hasAttribute("tangent")===!1&&this.setAttribute("tangent",new je(new Float32Array(4*a),4));let l=this.getAttribute("tangent").array,c=[],h=[];for(let R=0;R<a;R++)c[R]=new B,h[R]=new B;let u=new B,f=new B,p=new B,g=new Be,A=new Be,m=new Be,_=new B,E=new B;function x(R,N,z){u.fromArray(i,R*3),f.fromArray(i,N*3),p.fromArray(i,z*3),g.fromArray(r,R*2),A.fromArray(r,N*2),m.fromArray(r,z*2),f.sub(u),p.sub(u),A.sub(g),m.sub(g);let O=1/(A.x*m.y-m.x*A.y);isFinite(O)&&(_.copy(f).multiplyScalar(m.y).addScaledVector(p,-A.y).multiplyScalar(O),E.copy(p).multiplyScalar(A.x).addScaledVector(f,-m.x).multiplyScalar(O),c[R].add(_),c[N].add(_),c[z].add(_),h[R].add(E),h[N].add(E),h[z].add(E))}d(x,"handleTriangle");let y=this.groups;y.length===0&&(y=[{start:0,count:n.length}]);for(let R=0,N=y.length;R<N;++R){let z=y[R],O=z.start,D=z.count;for(let Q=O,q=O+D;Q<q;Q+=3)x(n[Q+0],n[Q+1],n[Q+2])}let w=new B,I=new B,S=new B,v=new B;function b(R){S.fromArray(s,R*3),v.copy(S);let N=c[R];w.copy(N),w.sub(S.multiplyScalar(S.dot(N))).normalize(),I.crossVectors(v,N);let O=I.dot(h[R])<0?-1:1;l[R*4]=w.x,l[R*4+1]=w.y,l[R*4+2]=w.z,l[R*4+3]=O}d(b,"handleVertex");for(let R=0,N=y.length;R<N;++R){let z=y[R],O=z.start,D=z.count;for(let Q=O,q=O+D;Q<q;Q+=3)b(n[Q+0]),b(n[Q+1]),b(n[Q+2])}}computeVertexNormals(){let e=this.index,t=this.getAttribute("position");if(t!==void 0){let n=this.getAttribute("normal");if(n===void 0)n=new je(new Float32Array(t.count*3),3),this.setAttribute("normal",n);else for(let f=0,p=n.count;f<p;f++)n.setXYZ(f,0,0,0);let i=new B,s=new B,r=new B,a=new B,l=new B,c=new B,h=new B,u=new B;if(e)for(let f=0,p=e.count;f<p;f+=3){let g=e.getX(f+0),A=e.getX(f+1),m=e.getX(f+2);i.fromBufferAttribute(t,g),s.fromBufferAttribute(t,A),r.fromBufferAttribute(t,m),h.subVectors(r,s),u.subVectors(i,s),h.cross(u),a.fromBufferAttribute(n,g),l.fromBufferAttribute(n,A),c.fromBufferAttribute(n,m),a.add(h),l.add(h),c.add(h),n.setXYZ(g,a.x,a.y,a.z),n.setXYZ(A,l.x,l.y,l.z),n.setXYZ(m,c.x,c.y,c.z)}else for(let f=0,p=t.count;f<p;f+=3)i.fromBufferAttribute(t,f+0),s.fromBufferAttribute(t,f+1),r.fromBufferAttribute(t,f+2),h.subVectors(r,s),u.subVectors(i,s),h.cross(u),n.setXYZ(f+0,h.x,h.y,h.z),n.setXYZ(f+1,h.x,h.y,h.z),n.setXYZ(f+2,h.x,h.y,h.z);this.normalizeNormals(),n.needsUpdate=!0}}merge(){return console.error("THREE.BufferGeometry.merge() has been removed. Use THREE.BufferGeometryUtils.mergeBufferGeometries() instead."),this}normalizeNormals(){let e=this.attributes.normal;for(let t=0,n=e.count;t<n;t++)Dt.fromBufferAttribute(e,t),Dt.normalize(),e.setXYZ(t,Dt.x,Dt.y,Dt.z)}toNonIndexed(){function e(a,l){let c=a.array,h=a.itemSize,u=a.normalized,f=new c.constructor(l.length*h),p=0,g=0;for(let A=0,m=l.length;A<m;A++){a.isInterleavedBufferAttribute?p=l[A]*a.data.stride+a.offset:p=l[A]*h;for(let _=0;_<h;_++)f[g++]=c[p++]}return new je(f,h,u)}if(d(e,"convertBufferAttribute"),this.index===null)return console.warn("THREE.BufferGeometry.toNonIndexed(): BufferGeometry is already non-indexed."),this;let t=new o,n=this.index.array,i=this.attributes;for(let a in i){let l=i[a],c=e(l,n);t.setAttribute(a,c)}let s=this.morphAttributes;for(let a in s){let l=[],c=s[a];for(let h=0,u=c.length;h<u;h++){let f=c[h],p=e(f,n);l.push(p)}t.morphAttributes[a]=l}t.morphTargetsRelative=this.morphTargetsRelative;let r=this.groups;for(let a=0,l=r.length;a<l;a++){let c=r[a];t.addGroup(c.start,c.count,c.materialIndex)}return t}toJSON(){let e={metadata:{version:4.5,type:"BufferGeometry",generator:"BufferGeometry.toJSON"}};if(e.uuid=this.uuid,e.type=this.type,this.name!==""&&(e.name=this.name),Object.keys(this.userData).length>0&&(e.userData=this.userData),this.parameters!==void 0){let l=this.parameters;for(let c in l)l[c]!==void 0&&(e[c]=l[c]);return e}e.data={attributes:{}};let t=this.index;t!==null&&(e.data.index={type:t.array.constructor.name,array:Array.prototype.slice.call(t.array)});let n=this.attributes;for(let l in n){let c=n[l];e.data.attributes[l]=c.toJSON(e.data)}let i={},s=!1;for(let l in this.morphAttributes){let c=this.morphAttributes[l],h=[];for(let u=0,f=c.length;u<f;u++){let p=c[u];h.push(p.toJSON(e.data))}h.length>0&&(i[l]=h,s=!0)}s&&(e.data.morphAttributes=i,e.data.morphTargetsRelative=this.morphTargetsRelative);let r=this.groups;r.length>0&&(e.data.groups=JSON.parse(JSON.stringify(r)));let a=this.boundingSphere;return a!==null&&(e.data.boundingSphere={center:a.center.toArray(),radius:a.radius}),e}clone(){return new this.constructor().copy(this)}copy(e){this.index=null,this.attributes={},this.morphAttributes={},this.groups=[],this.boundingBox=null,this.boundingSphere=null;let t={};this.name=e.name;let n=e.index;n!==null&&this.setIndex(n.clone(t));let i=e.attributes;for(let c in i){let h=i[c];this.setAttribute(c,h.clone(t))}let s=e.morphAttributes;for(let c in s){let h=[],u=s[c];for(let f=0,p=u.length;f<p;f++)h.push(u[f].clone(t));this.morphAttributes[c]=h}this.morphTargetsRelative=e.morphTargetsRelative;let r=e.groups;for(let c=0,h=r.length;c<h;c++){let u=r[c];this.addGroup(u.start,u.count,u.materialIndex)}let a=e.boundingBox;a!==null&&(this.boundingBox=a.clone());let l=e.boundingSphere;return l!==null&&(this.boundingSphere=l.clone()),this.drawRange.start=e.drawRange.start,this.drawRange.count=e.drawRange.count,this.userData=e.userData,e.parameters!==void 0&&(this.parameters=Object.assign({},e.parameters)),this}dispose(){this.dispatchEvent({type:"dispose"})}},Yp=new Ie,Ws=new lr,Nh=new Mn,Ao=new B,mo=new B,go=new B,Uh=new B,Ja=new B,ja=new Be,Za=new Be,el=new Be,Qh=new B,tl=new B,pe=class extends Ze{static{d(this,"Mesh")}constructor(e=new kt,t=new Ft){super(),this.isMesh=!0,this.type="Mesh",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),e.morphTargetInfluences!==void 0&&(this.morphTargetInfluences=e.morphTargetInfluences.slice()),e.morphTargetDictionary!==void 0&&(this.morphTargetDictionary=Object.assign({},e.morphTargetDictionary)),this.material=e.material,this.geometry=e.geometry,this}updateMorphTargets(){let t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){let i=t[n[0]];if(i!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let s=0,r=i.length;s<r;s++){let a=i[s].name||String(s);this.morphTargetInfluences.push(0),this.morphTargetDictionary[a]=s}}}}getVertexPosition(e,t){let n=this.geometry,i=n.attributes.position,s=n.morphAttributes.position,r=n.morphTargetsRelative;t.fromBufferAttribute(i,e);let a=this.morphTargetInfluences;if(s&&a){Ja.set(0,0,0);for(let l=0,c=s.length;l<c;l++){let h=a[l],u=s[l];h!==0&&(Uh.fromBufferAttribute(u,e),r?Ja.addScaledVector(Uh,h):Ja.addScaledVector(Uh.sub(t),h))}t.add(Ja)}return this.isSkinnedMesh&&this.boneTransform(e,t),t}raycast(e,t){let n=this.geometry,i=this.material,s=this.matrixWorld;if(i===void 0||(n.boundingSphere===null&&n.computeBoundingSphere(),Nh.copy(n.boundingSphere),Nh.applyMatrix4(s),e.ray.intersectsSphere(Nh)===!1)||(Yp.copy(s).invert(),Ws.copy(e.ray).applyMatrix4(Yp),n.boundingBox!==null&&Ws.intersectsBox(n.boundingBox)===!1))return;let r,a=n.index,l=n.attributes.position,c=n.attributes.uv,h=n.attributes.uv2,u=n.groups,f=n.drawRange;if(a!==null)if(Array.isArray(i))for(let p=0,g=u.length;p<g;p++){let A=u[p],m=i[A.materialIndex],_=Math.max(A.start,f.start),E=Math.min(a.count,Math.min(A.start+A.count,f.start+f.count));for(let x=_,y=E;x<y;x+=3){let w=a.getX(x),I=a.getX(x+1),S=a.getX(x+2);r=nl(this,m,e,Ws,c,h,w,I,S),r&&(r.faceIndex=Math.floor(x/3),r.face.materialIndex=A.materialIndex,t.push(r))}}else{let p=Math.max(0,f.start),g=Math.min(a.count,f.start+f.count);for(let A=p,m=g;A<m;A+=3){let _=a.getX(A),E=a.getX(A+1),x=a.getX(A+2);r=nl(this,i,e,Ws,c,h,_,E,x),r&&(r.faceIndex=Math.floor(A/3),t.push(r))}}else if(l!==void 0)if(Array.isArray(i))for(let p=0,g=u.length;p<g;p++){let A=u[p],m=i[A.materialIndex],_=Math.max(A.start,f.start),E=Math.min(l.count,Math.min(A.start+A.count,f.start+f.count));for(let x=_,y=E;x<y;x+=3){let w=x,I=x+1,S=x+2;r=nl(this,m,e,Ws,c,h,w,I,S),r&&(r.faceIndex=Math.floor(x/3),r.face.materialIndex=A.materialIndex,t.push(r))}}else{let p=Math.max(0,f.start),g=Math.min(l.count,f.start+f.count);for(let A=p,m=g;A<m;A+=3){let _=A,E=A+1,x=A+2;r=nl(this,i,e,Ws,c,h,_,E,x),r&&(r.faceIndex=Math.floor(A/3),t.push(r))}}}};function mx(o,e,t,n,i,s,r,a){let l;if(e.side===dt?l=n.intersectTriangle(r,s,i,!0,a):l=n.intersectTriangle(i,s,r,e.side===fn,a),l===null)return null;tl.copy(a),tl.applyMatrix4(o.matrixWorld);let c=t.ray.origin.distanceTo(tl);return c<t.near||c>t.far?null:{distance:c,point:tl.clone(),object:o}}d(mx,"checkIntersection");function nl(o,e,t,n,i,s,r,a,l){o.getVertexPosition(r,Ao),o.getVertexPosition(a,mo),o.getVertexPosition(l,go);let c=mx(o,e,t,n,Ao,mo,go,Qh);if(c){i&&(ja.fromBufferAttribute(i,r),Za.fromBufferAttribute(i,a),el.fromBufferAttribute(i,l),c.uv=Ei.getUV(Qh,Ao,mo,go,ja,Za,el,new Be)),s&&(ja.fromBufferAttribute(s,r),Za.fromBufferAttribute(s,a),el.fromBufferAttribute(s,l),c.uv2=Ei.getUV(Qh,Ao,mo,go,ja,Za,el,new Be));let h={a:r,b:a,c:l,normal:new B,materialIndex:0};Ei.getNormal(Ao,mo,go,h.normal),c.face=h}return c}d(nl,"checkBufferGeometryIntersection");var $n=class o extends kt{static{d(this,"BoxGeometry")}constructor(e=1,t=1,n=1,i=1,s=1,r=1){super(),this.type="BoxGeometry",this.parameters={width:e,height:t,depth:n,widthSegments:i,heightSegments:s,depthSegments:r};let a=this;i=Math.floor(i),s=Math.floor(s),r=Math.floor(r);let l=[],c=[],h=[],u=[],f=0,p=0;g("z","y","x",-1,-1,n,t,e,r,s,0),g("z","y","x",1,-1,n,t,-e,r,s,1),g("x","z","y",1,1,e,n,t,i,r,2),g("x","z","y",1,-1,e,n,-t,i,r,3),g("x","y","z",1,-1,e,t,n,i,s,4),g("x","y","z",-1,-1,e,t,-n,i,s,5),this.setIndex(l),this.setAttribute("position",new dn(c,3)),this.setAttribute("normal",new dn(h,3)),this.setAttribute("uv",new dn(u,2));function g(A,m,_,E,x,y,w,I,S,v,b){let R=y/S,N=w/v,z=y/2,O=w/2,D=I/2,Q=S+1,q=v+1,H=0,k=0,j=new B;for(let Z=0;Z<q;Z++){let fe=Z*N-O;for(let V=0;V<Q;V++){let ee=V*R-z;j[A]=ee*E,j[m]=fe*x,j[_]=D,c.push(j.x,j.y,j.z),j[A]=0,j[m]=0,j[_]=I>0?1:-1,h.push(j.x,j.y,j.z),u.push(V/S),u.push(1-Z/v),H+=1}}for(let Z=0;Z<v;Z++)for(let fe=0;fe<S;fe++){let V=f+fe+Q*Z,ee=f+fe+Q*(Z+1),re=f+(fe+1)+Q*(Z+1),ie=f+(fe+1)+Q*Z;l.push(V,ee,ie),l.push(ee,re,ie),k+=6}a.addGroup(p,k,b),p+=k,f+=H}d(g,"buildPlane")}static fromJSON(e){return new o(e.width,e.height,e.depth,e.widthSegments,e.heightSegments,e.depthSegments)}};function cr(o){let e={};for(let t in o){e[t]={};for(let n in o[t]){let i=o[t][n];i&&(i.isColor||i.isMatrix3||i.isMatrix4||i.isVector2||i.isVector3||i.isVector4||i.isTexture||i.isQuaternion)?e[t][n]=i.clone():Array.isArray(i)?e[t][n]=i.slice():e[t][n]=i}}return e}d(cr,"cloneUniforms");function nn(o){let e={};for(let t=0;t<o.length;t++){let n=cr(o[t]);for(let i in n)e[i]=n[i]}return e}d(nn,"mergeUniforms");function gx(o){let e=[];for(let t=0;t<o.length;t++)e.push(o[t].clone());return e}d(gx,"cloneUniformsGroups");function $A(o){return o.getRenderTarget()===null&&o.outputEncoding===Se?ii:To}d($A,"getUnlitUniformColorSpace");var _x={clone:cr,merge:nn},yx=`void main() {
	gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}`,xx=`void main() {
	gl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );
}`,Yt=class extends sn{static{d(this,"ShaderMaterial")}constructor(e){super(),this.isShaderMaterial=!0,this.type="ShaderMaterial",this.defines={},this.uniforms={},this.uniformsGroups=[],this.vertexShader=yx,this.fragmentShader=xx,this.linewidth=1,this.wireframe=!1,this.wireframeLinewidth=1,this.fog=!1,this.lights=!1,this.clipping=!1,this.extensions={derivatives:!1,fragDepth:!1,drawBuffers:!1,shaderTextureLOD:!1},this.defaultAttributeValues={color:[1,1,1],uv:[0,0],uv2:[0,0]},this.index0AttributeName=void 0,this.uniformsNeedUpdate=!1,this.glslVersion=null,e!==void 0&&this.setValues(e)}copy(e){return super.copy(e),this.fragmentShader=e.fragmentShader,this.vertexShader=e.vertexShader,this.uniforms=cr(e.uniforms),this.uniformsGroups=gx(e.uniformsGroups),this.defines=Object.assign({},e.defines),this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.fog=e.fog,this.lights=e.lights,this.clipping=e.clipping,this.extensions=Object.assign({},e.extensions),this.glslVersion=e.glslVersion,this}toJSON(e){let t=super.toJSON(e);t.glslVersion=this.glslVersion,t.uniforms={};for(let i in this.uniforms){let r=this.uniforms[i].value;r&&r.isTexture?t.uniforms[i]={type:"t",value:r.toJSON(e).uuid}:r&&r.isColor?t.uniforms[i]={type:"c",value:r.getHex()}:r&&r.isVector2?t.uniforms[i]={type:"v2",value:r.toArray()}:r&&r.isVector3?t.uniforms[i]={type:"v3",value:r.toArray()}:r&&r.isVector4?t.uniforms[i]={type:"v4",value:r.toArray()}:r&&r.isMatrix3?t.uniforms[i]={type:"m3",value:r.toArray()}:r&&r.isMatrix4?t.uniforms[i]={type:"m4",value:r.toArray()}:t.uniforms[i]={value:r}}Object.keys(this.defines).length>0&&(t.defines=this.defines),t.vertexShader=this.vertexShader,t.fragmentShader=this.fragmentShader;let n={};for(let i in this.extensions)this.extensions[i]===!0&&(n[i]=!0);return Object.keys(n).length>0&&(t.extensions=n),t}},wl=class extends Ze{static{d(this,"Camera")}constructor(){super(),this.isCamera=!0,this.type="Camera",this.matrixWorldInverse=new Ie,this.projectionMatrix=new Ie,this.projectionMatrixInverse=new Ie}copy(e,t){return super.copy(e,t),this.matrixWorldInverse.copy(e.matrixWorldInverse),this.projectionMatrix.copy(e.projectionMatrix),this.projectionMatrixInverse.copy(e.projectionMatrixInverse),this}getWorldDirection(e){this.updateWorldMatrix(!0,!1);let t=this.matrixWorld.elements;return e.set(-t[8],-t[9],-t[10]).normalize()}updateMatrixWorld(e){super.updateMatrixWorld(e),this.matrixWorldInverse.copy(this.matrixWorld).invert()}updateWorldMatrix(e,t){super.updateWorldMatrix(e,t),this.matrixWorldInverse.copy(this.matrixWorld).invert()}clone(){return new this.constructor().copy(this)}},ht=class extends wl{static{d(this,"PerspectiveCamera")}constructor(e=50,t=1,n=.1,i=2e3){super(),this.isPerspectiveCamera=!0,this.type="PerspectiveCamera",this.fov=e,this.zoom=1,this.near=n,this.far=i,this.focus=10,this.aspect=t,this.view=null,this.filmGauge=35,this.filmOffset=0,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.fov=e.fov,this.zoom=e.zoom,this.near=e.near,this.far=e.far,this.focus=e.focus,this.aspect=e.aspect,this.view=e.view===null?null:Object.assign({},e.view),this.filmGauge=e.filmGauge,this.filmOffset=e.filmOffset,this}setFocalLength(e){let t=.5*this.getFilmHeight()/e;this.fov=Bo*2*Math.atan(t),this.updateProjectionMatrix()}getFocalLength(){let e=Math.tan(bo*.5*this.fov);return .5*this.getFilmHeight()/e}getEffectiveFOV(){return Bo*2*Math.atan(Math.tan(bo*.5*this.fov)/this.zoom)}getFilmWidth(){return this.filmGauge*Math.min(this.aspect,1)}getFilmHeight(){return this.filmGauge/Math.max(this.aspect,1)}setViewOffset(e,t,n,i,s,r){this.aspect=e/t,this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=i,this.view.width=s,this.view.height=r,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){let e=this.near,t=e*Math.tan(bo*.5*this.fov)/this.zoom,n=2*t,i=this.aspect*n,s=-.5*i,r=this.view;if(this.view!==null&&this.view.enabled){let l=r.fullWidth,c=r.fullHeight;s+=r.offsetX*i/l,t-=r.offsetY*n/c,i*=r.width/l,n*=r.height/c}let a=this.filmOffset;a!==0&&(s+=e*a/this.getFilmWidth()),this.projectionMatrix.makePerspective(s,s+i,t,t-n,e,this.far),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){let t=super.toJSON(e);return t.object.fov=this.fov,t.object.zoom=this.zoom,t.object.near=this.near,t.object.far=this.far,t.object.focus=this.focus,t.object.aspect=this.aspect,this.view!==null&&(t.object.view=Object.assign({},this.view)),t.object.filmGauge=this.filmGauge,t.object.filmOffset=this.filmOffset,t}},qs=-90,Ks=1,hr=class extends Ze{static{d(this,"CubeCamera")}constructor(e,t,n){super(),this.type="CubeCamera",this.renderTarget=n;let i=new ht(qs,Ks,e,t);i.layers=this.layers,i.up.set(0,1,0),i.lookAt(1,0,0),this.add(i);let s=new ht(qs,Ks,e,t);s.layers=this.layers,s.up.set(0,1,0),s.lookAt(-1,0,0),this.add(s);let r=new ht(qs,Ks,e,t);r.layers=this.layers,r.up.set(0,0,-1),r.lookAt(0,1,0),this.add(r);let a=new ht(qs,Ks,e,t);a.layers=this.layers,a.up.set(0,0,1),a.lookAt(0,-1,0),this.add(a);let l=new ht(qs,Ks,e,t);l.layers=this.layers,l.up.set(0,1,0),l.lookAt(0,0,1),this.add(l);let c=new ht(qs,Ks,e,t);c.layers=this.layers,c.up.set(0,1,0),c.lookAt(0,0,-1),this.add(c)}update(e,t){this.parent===null&&this.updateMatrixWorld();let n=this.renderTarget,[i,s,r,a,l,c]=this.children,h=e.getRenderTarget(),u=e.toneMapping,f=e.xr.enabled;e.toneMapping=qn,e.xr.enabled=!1;let p=n.texture.generateMipmaps;n.texture.generateMipmaps=!1,e.setRenderTarget(n,0),e.render(t,i),e.setRenderTarget(n,1),e.render(t,s),e.setRenderTarget(n,2),e.render(t,r),e.setRenderTarget(n,3),e.render(t,a),e.setRenderTarget(n,4),e.render(t,l),n.texture.generateMipmaps=p,e.setRenderTarget(n,5),e.render(t,c),e.setRenderTarget(h),e.toneMapping=u,e.xr.enabled=f,n.texture.needsPMREMUpdate=!0}},Ml=class extends st{static{d(this,"CubeTexture")}constructor(e,t,n,i,s,r,a,l,c,h){e=e!==void 0?e:[],t=t!==void 0?t:ir,super(e,t,n,i,s,r,a,l,c,h),this.isCubeTexture=!0,this.flipY=!1}get images(){return this.image}set images(e){this.image=e}},Es=class extends Xt{static{d(this,"WebGLCubeRenderTarget")}constructor(e=1,t={}){super(e,e,t),this.isWebGLCubeRenderTarget=!0;let n={width:e,height:e,depth:1},i=[n,n,n,n,n,n];this.texture=new Ml(i,t.mapping,t.wrapS,t.wrapT,t.magFilter,t.minFilter,t.format,t.type,t.anisotropy,t.encoding),this.texture.isRenderTargetTexture=!0,this.texture.generateMipmaps=t.generateMipmaps!==void 0?t.generateMipmaps:!1,this.texture.minFilter=t.minFilter!==void 0?t.minFilter:Je}fromEquirectangularTexture(e,t){this.texture.type=t.type,this.texture.encoding=t.encoding,this.texture.generateMipmaps=t.generateMipmaps,this.texture.minFilter=t.minFilter,this.texture.magFilter=t.magFilter;let n={uniforms:{tEquirect:{value:null}},vertexShader:`

				varying vec3 vWorldDirection;

				vec3 transformDirection( in vec3 dir, in mat4 matrix ) {

					return normalize( ( matrix * vec4( dir, 0.0 ) ).xyz );

				}

				void main() {

					vWorldDirection = transformDirection( position, modelMatrix );

					#include <begin_vertex>
					#include <project_vertex>

				}
			`,fragmentShader:`

				uniform sampler2D tEquirect;

				varying vec3 vWorldDirection;

				#include <common>

				void main() {

					vec3 direction = normalize( vWorldDirection );

					vec2 sampleUV = equirectUv( direction );

					gl_FragColor = texture2D( tEquirect, sampleUV );

				}
			`},i=new $n(5,5,5),s=new Yt({name:"CubemapFromEquirect",uniforms:cr(n.uniforms),vertexShader:n.vertexShader,fragmentShader:n.fragmentShader,side:dt,blending:ri});s.uniforms.tEquirect.value=t;let r=new pe(i,s),a=t.minFilter;return t.minFilter===wn&&(t.minFilter=Je),new hr(1,10,this).update(e,r),t.minFilter=a,r.geometry.dispose(),r.material.dispose(),this}clear(e,t,n,i){let s=e.getRenderTarget();for(let r=0;r<6;r++)e.setRenderTarget(this,r),e.clear(t,n,i);e.setRenderTarget(s)}},kh=new B,vx=new B,Ex=new wt,yi=class{static{d(this,"Plane")}constructor(e=new B(1,0,0),t=0){this.isPlane=!0,this.normal=e,this.constant=t}set(e,t){return this.normal.copy(e),this.constant=t,this}setComponents(e,t,n,i){return this.normal.set(e,t,n),this.constant=i,this}setFromNormalAndCoplanarPoint(e,t){return this.normal.copy(e),this.constant=-t.dot(this.normal),this}setFromCoplanarPoints(e,t,n){let i=kh.subVectors(n,t).cross(vx.subVectors(e,t)).normalize();return this.setFromNormalAndCoplanarPoint(i,e),this}copy(e){return this.normal.copy(e.normal),this.constant=e.constant,this}normalize(){let e=1/this.normal.length();return this.normal.multiplyScalar(e),this.constant*=e,this}negate(){return this.constant*=-1,this.normal.negate(),this}distanceToPoint(e){return this.normal.dot(e)+this.constant}distanceToSphere(e){return this.distanceToPoint(e.center)-e.radius}projectPoint(e,t){return t.copy(this.normal).multiplyScalar(-this.distanceToPoint(e)).add(e)}intersectLine(e,t){let n=e.delta(kh),i=this.normal.dot(n);if(i===0)return this.distanceToPoint(e.start)===0?t.copy(e.start):null;let s=-(e.start.dot(this.normal)+this.constant)/i;return s<0||s>1?null:t.copy(n).multiplyScalar(s).add(e.start)}intersectsLine(e){let t=this.distanceToPoint(e.start),n=this.distanceToPoint(e.end);return t<0&&n>0||n<0&&t>0}intersectsBox(e){return e.intersectsPlane(this)}intersectsSphere(e){return e.intersectsPlane(this)}coplanarPoint(e){return e.copy(this.normal).multiplyScalar(-this.constant)}applyMatrix4(e,t){let n=t||Ex.getNormalMatrix(e),i=this.coplanarPoint(kh).applyMatrix4(e),s=this.normal.applyMatrix3(n).normalize();return this.constant=-i.dot(s),this}translate(e){return this.constant-=e.dot(this.normal),this}equals(e){return e.normal.equals(this.normal)&&e.constant===this.constant}clone(){return new this.constructor().copy(this)}},$s=new Mn,il=new B,Po=class{static{d(this,"Frustum")}constructor(e=new yi,t=new yi,n=new yi,i=new yi,s=new yi,r=new yi){this.planes=[e,t,n,i,s,r]}set(e,t,n,i,s,r){let a=this.planes;return a[0].copy(e),a[1].copy(t),a[2].copy(n),a[3].copy(i),a[4].copy(s),a[5].copy(r),this}copy(e){let t=this.planes;for(let n=0;n<6;n++)t[n].copy(e.planes[n]);return this}setFromProjectionMatrix(e){let t=this.planes,n=e.elements,i=n[0],s=n[1],r=n[2],a=n[3],l=n[4],c=n[5],h=n[6],u=n[7],f=n[8],p=n[9],g=n[10],A=n[11],m=n[12],_=n[13],E=n[14],x=n[15];return t[0].setComponents(a-i,u-l,A-f,x-m).normalize(),t[1].setComponents(a+i,u+l,A+f,x+m).normalize(),t[2].setComponents(a+s,u+c,A+p,x+_).normalize(),t[3].setComponents(a-s,u-c,A-p,x-_).normalize(),t[4].setComponents(a-r,u-h,A-g,x-E).normalize(),t[5].setComponents(a+r,u+h,A+g,x+E).normalize(),this}intersectsObject(e){let t=e.geometry;return t.boundingSphere===null&&t.computeBoundingSphere(),$s.copy(t.boundingSphere).applyMatrix4(e.matrixWorld),this.intersectsSphere($s)}intersectsSprite(e){return $s.center.set(0,0,0),$s.radius=.7071067811865476,$s.applyMatrix4(e.matrixWorld),this.intersectsSphere($s)}intersectsSphere(e){let t=this.planes,n=e.center,i=-e.radius;for(let s=0;s<6;s++)if(t[s].distanceToPoint(n)<i)return!1;return!0}intersectsBox(e){let t=this.planes;for(let n=0;n<6;n++){let i=t[n];if(il.x=i.normal.x>0?e.max.x:e.min.x,il.y=i.normal.y>0?e.max.y:e.min.y,il.z=i.normal.z>0?e.max.z:e.min.z,i.distanceToPoint(il)<0)return!1}return!0}containsPoint(e){let t=this.planes;for(let n=0;n<6;n++)if(t[n].distanceToPoint(e)<0)return!1;return!0}clone(){return new this.constructor().copy(this)}};function XA(){let o=null,e=!1,t=null,n=null;function i(s,r){t(s,r),n=o.requestAnimationFrame(i)}return d(i,"onAnimationFrame"),{start:d(function(){e!==!0&&t!==null&&(n=o.requestAnimationFrame(i),e=!0)},"start"),stop:d(function(){o.cancelAnimationFrame(n),e=!1},"stop"),setAnimationLoop:d(function(s){t=s},"setAnimationLoop"),setContext:d(function(s){o=s},"setContext")}}d(XA,"WebGLAnimation");function wx(o,e){let t=e.isWebGL2,n=new WeakMap;function i(c,h){let u=c.array,f=c.usage,p=o.createBuffer();o.bindBuffer(h,p),o.bufferData(h,u,f),c.onUploadCallback();let g;if(u instanceof Float32Array)g=5126;else if(u instanceof Uint16Array)if(c.isFloat16BufferAttribute)if(t)g=5131;else throw new Error("THREE.WebGLAttributes: Usage of Float16BufferAttribute requires WebGL2.");else g=5123;else if(u instanceof Int16Array)g=5122;else if(u instanceof Uint32Array)g=5125;else if(u instanceof Int32Array)g=5124;else if(u instanceof Int8Array)g=5120;else if(u instanceof Uint8Array)g=5121;else if(u instanceof Uint8ClampedArray)g=5121;else throw new Error("THREE.WebGLAttributes: Unsupported buffer data format: "+u);return{buffer:p,type:g,bytesPerElement:u.BYTES_PER_ELEMENT,version:c.version}}d(i,"createBuffer");function s(c,h,u){let f=h.array,p=h.updateRange;o.bindBuffer(u,c),p.count===-1?o.bufferSubData(u,0,f):(t?o.bufferSubData(u,p.offset*f.BYTES_PER_ELEMENT,f,p.offset,p.count):o.bufferSubData(u,p.offset*f.BYTES_PER_ELEMENT,f.subarray(p.offset,p.offset+p.count)),p.count=-1),h.onUploadCallback()}d(s,"updateBuffer");function r(c){return c.isInterleavedBufferAttribute&&(c=c.data),n.get(c)}d(r,"get");function a(c){c.isInterleavedBufferAttribute&&(c=c.data);let h=n.get(c);h&&(o.deleteBuffer(h.buffer),n.delete(c))}d(a,"remove");function l(c,h){if(c.isGLBufferAttribute){let f=n.get(c);(!f||f.version<c.version)&&n.set(c,{buffer:c.buffer,type:c.type,bytesPerElement:c.elementSize,version:c.version});return}c.isInterleavedBufferAttribute&&(c=c.data);let u=n.get(c);u===void 0?n.set(c,i(c,h)):u.version<c.version&&(s(u.buffer,c,h),u.version=c.version)}return d(l,"update"),{get:r,remove:a,update:l}}d(wx,"WebGLAttributes");var Xn=class o extends kt{static{d(this,"PlaneGeometry")}constructor(e=1,t=1,n=1,i=1){super(),this.type="PlaneGeometry",this.parameters={width:e,height:t,widthSegments:n,heightSegments:i};let s=e/2,r=t/2,a=Math.floor(n),l=Math.floor(i),c=a+1,h=l+1,u=e/a,f=t/l,p=[],g=[],A=[],m=[];for(let _=0;_<h;_++){let E=_*f-r;for(let x=0;x<c;x++){let y=x*u-s;g.push(y,-E,0),A.push(0,0,1),m.push(x/a),m.push(1-_/l)}}for(let _=0;_<l;_++)for(let E=0;E<a;E++){let x=E+c*_,y=E+c*(_+1),w=E+1+c*(_+1),I=E+1+c*_;p.push(x,y,I),p.push(y,w,I)}this.setIndex(p),this.setAttribute("position",new dn(g,3)),this.setAttribute("normal",new dn(A,3)),this.setAttribute("uv",new dn(m,2))}static fromJSON(e){return new o(e.width,e.height,e.widthSegments,e.heightSegments)}},Mx=`#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, vUv ).g;
#endif`,bx=`#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,Ix=`#ifdef USE_ALPHATEST
	if ( diffuseColor.a < alphaTest ) discard;
#endif`,Cx=`#ifdef USE_ALPHATEST
	uniform float alphaTest;
#endif`,Sx=`#ifdef USE_AOMAP
	float ambientOcclusion = ( texture2D( aoMap, vUv2 ).r - 1.0 ) * aoMapIntensity + 1.0;
	reflectedLight.indirectDiffuse *= ambientOcclusion;
	#if defined( USE_ENVMAP ) && defined( STANDARD )
		float dotNV = saturate( dot( geometry.normal, geometry.viewDir ) );
		reflectedLight.indirectSpecular *= computeSpecularOcclusion( dotNV, ambientOcclusion, material.roughness );
	#endif
#endif`,Tx=`#ifdef USE_AOMAP
	uniform sampler2D aoMap;
	uniform float aoMapIntensity;
#endif`,Bx="vec3 transformed = vec3( position );",Rx=`vec3 objectNormal = vec3( normal );
#ifdef USE_TANGENT
	vec3 objectTangent = vec3( tangent.xyz );
#endif`,Dx=`vec3 BRDF_Lambert( const in vec3 diffuseColor ) {
	return RECIPROCAL_PI * diffuseColor;
}
vec3 F_Schlick( const in vec3 f0, const in float f90, const in float dotVH ) {
	float fresnel = exp2( ( - 5.55473 * dotVH - 6.98316 ) * dotVH );
	return f0 * ( 1.0 - fresnel ) + ( f90 * fresnel );
}
float F_Schlick( const in float f0, const in float f90, const in float dotVH ) {
	float fresnel = exp2( ( - 5.55473 * dotVH - 6.98316 ) * dotVH );
	return f0 * ( 1.0 - fresnel ) + ( f90 * fresnel );
}
vec3 Schlick_to_F0( const in vec3 f, const in float f90, const in float dotVH ) {
    float x = clamp( 1.0 - dotVH, 0.0, 1.0 );
    float x2 = x * x;
    float x5 = clamp( x * x2 * x2, 0.0, 0.9999 );
    return ( f - vec3( f90 ) * x5 ) / ( 1.0 - x5 );
}
float V_GGX_SmithCorrelated( const in float alpha, const in float dotNL, const in float dotNV ) {
	float a2 = pow2( alpha );
	float gv = dotNL * sqrt( a2 + ( 1.0 - a2 ) * pow2( dotNV ) );
	float gl = dotNV * sqrt( a2 + ( 1.0 - a2 ) * pow2( dotNL ) );
	return 0.5 / max( gv + gl, EPSILON );
}
float D_GGX( const in float alpha, const in float dotNH ) {
	float a2 = pow2( alpha );
	float denom = pow2( dotNH ) * ( a2 - 1.0 ) + 1.0;
	return RECIPROCAL_PI * a2 / pow2( denom );
}
vec3 BRDF_GGX( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in vec3 f0, const in float f90, const in float roughness ) {
	float alpha = pow2( roughness );
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNL = saturate( dot( normal, lightDir ) );
	float dotNV = saturate( dot( normal, viewDir ) );
	float dotNH = saturate( dot( normal, halfDir ) );
	float dotVH = saturate( dot( viewDir, halfDir ) );
	vec3 F = F_Schlick( f0, f90, dotVH );
	float V = V_GGX_SmithCorrelated( alpha, dotNL, dotNV );
	float D = D_GGX( alpha, dotNH );
	return F * ( V * D );
}
#ifdef USE_IRIDESCENCE
	vec3 BRDF_GGX_Iridescence( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in vec3 f0, const in float f90, const in float iridescence, const in vec3 iridescenceFresnel, const in float roughness ) {
		float alpha = pow2( roughness );
		vec3 halfDir = normalize( lightDir + viewDir );
		float dotNL = saturate( dot( normal, lightDir ) );
		float dotNV = saturate( dot( normal, viewDir ) );
		float dotNH = saturate( dot( normal, halfDir ) );
		float dotVH = saturate( dot( viewDir, halfDir ) );
		vec3 F = mix( F_Schlick( f0, f90, dotVH ), iridescenceFresnel, iridescence );
		float V = V_GGX_SmithCorrelated( alpha, dotNL, dotNV );
		float D = D_GGX( alpha, dotNH );
		return F * ( V * D );
	}
#endif
vec2 LTC_Uv( const in vec3 N, const in vec3 V, const in float roughness ) {
	const float LUT_SIZE = 64.0;
	const float LUT_SCALE = ( LUT_SIZE - 1.0 ) / LUT_SIZE;
	const float LUT_BIAS = 0.5 / LUT_SIZE;
	float dotNV = saturate( dot( N, V ) );
	vec2 uv = vec2( roughness, sqrt( 1.0 - dotNV ) );
	uv = uv * LUT_SCALE + LUT_BIAS;
	return uv;
}
float LTC_ClippedSphereFormFactor( const in vec3 f ) {
	float l = length( f );
	return max( ( l * l + f.z ) / ( l + 1.0 ), 0.0 );
}
vec3 LTC_EdgeVectorFormFactor( const in vec3 v1, const in vec3 v2 ) {
	float x = dot( v1, v2 );
	float y = abs( x );
	float a = 0.8543985 + ( 0.4965155 + 0.0145206 * y ) * y;
	float b = 3.4175940 + ( 4.1616724 + y ) * y;
	float v = a / b;
	float theta_sintheta = ( x > 0.0 ) ? v : 0.5 * inversesqrt( max( 1.0 - x * x, 1e-7 ) ) - v;
	return cross( v1, v2 ) * theta_sintheta;
}
vec3 LTC_Evaluate( const in vec3 N, const in vec3 V, const in vec3 P, const in mat3 mInv, const in vec3 rectCoords[ 4 ] ) {
	vec3 v1 = rectCoords[ 1 ] - rectCoords[ 0 ];
	vec3 v2 = rectCoords[ 3 ] - rectCoords[ 0 ];
	vec3 lightNormal = cross( v1, v2 );
	if( dot( lightNormal, P - rectCoords[ 0 ] ) < 0.0 ) return vec3( 0.0 );
	vec3 T1, T2;
	T1 = normalize( V - N * dot( V, N ) );
	T2 = - cross( N, T1 );
	mat3 mat = mInv * transposeMat3( mat3( T1, T2, N ) );
	vec3 coords[ 4 ];
	coords[ 0 ] = mat * ( rectCoords[ 0 ] - P );
	coords[ 1 ] = mat * ( rectCoords[ 1 ] - P );
	coords[ 2 ] = mat * ( rectCoords[ 2 ] - P );
	coords[ 3 ] = mat * ( rectCoords[ 3 ] - P );
	coords[ 0 ] = normalize( coords[ 0 ] );
	coords[ 1 ] = normalize( coords[ 1 ] );
	coords[ 2 ] = normalize( coords[ 2 ] );
	coords[ 3 ] = normalize( coords[ 3 ] );
	vec3 vectorFormFactor = vec3( 0.0 );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 0 ], coords[ 1 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 1 ], coords[ 2 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 2 ], coords[ 3 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 3 ], coords[ 0 ] );
	float result = LTC_ClippedSphereFormFactor( vectorFormFactor );
	return vec3( result );
}
float G_BlinnPhong_Implicit( ) {
	return 0.25;
}
float D_BlinnPhong( const in float shininess, const in float dotNH ) {
	return RECIPROCAL_PI * ( shininess * 0.5 + 1.0 ) * pow( dotNH, shininess );
}
vec3 BRDF_BlinnPhong( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in vec3 specularColor, const in float shininess ) {
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNH = saturate( dot( normal, halfDir ) );
	float dotVH = saturate( dot( viewDir, halfDir ) );
	vec3 F = F_Schlick( specularColor, 1.0, dotVH );
	float G = G_BlinnPhong_Implicit( );
	float D = D_BlinnPhong( shininess, dotNH );
	return F * ( G * D );
}
#if defined( USE_SHEEN )
float D_Charlie( float roughness, float dotNH ) {
	float alpha = pow2( roughness );
	float invAlpha = 1.0 / alpha;
	float cos2h = dotNH * dotNH;
	float sin2h = max( 1.0 - cos2h, 0.0078125 );
	return ( 2.0 + invAlpha ) * pow( sin2h, invAlpha * 0.5 ) / ( 2.0 * PI );
}
float V_Neubelt( float dotNV, float dotNL ) {
	return saturate( 1.0 / ( 4.0 * ( dotNL + dotNV - dotNL * dotNV ) ) );
}
vec3 BRDF_Sheen( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, vec3 sheenColor, const in float sheenRoughness ) {
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNL = saturate( dot( normal, lightDir ) );
	float dotNV = saturate( dot( normal, viewDir ) );
	float dotNH = saturate( dot( normal, halfDir ) );
	float D = D_Charlie( sheenRoughness, dotNH );
	float V = V_Neubelt( dotNV, dotNL );
	return sheenColor * ( D * V );
}
#endif`,Lx=`#ifdef USE_IRIDESCENCE
	const mat3 XYZ_TO_REC709 = mat3(
		 3.2404542, -0.9692660,  0.0556434,
		-1.5371385,  1.8760108, -0.2040259,
		-0.4985314,  0.0415560,  1.0572252
	);
	vec3 Fresnel0ToIor( vec3 fresnel0 ) {
		vec3 sqrtF0 = sqrt( fresnel0 );
		return ( vec3( 1.0 ) + sqrtF0 ) / ( vec3( 1.0 ) - sqrtF0 );
	}
	vec3 IorToFresnel0( vec3 transmittedIor, float incidentIor ) {
		return pow2( ( transmittedIor - vec3( incidentIor ) ) / ( transmittedIor + vec3( incidentIor ) ) );
	}
	float IorToFresnel0( float transmittedIor, float incidentIor ) {
		return pow2( ( transmittedIor - incidentIor ) / ( transmittedIor + incidentIor ));
	}
	vec3 evalSensitivity( float OPD, vec3 shift ) {
		float phase = 2.0 * PI * OPD * 1.0e-9;
		vec3 val = vec3( 5.4856e-13, 4.4201e-13, 5.2481e-13 );
		vec3 pos = vec3( 1.6810e+06, 1.7953e+06, 2.2084e+06 );
		vec3 var = vec3( 4.3278e+09, 9.3046e+09, 6.6121e+09 );
		vec3 xyz = val * sqrt( 2.0 * PI * var ) * cos( pos * phase + shift ) * exp( - pow2( phase ) * var );
		xyz.x += 9.7470e-14 * sqrt( 2.0 * PI * 4.5282e+09 ) * cos( 2.2399e+06 * phase + shift[ 0 ] ) * exp( - 4.5282e+09 * pow2( phase ) );
		xyz /= 1.0685e-7;
		vec3 rgb = XYZ_TO_REC709 * xyz;
		return rgb;
	}
	vec3 evalIridescence( float outsideIOR, float eta2, float cosTheta1, float thinFilmThickness, vec3 baseF0 ) {
		vec3 I;
		float iridescenceIOR = mix( outsideIOR, eta2, smoothstep( 0.0, 0.03, thinFilmThickness ) );
		float sinTheta2Sq = pow2( outsideIOR / iridescenceIOR ) * ( 1.0 - pow2( cosTheta1 ) );
		float cosTheta2Sq = 1.0 - sinTheta2Sq;
		if ( cosTheta2Sq < 0.0 ) {
			 return vec3( 1.0 );
		}
		float cosTheta2 = sqrt( cosTheta2Sq );
		float R0 = IorToFresnel0( iridescenceIOR, outsideIOR );
		float R12 = F_Schlick( R0, 1.0, cosTheta1 );
		float R21 = R12;
		float T121 = 1.0 - R12;
		float phi12 = 0.0;
		if ( iridescenceIOR < outsideIOR ) phi12 = PI;
		float phi21 = PI - phi12;
		vec3 baseIOR = Fresnel0ToIor( clamp( baseF0, 0.0, 0.9999 ) );		vec3 R1 = IorToFresnel0( baseIOR, iridescenceIOR );
		vec3 R23 = F_Schlick( R1, 1.0, cosTheta2 );
		vec3 phi23 = vec3( 0.0 );
		if ( baseIOR[ 0 ] < iridescenceIOR ) phi23[ 0 ] = PI;
		if ( baseIOR[ 1 ] < iridescenceIOR ) phi23[ 1 ] = PI;
		if ( baseIOR[ 2 ] < iridescenceIOR ) phi23[ 2 ] = PI;
		float OPD = 2.0 * iridescenceIOR * thinFilmThickness * cosTheta2;
		vec3 phi = vec3( phi21 ) + phi23;
		vec3 R123 = clamp( R12 * R23, 1e-5, 0.9999 );
		vec3 r123 = sqrt( R123 );
		vec3 Rs = pow2( T121 ) * R23 / ( vec3( 1.0 ) - R123 );
		vec3 C0 = R12 + Rs;
		I = C0;
		vec3 Cm = Rs - T121;
		for ( int m = 1; m <= 2; ++ m ) {
			Cm *= r123;
			vec3 Sm = 2.0 * evalSensitivity( float( m ) * OPD, float( m ) * phi );
			I += Cm * Sm;
		}
		return max( I, vec3( 0.0 ) );
	}
#endif`,Px=`#ifdef USE_BUMPMAP
	uniform sampler2D bumpMap;
	uniform float bumpScale;
	vec2 dHdxy_fwd() {
		vec2 dSTdx = dFdx( vUv );
		vec2 dSTdy = dFdy( vUv );
		float Hll = bumpScale * texture2D( bumpMap, vUv ).x;
		float dBx = bumpScale * texture2D( bumpMap, vUv + dSTdx ).x - Hll;
		float dBy = bumpScale * texture2D( bumpMap, vUv + dSTdy ).x - Hll;
		return vec2( dBx, dBy );
	}
	vec3 perturbNormalArb( vec3 surf_pos, vec3 surf_norm, vec2 dHdxy, float faceDirection ) {
		vec3 vSigmaX = dFdx( surf_pos.xyz );
		vec3 vSigmaY = dFdy( surf_pos.xyz );
		vec3 vN = surf_norm;
		vec3 R1 = cross( vSigmaY, vN );
		vec3 R2 = cross( vN, vSigmaX );
		float fDet = dot( vSigmaX, R1 ) * faceDirection;
		vec3 vGrad = sign( fDet ) * ( dHdxy.x * R1 + dHdxy.y * R2 );
		return normalize( abs( fDet ) * surf_norm - vGrad );
	}
#endif`,Fx=`#if NUM_CLIPPING_PLANES > 0
	vec4 plane;
	#pragma unroll_loop_start
	for ( int i = 0; i < UNION_CLIPPING_PLANES; i ++ ) {
		plane = clippingPlanes[ i ];
		if ( dot( vClipPosition, plane.xyz ) > plane.w ) discard;
	}
	#pragma unroll_loop_end
	#if UNION_CLIPPING_PLANES < NUM_CLIPPING_PLANES
		bool clipped = true;
		#pragma unroll_loop_start
		for ( int i = UNION_CLIPPING_PLANES; i < NUM_CLIPPING_PLANES; i ++ ) {
			plane = clippingPlanes[ i ];
			clipped = ( dot( vClipPosition, plane.xyz ) > plane.w ) && clipped;
		}
		#pragma unroll_loop_end
		if ( clipped ) discard;
	#endif
#endif`,Ox=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
	uniform vec4 clippingPlanes[ NUM_CLIPPING_PLANES ];
#endif`,Nx=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
#endif`,Ux=`#if NUM_CLIPPING_PLANES > 0
	vClipPosition = - mvPosition.xyz;
#endif`,Qx=`#if defined( USE_COLOR_ALPHA )
	diffuseColor *= vColor;
#elif defined( USE_COLOR )
	diffuseColor.rgb *= vColor;
#endif`,kx=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR )
	varying vec3 vColor;
#endif`,Gx=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR ) || defined( USE_INSTANCING_COLOR )
	varying vec3 vColor;
#endif`,zx=`#if defined( USE_COLOR_ALPHA )
	vColor = vec4( 1.0 );
#elif defined( USE_COLOR ) || defined( USE_INSTANCING_COLOR )
	vColor = vec3( 1.0 );
#endif
#ifdef USE_COLOR
	vColor *= color;
#endif
#ifdef USE_INSTANCING_COLOR
	vColor.xyz *= instanceColor.xyz;
#endif`,Vx=`#define PI 3.141592653589793
#define PI2 6.283185307179586
#define PI_HALF 1.5707963267948966
#define RECIPROCAL_PI 0.3183098861837907
#define RECIPROCAL_PI2 0.15915494309189535
#define EPSILON 1e-6
#ifndef saturate
#define saturate( a ) clamp( a, 0.0, 1.0 )
#endif
#define whiteComplement( a ) ( 1.0 - saturate( a ) )
float pow2( const in float x ) { return x*x; }
vec3 pow2( const in vec3 x ) { return x*x; }
float pow3( const in float x ) { return x*x*x; }
float pow4( const in float x ) { float x2 = x*x; return x2*x2; }
float max3( const in vec3 v ) { return max( max( v.x, v.y ), v.z ); }
float average( const in vec3 v ) { return dot( v, vec3( 0.3333333 ) ); }
highp float rand( const in vec2 uv ) {
	const highp float a = 12.9898, b = 78.233, c = 43758.5453;
	highp float dt = dot( uv.xy, vec2( a,b ) ), sn = mod( dt, PI );
	return fract( sin( sn ) * c );
}
#ifdef HIGH_PRECISION
	float precisionSafeLength( vec3 v ) { return length( v ); }
#else
	float precisionSafeLength( vec3 v ) {
		float maxComponent = max3( abs( v ) );
		return length( v / maxComponent ) * maxComponent;
	}
#endif
struct IncidentLight {
	vec3 color;
	vec3 direction;
	bool visible;
};
struct ReflectedLight {
	vec3 directDiffuse;
	vec3 directSpecular;
	vec3 indirectDiffuse;
	vec3 indirectSpecular;
};
struct GeometricContext {
	vec3 position;
	vec3 normal;
	vec3 viewDir;
#ifdef USE_CLEARCOAT
	vec3 clearcoatNormal;
#endif
};
vec3 transformDirection( in vec3 dir, in mat4 matrix ) {
	return normalize( ( matrix * vec4( dir, 0.0 ) ).xyz );
}
vec3 inverseTransformDirection( in vec3 dir, in mat4 matrix ) {
	return normalize( ( vec4( dir, 0.0 ) * matrix ).xyz );
}
mat3 transposeMat3( const in mat3 m ) {
	mat3 tmp;
	tmp[ 0 ] = vec3( m[ 0 ].x, m[ 1 ].x, m[ 2 ].x );
	tmp[ 1 ] = vec3( m[ 0 ].y, m[ 1 ].y, m[ 2 ].y );
	tmp[ 2 ] = vec3( m[ 0 ].z, m[ 1 ].z, m[ 2 ].z );
	return tmp;
}
float luminance( const in vec3 rgb ) {
	const vec3 weights = vec3( 0.2126729, 0.7151522, 0.0721750 );
	return dot( weights, rgb );
}
bool isPerspectiveMatrix( mat4 m ) {
	return m[ 2 ][ 3 ] == - 1.0;
}
vec2 equirectUv( in vec3 dir ) {
	float u = atan( dir.z, dir.x ) * RECIPROCAL_PI2 + 0.5;
	float v = asin( clamp( dir.y, - 1.0, 1.0 ) ) * RECIPROCAL_PI + 0.5;
	return vec2( u, v );
}`,Hx=`#ifdef ENVMAP_TYPE_CUBE_UV
	#define cubeUV_minMipLevel 4.0
	#define cubeUV_minTileSize 16.0
	float getFace( vec3 direction ) {
		vec3 absDirection = abs( direction );
		float face = - 1.0;
		if ( absDirection.x > absDirection.z ) {
			if ( absDirection.x > absDirection.y )
				face = direction.x > 0.0 ? 0.0 : 3.0;
			else
				face = direction.y > 0.0 ? 1.0 : 4.0;
		} else {
			if ( absDirection.z > absDirection.y )
				face = direction.z > 0.0 ? 2.0 : 5.0;
			else
				face = direction.y > 0.0 ? 1.0 : 4.0;
		}
		return face;
	}
	vec2 getUV( vec3 direction, float face ) {
		vec2 uv;
		if ( face == 0.0 ) {
			uv = vec2( direction.z, direction.y ) / abs( direction.x );
		} else if ( face == 1.0 ) {
			uv = vec2( - direction.x, - direction.z ) / abs( direction.y );
		} else if ( face == 2.0 ) {
			uv = vec2( - direction.x, direction.y ) / abs( direction.z );
		} else if ( face == 3.0 ) {
			uv = vec2( - direction.z, direction.y ) / abs( direction.x );
		} else if ( face == 4.0 ) {
			uv = vec2( - direction.x, direction.z ) / abs( direction.y );
		} else {
			uv = vec2( direction.x, direction.y ) / abs( direction.z );
		}
		return 0.5 * ( uv + 1.0 );
	}
	vec3 bilinearCubeUV( sampler2D envMap, vec3 direction, float mipInt ) {
		float face = getFace( direction );
		float filterInt = max( cubeUV_minMipLevel - mipInt, 0.0 );
		mipInt = max( mipInt, cubeUV_minMipLevel );
		float faceSize = exp2( mipInt );
		highp vec2 uv = getUV( direction, face ) * ( faceSize - 2.0 ) + 1.0;
		if ( face > 2.0 ) {
			uv.y += faceSize;
			face -= 3.0;
		}
		uv.x += face * faceSize;
		uv.x += filterInt * 3.0 * cubeUV_minTileSize;
		uv.y += 4.0 * ( exp2( CUBEUV_MAX_MIP ) - faceSize );
		uv.x *= CUBEUV_TEXEL_WIDTH;
		uv.y *= CUBEUV_TEXEL_HEIGHT;
		#ifdef texture2DGradEXT
			return texture2DGradEXT( envMap, uv, vec2( 0.0 ), vec2( 0.0 ) ).rgb;
		#else
			return texture2D( envMap, uv ).rgb;
		#endif
	}
	#define cubeUV_r0 1.0
	#define cubeUV_v0 0.339
	#define cubeUV_m0 - 2.0
	#define cubeUV_r1 0.8
	#define cubeUV_v1 0.276
	#define cubeUV_m1 - 1.0
	#define cubeUV_r4 0.4
	#define cubeUV_v4 0.046
	#define cubeUV_m4 2.0
	#define cubeUV_r5 0.305
	#define cubeUV_v5 0.016
	#define cubeUV_m5 3.0
	#define cubeUV_r6 0.21
	#define cubeUV_v6 0.0038
	#define cubeUV_m6 4.0
	float roughnessToMip( float roughness ) {
		float mip = 0.0;
		if ( roughness >= cubeUV_r1 ) {
			mip = ( cubeUV_r0 - roughness ) * ( cubeUV_m1 - cubeUV_m0 ) / ( cubeUV_r0 - cubeUV_r1 ) + cubeUV_m0;
		} else if ( roughness >= cubeUV_r4 ) {
			mip = ( cubeUV_r1 - roughness ) * ( cubeUV_m4 - cubeUV_m1 ) / ( cubeUV_r1 - cubeUV_r4 ) + cubeUV_m1;
		} else if ( roughness >= cubeUV_r5 ) {
			mip = ( cubeUV_r4 - roughness ) * ( cubeUV_m5 - cubeUV_m4 ) / ( cubeUV_r4 - cubeUV_r5 ) + cubeUV_m4;
		} else if ( roughness >= cubeUV_r6 ) {
			mip = ( cubeUV_r5 - roughness ) * ( cubeUV_m6 - cubeUV_m5 ) / ( cubeUV_r5 - cubeUV_r6 ) + cubeUV_m5;
		} else {
			mip = - 2.0 * log2( 1.16 * roughness );		}
		return mip;
	}
	vec4 textureCubeUV( sampler2D envMap, vec3 sampleDir, float roughness ) {
		float mip = clamp( roughnessToMip( roughness ), cubeUV_m0, CUBEUV_MAX_MIP );
		float mipF = fract( mip );
		float mipInt = floor( mip );
		vec3 color0 = bilinearCubeUV( envMap, sampleDir, mipInt );
		if ( mipF == 0.0 ) {
			return vec4( color0, 1.0 );
		} else {
			vec3 color1 = bilinearCubeUV( envMap, sampleDir, mipInt + 1.0 );
			return vec4( mix( color0, color1, mipF ), 1.0 );
		}
	}
#endif`,Wx=`vec3 transformedNormal = objectNormal;
#ifdef USE_INSTANCING
	mat3 m = mat3( instanceMatrix );
	transformedNormal /= vec3( dot( m[ 0 ], m[ 0 ] ), dot( m[ 1 ], m[ 1 ] ), dot( m[ 2 ], m[ 2 ] ) );
	transformedNormal = m * transformedNormal;
#endif
transformedNormal = normalMatrix * transformedNormal;
#ifdef FLIP_SIDED
	transformedNormal = - transformedNormal;
#endif
#ifdef USE_TANGENT
	vec3 transformedTangent = ( modelViewMatrix * vec4( objectTangent, 0.0 ) ).xyz;
	#ifdef FLIP_SIDED
		transformedTangent = - transformedTangent;
	#endif
#endif`,qx=`#ifdef USE_DISPLACEMENTMAP
	uniform sampler2D displacementMap;
	uniform float displacementScale;
	uniform float displacementBias;
#endif`,Kx=`#ifdef USE_DISPLACEMENTMAP
	transformed += normalize( objectNormal ) * ( texture2D( displacementMap, vUv ).x * displacementScale + displacementBias );
#endif`,$x=`#ifdef USE_EMISSIVEMAP
	vec4 emissiveColor = texture2D( emissiveMap, vUv );
	totalEmissiveRadiance *= emissiveColor.rgb;
#endif`,Xx=`#ifdef USE_EMISSIVEMAP
	uniform sampler2D emissiveMap;
#endif`,Yx="gl_FragColor = linearToOutputTexel( gl_FragColor );",Jx=`vec4 LinearToLinear( in vec4 value ) {
	return value;
}
vec4 LinearTosRGB( in vec4 value ) {
	return vec4( mix( pow( value.rgb, vec3( 0.41666 ) ) * 1.055 - vec3( 0.055 ), value.rgb * 12.92, vec3( lessThanEqual( value.rgb, vec3( 0.0031308 ) ) ) ), value.a );
}`,jx=`#ifdef USE_ENVMAP
	#ifdef ENV_WORLDPOS
		vec3 cameraToFrag;
		if ( isOrthographic ) {
			cameraToFrag = normalize( vec3( - viewMatrix[ 0 ][ 2 ], - viewMatrix[ 1 ][ 2 ], - viewMatrix[ 2 ][ 2 ] ) );
		} else {
			cameraToFrag = normalize( vWorldPosition - cameraPosition );
		}
		vec3 worldNormal = inverseTransformDirection( normal, viewMatrix );
		#ifdef ENVMAP_MODE_REFLECTION
			vec3 reflectVec = reflect( cameraToFrag, worldNormal );
		#else
			vec3 reflectVec = refract( cameraToFrag, worldNormal, refractionRatio );
		#endif
	#else
		vec3 reflectVec = vReflect;
	#endif
	#ifdef ENVMAP_TYPE_CUBE
		vec4 envColor = textureCube( envMap, vec3( flipEnvMap * reflectVec.x, reflectVec.yz ) );
	#else
		vec4 envColor = vec4( 0.0 );
	#endif
	#ifdef ENVMAP_BLENDING_MULTIPLY
		outgoingLight = mix( outgoingLight, outgoingLight * envColor.xyz, specularStrength * reflectivity );
	#elif defined( ENVMAP_BLENDING_MIX )
		outgoingLight = mix( outgoingLight, envColor.xyz, specularStrength * reflectivity );
	#elif defined( ENVMAP_BLENDING_ADD )
		outgoingLight += envColor.xyz * specularStrength * reflectivity;
	#endif
#endif`,Zx=`#ifdef USE_ENVMAP
	uniform float envMapIntensity;
	uniform float flipEnvMap;
	#ifdef ENVMAP_TYPE_CUBE
		uniform samplerCube envMap;
	#else
		uniform sampler2D envMap;
	#endif
	
#endif`,ev=`#ifdef USE_ENVMAP
	uniform float reflectivity;
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		varying vec3 vWorldPosition;
		uniform float refractionRatio;
	#else
		varying vec3 vReflect;
	#endif
#endif`,tv=`#ifdef USE_ENVMAP
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		
		varying vec3 vWorldPosition;
	#else
		varying vec3 vReflect;
		uniform float refractionRatio;
	#endif
#endif`,nv=`#ifdef USE_ENVMAP
	#ifdef ENV_WORLDPOS
		vWorldPosition = worldPosition.xyz;
	#else
		vec3 cameraToVertex;
		if ( isOrthographic ) {
			cameraToVertex = normalize( vec3( - viewMatrix[ 0 ][ 2 ], - viewMatrix[ 1 ][ 2 ], - viewMatrix[ 2 ][ 2 ] ) );
		} else {
			cameraToVertex = normalize( worldPosition.xyz - cameraPosition );
		}
		vec3 worldNormal = inverseTransformDirection( transformedNormal, viewMatrix );
		#ifdef ENVMAP_MODE_REFLECTION
			vReflect = reflect( cameraToVertex, worldNormal );
		#else
			vReflect = refract( cameraToVertex, worldNormal, refractionRatio );
		#endif
	#endif
#endif`,iv=`#ifdef USE_FOG
	vFogDepth = - mvPosition.z;
#endif`,sv=`#ifdef USE_FOG
	varying float vFogDepth;
#endif`,rv=`#ifdef USE_FOG
	#ifdef FOG_EXP2
		float fogFactor = 1.0 - exp( - fogDensity * fogDensity * vFogDepth * vFogDepth );
	#else
		float fogFactor = smoothstep( fogNear, fogFar, vFogDepth );
	#endif
	gl_FragColor.rgb = mix( gl_FragColor.rgb, fogColor, fogFactor );
#endif`,ov=`#ifdef USE_FOG
	uniform vec3 fogColor;
	varying float vFogDepth;
	#ifdef FOG_EXP2
		uniform float fogDensity;
	#else
		uniform float fogNear;
		uniform float fogFar;
	#endif
#endif`,av=`#ifdef USE_GRADIENTMAP
	uniform sampler2D gradientMap;
#endif
vec3 getGradientIrradiance( vec3 normal, vec3 lightDirection ) {
	float dotNL = dot( normal, lightDirection );
	vec2 coord = vec2( dotNL * 0.5 + 0.5, 0.0 );
	#ifdef USE_GRADIENTMAP
		return vec3( texture2D( gradientMap, coord ).r );
	#else
		vec2 fw = fwidth( coord ) * 0.5;
		return mix( vec3( 0.7 ), vec3( 1.0 ), smoothstep( 0.7 - fw.x, 0.7 + fw.x, coord.x ) );
	#endif
}`,lv=`#ifdef USE_LIGHTMAP
	vec4 lightMapTexel = texture2D( lightMap, vUv2 );
	vec3 lightMapIrradiance = lightMapTexel.rgb * lightMapIntensity;
	reflectedLight.indirectDiffuse += lightMapIrradiance;
#endif`,cv=`#ifdef USE_LIGHTMAP
	uniform sampler2D lightMap;
	uniform float lightMapIntensity;
#endif`,hv=`LambertMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularStrength = specularStrength;`,uv=`varying vec3 vViewPosition;
struct LambertMaterial {
	vec3 diffuseColor;
	float specularStrength;
};
void RE_Direct_Lambert( const in IncidentLight directLight, const in GeometricContext geometry, const in LambertMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometry.normal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Lambert( const in vec3 irradiance, const in GeometricContext geometry, const in LambertMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_Lambert
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Lambert`,dv=`uniform bool receiveShadow;
uniform vec3 ambientLightColor;
uniform vec3 lightProbe[ 9 ];
vec3 shGetIrradianceAt( in vec3 normal, in vec3 shCoefficients[ 9 ] ) {
	float x = normal.x, y = normal.y, z = normal.z;
	vec3 result = shCoefficients[ 0 ] * 0.886227;
	result += shCoefficients[ 1 ] * 2.0 * 0.511664 * y;
	result += shCoefficients[ 2 ] * 2.0 * 0.511664 * z;
	result += shCoefficients[ 3 ] * 2.0 * 0.511664 * x;
	result += shCoefficients[ 4 ] * 2.0 * 0.429043 * x * y;
	result += shCoefficients[ 5 ] * 2.0 * 0.429043 * y * z;
	result += shCoefficients[ 6 ] * ( 0.743125 * z * z - 0.247708 );
	result += shCoefficients[ 7 ] * 2.0 * 0.429043 * x * z;
	result += shCoefficients[ 8 ] * 0.429043 * ( x * x - y * y );
	return result;
}
vec3 getLightProbeIrradiance( const in vec3 lightProbe[ 9 ], const in vec3 normal ) {
	vec3 worldNormal = inverseTransformDirection( normal, viewMatrix );
	vec3 irradiance = shGetIrradianceAt( worldNormal, lightProbe );
	return irradiance;
}
vec3 getAmbientLightIrradiance( const in vec3 ambientLightColor ) {
	vec3 irradiance = ambientLightColor;
	return irradiance;
}
float getDistanceAttenuation( const in float lightDistance, const in float cutoffDistance, const in float decayExponent ) {
	#if defined ( PHYSICALLY_CORRECT_LIGHTS )
		float distanceFalloff = 1.0 / max( pow( lightDistance, decayExponent ), 0.01 );
		if ( cutoffDistance > 0.0 ) {
			distanceFalloff *= pow2( saturate( 1.0 - pow4( lightDistance / cutoffDistance ) ) );
		}
		return distanceFalloff;
	#else
		if ( cutoffDistance > 0.0 && decayExponent > 0.0 ) {
			return pow( saturate( - lightDistance / cutoffDistance + 1.0 ), decayExponent );
		}
		return 1.0;
	#endif
}
float getSpotAttenuation( const in float coneCosine, const in float penumbraCosine, const in float angleCosine ) {
	return smoothstep( coneCosine, penumbraCosine, angleCosine );
}
#if NUM_DIR_LIGHTS > 0
	struct DirectionalLight {
		vec3 direction;
		vec3 color;
	};
	uniform DirectionalLight directionalLights[ NUM_DIR_LIGHTS ];
	void getDirectionalLightInfo( const in DirectionalLight directionalLight, const in GeometricContext geometry, out IncidentLight light ) {
		light.color = directionalLight.color;
		light.direction = directionalLight.direction;
		light.visible = true;
	}
#endif
#if NUM_POINT_LIGHTS > 0
	struct PointLight {
		vec3 position;
		vec3 color;
		float distance;
		float decay;
	};
	uniform PointLight pointLights[ NUM_POINT_LIGHTS ];
	void getPointLightInfo( const in PointLight pointLight, const in GeometricContext geometry, out IncidentLight light ) {
		vec3 lVector = pointLight.position - geometry.position;
		light.direction = normalize( lVector );
		float lightDistance = length( lVector );
		light.color = pointLight.color;
		light.color *= getDistanceAttenuation( lightDistance, pointLight.distance, pointLight.decay );
		light.visible = ( light.color != vec3( 0.0 ) );
	}
#endif
#if NUM_SPOT_LIGHTS > 0
	struct SpotLight {
		vec3 position;
		vec3 direction;
		vec3 color;
		float distance;
		float decay;
		float coneCos;
		float penumbraCos;
	};
	uniform SpotLight spotLights[ NUM_SPOT_LIGHTS ];
	void getSpotLightInfo( const in SpotLight spotLight, const in GeometricContext geometry, out IncidentLight light ) {
		vec3 lVector = spotLight.position - geometry.position;
		light.direction = normalize( lVector );
		float angleCos = dot( light.direction, spotLight.direction );
		float spotAttenuation = getSpotAttenuation( spotLight.coneCos, spotLight.penumbraCos, angleCos );
		if ( spotAttenuation > 0.0 ) {
			float lightDistance = length( lVector );
			light.color = spotLight.color * spotAttenuation;
			light.color *= getDistanceAttenuation( lightDistance, spotLight.distance, spotLight.decay );
			light.visible = ( light.color != vec3( 0.0 ) );
		} else {
			light.color = vec3( 0.0 );
			light.visible = false;
		}
	}
#endif
#if NUM_RECT_AREA_LIGHTS > 0
	struct RectAreaLight {
		vec3 color;
		vec3 position;
		vec3 halfWidth;
		vec3 halfHeight;
	};
	uniform sampler2D ltc_1;	uniform sampler2D ltc_2;
	uniform RectAreaLight rectAreaLights[ NUM_RECT_AREA_LIGHTS ];
#endif
#if NUM_HEMI_LIGHTS > 0
	struct HemisphereLight {
		vec3 direction;
		vec3 skyColor;
		vec3 groundColor;
	};
	uniform HemisphereLight hemisphereLights[ NUM_HEMI_LIGHTS ];
	vec3 getHemisphereLightIrradiance( const in HemisphereLight hemiLight, const in vec3 normal ) {
		float dotNL = dot( normal, hemiLight.direction );
		float hemiDiffuseWeight = 0.5 * dotNL + 0.5;
		vec3 irradiance = mix( hemiLight.groundColor, hemiLight.skyColor, hemiDiffuseWeight );
		return irradiance;
	}
#endif`,fv=`#if defined( USE_ENVMAP )
	vec3 getIBLIrradiance( const in vec3 normal ) {
		#if defined( ENVMAP_TYPE_CUBE_UV )
			vec3 worldNormal = inverseTransformDirection( normal, viewMatrix );
			vec4 envMapColor = textureCubeUV( envMap, worldNormal, 1.0 );
			return PI * envMapColor.rgb * envMapIntensity;
		#else
			return vec3( 0.0 );
		#endif
	}
	vec3 getIBLRadiance( const in vec3 viewDir, const in vec3 normal, const in float roughness ) {
		#if defined( ENVMAP_TYPE_CUBE_UV )
			vec3 reflectVec = reflect( - viewDir, normal );
			reflectVec = normalize( mix( reflectVec, normal, roughness * roughness) );
			reflectVec = inverseTransformDirection( reflectVec, viewMatrix );
			vec4 envMapColor = textureCubeUV( envMap, reflectVec, roughness );
			return envMapColor.rgb * envMapIntensity;
		#else
			return vec3( 0.0 );
		#endif
	}
#endif`,pv=`ToonMaterial material;
material.diffuseColor = diffuseColor.rgb;`,Av=`varying vec3 vViewPosition;
struct ToonMaterial {
	vec3 diffuseColor;
};
void RE_Direct_Toon( const in IncidentLight directLight, const in GeometricContext geometry, const in ToonMaterial material, inout ReflectedLight reflectedLight ) {
	vec3 irradiance = getGradientIrradiance( geometry.normal, directLight.direction ) * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Toon( const in vec3 irradiance, const in GeometricContext geometry, const in ToonMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_Toon
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Toon`,mv=`BlinnPhongMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularColor = specular;
material.specularShininess = shininess;
material.specularStrength = specularStrength;`,gv=`varying vec3 vViewPosition;
struct BlinnPhongMaterial {
	vec3 diffuseColor;
	vec3 specularColor;
	float specularShininess;
	float specularStrength;
};
void RE_Direct_BlinnPhong( const in IncidentLight directLight, const in GeometricContext geometry, const in BlinnPhongMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometry.normal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
	reflectedLight.directSpecular += irradiance * BRDF_BlinnPhong( directLight.direction, geometry.viewDir, geometry.normal, material.specularColor, material.specularShininess ) * material.specularStrength;
}
void RE_IndirectDiffuse_BlinnPhong( const in vec3 irradiance, const in GeometricContext geometry, const in BlinnPhongMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_BlinnPhong
#define RE_IndirectDiffuse		RE_IndirectDiffuse_BlinnPhong`,_v=`PhysicalMaterial material;
material.diffuseColor = diffuseColor.rgb * ( 1.0 - metalnessFactor );
vec3 dxy = max( abs( dFdx( geometryNormal ) ), abs( dFdy( geometryNormal ) ) );
float geometryRoughness = max( max( dxy.x, dxy.y ), dxy.z );
material.roughness = max( roughnessFactor, 0.0525 );material.roughness += geometryRoughness;
material.roughness = min( material.roughness, 1.0 );
#ifdef IOR
	material.ior = ior;
	#ifdef SPECULAR
		float specularIntensityFactor = specularIntensity;
		vec3 specularColorFactor = specularColor;
		#ifdef USE_SPECULARINTENSITYMAP
			specularIntensityFactor *= texture2D( specularIntensityMap, vUv ).a;
		#endif
		#ifdef USE_SPECULARCOLORMAP
			specularColorFactor *= texture2D( specularColorMap, vUv ).rgb;
		#endif
		material.specularF90 = mix( specularIntensityFactor, 1.0, metalnessFactor );
	#else
		float specularIntensityFactor = 1.0;
		vec3 specularColorFactor = vec3( 1.0 );
		material.specularF90 = 1.0;
	#endif
	material.specularColor = mix( min( pow2( ( material.ior - 1.0 ) / ( material.ior + 1.0 ) ) * specularColorFactor, vec3( 1.0 ) ) * specularIntensityFactor, diffuseColor.rgb, metalnessFactor );
#else
	material.specularColor = mix( vec3( 0.04 ), diffuseColor.rgb, metalnessFactor );
	material.specularF90 = 1.0;
#endif
#ifdef USE_CLEARCOAT
	material.clearcoat = clearcoat;
	material.clearcoatRoughness = clearcoatRoughness;
	material.clearcoatF0 = vec3( 0.04 );
	material.clearcoatF90 = 1.0;
	#ifdef USE_CLEARCOATMAP
		material.clearcoat *= texture2D( clearcoatMap, vUv ).x;
	#endif
	#ifdef USE_CLEARCOAT_ROUGHNESSMAP
		material.clearcoatRoughness *= texture2D( clearcoatRoughnessMap, vUv ).y;
	#endif
	material.clearcoat = saturate( material.clearcoat );	material.clearcoatRoughness = max( material.clearcoatRoughness, 0.0525 );
	material.clearcoatRoughness += geometryRoughness;
	material.clearcoatRoughness = min( material.clearcoatRoughness, 1.0 );
#endif
#ifdef USE_IRIDESCENCE
	material.iridescence = iridescence;
	material.iridescenceIOR = iridescenceIOR;
	#ifdef USE_IRIDESCENCEMAP
		material.iridescence *= texture2D( iridescenceMap, vUv ).r;
	#endif
	#ifdef USE_IRIDESCENCE_THICKNESSMAP
		material.iridescenceThickness = (iridescenceThicknessMaximum - iridescenceThicknessMinimum) * texture2D( iridescenceThicknessMap, vUv ).g + iridescenceThicknessMinimum;
	#else
		material.iridescenceThickness = iridescenceThicknessMaximum;
	#endif
#endif
#ifdef USE_SHEEN
	material.sheenColor = sheenColor;
	#ifdef USE_SHEENCOLORMAP
		material.sheenColor *= texture2D( sheenColorMap, vUv ).rgb;
	#endif
	material.sheenRoughness = clamp( sheenRoughness, 0.07, 1.0 );
	#ifdef USE_SHEENROUGHNESSMAP
		material.sheenRoughness *= texture2D( sheenRoughnessMap, vUv ).a;
	#endif
#endif`,yv=`struct PhysicalMaterial {
	vec3 diffuseColor;
	float roughness;
	vec3 specularColor;
	float specularF90;
	#ifdef USE_CLEARCOAT
		float clearcoat;
		float clearcoatRoughness;
		vec3 clearcoatF0;
		float clearcoatF90;
	#endif
	#ifdef USE_IRIDESCENCE
		float iridescence;
		float iridescenceIOR;
		float iridescenceThickness;
		vec3 iridescenceFresnel;
		vec3 iridescenceF0;
	#endif
	#ifdef USE_SHEEN
		vec3 sheenColor;
		float sheenRoughness;
	#endif
	#ifdef IOR
		float ior;
	#endif
	#ifdef USE_TRANSMISSION
		float transmission;
		float transmissionAlpha;
		float thickness;
		float attenuationDistance;
		vec3 attenuationColor;
	#endif
};
vec3 clearcoatSpecular = vec3( 0.0 );
vec3 sheenSpecular = vec3( 0.0 );
float IBLSheenBRDF( const in vec3 normal, const in vec3 viewDir, const in float roughness ) {
	float dotNV = saturate( dot( normal, viewDir ) );
	float r2 = roughness * roughness;
	float a = roughness < 0.25 ? -339.2 * r2 + 161.4 * roughness - 25.9 : -8.48 * r2 + 14.3 * roughness - 9.95;
	float b = roughness < 0.25 ? 44.0 * r2 - 23.7 * roughness + 3.26 : 1.97 * r2 - 3.27 * roughness + 0.72;
	float DG = exp( a * dotNV + b ) + ( roughness < 0.25 ? 0.0 : 0.1 * ( roughness - 0.25 ) );
	return saturate( DG * RECIPROCAL_PI );
}
vec2 DFGApprox( const in vec3 normal, const in vec3 viewDir, const in float roughness ) {
	float dotNV = saturate( dot( normal, viewDir ) );
	const vec4 c0 = vec4( - 1, - 0.0275, - 0.572, 0.022 );
	const vec4 c1 = vec4( 1, 0.0425, 1.04, - 0.04 );
	vec4 r = roughness * c0 + c1;
	float a004 = min( r.x * r.x, exp2( - 9.28 * dotNV ) ) * r.x + r.y;
	vec2 fab = vec2( - 1.04, 1.04 ) * a004 + r.zw;
	return fab;
}
vec3 EnvironmentBRDF( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float roughness ) {
	vec2 fab = DFGApprox( normal, viewDir, roughness );
	return specularColor * fab.x + specularF90 * fab.y;
}
#ifdef USE_IRIDESCENCE
void computeMultiscatteringIridescence( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float iridescence, const in vec3 iridescenceF0, const in float roughness, inout vec3 singleScatter, inout vec3 multiScatter ) {
#else
void computeMultiscattering( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float roughness, inout vec3 singleScatter, inout vec3 multiScatter ) {
#endif
	vec2 fab = DFGApprox( normal, viewDir, roughness );
	#ifdef USE_IRIDESCENCE
		vec3 Fr = mix( specularColor, iridescenceF0, iridescence );
	#else
		vec3 Fr = specularColor;
	#endif
	vec3 FssEss = Fr * fab.x + specularF90 * fab.y;
	float Ess = fab.x + fab.y;
	float Ems = 1.0 - Ess;
	vec3 Favg = Fr + ( 1.0 - Fr ) * 0.047619;	vec3 Fms = FssEss * Favg / ( 1.0 - Ems * Favg );
	singleScatter += FssEss;
	multiScatter += Fms * Ems;
}
#if NUM_RECT_AREA_LIGHTS > 0
	void RE_Direct_RectArea_Physical( const in RectAreaLight rectAreaLight, const in GeometricContext geometry, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
		vec3 normal = geometry.normal;
		vec3 viewDir = geometry.viewDir;
		vec3 position = geometry.position;
		vec3 lightPos = rectAreaLight.position;
		vec3 halfWidth = rectAreaLight.halfWidth;
		vec3 halfHeight = rectAreaLight.halfHeight;
		vec3 lightColor = rectAreaLight.color;
		float roughness = material.roughness;
		vec3 rectCoords[ 4 ];
		rectCoords[ 0 ] = lightPos + halfWidth - halfHeight;		rectCoords[ 1 ] = lightPos - halfWidth - halfHeight;
		rectCoords[ 2 ] = lightPos - halfWidth + halfHeight;
		rectCoords[ 3 ] = lightPos + halfWidth + halfHeight;
		vec2 uv = LTC_Uv( normal, viewDir, roughness );
		vec4 t1 = texture2D( ltc_1, uv );
		vec4 t2 = texture2D( ltc_2, uv );
		mat3 mInv = mat3(
			vec3( t1.x, 0, t1.y ),
			vec3(    0, 1,    0 ),
			vec3( t1.z, 0, t1.w )
		);
		vec3 fresnel = ( material.specularColor * t2.x + ( vec3( 1.0 ) - material.specularColor ) * t2.y );
		reflectedLight.directSpecular += lightColor * fresnel * LTC_Evaluate( normal, viewDir, position, mInv, rectCoords );
		reflectedLight.directDiffuse += lightColor * material.diffuseColor * LTC_Evaluate( normal, viewDir, position, mat3( 1.0 ), rectCoords );
	}
#endif
void RE_Direct_Physical( const in IncidentLight directLight, const in GeometricContext geometry, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometry.normal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	#ifdef USE_CLEARCOAT
		float dotNLcc = saturate( dot( geometry.clearcoatNormal, directLight.direction ) );
		vec3 ccIrradiance = dotNLcc * directLight.color;
		clearcoatSpecular += ccIrradiance * BRDF_GGX( directLight.direction, geometry.viewDir, geometry.clearcoatNormal, material.clearcoatF0, material.clearcoatF90, material.clearcoatRoughness );
	#endif
	#ifdef USE_SHEEN
		sheenSpecular += irradiance * BRDF_Sheen( directLight.direction, geometry.viewDir, geometry.normal, material.sheenColor, material.sheenRoughness );
	#endif
	#ifdef USE_IRIDESCENCE
		reflectedLight.directSpecular += irradiance * BRDF_GGX_Iridescence( directLight.direction, geometry.viewDir, geometry.normal, material.specularColor, material.specularF90, material.iridescence, material.iridescenceFresnel, material.roughness );
	#else
		reflectedLight.directSpecular += irradiance * BRDF_GGX( directLight.direction, geometry.viewDir, geometry.normal, material.specularColor, material.specularF90, material.roughness );
	#endif
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Physical( const in vec3 irradiance, const in GeometricContext geometry, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectSpecular_Physical( const in vec3 radiance, const in vec3 irradiance, const in vec3 clearcoatRadiance, const in GeometricContext geometry, const in PhysicalMaterial material, inout ReflectedLight reflectedLight) {
	#ifdef USE_CLEARCOAT
		clearcoatSpecular += clearcoatRadiance * EnvironmentBRDF( geometry.clearcoatNormal, geometry.viewDir, material.clearcoatF0, material.clearcoatF90, material.clearcoatRoughness );
	#endif
	#ifdef USE_SHEEN
		sheenSpecular += irradiance * material.sheenColor * IBLSheenBRDF( geometry.normal, geometry.viewDir, material.sheenRoughness );
	#endif
	vec3 singleScattering = vec3( 0.0 );
	vec3 multiScattering = vec3( 0.0 );
	vec3 cosineWeightedIrradiance = irradiance * RECIPROCAL_PI;
	#ifdef USE_IRIDESCENCE
		computeMultiscatteringIridescence( geometry.normal, geometry.viewDir, material.specularColor, material.specularF90, material.iridescence, material.iridescenceFresnel, material.roughness, singleScattering, multiScattering );
	#else
		computeMultiscattering( geometry.normal, geometry.viewDir, material.specularColor, material.specularF90, material.roughness, singleScattering, multiScattering );
	#endif
	vec3 totalScattering = singleScattering + multiScattering;
	vec3 diffuse = material.diffuseColor * ( 1.0 - max( max( totalScattering.r, totalScattering.g ), totalScattering.b ) );
	reflectedLight.indirectSpecular += radiance * singleScattering;
	reflectedLight.indirectSpecular += multiScattering * cosineWeightedIrradiance;
	reflectedLight.indirectDiffuse += diffuse * cosineWeightedIrradiance;
}
#define RE_Direct				RE_Direct_Physical
#define RE_Direct_RectArea		RE_Direct_RectArea_Physical
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Physical
#define RE_IndirectSpecular		RE_IndirectSpecular_Physical
float computeSpecularOcclusion( const in float dotNV, const in float ambientOcclusion, const in float roughness ) {
	return saturate( pow( dotNV + ambientOcclusion, exp2( - 16.0 * roughness - 1.0 ) ) - 1.0 + ambientOcclusion );
}`,xv=`
GeometricContext geometry;
geometry.position = - vViewPosition;
geometry.normal = normal;
geometry.viewDir = ( isOrthographic ) ? vec3( 0, 0, 1 ) : normalize( vViewPosition );
#ifdef USE_CLEARCOAT
	geometry.clearcoatNormal = clearcoatNormal;
#endif
#ifdef USE_IRIDESCENCE
	float dotNVi = saturate( dot( normal, geometry.viewDir ) );
	if ( material.iridescenceThickness == 0.0 ) {
		material.iridescence = 0.0;
	} else {
		material.iridescence = saturate( material.iridescence );
	}
	if ( material.iridescence > 0.0 ) {
		material.iridescenceFresnel = evalIridescence( 1.0, material.iridescenceIOR, dotNVi, material.iridescenceThickness, material.specularColor );
		material.iridescenceF0 = Schlick_to_F0( material.iridescenceFresnel, 1.0, dotNVi );
	}
#endif
IncidentLight directLight;
#if ( NUM_POINT_LIGHTS > 0 ) && defined( RE_Direct )
	PointLight pointLight;
	#if defined( USE_SHADOWMAP ) && NUM_POINT_LIGHT_SHADOWS > 0
	PointLightShadow pointLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_POINT_LIGHTS; i ++ ) {
		pointLight = pointLights[ i ];
		getPointLightInfo( pointLight, geometry, directLight );
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_POINT_LIGHT_SHADOWS )
		pointLightShadow = pointLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getPointShadow( pointShadowMap[ i ], pointLightShadow.shadowMapSize, pointLightShadow.shadowBias, pointLightShadow.shadowRadius, vPointShadowCoord[ i ], pointLightShadow.shadowCameraNear, pointLightShadow.shadowCameraFar ) : 1.0;
		#endif
		RE_Direct( directLight, geometry, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_SPOT_LIGHTS > 0 ) && defined( RE_Direct )
	SpotLight spotLight;
	vec4 spotColor;
	vec3 spotLightCoord;
	bool inSpotLightMap;
	#if defined( USE_SHADOWMAP ) && NUM_SPOT_LIGHT_SHADOWS > 0
	SpotLightShadow spotLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHTS; i ++ ) {
		spotLight = spotLights[ i ];
		getSpotLightInfo( spotLight, geometry, directLight );
		#if ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS )
		#define SPOT_LIGHT_MAP_INDEX UNROLLED_LOOP_INDEX
		#elif ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
		#define SPOT_LIGHT_MAP_INDEX NUM_SPOT_LIGHT_MAPS
		#else
		#define SPOT_LIGHT_MAP_INDEX ( UNROLLED_LOOP_INDEX - NUM_SPOT_LIGHT_SHADOWS + NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS )
		#endif
		#if ( SPOT_LIGHT_MAP_INDEX < NUM_SPOT_LIGHT_MAPS )
			spotLightCoord = vSpotLightCoord[ i ].xyz / vSpotLightCoord[ i ].w;
			inSpotLightMap = all( lessThan( abs( spotLightCoord * 2. - 1. ), vec3( 1.0 ) ) );
			spotColor = texture2D( spotLightMap[ SPOT_LIGHT_MAP_INDEX ], spotLightCoord.xy );
			directLight.color = inSpotLightMap ? directLight.color * spotColor.rgb : directLight.color;
		#endif
		#undef SPOT_LIGHT_MAP_INDEX
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
		spotLightShadow = spotLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getShadow( spotShadowMap[ i ], spotLightShadow.shadowMapSize, spotLightShadow.shadowBias, spotLightShadow.shadowRadius, vSpotLightCoord[ i ] ) : 1.0;
		#endif
		RE_Direct( directLight, geometry, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_DIR_LIGHTS > 0 ) && defined( RE_Direct )
	DirectionalLight directionalLight;
	#if defined( USE_SHADOWMAP ) && NUM_DIR_LIGHT_SHADOWS > 0
	DirectionalLightShadow directionalLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_DIR_LIGHTS; i ++ ) {
		directionalLight = directionalLights[ i ];
		getDirectionalLightInfo( directionalLight, geometry, directLight );
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_DIR_LIGHT_SHADOWS )
		directionalLightShadow = directionalLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getShadow( directionalShadowMap[ i ], directionalLightShadow.shadowMapSize, directionalLightShadow.shadowBias, directionalLightShadow.shadowRadius, vDirectionalShadowCoord[ i ] ) : 1.0;
		#endif
		RE_Direct( directLight, geometry, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_RECT_AREA_LIGHTS > 0 ) && defined( RE_Direct_RectArea )
	RectAreaLight rectAreaLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_RECT_AREA_LIGHTS; i ++ ) {
		rectAreaLight = rectAreaLights[ i ];
		RE_Direct_RectArea( rectAreaLight, geometry, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if defined( RE_IndirectDiffuse )
	vec3 iblIrradiance = vec3( 0.0 );
	vec3 irradiance = getAmbientLightIrradiance( ambientLightColor );
	irradiance += getLightProbeIrradiance( lightProbe, geometry.normal );
	#if ( NUM_HEMI_LIGHTS > 0 )
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_HEMI_LIGHTS; i ++ ) {
			irradiance += getHemisphereLightIrradiance( hemisphereLights[ i ], geometry.normal );
		}
		#pragma unroll_loop_end
	#endif
#endif
#if defined( RE_IndirectSpecular )
	vec3 radiance = vec3( 0.0 );
	vec3 clearcoatRadiance = vec3( 0.0 );
#endif`,vv=`#if defined( RE_IndirectDiffuse )
	#ifdef USE_LIGHTMAP
		vec4 lightMapTexel = texture2D( lightMap, vUv2 );
		vec3 lightMapIrradiance = lightMapTexel.rgb * lightMapIntensity;
		irradiance += lightMapIrradiance;
	#endif
	#if defined( USE_ENVMAP ) && defined( STANDARD ) && defined( ENVMAP_TYPE_CUBE_UV )
		iblIrradiance += getIBLIrradiance( geometry.normal );
	#endif
#endif
#if defined( USE_ENVMAP ) && defined( RE_IndirectSpecular )
	radiance += getIBLRadiance( geometry.viewDir, geometry.normal, material.roughness );
	#ifdef USE_CLEARCOAT
		clearcoatRadiance += getIBLRadiance( geometry.viewDir, geometry.clearcoatNormal, material.clearcoatRoughness );
	#endif
#endif`,Ev=`#if defined( RE_IndirectDiffuse )
	RE_IndirectDiffuse( irradiance, geometry, material, reflectedLight );
#endif
#if defined( RE_IndirectSpecular )
	RE_IndirectSpecular( radiance, iblIrradiance, clearcoatRadiance, geometry, material, reflectedLight );
#endif`,wv=`#if defined( USE_LOGDEPTHBUF ) && defined( USE_LOGDEPTHBUF_EXT )
	gl_FragDepthEXT = vIsPerspective == 0.0 ? gl_FragCoord.z : log2( vFragDepth ) * logDepthBufFC * 0.5;
#endif`,Mv=`#if defined( USE_LOGDEPTHBUF ) && defined( USE_LOGDEPTHBUF_EXT )
	uniform float logDepthBufFC;
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,bv=`#ifdef USE_LOGDEPTHBUF
	#ifdef USE_LOGDEPTHBUF_EXT
		varying float vFragDepth;
		varying float vIsPerspective;
	#else
		uniform float logDepthBufFC;
	#endif
#endif`,Iv=`#ifdef USE_LOGDEPTHBUF
	#ifdef USE_LOGDEPTHBUF_EXT
		vFragDepth = 1.0 + gl_Position.w;
		vIsPerspective = float( isPerspectiveMatrix( projectionMatrix ) );
	#else
		if ( isPerspectiveMatrix( projectionMatrix ) ) {
			gl_Position.z = log2( max( EPSILON, gl_Position.w + 1.0 ) ) * logDepthBufFC - 1.0;
			gl_Position.z *= gl_Position.w;
		}
	#endif
#endif`,Cv=`#ifdef USE_MAP
	vec4 sampledDiffuseColor = texture2D( map, vUv );
	#ifdef DECODE_VIDEO_TEXTURE
		sampledDiffuseColor = vec4( mix( pow( sampledDiffuseColor.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), sampledDiffuseColor.rgb * 0.0773993808, vec3( lessThanEqual( sampledDiffuseColor.rgb, vec3( 0.04045 ) ) ) ), sampledDiffuseColor.w );
	#endif
	diffuseColor *= sampledDiffuseColor;
#endif`,Sv=`#ifdef USE_MAP
	uniform sampler2D map;
#endif`,Tv=`#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
	vec2 uv = ( uvTransform * vec3( gl_PointCoord.x, 1.0 - gl_PointCoord.y, 1 ) ).xy;
#endif
#ifdef USE_MAP
	diffuseColor *= texture2D( map, uv );
#endif
#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, uv ).g;
#endif`,Bv=`#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
	uniform mat3 uvTransform;
#endif
#ifdef USE_MAP
	uniform sampler2D map;
#endif
#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,Rv=`float metalnessFactor = metalness;
#ifdef USE_METALNESSMAP
	vec4 texelMetalness = texture2D( metalnessMap, vUv );
	metalnessFactor *= texelMetalness.b;
#endif`,Dv=`#ifdef USE_METALNESSMAP
	uniform sampler2D metalnessMap;
#endif`,Lv=`#if defined( USE_MORPHCOLORS ) && defined( MORPHTARGETS_TEXTURE )
	vColor *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		#if defined( USE_COLOR_ALPHA )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ) * morphTargetInfluences[ i ];
		#elif defined( USE_COLOR )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ).rgb * morphTargetInfluences[ i ];
		#endif
	}
#endif`,Pv=`#ifdef USE_MORPHNORMALS
	objectNormal *= morphTargetBaseInfluence;
	#ifdef MORPHTARGETS_TEXTURE
		for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
			if ( morphTargetInfluences[ i ] != 0.0 ) objectNormal += getMorph( gl_VertexID, i, 1 ).xyz * morphTargetInfluences[ i ];
		}
	#else
		objectNormal += morphNormal0 * morphTargetInfluences[ 0 ];
		objectNormal += morphNormal1 * morphTargetInfluences[ 1 ];
		objectNormal += morphNormal2 * morphTargetInfluences[ 2 ];
		objectNormal += morphNormal3 * morphTargetInfluences[ 3 ];
	#endif
#endif`,Fv=`#ifdef USE_MORPHTARGETS
	uniform float morphTargetBaseInfluence;
	#ifdef MORPHTARGETS_TEXTURE
		uniform float morphTargetInfluences[ MORPHTARGETS_COUNT ];
		uniform sampler2DArray morphTargetsTexture;
		uniform ivec2 morphTargetsTextureSize;
		vec4 getMorph( const in int vertexIndex, const in int morphTargetIndex, const in int offset ) {
			int texelIndex = vertexIndex * MORPHTARGETS_TEXTURE_STRIDE + offset;
			int y = texelIndex / morphTargetsTextureSize.x;
			int x = texelIndex - y * morphTargetsTextureSize.x;
			ivec3 morphUV = ivec3( x, y, morphTargetIndex );
			return texelFetch( morphTargetsTexture, morphUV, 0 );
		}
	#else
		#ifndef USE_MORPHNORMALS
			uniform float morphTargetInfluences[ 8 ];
		#else
			uniform float morphTargetInfluences[ 4 ];
		#endif
	#endif
#endif`,Ov=`#ifdef USE_MORPHTARGETS
	transformed *= morphTargetBaseInfluence;
	#ifdef MORPHTARGETS_TEXTURE
		for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
			if ( morphTargetInfluences[ i ] != 0.0 ) transformed += getMorph( gl_VertexID, i, 0 ).xyz * morphTargetInfluences[ i ];
		}
	#else
		transformed += morphTarget0 * morphTargetInfluences[ 0 ];
		transformed += morphTarget1 * morphTargetInfluences[ 1 ];
		transformed += morphTarget2 * morphTargetInfluences[ 2 ];
		transformed += morphTarget3 * morphTargetInfluences[ 3 ];
		#ifndef USE_MORPHNORMALS
			transformed += morphTarget4 * morphTargetInfluences[ 4 ];
			transformed += morphTarget5 * morphTargetInfluences[ 5 ];
			transformed += morphTarget6 * morphTargetInfluences[ 6 ];
			transformed += morphTarget7 * morphTargetInfluences[ 7 ];
		#endif
	#endif
#endif`,Nv=`float faceDirection = gl_FrontFacing ? 1.0 : - 1.0;
#ifdef FLAT_SHADED
	vec3 fdx = dFdx( vViewPosition );
	vec3 fdy = dFdy( vViewPosition );
	vec3 normal = normalize( cross( fdx, fdy ) );
#else
	vec3 normal = normalize( vNormal );
	#ifdef DOUBLE_SIDED
		normal = normal * faceDirection;
	#endif
	#ifdef USE_TANGENT
		vec3 tangent = normalize( vTangent );
		vec3 bitangent = normalize( vBitangent );
		#ifdef DOUBLE_SIDED
			tangent = tangent * faceDirection;
			bitangent = bitangent * faceDirection;
		#endif
		#if defined( TANGENTSPACE_NORMALMAP ) || defined( USE_CLEARCOAT_NORMALMAP )
			mat3 vTBN = mat3( tangent, bitangent, normal );
		#endif
	#endif
#endif
vec3 geometryNormal = normal;`,Uv=`#ifdef OBJECTSPACE_NORMALMAP
	normal = texture2D( normalMap, vUv ).xyz * 2.0 - 1.0;
	#ifdef FLIP_SIDED
		normal = - normal;
	#endif
	#ifdef DOUBLE_SIDED
		normal = normal * faceDirection;
	#endif
	normal = normalize( normalMatrix * normal );
#elif defined( TANGENTSPACE_NORMALMAP )
	vec3 mapN = texture2D( normalMap, vUv ).xyz * 2.0 - 1.0;
	mapN.xy *= normalScale;
	#ifdef USE_TANGENT
		normal = normalize( vTBN * mapN );
	#else
		normal = perturbNormal2Arb( - vViewPosition, normal, mapN, faceDirection );
	#endif
#elif defined( USE_BUMPMAP )
	normal = perturbNormalArb( - vViewPosition, normal, dHdxy_fwd(), faceDirection );
#endif`,Qv=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,kv=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,Gv=`#ifndef FLAT_SHADED
	vNormal = normalize( transformedNormal );
	#ifdef USE_TANGENT
		vTangent = normalize( transformedTangent );
		vBitangent = normalize( cross( vNormal, vTangent ) * tangent.w );
	#endif
#endif`,zv=`#ifdef USE_NORMALMAP
	uniform sampler2D normalMap;
	uniform vec2 normalScale;
#endif
#ifdef OBJECTSPACE_NORMALMAP
	uniform mat3 normalMatrix;
#endif
#if ! defined ( USE_TANGENT ) && ( defined ( TANGENTSPACE_NORMALMAP ) || defined ( USE_CLEARCOAT_NORMALMAP ) )
	vec3 perturbNormal2Arb( vec3 eye_pos, vec3 surf_norm, vec3 mapN, float faceDirection ) {
		vec3 q0 = dFdx( eye_pos.xyz );
		vec3 q1 = dFdy( eye_pos.xyz );
		vec2 st0 = dFdx( vUv.st );
		vec2 st1 = dFdy( vUv.st );
		vec3 N = surf_norm;
		vec3 q1perp = cross( q1, N );
		vec3 q0perp = cross( N, q0 );
		vec3 T = q1perp * st0.x + q0perp * st1.x;
		vec3 B = q1perp * st0.y + q0perp * st1.y;
		float det = max( dot( T, T ), dot( B, B ) );
		float scale = ( det == 0.0 ) ? 0.0 : faceDirection * inversesqrt( det );
		return normalize( T * ( mapN.x * scale ) + B * ( mapN.y * scale ) + N * mapN.z );
	}
#endif`,Vv=`#ifdef USE_CLEARCOAT
	vec3 clearcoatNormal = geometryNormal;
#endif`,Hv=`#ifdef USE_CLEARCOAT_NORMALMAP
	vec3 clearcoatMapN = texture2D( clearcoatNormalMap, vUv ).xyz * 2.0 - 1.0;
	clearcoatMapN.xy *= clearcoatNormalScale;
	#ifdef USE_TANGENT
		clearcoatNormal = normalize( vTBN * clearcoatMapN );
	#else
		clearcoatNormal = perturbNormal2Arb( - vViewPosition, clearcoatNormal, clearcoatMapN, faceDirection );
	#endif
#endif`,Wv=`#ifdef USE_CLEARCOATMAP
	uniform sampler2D clearcoatMap;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform sampler2D clearcoatRoughnessMap;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform sampler2D clearcoatNormalMap;
	uniform vec2 clearcoatNormalScale;
#endif`,qv=`#ifdef USE_IRIDESCENCEMAP
	uniform sampler2D iridescenceMap;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform sampler2D iridescenceThicknessMap;
#endif`,Kv=`#ifdef OPAQUE
diffuseColor.a = 1.0;
#endif
#ifdef USE_TRANSMISSION
diffuseColor.a *= material.transmissionAlpha + 0.1;
#endif
gl_FragColor = vec4( outgoingLight, diffuseColor.a );`,$v=`vec3 packNormalToRGB( const in vec3 normal ) {
	return normalize( normal ) * 0.5 + 0.5;
}
vec3 unpackRGBToNormal( const in vec3 rgb ) {
	return 2.0 * rgb.xyz - 1.0;
}
const float PackUpscale = 256. / 255.;const float UnpackDownscale = 255. / 256.;
const vec3 PackFactors = vec3( 256. * 256. * 256., 256. * 256., 256. );
const vec4 UnpackFactors = UnpackDownscale / vec4( PackFactors, 1. );
const float ShiftRight8 = 1. / 256.;
vec4 packDepthToRGBA( const in float v ) {
	vec4 r = vec4( fract( v * PackFactors ), v );
	r.yzw -= r.xyz * ShiftRight8;	return r * PackUpscale;
}
float unpackRGBAToDepth( const in vec4 v ) {
	return dot( v, UnpackFactors );
}
vec2 packDepthToRG( in highp float v ) {
	return packDepthToRGBA( v ).yx;
}
float unpackRGToDepth( const in highp vec2 v ) {
	return unpackRGBAToDepth( vec4( v.xy, 0.0, 0.0 ) );
}
vec4 pack2HalfToRGBA( vec2 v ) {
	vec4 r = vec4( v.x, fract( v.x * 255.0 ), v.y, fract( v.y * 255.0 ) );
	return vec4( r.x - r.y / 255.0, r.y, r.z - r.w / 255.0, r.w );
}
vec2 unpackRGBATo2Half( vec4 v ) {
	return vec2( v.x + ( v.y / 255.0 ), v.z + ( v.w / 255.0 ) );
}
float viewZToOrthographicDepth( const in float viewZ, const in float near, const in float far ) {
	return ( viewZ + near ) / ( near - far );
}
float orthographicDepthToViewZ( const in float linearClipZ, const in float near, const in float far ) {
	return linearClipZ * ( near - far ) - near;
}
float viewZToPerspectiveDepth( const in float viewZ, const in float near, const in float far ) {
	return ( ( near + viewZ ) * far ) / ( ( far - near ) * viewZ );
}
float perspectiveDepthToViewZ( const in float invClipZ, const in float near, const in float far ) {
	return ( near * far ) / ( ( far - near ) * invClipZ - far );
}`,Xv=`#ifdef PREMULTIPLIED_ALPHA
	gl_FragColor.rgb *= gl_FragColor.a;
#endif`,Yv=`vec4 mvPosition = vec4( transformed, 1.0 );
#ifdef USE_INSTANCING
	mvPosition = instanceMatrix * mvPosition;
#endif
mvPosition = modelViewMatrix * mvPosition;
gl_Position = projectionMatrix * mvPosition;`,Jv=`#ifdef DITHERING
	gl_FragColor.rgb = dithering( gl_FragColor.rgb );
#endif`,jv=`#ifdef DITHERING
	vec3 dithering( vec3 color ) {
		float grid_position = rand( gl_FragCoord.xy );
		vec3 dither_shift_RGB = vec3( 0.25 / 255.0, -0.25 / 255.0, 0.25 / 255.0 );
		dither_shift_RGB = mix( 2.0 * dither_shift_RGB, -2.0 * dither_shift_RGB, grid_position );
		return color + dither_shift_RGB;
	}
#endif`,Zv=`float roughnessFactor = roughness;
#ifdef USE_ROUGHNESSMAP
	vec4 texelRoughness = texture2D( roughnessMap, vUv );
	roughnessFactor *= texelRoughness.g;
#endif`,eE=`#ifdef USE_ROUGHNESSMAP
	uniform sampler2D roughnessMap;
#endif`,tE=`#if NUM_SPOT_LIGHT_COORDS > 0
  varying vec4 vSpotLightCoord[ NUM_SPOT_LIGHT_COORDS ];
#endif
#if NUM_SPOT_LIGHT_MAPS > 0
  uniform sampler2D spotLightMap[ NUM_SPOT_LIGHT_MAPS ];
#endif
#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
		uniform sampler2D directionalShadowMap[ NUM_DIR_LIGHT_SHADOWS ];
		varying vec4 vDirectionalShadowCoord[ NUM_DIR_LIGHT_SHADOWS ];
		struct DirectionalLightShadow {
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform DirectionalLightShadow directionalLightShadows[ NUM_DIR_LIGHT_SHADOWS ];
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
		uniform sampler2D spotShadowMap[ NUM_SPOT_LIGHT_SHADOWS ];
		struct SpotLightShadow {
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform SpotLightShadow spotLightShadows[ NUM_SPOT_LIGHT_SHADOWS ];
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		uniform sampler2D pointShadowMap[ NUM_POINT_LIGHT_SHADOWS ];
		varying vec4 vPointShadowCoord[ NUM_POINT_LIGHT_SHADOWS ];
		struct PointLightShadow {
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
			float shadowCameraNear;
			float shadowCameraFar;
		};
		uniform PointLightShadow pointLightShadows[ NUM_POINT_LIGHT_SHADOWS ];
	#endif
	float texture2DCompare( sampler2D depths, vec2 uv, float compare ) {
		return step( compare, unpackRGBAToDepth( texture2D( depths, uv ) ) );
	}
	vec2 texture2DDistribution( sampler2D shadow, vec2 uv ) {
		return unpackRGBATo2Half( texture2D( shadow, uv ) );
	}
	float VSMShadow (sampler2D shadow, vec2 uv, float compare ){
		float occlusion = 1.0;
		vec2 distribution = texture2DDistribution( shadow, uv );
		float hard_shadow = step( compare , distribution.x );
		if (hard_shadow != 1.0 ) {
			float distance = compare - distribution.x ;
			float variance = max( 0.00000, distribution.y * distribution.y );
			float softness_probability = variance / (variance + distance * distance );			softness_probability = clamp( ( softness_probability - 0.3 ) / ( 0.95 - 0.3 ), 0.0, 1.0 );			occlusion = clamp( max( hard_shadow, softness_probability ), 0.0, 1.0 );
		}
		return occlusion;
	}
	float getShadow( sampler2D shadowMap, vec2 shadowMapSize, float shadowBias, float shadowRadius, vec4 shadowCoord ) {
		float shadow = 1.0;
		shadowCoord.xyz /= shadowCoord.w;
		shadowCoord.z += shadowBias;
		bool inFrustum = shadowCoord.x >= 0.0 && shadowCoord.x <= 1.0 && shadowCoord.y >= 0.0 && shadowCoord.y <= 1.0;
		bool frustumTest = inFrustum && shadowCoord.z <= 1.0;
		if ( frustumTest ) {
		#if defined( SHADOWMAP_TYPE_PCF )
			vec2 texelSize = vec2( 1.0 ) / shadowMapSize;
			float dx0 = - texelSize.x * shadowRadius;
			float dy0 = - texelSize.y * shadowRadius;
			float dx1 = + texelSize.x * shadowRadius;
			float dy1 = + texelSize.y * shadowRadius;
			float dx2 = dx0 / 2.0;
			float dy2 = dy0 / 2.0;
			float dx3 = dx1 / 2.0;
			float dy3 = dy1 / 2.0;
			shadow = (
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx0, dy0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( 0.0, dy0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx1, dy0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx2, dy2 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( 0.0, dy2 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx3, dy2 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx0, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx2, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy, shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx3, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx1, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx2, dy3 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( 0.0, dy3 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx3, dy3 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx0, dy1 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( 0.0, dy1 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx1, dy1 ), shadowCoord.z )
			) * ( 1.0 / 17.0 );
		#elif defined( SHADOWMAP_TYPE_PCF_SOFT )
			vec2 texelSize = vec2( 1.0 ) / shadowMapSize;
			float dx = texelSize.x;
			float dy = texelSize.y;
			vec2 uv = shadowCoord.xy;
			vec2 f = fract( uv * shadowMapSize + 0.5 );
			uv -= f * texelSize;
			shadow = (
				texture2DCompare( shadowMap, uv, shadowCoord.z ) +
				texture2DCompare( shadowMap, uv + vec2( dx, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, uv + vec2( 0.0, dy ), shadowCoord.z ) +
				texture2DCompare( shadowMap, uv + texelSize, shadowCoord.z ) +
				mix( texture2DCompare( shadowMap, uv + vec2( -dx, 0.0 ), shadowCoord.z ),
					 texture2DCompare( shadowMap, uv + vec2( 2.0 * dx, 0.0 ), shadowCoord.z ),
					 f.x ) +
				mix( texture2DCompare( shadowMap, uv + vec2( -dx, dy ), shadowCoord.z ),
					 texture2DCompare( shadowMap, uv + vec2( 2.0 * dx, dy ), shadowCoord.z ),
					 f.x ) +
				mix( texture2DCompare( shadowMap, uv + vec2( 0.0, -dy ), shadowCoord.z ),
					 texture2DCompare( shadowMap, uv + vec2( 0.0, 2.0 * dy ), shadowCoord.z ),
					 f.y ) +
				mix( texture2DCompare( shadowMap, uv + vec2( dx, -dy ), shadowCoord.z ),
					 texture2DCompare( shadowMap, uv + vec2( dx, 2.0 * dy ), shadowCoord.z ),
					 f.y ) +
				mix( mix( texture2DCompare( shadowMap, uv + vec2( -dx, -dy ), shadowCoord.z ),
						  texture2DCompare( shadowMap, uv + vec2( 2.0 * dx, -dy ), shadowCoord.z ),
						  f.x ),
					 mix( texture2DCompare( shadowMap, uv + vec2( -dx, 2.0 * dy ), shadowCoord.z ),
						  texture2DCompare( shadowMap, uv + vec2( 2.0 * dx, 2.0 * dy ), shadowCoord.z ),
						  f.x ),
					 f.y )
			) * ( 1.0 / 9.0 );
		#elif defined( SHADOWMAP_TYPE_VSM )
			shadow = VSMShadow( shadowMap, shadowCoord.xy, shadowCoord.z );
		#else
			shadow = texture2DCompare( shadowMap, shadowCoord.xy, shadowCoord.z );
		#endif
		}
		return shadow;
	}
	vec2 cubeToUV( vec3 v, float texelSizeY ) {
		vec3 absV = abs( v );
		float scaleToCube = 1.0 / max( absV.x, max( absV.y, absV.z ) );
		absV *= scaleToCube;
		v *= scaleToCube * ( 1.0 - 2.0 * texelSizeY );
		vec2 planar = v.xy;
		float almostATexel = 1.5 * texelSizeY;
		float almostOne = 1.0 - almostATexel;
		if ( absV.z >= almostOne ) {
			if ( v.z > 0.0 )
				planar.x = 4.0 - v.x;
		} else if ( absV.x >= almostOne ) {
			float signX = sign( v.x );
			planar.x = v.z * signX + 2.0 * signX;
		} else if ( absV.y >= almostOne ) {
			float signY = sign( v.y );
			planar.x = v.x + 2.0 * signY + 2.0;
			planar.y = v.z * signY - 2.0;
		}
		return vec2( 0.125, 0.25 ) * planar + vec2( 0.375, 0.75 );
	}
	float getPointShadow( sampler2D shadowMap, vec2 shadowMapSize, float shadowBias, float shadowRadius, vec4 shadowCoord, float shadowCameraNear, float shadowCameraFar ) {
		vec2 texelSize = vec2( 1.0 ) / ( shadowMapSize * vec2( 4.0, 2.0 ) );
		vec3 lightToPosition = shadowCoord.xyz;
		float dp = ( length( lightToPosition ) - shadowCameraNear ) / ( shadowCameraFar - shadowCameraNear );		dp += shadowBias;
		vec3 bd3D = normalize( lightToPosition );
		#if defined( SHADOWMAP_TYPE_PCF ) || defined( SHADOWMAP_TYPE_PCF_SOFT ) || defined( SHADOWMAP_TYPE_VSM )
			vec2 offset = vec2( - 1, 1 ) * shadowRadius * texelSize.y;
			return (
				texture2DCompare( shadowMap, cubeToUV( bd3D + offset.xyy, texelSize.y ), dp ) +
				texture2DCompare( shadowMap, cubeToUV( bd3D + offset.yyy, texelSize.y ), dp ) +
				texture2DCompare( shadowMap, cubeToUV( bd3D + offset.xyx, texelSize.y ), dp ) +
				texture2DCompare( shadowMap, cubeToUV( bd3D + offset.yyx, texelSize.y ), dp ) +
				texture2DCompare( shadowMap, cubeToUV( bd3D, texelSize.y ), dp ) +
				texture2DCompare( shadowMap, cubeToUV( bd3D + offset.xxy, texelSize.y ), dp ) +
				texture2DCompare( shadowMap, cubeToUV( bd3D + offset.yxy, texelSize.y ), dp ) +
				texture2DCompare( shadowMap, cubeToUV( bd3D + offset.xxx, texelSize.y ), dp ) +
				texture2DCompare( shadowMap, cubeToUV( bd3D + offset.yxx, texelSize.y ), dp )
			) * ( 1.0 / 9.0 );
		#else
			return texture2DCompare( shadowMap, cubeToUV( bd3D, texelSize.y ), dp );
		#endif
	}
#endif`,nE=`#if NUM_SPOT_LIGHT_COORDS > 0
  uniform mat4 spotLightMatrix[ NUM_SPOT_LIGHT_COORDS ];
  varying vec4 vSpotLightCoord[ NUM_SPOT_LIGHT_COORDS ];
#endif
#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
		uniform mat4 directionalShadowMatrix[ NUM_DIR_LIGHT_SHADOWS ];
		varying vec4 vDirectionalShadowCoord[ NUM_DIR_LIGHT_SHADOWS ];
		struct DirectionalLightShadow {
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform DirectionalLightShadow directionalLightShadows[ NUM_DIR_LIGHT_SHADOWS ];
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
		struct SpotLightShadow {
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform SpotLightShadow spotLightShadows[ NUM_SPOT_LIGHT_SHADOWS ];
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		uniform mat4 pointShadowMatrix[ NUM_POINT_LIGHT_SHADOWS ];
		varying vec4 vPointShadowCoord[ NUM_POINT_LIGHT_SHADOWS ];
		struct PointLightShadow {
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
			float shadowCameraNear;
			float shadowCameraFar;
		};
		uniform PointLightShadow pointLightShadows[ NUM_POINT_LIGHT_SHADOWS ];
	#endif
#endif`,iE=`#if ( defined( USE_SHADOWMAP ) && ( NUM_DIR_LIGHT_SHADOWS > 0 || NUM_POINT_LIGHT_SHADOWS > 0 ) ) || ( NUM_SPOT_LIGHT_COORDS > 0 )
	vec3 shadowWorldNormal = inverseTransformDirection( transformedNormal, viewMatrix );
	vec4 shadowWorldPosition;
#endif
#if defined( USE_SHADOWMAP )
	#if NUM_DIR_LIGHT_SHADOWS > 0
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_DIR_LIGHT_SHADOWS; i ++ ) {
			shadowWorldPosition = worldPosition + vec4( shadowWorldNormal * directionalLightShadows[ i ].shadowNormalBias, 0 );
			vDirectionalShadowCoord[ i ] = directionalShadowMatrix[ i ] * shadowWorldPosition;
		}
		#pragma unroll_loop_end
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_POINT_LIGHT_SHADOWS; i ++ ) {
			shadowWorldPosition = worldPosition + vec4( shadowWorldNormal * pointLightShadows[ i ].shadowNormalBias, 0 );
			vPointShadowCoord[ i ] = pointShadowMatrix[ i ] * shadowWorldPosition;
		}
		#pragma unroll_loop_end
	#endif
#endif
#if NUM_SPOT_LIGHT_COORDS > 0
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHT_COORDS; i ++ ) {
		shadowWorldPosition = worldPosition;
		#if ( defined( USE_SHADOWMAP ) && UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
			shadowWorldPosition.xyz += shadowWorldNormal * spotLightShadows[ i ].shadowNormalBias;
		#endif
		vSpotLightCoord[ i ] = spotLightMatrix[ i ] * shadowWorldPosition;
	}
	#pragma unroll_loop_end
#endif`,sE=`float getShadowMask() {
	float shadow = 1.0;
	#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
	DirectionalLightShadow directionalLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_DIR_LIGHT_SHADOWS; i ++ ) {
		directionalLight = directionalLightShadows[ i ];
		shadow *= receiveShadow ? getShadow( directionalShadowMap[ i ], directionalLight.shadowMapSize, directionalLight.shadowBias, directionalLight.shadowRadius, vDirectionalShadowCoord[ i ] ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
	SpotLightShadow spotLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHT_SHADOWS; i ++ ) {
		spotLight = spotLightShadows[ i ];
		shadow *= receiveShadow ? getShadow( spotShadowMap[ i ], spotLight.shadowMapSize, spotLight.shadowBias, spotLight.shadowRadius, vSpotLightCoord[ i ] ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
	PointLightShadow pointLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_POINT_LIGHT_SHADOWS; i ++ ) {
		pointLight = pointLightShadows[ i ];
		shadow *= receiveShadow ? getPointShadow( pointShadowMap[ i ], pointLight.shadowMapSize, pointLight.shadowBias, pointLight.shadowRadius, vPointShadowCoord[ i ], pointLight.shadowCameraNear, pointLight.shadowCameraFar ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#endif
	return shadow;
}`,rE=`#ifdef USE_SKINNING
	mat4 boneMatX = getBoneMatrix( skinIndex.x );
	mat4 boneMatY = getBoneMatrix( skinIndex.y );
	mat4 boneMatZ = getBoneMatrix( skinIndex.z );
	mat4 boneMatW = getBoneMatrix( skinIndex.w );
#endif`,oE=`#ifdef USE_SKINNING
	uniform mat4 bindMatrix;
	uniform mat4 bindMatrixInverse;
	uniform highp sampler2D boneTexture;
	uniform int boneTextureSize;
	mat4 getBoneMatrix( const in float i ) {
		float j = i * 4.0;
		float x = mod( j, float( boneTextureSize ) );
		float y = floor( j / float( boneTextureSize ) );
		float dx = 1.0 / float( boneTextureSize );
		float dy = 1.0 / float( boneTextureSize );
		y = dy * ( y + 0.5 );
		vec4 v1 = texture2D( boneTexture, vec2( dx * ( x + 0.5 ), y ) );
		vec4 v2 = texture2D( boneTexture, vec2( dx * ( x + 1.5 ), y ) );
		vec4 v3 = texture2D( boneTexture, vec2( dx * ( x + 2.5 ), y ) );
		vec4 v4 = texture2D( boneTexture, vec2( dx * ( x + 3.5 ), y ) );
		mat4 bone = mat4( v1, v2, v3, v4 );
		return bone;
	}
#endif`,aE=`#ifdef USE_SKINNING
	vec4 skinVertex = bindMatrix * vec4( transformed, 1.0 );
	vec4 skinned = vec4( 0.0 );
	skinned += boneMatX * skinVertex * skinWeight.x;
	skinned += boneMatY * skinVertex * skinWeight.y;
	skinned += boneMatZ * skinVertex * skinWeight.z;
	skinned += boneMatW * skinVertex * skinWeight.w;
	transformed = ( bindMatrixInverse * skinned ).xyz;
#endif`,lE=`#ifdef USE_SKINNING
	mat4 skinMatrix = mat4( 0.0 );
	skinMatrix += skinWeight.x * boneMatX;
	skinMatrix += skinWeight.y * boneMatY;
	skinMatrix += skinWeight.z * boneMatZ;
	skinMatrix += skinWeight.w * boneMatW;
	skinMatrix = bindMatrixInverse * skinMatrix * bindMatrix;
	objectNormal = vec4( skinMatrix * vec4( objectNormal, 0.0 ) ).xyz;
	#ifdef USE_TANGENT
		objectTangent = vec4( skinMatrix * vec4( objectTangent, 0.0 ) ).xyz;
	#endif
#endif`,cE=`float specularStrength;
#ifdef USE_SPECULARMAP
	vec4 texelSpecular = texture2D( specularMap, vUv );
	specularStrength = texelSpecular.r;
#else
	specularStrength = 1.0;
#endif`,hE=`#ifdef USE_SPECULARMAP
	uniform sampler2D specularMap;
#endif`,uE=`#if defined( TONE_MAPPING )
	gl_FragColor.rgb = toneMapping( gl_FragColor.rgb );
#endif`,dE=`#ifndef saturate
#define saturate( a ) clamp( a, 0.0, 1.0 )
#endif
uniform float toneMappingExposure;
vec3 LinearToneMapping( vec3 color ) {
	return toneMappingExposure * color;
}
vec3 ReinhardToneMapping( vec3 color ) {
	color *= toneMappingExposure;
	return saturate( color / ( vec3( 1.0 ) + color ) );
}
vec3 OptimizedCineonToneMapping( vec3 color ) {
	color *= toneMappingExposure;
	color = max( vec3( 0.0 ), color - 0.004 );
	return pow( ( color * ( 6.2 * color + 0.5 ) ) / ( color * ( 6.2 * color + 1.7 ) + 0.06 ), vec3( 2.2 ) );
}
vec3 RRTAndODTFit( vec3 v ) {
	vec3 a = v * ( v + 0.0245786 ) - 0.000090537;
	vec3 b = v * ( 0.983729 * v + 0.4329510 ) + 0.238081;
	return a / b;
}
vec3 ACESFilmicToneMapping( vec3 color ) {
	const mat3 ACESInputMat = mat3(
		vec3( 0.59719, 0.07600, 0.02840 ),		vec3( 0.35458, 0.90834, 0.13383 ),
		vec3( 0.04823, 0.01566, 0.83777 )
	);
	const mat3 ACESOutputMat = mat3(
		vec3(  1.60475, -0.10208, -0.00327 ),		vec3( -0.53108,  1.10813, -0.07276 ),
		vec3( -0.07367, -0.00605,  1.07602 )
	);
	color *= toneMappingExposure / 0.6;
	color = ACESInputMat * color;
	color = RRTAndODTFit( color );
	color = ACESOutputMat * color;
	return saturate( color );
}
vec3 CustomToneMapping( vec3 color ) { return color; }`,fE=`#ifdef USE_TRANSMISSION
	material.transmission = transmission;
	material.transmissionAlpha = 1.0;
	material.thickness = thickness;
	material.attenuationDistance = attenuationDistance;
	material.attenuationColor = attenuationColor;
	#ifdef USE_TRANSMISSIONMAP
		material.transmission *= texture2D( transmissionMap, vUv ).r;
	#endif
	#ifdef USE_THICKNESSMAP
		material.thickness *= texture2D( thicknessMap, vUv ).g;
	#endif
	vec3 pos = vWorldPosition;
	vec3 v = normalize( cameraPosition - pos );
	vec3 n = inverseTransformDirection( normal, viewMatrix );
	vec4 transmission = getIBLVolumeRefraction(
		n, v, material.roughness, material.diffuseColor, material.specularColor, material.specularF90,
		pos, modelMatrix, viewMatrix, projectionMatrix, material.ior, material.thickness,
		material.attenuationColor, material.attenuationDistance );
	material.transmissionAlpha = mix( material.transmissionAlpha, transmission.a, material.transmission );
	totalDiffuse = mix( totalDiffuse, transmission.rgb, material.transmission );
#endif`,pE=`#ifdef USE_TRANSMISSION
	uniform float transmission;
	uniform float thickness;
	uniform float attenuationDistance;
	uniform vec3 attenuationColor;
	#ifdef USE_TRANSMISSIONMAP
		uniform sampler2D transmissionMap;
	#endif
	#ifdef USE_THICKNESSMAP
		uniform sampler2D thicknessMap;
	#endif
	uniform vec2 transmissionSamplerSize;
	uniform sampler2D transmissionSamplerMap;
	uniform mat4 modelMatrix;
	uniform mat4 projectionMatrix;
	varying vec3 vWorldPosition;
	vec3 getVolumeTransmissionRay( const in vec3 n, const in vec3 v, const in float thickness, const in float ior, const in mat4 modelMatrix ) {
		vec3 refractionVector = refract( - v, normalize( n ), 1.0 / ior );
		vec3 modelScale;
		modelScale.x = length( vec3( modelMatrix[ 0 ].xyz ) );
		modelScale.y = length( vec3( modelMatrix[ 1 ].xyz ) );
		modelScale.z = length( vec3( modelMatrix[ 2 ].xyz ) );
		return normalize( refractionVector ) * thickness * modelScale;
	}
	float applyIorToRoughness( const in float roughness, const in float ior ) {
		return roughness * clamp( ior * 2.0 - 2.0, 0.0, 1.0 );
	}
	vec4 getTransmissionSample( const in vec2 fragCoord, const in float roughness, const in float ior ) {
		float framebufferLod = log2( transmissionSamplerSize.x ) * applyIorToRoughness( roughness, ior );
		#ifdef texture2DLodEXT
			return texture2DLodEXT( transmissionSamplerMap, fragCoord.xy, framebufferLod );
		#else
			return texture2D( transmissionSamplerMap, fragCoord.xy, framebufferLod );
		#endif
	}
	vec3 applyVolumeAttenuation( const in vec3 radiance, const in float transmissionDistance, const in vec3 attenuationColor, const in float attenuationDistance ) {
		if ( isinf( attenuationDistance ) ) {
			return radiance;
		} else {
			vec3 attenuationCoefficient = -log( attenuationColor ) / attenuationDistance;
			vec3 transmittance = exp( - attenuationCoefficient * transmissionDistance );			return transmittance * radiance;
		}
	}
	vec4 getIBLVolumeRefraction( const in vec3 n, const in vec3 v, const in float roughness, const in vec3 diffuseColor,
		const in vec3 specularColor, const in float specularF90, const in vec3 position, const in mat4 modelMatrix,
		const in mat4 viewMatrix, const in mat4 projMatrix, const in float ior, const in float thickness,
		const in vec3 attenuationColor, const in float attenuationDistance ) {
		vec3 transmissionRay = getVolumeTransmissionRay( n, v, thickness, ior, modelMatrix );
		vec3 refractedRayExit = position + transmissionRay;
		vec4 ndcPos = projMatrix * viewMatrix * vec4( refractedRayExit, 1.0 );
		vec2 refractionCoords = ndcPos.xy / ndcPos.w;
		refractionCoords += 1.0;
		refractionCoords /= 2.0;
		vec4 transmittedLight = getTransmissionSample( refractionCoords, roughness, ior );
		vec3 attenuatedColor = applyVolumeAttenuation( transmittedLight.rgb, length( transmissionRay ), attenuationColor, attenuationDistance );
		vec3 F = EnvironmentBRDF( n, v, specularColor, specularF90, roughness );
		return vec4( ( 1.0 - F ) * attenuatedColor * diffuseColor, transmittedLight.a );
	}
#endif`,AE=`#if ( defined( USE_UV ) && ! defined( UVS_VERTEX_ONLY ) )
	varying vec2 vUv;
#endif`,mE=`#ifdef USE_UV
	#ifdef UVS_VERTEX_ONLY
		vec2 vUv;
	#else
		varying vec2 vUv;
	#endif
	uniform mat3 uvTransform;
#endif`,gE=`#ifdef USE_UV
	vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
#endif`,_E=`#if defined( USE_LIGHTMAP ) || defined( USE_AOMAP )
	varying vec2 vUv2;
#endif`,yE=`#if defined( USE_LIGHTMAP ) || defined( USE_AOMAP )
	attribute vec2 uv2;
	varying vec2 vUv2;
	uniform mat3 uv2Transform;
#endif`,xE=`#if defined( USE_LIGHTMAP ) || defined( USE_AOMAP )
	vUv2 = ( uv2Transform * vec3( uv2, 1 ) ).xy;
#endif`,vE=`#if defined( USE_ENVMAP ) || defined( DISTANCE ) || defined ( USE_SHADOWMAP ) || defined ( USE_TRANSMISSION ) || NUM_SPOT_LIGHT_COORDS > 0
	vec4 worldPosition = vec4( transformed, 1.0 );
	#ifdef USE_INSTANCING
		worldPosition = instanceMatrix * worldPosition;
	#endif
	worldPosition = modelMatrix * worldPosition;
#endif`,EE=`varying vec2 vUv;
uniform mat3 uvTransform;
void main() {
	vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	gl_Position = vec4( position.xy, 1.0, 1.0 );
}`,wE=`uniform sampler2D t2D;
uniform float backgroundIntensity;
varying vec2 vUv;
void main() {
	vec4 texColor = texture2D( t2D, vUv );
	#ifdef DECODE_VIDEO_TEXTURE
		texColor = vec4( mix( pow( texColor.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), texColor.rgb * 0.0773993808, vec3( lessThanEqual( texColor.rgb, vec3( 0.04045 ) ) ) ), texColor.w );
	#endif
	texColor.rgb *= backgroundIntensity;
	gl_FragColor = texColor;
	#include <tonemapping_fragment>
	#include <encodings_fragment>
}`,ME=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,bE=`#ifdef ENVMAP_TYPE_CUBE
	uniform samplerCube envMap;
#elif defined( ENVMAP_TYPE_CUBE_UV )
	uniform sampler2D envMap;
#endif
uniform float flipEnvMap;
uniform float backgroundBlurriness;
uniform float backgroundIntensity;
varying vec3 vWorldDirection;
#include <cube_uv_reflection_fragment>
void main() {
	#ifdef ENVMAP_TYPE_CUBE
		vec4 texColor = textureCube( envMap, vec3( flipEnvMap * vWorldDirection.x, vWorldDirection.yz ) );
	#elif defined( ENVMAP_TYPE_CUBE_UV )
		vec4 texColor = textureCubeUV( envMap, vWorldDirection, backgroundBlurriness );
	#else
		vec4 texColor = vec4( 0.0, 0.0, 0.0, 1.0 );
	#endif
	texColor.rgb *= backgroundIntensity;
	gl_FragColor = texColor;
	#include <tonemapping_fragment>
	#include <encodings_fragment>
}`,IE=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,CE=`uniform samplerCube tCube;
uniform float tFlip;
uniform float opacity;
varying vec3 vWorldDirection;
void main() {
	vec4 texColor = textureCube( tCube, vec3( tFlip * vWorldDirection.x, vWorldDirection.yz ) );
	gl_FragColor = texColor;
	gl_FragColor.a *= opacity;
	#include <tonemapping_fragment>
	#include <encodings_fragment>
}`,SE=`#include <common>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
varying vec2 vHighPrecisionZW;
void main() {
	#include <uv_vertex>
	#include <skinbase_vertex>
	#ifdef USE_DISPLACEMENTMAP
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vHighPrecisionZW = gl_Position.zw;
}`,TE=`#if DEPTH_PACKING == 3200
	uniform float opacity;
#endif
#include <common>
#include <packing>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
varying vec2 vHighPrecisionZW;
void main() {
	#include <clipping_planes_fragment>
	vec4 diffuseColor = vec4( 1.0 );
	#if DEPTH_PACKING == 3200
		diffuseColor.a = opacity;
	#endif
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <logdepthbuf_fragment>
	float fragCoordZ = 0.5 * vHighPrecisionZW[0] / vHighPrecisionZW[1] + 0.5;
	#if DEPTH_PACKING == 3200
		gl_FragColor = vec4( vec3( 1.0 - fragCoordZ ), opacity );
	#elif DEPTH_PACKING == 3201
		gl_FragColor = packDepthToRGBA( fragCoordZ );
	#endif
}`,BE=`#define DISTANCE
varying vec3 vWorldPosition;
#include <common>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <skinbase_vertex>
	#ifdef USE_DISPLACEMENTMAP
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <worldpos_vertex>
	#include <clipping_planes_vertex>
	vWorldPosition = worldPosition.xyz;
}`,RE=`#define DISTANCE
uniform vec3 referencePosition;
uniform float nearDistance;
uniform float farDistance;
varying vec3 vWorldPosition;
#include <common>
#include <packing>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <clipping_planes_pars_fragment>
void main () {
	#include <clipping_planes_fragment>
	vec4 diffuseColor = vec4( 1.0 );
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	float dist = length( vWorldPosition - referencePosition );
	dist = ( dist - nearDistance ) / ( farDistance - nearDistance );
	dist = saturate( dist );
	gl_FragColor = packDepthToRGBA( dist );
}`,DE=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
}`,LE=`uniform sampler2D tEquirect;
varying vec3 vWorldDirection;
#include <common>
void main() {
	vec3 direction = normalize( vWorldDirection );
	vec2 sampleUV = equirectUv( direction );
	gl_FragColor = texture2D( tEquirect, sampleUV );
	#include <tonemapping_fragment>
	#include <encodings_fragment>
}`,PE=`uniform float scale;
attribute float lineDistance;
varying float vLineDistance;
#include <common>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	vLineDistance = scale * lineDistance;
	#include <color_vertex>
	#include <morphcolor_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
}`,FE=`uniform vec3 diffuse;
uniform float opacity;
uniform float dashSize;
uniform float totalSize;
varying float vLineDistance;
#include <common>
#include <color_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	#include <clipping_planes_fragment>
	if ( mod( vLineDistance, totalSize ) > dashSize ) {
		discard;
	}
	vec3 outgoingLight = vec3( 0.0 );
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <logdepthbuf_fragment>
	#include <color_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <output_fragment>
	#include <tonemapping_fragment>
	#include <encodings_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
}`,OE=`#include <common>
#include <uv_pars_vertex>
#include <uv2_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <uv2_vertex>
	#include <color_vertex>
	#include <morphcolor_vertex>
	#if defined ( USE_ENVMAP ) || defined ( USE_SKINNING )
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinbase_vertex>
		#include <skinnormal_vertex>
		#include <defaultnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <fog_vertex>
}`,NE=`uniform vec3 diffuse;
uniform float opacity;
#ifndef FLAT_SHADED
	varying vec3 vNormal;
#endif
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <uv2_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <fog_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	#include <clipping_planes_fragment>
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <specularmap_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	#ifdef USE_LIGHTMAP
		vec4 lightMapTexel = texture2D( lightMap, vUv2 );
		reflectedLight.indirectDiffuse += lightMapTexel.rgb * lightMapIntensity * RECIPROCAL_PI;
	#else
		reflectedLight.indirectDiffuse += vec3( 1.0 );
	#endif
	#include <aomap_fragment>
	reflectedLight.indirectDiffuse *= diffuseColor.rgb;
	vec3 outgoingLight = reflectedLight.indirectDiffuse;
	#include <envmap_fragment>
	#include <output_fragment>
	#include <tonemapping_fragment>
	#include <encodings_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,UE=`#define LAMBERT
varying vec3 vViewPosition;
#include <common>
#include <uv_pars_vertex>
#include <uv2_pars_vertex>
#include <displacementmap_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <uv2_vertex>
	#include <color_vertex>
	#include <morphcolor_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,QE=`#define LAMBERT
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float opacity;
#include <common>
#include <packing>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <uv2_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_lambert_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	#include <clipping_planes_fragment>
	vec4 diffuseColor = vec4( diffuse, opacity );
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <specularmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_lambert_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + totalEmissiveRadiance;
	#include <envmap_fragment>
	#include <output_fragment>
	#include <tonemapping_fragment>
	#include <encodings_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,kE=`#define MATCAP
varying vec3 vViewPosition;
#include <common>
#include <uv_pars_vertex>
#include <color_pars_vertex>
#include <displacementmap_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphcolor_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
	vViewPosition = - mvPosition.xyz;
}`,GE=`#define MATCAP
uniform vec3 diffuse;
uniform float opacity;
uniform sampler2D matcap;
varying vec3 vViewPosition;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <fog_pars_fragment>
#include <normal_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	#include <clipping_planes_fragment>
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	vec3 viewDir = normalize( vViewPosition );
	vec3 x = normalize( vec3( viewDir.z, 0.0, - viewDir.x ) );
	vec3 y = cross( viewDir, x );
	vec2 uv = vec2( dot( x, normal ), dot( y, normal ) ) * 0.495 + 0.5;
	#ifdef USE_MATCAP
		vec4 matcapColor = texture2D( matcap, uv );
	#else
		vec4 matcapColor = vec4( vec3( mix( 0.2, 0.8, uv.y ) ), 1.0 );
	#endif
	vec3 outgoingLight = diffuseColor.rgb * matcapColor.rgb;
	#include <output_fragment>
	#include <tonemapping_fragment>
	#include <encodings_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,zE=`#define NORMAL
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( TANGENTSPACE_NORMALMAP )
	varying vec3 vViewPosition;
#endif
#include <common>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( TANGENTSPACE_NORMALMAP )
	vViewPosition = - mvPosition.xyz;
#endif
}`,VE=`#define NORMAL
uniform float opacity;
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( TANGENTSPACE_NORMALMAP )
	varying vec3 vViewPosition;
#endif
#include <packing>
#include <uv_pars_fragment>
#include <normal_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	gl_FragColor = vec4( packNormalToRGB( normal ), opacity );
	#ifdef OPAQUE
		gl_FragColor.a = 1.0;
	#endif
}`,HE=`#define PHONG
varying vec3 vViewPosition;
#include <common>
#include <uv_pars_vertex>
#include <uv2_pars_vertex>
#include <displacementmap_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <uv2_vertex>
	#include <color_vertex>
	#include <morphcolor_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,WE=`#define PHONG
uniform vec3 diffuse;
uniform vec3 emissive;
uniform vec3 specular;
uniform float shininess;
uniform float opacity;
#include <common>
#include <packing>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <uv2_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_phong_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	#include <clipping_planes_fragment>
	vec4 diffuseColor = vec4( diffuse, opacity );
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <specularmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_phong_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + reflectedLight.directSpecular + reflectedLight.indirectSpecular + totalEmissiveRadiance;
	#include <envmap_fragment>
	#include <output_fragment>
	#include <tonemapping_fragment>
	#include <encodings_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,qE=`#define STANDARD
varying vec3 vViewPosition;
#ifdef USE_TRANSMISSION
	varying vec3 vWorldPosition;
#endif
#include <common>
#include <uv_pars_vertex>
#include <uv2_pars_vertex>
#include <displacementmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <uv2_vertex>
	#include <color_vertex>
	#include <morphcolor_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
#ifdef USE_TRANSMISSION
	vWorldPosition = worldPosition.xyz;
#endif
}`,KE=`#define STANDARD
#ifdef PHYSICAL
	#define IOR
	#define SPECULAR
#endif
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float roughness;
uniform float metalness;
uniform float opacity;
#ifdef IOR
	uniform float ior;
#endif
#ifdef SPECULAR
	uniform float specularIntensity;
	uniform vec3 specularColor;
	#ifdef USE_SPECULARINTENSITYMAP
		uniform sampler2D specularIntensityMap;
	#endif
	#ifdef USE_SPECULARCOLORMAP
		uniform sampler2D specularColorMap;
	#endif
#endif
#ifdef USE_CLEARCOAT
	uniform float clearcoat;
	uniform float clearcoatRoughness;
#endif
#ifdef USE_IRIDESCENCE
	uniform float iridescence;
	uniform float iridescenceIOR;
	uniform float iridescenceThicknessMinimum;
	uniform float iridescenceThicknessMaximum;
#endif
#ifdef USE_SHEEN
	uniform vec3 sheenColor;
	uniform float sheenRoughness;
	#ifdef USE_SHEENCOLORMAP
		uniform sampler2D sheenColorMap;
	#endif
	#ifdef USE_SHEENROUGHNESSMAP
		uniform sampler2D sheenRoughnessMap;
	#endif
#endif
varying vec3 vViewPosition;
#include <common>
#include <packing>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <uv2_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <bsdfs>
#include <iridescence_fragment>
#include <cube_uv_reflection_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_physical_pars_fragment>
#include <fog_pars_fragment>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_physical_pars_fragment>
#include <transmission_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <clearcoat_pars_fragment>
#include <iridescence_pars_fragment>
#include <roughnessmap_pars_fragment>
#include <metalnessmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	#include <clipping_planes_fragment>
	vec4 diffuseColor = vec4( diffuse, opacity );
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <roughnessmap_fragment>
	#include <metalnessmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <clearcoat_normal_fragment_begin>
	#include <clearcoat_normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_physical_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 totalDiffuse = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse;
	vec3 totalSpecular = reflectedLight.directSpecular + reflectedLight.indirectSpecular;
	#include <transmission_fragment>
	vec3 outgoingLight = totalDiffuse + totalSpecular + totalEmissiveRadiance;
	#ifdef USE_SHEEN
		float sheenEnergyComp = 1.0 - 0.157 * max3( material.sheenColor );
		outgoingLight = outgoingLight * sheenEnergyComp + sheenSpecular;
	#endif
	#ifdef USE_CLEARCOAT
		float dotNVcc = saturate( dot( geometry.clearcoatNormal, geometry.viewDir ) );
		vec3 Fcc = F_Schlick( material.clearcoatF0, material.clearcoatF90, dotNVcc );
		outgoingLight = outgoingLight * ( 1.0 - material.clearcoat * Fcc ) + clearcoatSpecular * material.clearcoat;
	#endif
	#include <output_fragment>
	#include <tonemapping_fragment>
	#include <encodings_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,$E=`#define TOON
varying vec3 vViewPosition;
#include <common>
#include <uv_pars_vertex>
#include <uv2_pars_vertex>
#include <displacementmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <uv2_vertex>
	#include <color_vertex>
	#include <morphcolor_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,XE=`#define TOON
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float opacity;
#include <common>
#include <packing>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <uv2_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <gradientmap_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_toon_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	#include <clipping_planes_fragment>
	vec4 diffuseColor = vec4( diffuse, opacity );
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_toon_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + totalEmissiveRadiance;
	#include <output_fragment>
	#include <tonemapping_fragment>
	#include <encodings_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,YE=`uniform float size;
uniform float scale;
#include <common>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <color_vertex>
	#include <morphcolor_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <project_vertex>
	gl_PointSize = size;
	#ifdef USE_SIZEATTENUATION
		bool isPerspective = isPerspectiveMatrix( projectionMatrix );
		if ( isPerspective ) gl_PointSize *= ( scale / - mvPosition.z );
	#endif
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <worldpos_vertex>
	#include <fog_vertex>
}`,JE=`uniform vec3 diffuse;
uniform float opacity;
#include <common>
#include <color_pars_fragment>
#include <map_particle_pars_fragment>
#include <alphatest_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	#include <clipping_planes_fragment>
	vec3 outgoingLight = vec3( 0.0 );
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <logdepthbuf_fragment>
	#include <map_particle_fragment>
	#include <color_fragment>
	#include <alphatest_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <output_fragment>
	#include <tonemapping_fragment>
	#include <encodings_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
}`,jE=`#include <common>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
void main() {
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <project_vertex>
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,ZE=`uniform vec3 color;
uniform float opacity;
#include <common>
#include <packing>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <shadowmap_pars_fragment>
#include <shadowmask_pars_fragment>
void main() {
	gl_FragColor = vec4( color, opacity * ( 1.0 - getShadowMask() ) );
	#include <tonemapping_fragment>
	#include <encodings_fragment>
	#include <fog_fragment>
}`,ew=`uniform float rotation;
uniform vec2 center;
#include <common>
#include <uv_pars_vertex>
#include <fog_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	vec4 mvPosition = modelViewMatrix * vec4( 0.0, 0.0, 0.0, 1.0 );
	vec2 scale;
	scale.x = length( vec3( modelMatrix[ 0 ].x, modelMatrix[ 0 ].y, modelMatrix[ 0 ].z ) );
	scale.y = length( vec3( modelMatrix[ 1 ].x, modelMatrix[ 1 ].y, modelMatrix[ 1 ].z ) );
	#ifndef USE_SIZEATTENUATION
		bool isPerspective = isPerspectiveMatrix( projectionMatrix );
		if ( isPerspective ) scale *= - mvPosition.z;
	#endif
	vec2 alignedPosition = ( position.xy - ( center - vec2( 0.5 ) ) ) * scale;
	vec2 rotatedPosition;
	rotatedPosition.x = cos( rotation ) * alignedPosition.x - sin( rotation ) * alignedPosition.y;
	rotatedPosition.y = sin( rotation ) * alignedPosition.x + cos( rotation ) * alignedPosition.y;
	mvPosition.xy += rotatedPosition;
	gl_Position = projectionMatrix * mvPosition;
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
}`,tw=`uniform vec3 diffuse;
uniform float opacity;
#include <common>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	#include <clipping_planes_fragment>
	vec3 outgoingLight = vec3( 0.0 );
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <output_fragment>
	#include <tonemapping_fragment>
	#include <encodings_fragment>
	#include <fog_fragment>
}`,Pe={alphamap_fragment:Mx,alphamap_pars_fragment:bx,alphatest_fragment:Ix,alphatest_pars_fragment:Cx,aomap_fragment:Sx,aomap_pars_fragment:Tx,begin_vertex:Bx,beginnormal_vertex:Rx,bsdfs:Dx,iridescence_fragment:Lx,bumpmap_pars_fragment:Px,clipping_planes_fragment:Fx,clipping_planes_pars_fragment:Ox,clipping_planes_pars_vertex:Nx,clipping_planes_vertex:Ux,color_fragment:Qx,color_pars_fragment:kx,color_pars_vertex:Gx,color_vertex:zx,common:Vx,cube_uv_reflection_fragment:Hx,defaultnormal_vertex:Wx,displacementmap_pars_vertex:qx,displacementmap_vertex:Kx,emissivemap_fragment:$x,emissivemap_pars_fragment:Xx,encodings_fragment:Yx,encodings_pars_fragment:Jx,envmap_fragment:jx,envmap_common_pars_fragment:Zx,envmap_pars_fragment:ev,envmap_pars_vertex:tv,envmap_physical_pars_fragment:fv,envmap_vertex:nv,fog_vertex:iv,fog_pars_vertex:sv,fog_fragment:rv,fog_pars_fragment:ov,gradientmap_pars_fragment:av,lightmap_fragment:lv,lightmap_pars_fragment:cv,lights_lambert_fragment:hv,lights_lambert_pars_fragment:uv,lights_pars_begin:dv,lights_toon_fragment:pv,lights_toon_pars_fragment:Av,lights_phong_fragment:mv,lights_phong_pars_fragment:gv,lights_physical_fragment:_v,lights_physical_pars_fragment:yv,lights_fragment_begin:xv,lights_fragment_maps:vv,lights_fragment_end:Ev,logdepthbuf_fragment:wv,logdepthbuf_pars_fragment:Mv,logdepthbuf_pars_vertex:bv,logdepthbuf_vertex:Iv,map_fragment:Cv,map_pars_fragment:Sv,map_particle_fragment:Tv,map_particle_pars_fragment:Bv,metalnessmap_fragment:Rv,metalnessmap_pars_fragment:Dv,morphcolor_vertex:Lv,morphnormal_vertex:Pv,morphtarget_pars_vertex:Fv,morphtarget_vertex:Ov,normal_fragment_begin:Nv,normal_fragment_maps:Uv,normal_pars_fragment:Qv,normal_pars_vertex:kv,normal_vertex:Gv,normalmap_pars_fragment:zv,clearcoat_normal_fragment_begin:Vv,clearcoat_normal_fragment_maps:Hv,clearcoat_pars_fragment:Wv,iridescence_pars_fragment:qv,output_fragment:Kv,packing:$v,premultiplied_alpha_fragment:Xv,project_vertex:Yv,dithering_fragment:Jv,dithering_pars_fragment:jv,roughnessmap_fragment:Zv,roughnessmap_pars_fragment:eE,shadowmap_pars_fragment:tE,shadowmap_pars_vertex:nE,shadowmap_vertex:iE,shadowmask_pars_fragment:sE,skinbase_vertex:rE,skinning_pars_vertex:oE,skinning_vertex:aE,skinnormal_vertex:lE,specularmap_fragment:cE,specularmap_pars_fragment:hE,tonemapping_fragment:uE,tonemapping_pars_fragment:dE,transmission_fragment:fE,transmission_pars_fragment:pE,uv_pars_fragment:AE,uv_pars_vertex:mE,uv_vertex:gE,uv2_pars_fragment:_E,uv2_pars_vertex:yE,uv2_vertex:xE,worldpos_vertex:vE,background_vert:EE,background_frag:wE,backgroundCube_vert:ME,backgroundCube_frag:bE,cube_vert:IE,cube_frag:CE,depth_vert:SE,depth_frag:TE,distanceRGBA_vert:BE,distanceRGBA_frag:RE,equirect_vert:DE,equirect_frag:LE,linedashed_vert:PE,linedashed_frag:FE,meshbasic_vert:OE,meshbasic_frag:NE,meshlambert_vert:UE,meshlambert_frag:QE,meshmatcap_vert:kE,meshmatcap_frag:GE,meshnormal_vert:zE,meshnormal_frag:VE,meshphong_vert:HE,meshphong_frag:WE,meshphysical_vert:qE,meshphysical_frag:KE,meshtoon_vert:$E,meshtoon_frag:XE,points_vert:YE,points_frag:JE,shadow_vert:jE,shadow_frag:ZE,sprite_vert:ew,sprite_frag:tw},le={common:{diffuse:{value:new Me(16777215)},opacity:{value:1},map:{value:null},uvTransform:{value:new wt},uv2Transform:{value:new wt},alphaMap:{value:null},alphaTest:{value:0}},specularmap:{specularMap:{value:null}},envmap:{envMap:{value:null},flipEnvMap:{value:-1},reflectivity:{value:1},ior:{value:1.5},refractionRatio:{value:.98}},aomap:{aoMap:{value:null},aoMapIntensity:{value:1}},lightmap:{lightMap:{value:null},lightMapIntensity:{value:1}},emissivemap:{emissiveMap:{value:null}},bumpmap:{bumpMap:{value:null},bumpScale:{value:1}},normalmap:{normalMap:{value:null},normalScale:{value:new Be(1,1)}},displacementmap:{displacementMap:{value:null},displacementScale:{value:1},displacementBias:{value:0}},roughnessmap:{roughnessMap:{value:null}},metalnessmap:{metalnessMap:{value:null}},gradientmap:{gradientMap:{value:null}},fog:{fogDensity:{value:25e-5},fogNear:{value:1},fogFar:{value:2e3},fogColor:{value:new Me(16777215)}},lights:{ambientLightColor:{value:[]},lightProbe:{value:[]},directionalLights:{value:[],properties:{direction:{},color:{}}},directionalLightShadows:{value:[],properties:{shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},directionalShadowMap:{value:[]},directionalShadowMatrix:{value:[]},spotLights:{value:[],properties:{color:{},position:{},direction:{},distance:{},coneCos:{},penumbraCos:{},decay:{}}},spotLightShadows:{value:[],properties:{shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},spotLightMap:{value:[]},spotShadowMap:{value:[]},spotLightMatrix:{value:[]},pointLights:{value:[],properties:{color:{},position:{},decay:{},distance:{}}},pointLightShadows:{value:[],properties:{shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{},shadowCameraNear:{},shadowCameraFar:{}}},pointShadowMap:{value:[]},pointShadowMatrix:{value:[]},hemisphereLights:{value:[],properties:{direction:{},skyColor:{},groundColor:{}}},rectAreaLights:{value:[],properties:{color:{},position:{},width:{},height:{}}},ltc_1:{value:null},ltc_2:{value:null}},points:{diffuse:{value:new Me(16777215)},opacity:{value:1},size:{value:1},scale:{value:1},map:{value:null},alphaMap:{value:null},alphaTest:{value:0},uvTransform:{value:new wt}},sprite:{diffuse:{value:new Me(16777215)},opacity:{value:1},center:{value:new Be(.5,.5)},rotation:{value:0},map:{value:null},alphaMap:{value:null},alphaTest:{value:0},uvTransform:{value:new wt}}},si={basic:{uniforms:nn([le.common,le.specularmap,le.envmap,le.aomap,le.lightmap,le.fog]),vertexShader:Pe.meshbasic_vert,fragmentShader:Pe.meshbasic_frag},lambert:{uniforms:nn([le.common,le.specularmap,le.envmap,le.aomap,le.lightmap,le.emissivemap,le.bumpmap,le.normalmap,le.displacementmap,le.fog,le.lights,{emissive:{value:new Me(0)}}]),vertexShader:Pe.meshlambert_vert,fragmentShader:Pe.meshlambert_frag},phong:{uniforms:nn([le.common,le.specularmap,le.envmap,le.aomap,le.lightmap,le.emissivemap,le.bumpmap,le.normalmap,le.displacementmap,le.fog,le.lights,{emissive:{value:new Me(0)},specular:{value:new Me(1118481)},shininess:{value:30}}]),vertexShader:Pe.meshphong_vert,fragmentShader:Pe.meshphong_frag},standard:{uniforms:nn([le.common,le.envmap,le.aomap,le.lightmap,le.emissivemap,le.bumpmap,le.normalmap,le.displacementmap,le.roughnessmap,le.metalnessmap,le.fog,le.lights,{emissive:{value:new Me(0)},roughness:{value:1},metalness:{value:0},envMapIntensity:{value:1}}]),vertexShader:Pe.meshphysical_vert,fragmentShader:Pe.meshphysical_frag},toon:{uniforms:nn([le.common,le.aomap,le.lightmap,le.emissivemap,le.bumpmap,le.normalmap,le.displacementmap,le.gradientmap,le.fog,le.lights,{emissive:{value:new Me(0)}}]),vertexShader:Pe.meshtoon_vert,fragmentShader:Pe.meshtoon_frag},matcap:{uniforms:nn([le.common,le.bumpmap,le.normalmap,le.displacementmap,le.fog,{matcap:{value:null}}]),vertexShader:Pe.meshmatcap_vert,fragmentShader:Pe.meshmatcap_frag},points:{uniforms:nn([le.points,le.fog]),vertexShader:Pe.points_vert,fragmentShader:Pe.points_frag},dashed:{uniforms:nn([le.common,le.fog,{scale:{value:1},dashSize:{value:1},totalSize:{value:2}}]),vertexShader:Pe.linedashed_vert,fragmentShader:Pe.linedashed_frag},depth:{uniforms:nn([le.common,le.displacementmap]),vertexShader:Pe.depth_vert,fragmentShader:Pe.depth_frag},normal:{uniforms:nn([le.common,le.bumpmap,le.normalmap,le.displacementmap,{opacity:{value:1}}]),vertexShader:Pe.meshnormal_vert,fragmentShader:Pe.meshnormal_frag},sprite:{uniforms:nn([le.sprite,le.fog]),vertexShader:Pe.sprite_vert,fragmentShader:Pe.sprite_frag},background:{uniforms:{uvTransform:{value:new wt},t2D:{value:null},backgroundIntensity:{value:1}},vertexShader:Pe.background_vert,fragmentShader:Pe.background_frag},backgroundCube:{uniforms:{envMap:{value:null},flipEnvMap:{value:-1},backgroundBlurriness:{value:0},backgroundIntensity:{value:1}},vertexShader:Pe.backgroundCube_vert,fragmentShader:Pe.backgroundCube_frag},cube:{uniforms:{tCube:{value:null},tFlip:{value:-1},opacity:{value:1}},vertexShader:Pe.cube_vert,fragmentShader:Pe.cube_frag},equirect:{uniforms:{tEquirect:{value:null}},vertexShader:Pe.equirect_vert,fragmentShader:Pe.equirect_frag},distanceRGBA:{uniforms:nn([le.common,le.displacementmap,{referencePosition:{value:new B},nearDistance:{value:1},farDistance:{value:1e3}}]),vertexShader:Pe.distanceRGBA_vert,fragmentShader:Pe.distanceRGBA_frag},shadow:{uniforms:nn([le.lights,le.fog,{color:{value:new Me(0)},opacity:{value:1}}]),vertexShader:Pe.shadow_vert,fragmentShader:Pe.shadow_frag}};si.physical={uniforms:nn([si.standard.uniforms,{clearcoat:{value:0},clearcoatMap:{value:null},clearcoatRoughness:{value:0},clearcoatRoughnessMap:{value:null},clearcoatNormalScale:{value:new Be(1,1)},clearcoatNormalMap:{value:null},iridescence:{value:0},iridescenceMap:{value:null},iridescenceIOR:{value:1.3},iridescenceThicknessMinimum:{value:100},iridescenceThicknessMaximum:{value:400},iridescenceThicknessMap:{value:null},sheen:{value:0},sheenColor:{value:new Me(0)},sheenColorMap:{value:null},sheenRoughness:{value:1},sheenRoughnessMap:{value:null},transmission:{value:0},transmissionMap:{value:null},transmissionSamplerSize:{value:new Be},transmissionSamplerMap:{value:null},thickness:{value:0},thicknessMap:{value:null},attenuationDistance:{value:0},attenuationColor:{value:new Me(0)},specularIntensity:{value:1},specularIntensityMap:{value:null},specularColor:{value:new Me(1,1,1)},specularColorMap:{value:null}}]),vertexShader:Pe.meshphysical_vert,fragmentShader:Pe.meshphysical_frag};var sl={r:0,b:0,g:0};function nw(o,e,t,n,i,s,r){let a=new Me(0),l=s===!0?0:1,c,h,u=null,f=0,p=null;function g(m,_){let E=!1,x=_.isScene===!0?_.background:null;x&&x.isTexture&&(x=(_.backgroundBlurriness>0?t:e).get(x));let y=o.xr,w=y.getSession&&y.getSession();w&&w.environmentBlendMode==="additive"&&(x=null),x===null?A(a,l):x&&x.isColor&&(A(x,1),E=!0),(o.autoClear||E)&&o.clear(o.autoClearColor,o.autoClearDepth,o.autoClearStencil),x&&(x.isCubeTexture||x.mapping===zl)?(h===void 0&&(h=new pe(new $n(1,1,1),new Yt({name:"BackgroundCubeMaterial",uniforms:cr(si.backgroundCube.uniforms),vertexShader:si.backgroundCube.vertexShader,fragmentShader:si.backgroundCube.fragmentShader,side:dt,depthTest:!1,depthWrite:!1,fog:!1})),h.geometry.deleteAttribute("normal"),h.geometry.deleteAttribute("uv"),h.onBeforeRender=function(I,S,v){this.matrixWorld.copyPosition(v.matrixWorld)},Object.defineProperty(h.material,"envMap",{get:d(function(){return this.uniforms.envMap.value},"get")}),i.update(h)),h.material.uniforms.envMap.value=x,h.material.uniforms.flipEnvMap.value=x.isCubeTexture&&x.isRenderTargetTexture===!1?-1:1,h.material.uniforms.backgroundBlurriness.value=_.backgroundBlurriness,h.material.uniforms.backgroundIntensity.value=_.backgroundIntensity,h.material.toneMapped=x.encoding!==Se,(u!==x||f!==x.version||p!==o.toneMapping)&&(h.material.needsUpdate=!0,u=x,f=x.version,p=o.toneMapping),h.layers.enableAll(),m.unshift(h,h.geometry,h.material,0,0,null)):x&&x.isTexture&&(c===void 0&&(c=new pe(new Xn(2,2),new Yt({name:"BackgroundMaterial",uniforms:cr(si.background.uniforms),vertexShader:si.background.vertexShader,fragmentShader:si.background.fragmentShader,side:fn,depthTest:!1,depthWrite:!1,fog:!1})),c.geometry.deleteAttribute("normal"),Object.defineProperty(c.material,"map",{get:d(function(){return this.uniforms.t2D.value},"get")}),i.update(c)),c.material.uniforms.t2D.value=x,c.material.uniforms.backgroundIntensity.value=_.backgroundIntensity,c.material.toneMapped=x.encoding!==Se,x.matrixAutoUpdate===!0&&x.updateMatrix(),c.material.uniforms.uvTransform.value.copy(x.matrix),(u!==x||f!==x.version||p!==o.toneMapping)&&(c.material.needsUpdate=!0,u=x,f=x.version,p=o.toneMapping),c.layers.enableAll(),m.unshift(c,c.geometry,c.material,0,0,null))}d(g,"render");function A(m,_){m.getRGB(sl,$A(o)),n.buffers.color.setClear(sl.r,sl.g,sl.b,_,r)}return d(A,"setClear"),{getClearColor:d(function(){return a},"getClearColor"),setClearColor:d(function(m,_=1){a.set(m),l=_,A(a,l)},"setClearColor"),getClearAlpha:d(function(){return l},"getClearAlpha"),setClearAlpha:d(function(m){l=m,A(a,l)},"setClearAlpha"),render:g}}d(nw,"WebGLBackground");function iw(o,e,t,n){let i=o.getParameter(34921),s=n.isWebGL2?null:e.get("OES_vertex_array_object"),r=n.isWebGL2||s!==null,a={},l=m(null),c=l,h=!1;function u(D,Q,q,H,k){let j=!1;if(r){let Z=A(H,q,Q);c!==Z&&(c=Z,p(c.object)),j=_(D,H,q,k),j&&E(D,H,q,k)}else{let Z=Q.wireframe===!0;(c.geometry!==H.id||c.program!==q.id||c.wireframe!==Z)&&(c.geometry=H.id,c.program=q.id,c.wireframe=Z,j=!0)}k!==null&&t.update(k,34963),(j||h)&&(h=!1,v(D,Q,q,H),k!==null&&o.bindBuffer(34963,t.get(k).buffer))}d(u,"setup");function f(){return n.isWebGL2?o.createVertexArray():s.createVertexArrayOES()}d(f,"createVertexArrayObject");function p(D){return n.isWebGL2?o.bindVertexArray(D):s.bindVertexArrayOES(D)}d(p,"bindVertexArrayObject");function g(D){return n.isWebGL2?o.deleteVertexArray(D):s.deleteVertexArrayOES(D)}d(g,"deleteVertexArrayObject");function A(D,Q,q){let H=q.wireframe===!0,k=a[D.id];k===void 0&&(k={},a[D.id]=k);let j=k[Q.id];j===void 0&&(j={},k[Q.id]=j);let Z=j[H];return Z===void 0&&(Z=m(f()),j[H]=Z),Z}d(A,"getBindingState");function m(D){let Q=[],q=[],H=[];for(let k=0;k<i;k++)Q[k]=0,q[k]=0,H[k]=0;return{geometry:null,program:null,wireframe:!1,newAttributes:Q,enabledAttributes:q,attributeDivisors:H,object:D,attributes:{},index:null}}d(m,"createBindingState");function _(D,Q,q,H){let k=c.attributes,j=Q.attributes,Z=0,fe=q.getAttributes();for(let V in fe)if(fe[V].location>=0){let re=k[V],ie=j[V];if(ie===void 0&&(V==="instanceMatrix"&&D.instanceMatrix&&(ie=D.instanceMatrix),V==="instanceColor"&&D.instanceColor&&(ie=D.instanceColor)),re===void 0||re.attribute!==ie||ie&&re.data!==ie.data)return!0;Z++}return c.attributesNum!==Z||c.index!==H}d(_,"needsUpdate");function E(D,Q,q,H){let k={},j=Q.attributes,Z=0,fe=q.getAttributes();for(let V in fe)if(fe[V].location>=0){let re=j[V];re===void 0&&(V==="instanceMatrix"&&D.instanceMatrix&&(re=D.instanceMatrix),V==="instanceColor"&&D.instanceColor&&(re=D.instanceColor));let ie={};ie.attribute=re,re&&re.data&&(ie.data=re.data),k[V]=ie,Z++}c.attributes=k,c.attributesNum=Z,c.index=H}d(E,"saveCache");function x(){let D=c.newAttributes;for(let Q=0,q=D.length;Q<q;Q++)D[Q]=0}d(x,"initAttributes");function y(D){w(D,0)}d(y,"enableAttribute");function w(D,Q){let q=c.newAttributes,H=c.enabledAttributes,k=c.attributeDivisors;q[D]=1,H[D]===0&&(o.enableVertexAttribArray(D),H[D]=1),k[D]!==Q&&((n.isWebGL2?o:e.get("ANGLE_instanced_arrays"))[n.isWebGL2?"vertexAttribDivisor":"vertexAttribDivisorANGLE"](D,Q),k[D]=Q)}d(w,"enableAttributeAndDivisor");function I(){let D=c.newAttributes,Q=c.enabledAttributes;for(let q=0,H=Q.length;q<H;q++)Q[q]!==D[q]&&(o.disableVertexAttribArray(q),Q[q]=0)}d(I,"disableUnusedAttributes");function S(D,Q,q,H,k,j){n.isWebGL2===!0&&(q===5124||q===5125)?o.vertexAttribIPointer(D,Q,q,k,j):o.vertexAttribPointer(D,Q,q,H,k,j)}d(S,"vertexAttribPointer");function v(D,Q,q,H){if(n.isWebGL2===!1&&(D.isInstancedMesh||H.isInstancedBufferGeometry)&&e.get("ANGLE_instanced_arrays")===null)return;x();let k=H.attributes,j=q.getAttributes(),Z=Q.defaultAttributeValues;for(let fe in j){let V=j[fe];if(V.location>=0){let ee=k[fe];if(ee===void 0&&(fe==="instanceMatrix"&&D.instanceMatrix&&(ee=D.instanceMatrix),fe==="instanceColor"&&D.instanceColor&&(ee=D.instanceColor)),ee!==void 0){let re=ee.normalized,ie=ee.itemSize,W=t.get(ee);if(W===void 0)continue;let Te=W.buffer,Ae=W.type,ge=W.bytesPerElement;if(ee.isInterleavedBufferAttribute){let ce=ee.data,$e=ce.stride,Le=ee.offset;if(ce.isInstancedInterleavedBuffer){for(let Ce=0;Ce<V.locationSize;Ce++)w(V.location+Ce,ce.meshPerAttribute);D.isInstancedMesh!==!0&&H._maxInstanceCount===void 0&&(H._maxInstanceCount=ce.meshPerAttribute*ce.count)}else for(let Ce=0;Ce<V.locationSize;Ce++)y(V.location+Ce);o.bindBuffer(34962,Te);for(let Ce=0;Ce<V.locationSize;Ce++)S(V.location+Ce,ie/V.locationSize,Ae,re,$e*ge,(Le+ie/V.locationSize*Ce)*ge)}else{if(ee.isInstancedBufferAttribute){for(let ce=0;ce<V.locationSize;ce++)w(V.location+ce,ee.meshPerAttribute);D.isInstancedMesh!==!0&&H._maxInstanceCount===void 0&&(H._maxInstanceCount=ee.meshPerAttribute*ee.count)}else for(let ce=0;ce<V.locationSize;ce++)y(V.location+ce);o.bindBuffer(34962,Te);for(let ce=0;ce<V.locationSize;ce++)S(V.location+ce,ie/V.locationSize,Ae,re,ie*ge,ie/V.locationSize*ce*ge)}}else if(Z!==void 0){let re=Z[fe];if(re!==void 0)switch(re.length){case 2:o.vertexAttrib2fv(V.location,re);break;case 3:o.vertexAttrib3fv(V.location,re);break;case 4:o.vertexAttrib4fv(V.location,re);break;default:o.vertexAttrib1fv(V.location,re)}}}}I()}d(v,"setupVertexAttributes");function b(){z();for(let D in a){let Q=a[D];for(let q in Q){let H=Q[q];for(let k in H)g(H[k].object),delete H[k];delete Q[q]}delete a[D]}}d(b,"dispose");function R(D){if(a[D.id]===void 0)return;let Q=a[D.id];for(let q in Q){let H=Q[q];for(let k in H)g(H[k].object),delete H[k];delete Q[q]}delete a[D.id]}d(R,"releaseStatesOfGeometry");function N(D){for(let Q in a){let q=a[Q];if(q[D.id]===void 0)continue;let H=q[D.id];for(let k in H)g(H[k].object),delete H[k];delete q[D.id]}}d(N,"releaseStatesOfProgram");function z(){O(),h=!0,c!==l&&(c=l,p(c.object))}d(z,"reset");function O(){l.geometry=null,l.program=null,l.wireframe=!1}return d(O,"resetDefaultState"),{setup:u,reset:z,resetDefaultState:O,dispose:b,releaseStatesOfGeometry:R,releaseStatesOfProgram:N,initAttributes:x,enableAttribute:y,disableUnusedAttributes:I}}d(iw,"WebGLBindingStates");function sw(o,e,t,n){let i=n.isWebGL2,s;function r(c){s=c}d(r,"setMode");function a(c,h){o.drawArrays(s,c,h),t.update(h,s,1)}d(a,"render");function l(c,h,u){if(u===0)return;let f,p;if(i)f=o,p="drawArraysInstanced";else if(f=e.get("ANGLE_instanced_arrays"),p="drawArraysInstancedANGLE",f===null){console.error("THREE.WebGLBufferRenderer: using THREE.InstancedBufferGeometry but hardware does not support extension ANGLE_instanced_arrays.");return}f[p](s,c,h,u),t.update(h,s,u)}d(l,"renderInstances"),this.setMode=r,this.render=a,this.renderInstances=l}d(sw,"WebGLBufferRenderer");function rw(o,e,t){let n;function i(){if(n!==void 0)return n;if(e.has("EXT_texture_filter_anisotropic")===!0){let S=e.get("EXT_texture_filter_anisotropic");n=o.getParameter(S.MAX_TEXTURE_MAX_ANISOTROPY_EXT)}else n=0;return n}d(i,"getMaxAnisotropy");function s(S){if(S==="highp"){if(o.getShaderPrecisionFormat(35633,36338).precision>0&&o.getShaderPrecisionFormat(35632,36338).precision>0)return"highp";S="mediump"}return S==="mediump"&&o.getShaderPrecisionFormat(35633,36337).precision>0&&o.getShaderPrecisionFormat(35632,36337).precision>0?"mediump":"lowp"}d(s,"getMaxPrecision");let r=typeof WebGL2RenderingContext<"u"&&o instanceof WebGL2RenderingContext,a=t.precision!==void 0?t.precision:"highp",l=s(a);l!==a&&(console.warn("THREE.WebGLRenderer:",a,"not supported, using",l,"instead."),a=l);let c=r||e.has("WEBGL_draw_buffers"),h=t.logarithmicDepthBuffer===!0,u=o.getParameter(34930),f=o.getParameter(35660),p=o.getParameter(3379),g=o.getParameter(34076),A=o.getParameter(34921),m=o.getParameter(36347),_=o.getParameter(36348),E=o.getParameter(36349),x=f>0,y=r||e.has("OES_texture_float"),w=x&&y,I=r?o.getParameter(36183):0;return{isWebGL2:r,drawBuffers:c,getMaxAnisotropy:i,getMaxPrecision:s,precision:a,logarithmicDepthBuffer:h,maxTextures:u,maxVertexTextures:f,maxTextureSize:p,maxCubemapSize:g,maxAttributes:A,maxVertexUniforms:m,maxVaryings:_,maxFragmentUniforms:E,vertexTextures:x,floatFragmentTextures:y,floatVertexTextures:w,maxSamples:I}}d(rw,"WebGLCapabilities");function ow(o){let e=this,t=null,n=0,i=!1,s=!1,r=new yi,a=new wt,l={value:null,needsUpdate:!1};this.uniform=l,this.numPlanes=0,this.numIntersection=0,this.init=function(u,f){let p=u.length!==0||f||n!==0||i;return i=f,n=u.length,p},this.beginShadows=function(){s=!0,h(null)},this.endShadows=function(){s=!1},this.setGlobalState=function(u,f){t=h(u,f,0)},this.setState=function(u,f,p){let g=u.clippingPlanes,A=u.clipIntersection,m=u.clipShadows,_=o.get(u);if(!i||g===null||g.length===0||s&&!m)s?h(null):c();else{let E=s?0:n,x=E*4,y=_.clippingState||null;l.value=y,y=h(g,f,x,p);for(let w=0;w!==x;++w)y[w]=t[w];_.clippingState=y,this.numIntersection=A?this.numPlanes:0,this.numPlanes+=E}};function c(){l.value!==t&&(l.value=t,l.needsUpdate=n>0),e.numPlanes=n,e.numIntersection=0}d(c,"resetGlobalState");function h(u,f,p,g){let A=u!==null?u.length:0,m=null;if(A!==0){if(m=l.value,g!==!0||m===null){let _=p+A*4,E=f.matrixWorldInverse;a.getNormalMatrix(E),(m===null||m.length<_)&&(m=new Float32Array(_));for(let x=0,y=p;x!==A;++x,y+=4)r.copy(u[x]).applyMatrix4(E,a),r.normal.toArray(m,y),m[y+3]=r.constant}l.value=m,l.needsUpdate=!0}return e.numPlanes=A,e.numIntersection=0,m}d(h,"projectPlanes")}d(ow,"WebGLClipping");function aw(o){let e=new WeakMap;function t(r,a){return a===So?r.mapping=ir:a===$h&&(r.mapping=sr),r}d(t,"mapTextureMapping");function n(r){if(r&&r.isTexture&&r.isRenderTargetTexture===!1){let a=r.mapping;if(a===So||a===$h)if(e.has(r)){let l=e.get(r).texture;return t(l,r.mapping)}else{let l=r.image;if(l&&l.height>0){let c=new Es(l.height/2);return c.fromEquirectangularTexture(o,r),e.set(r,c),r.addEventListener("dispose",i),t(c.texture,r.mapping)}else return null}}return r}d(n,"get");function i(r){let a=r.target;a.removeEventListener("dispose",i);let l=e.get(a);l!==void 0&&(e.delete(a),l.dispose())}d(i,"onTextureDispose");function s(){e=new WeakMap}return d(s,"dispose"),{get:n,dispose:s}}d(aw,"WebGLCubeMaps");var Fn=class extends wl{static{d(this,"OrthographicCamera")}constructor(e=-1,t=1,n=1,i=-1,s=.1,r=2e3){super(),this.isOrthographicCamera=!0,this.type="OrthographicCamera",this.zoom=1,this.view=null,this.left=e,this.right=t,this.top=n,this.bottom=i,this.near=s,this.far=r,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.left=e.left,this.right=e.right,this.top=e.top,this.bottom=e.bottom,this.near=e.near,this.far=e.far,this.zoom=e.zoom,this.view=e.view===null?null:Object.assign({},e.view),this}setViewOffset(e,t,n,i,s,r){this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=i,this.view.width=s,this.view.height=r,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){let e=(this.right-this.left)/(2*this.zoom),t=(this.top-this.bottom)/(2*this.zoom),n=(this.right+this.left)/2,i=(this.top+this.bottom)/2,s=n-e,r=n+e,a=i+t,l=i-t;if(this.view!==null&&this.view.enabled){let c=(this.right-this.left)/this.view.fullWidth/this.zoom,h=(this.top-this.bottom)/this.view.fullHeight/this.zoom;s+=c*this.view.offsetX,r=s+c*this.view.width,a-=h*this.view.offsetY,l=a-h*this.view.height}this.projectionMatrix.makeOrthographic(s,r,a,l,this.near,this.far),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){let t=super.toJSON(e);return t.object.zoom=this.zoom,t.object.left=this.left,t.object.right=this.right,t.object.top=this.top,t.object.bottom=this.bottom,t.object.near=this.near,t.object.far=this.far,this.view!==null&&(t.object.view=Object.assign({},this.view)),t}},Zs=4,Jp=[.125,.215,.35,.446,.526,.582],ms=20,Gh=new Fn,jp=new Me,zh=null,As=(1+Math.sqrt(5))/2,Xs=1/As,Zp=[new B(1,1,1),new B(-1,1,1),new B(1,1,-1),new B(-1,1,-1),new B(0,As,Xs),new B(0,As,-Xs),new B(Xs,0,As),new B(-Xs,0,As),new B(As,Xs,0),new B(-As,Xs,0)],bl=class{static{d(this,"PMREMGenerator")}constructor(e){this._renderer=e,this._pingPongRenderTarget=null,this._lodMax=0,this._cubeSize=0,this._lodPlanes=[],this._sizeLods=[],this._sigmas=[],this._blurMaterial=null,this._cubemapMaterial=null,this._equirectMaterial=null,this._compileMaterial(this._blurMaterial)}fromScene(e,t=0,n=.1,i=100){zh=this._renderer.getRenderTarget(),this._setSize(256);let s=this._allocateTargets();return s.depthBuffer=!0,this._sceneToCubeUV(e,n,i,s),t>0&&this._blur(s,0,0,t),this._applyPMREM(s),this._cleanup(s),s}fromEquirectangular(e,t=null){return this._fromTexture(e,t)}fromCubemap(e,t=null){return this._fromTexture(e,t)}compileCubemapShader(){this._cubemapMaterial===null&&(this._cubemapMaterial=nA(),this._compileMaterial(this._cubemapMaterial))}compileEquirectangularShader(){this._equirectMaterial===null&&(this._equirectMaterial=tA(),this._compileMaterial(this._equirectMaterial))}dispose(){this._dispose(),this._cubemapMaterial!==null&&this._cubemapMaterial.dispose(),this._equirectMaterial!==null&&this._equirectMaterial.dispose()}_setSize(e){this._lodMax=Math.floor(Math.log2(e)),this._cubeSize=Math.pow(2,this._lodMax)}_dispose(){this._blurMaterial!==null&&this._blurMaterial.dispose(),this._pingPongRenderTarget!==null&&this._pingPongRenderTarget.dispose();for(let e=0;e<this._lodPlanes.length;e++)this._lodPlanes[e].dispose()}_cleanup(e){this._renderer.setRenderTarget(zh),e.scissorTest=!1,rl(e,0,0,e.width,e.height)}_fromTexture(e,t){e.mapping===ir||e.mapping===sr?this._setSize(e.image.length===0?16:e.image[0].width||e.image[0].image.width):this._setSize(e.image.width/4),zh=this._renderer.getRenderTarget();let n=t||this._allocateTargets();return this._textureToCubeUV(e,n),this._applyPMREM(n),this._cleanup(n),n}_allocateTargets(){let e=3*Math.max(this._cubeSize,112),t=4*this._cubeSize,n={magFilter:Je,minFilter:Je,generateMipmaps:!1,type:Pt,format:lt,encoding:ft,depthBuffer:!1},i=eA(e,t,n);if(this._pingPongRenderTarget===null||this._pingPongRenderTarget.width!==e||this._pingPongRenderTarget.height!==t){this._pingPongRenderTarget!==null&&this._dispose(),this._pingPongRenderTarget=eA(e,t,n);let{_lodMax:s}=this;({sizeLods:this._sizeLods,lodPlanes:this._lodPlanes,sigmas:this._sigmas}=lw(s)),this._blurMaterial=cw(s,e,t)}return i}_compileMaterial(e){let t=new pe(this._lodPlanes[0],e);this._renderer.compile(t,Gh)}_sceneToCubeUV(e,t,n,i){let a=new ht(90,1,t,n),l=[1,-1,1,1,1,1],c=[1,1,1,-1,-1,-1],h=this._renderer,u=h.autoClear,f=h.toneMapping;h.getClearColor(jp),h.toneMapping=qn,h.autoClear=!1;let p=new Ft({name:"PMREM.Background",side:dt,depthWrite:!1,depthTest:!1}),g=new pe(new $n,p),A=!1,m=e.background;m?m.isColor&&(p.color.copy(m),e.background=null,A=!0):(p.color.copy(jp),A=!0);for(let _=0;_<6;_++){let E=_%3;E===0?(a.up.set(0,l[_],0),a.lookAt(c[_],0,0)):E===1?(a.up.set(0,0,l[_]),a.lookAt(0,c[_],0)):(a.up.set(0,l[_],0),a.lookAt(0,0,c[_]));let x=this._cubeSize;rl(i,E*x,_>2?x:0,x,x),h.setRenderTarget(i),A&&h.render(g,a),h.render(e,a)}g.geometry.dispose(),g.material.dispose(),h.toneMapping=f,h.autoClear=u,e.background=m}_textureToCubeUV(e,t){let n=this._renderer,i=e.mapping===ir||e.mapping===sr;i?(this._cubemapMaterial===null&&(this._cubemapMaterial=nA()),this._cubemapMaterial.uniforms.flipEnvMap.value=e.isRenderTargetTexture===!1?-1:1):this._equirectMaterial===null&&(this._equirectMaterial=tA());let s=i?this._cubemapMaterial:this._equirectMaterial,r=new pe(this._lodPlanes[0],s),a=s.uniforms;a.envMap.value=e;let l=this._cubeSize;rl(t,0,0,3*l,2*l),n.setRenderTarget(t),n.render(r,Gh)}_applyPMREM(e){let t=this._renderer,n=t.autoClear;t.autoClear=!1;for(let i=1;i<this._lodPlanes.length;i++){let s=Math.sqrt(this._sigmas[i]*this._sigmas[i]-this._sigmas[i-1]*this._sigmas[i-1]),r=Zp[(i-1)%Zp.length];this._blur(e,i-1,i,s,r)}t.autoClear=n}_blur(e,t,n,i,s){let r=this._pingPongRenderTarget;this._halfBlur(e,r,t,n,i,"latitudinal",s),this._halfBlur(r,e,n,n,i,"longitudinal",s)}_halfBlur(e,t,n,i,s,r,a){let l=this._renderer,c=this._blurMaterial;r!=="latitudinal"&&r!=="longitudinal"&&console.error("blur direction must be either latitudinal or longitudinal!");let h=3,u=new pe(this._lodPlanes[i],c),f=c.uniforms,p=this._sizeLods[n]-1,g=isFinite(s)?Math.PI/(2*p):2*Math.PI/(2*ms-1),A=s/g,m=isFinite(s)?1+Math.floor(h*A):ms;m>ms&&console.warn(`sigmaRadians, ${s}, is too large and will clip, as it requested ${m} samples when the maximum is set to ${ms}`);let _=[],E=0;for(let S=0;S<ms;++S){let v=S/A,b=Math.exp(-v*v/2);_.push(b),S===0?E+=b:S<m&&(E+=2*b)}for(let S=0;S<_.length;S++)_[S]=_[S]/E;f.envMap.value=e.texture,f.samples.value=m,f.weights.value=_,f.latitudinal.value=r==="latitudinal",a&&(f.poleAxis.value=a);let{_lodMax:x}=this;f.dTheta.value=g,f.mipInt.value=x-n;let y=this._sizeLods[i],w=3*y*(i>x-Zs?i-x+Zs:0),I=4*(this._cubeSize-y);rl(t,w,I,3*y,2*y),l.setRenderTarget(t),l.render(u,Gh)}};function lw(o){let e=[],t=[],n=[],i=o,s=o-Zs+1+Jp.length;for(let r=0;r<s;r++){let a=Math.pow(2,i);t.push(a);let l=1/a;r>o-Zs?l=Jp[r-o+Zs-1]:r===0&&(l=0),n.push(l);let c=1/(a-2),h=-c,u=1+c,f=[h,h,u,h,u,u,h,h,u,u,h,u],p=6,g=6,A=3,m=2,_=1,E=new Float32Array(A*g*p),x=new Float32Array(m*g*p),y=new Float32Array(_*g*p);for(let I=0;I<p;I++){let S=I%3*2/3-1,v=I>2?0:-1,b=[S,v,0,S+2/3,v,0,S+2/3,v+1,0,S,v,0,S+2/3,v+1,0,S,v+1,0];E.set(b,A*g*I),x.set(f,m*g*I);let R=[I,I,I,I,I,I];y.set(R,_*g*I)}let w=new kt;w.setAttribute("position",new je(E,A)),w.setAttribute("uv",new je(x,m)),w.setAttribute("faceIndex",new je(y,_)),e.push(w),i>Zs&&i--}return{lodPlanes:e,sizeLods:t,sigmas:n}}d(lw,"_createPlanes");function eA(o,e,t){let n=new Xt(o,e,t);return n.texture.mapping=zl,n.texture.name="PMREM.cubeUv",n.scissorTest=!0,n}d(eA,"_createRenderTarget");function rl(o,e,t,n,i){o.viewport.set(e,t,n,i),o.scissor.set(e,t,n,i)}d(rl,"_setViewport");function cw(o,e,t){let n=new Float32Array(ms),i=new B(0,1,0);return new Yt({name:"SphericalGaussianBlur",defines:{n:ms,CUBEUV_TEXEL_WIDTH:1/e,CUBEUV_TEXEL_HEIGHT:1/t,CUBEUV_MAX_MIP:`${o}.0`},uniforms:{envMap:{value:null},samples:{value:1},weights:{value:n},latitudinal:{value:!1},dTheta:{value:0},mipInt:{value:0},poleAxis:{value:i}},vertexShader:Bu(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			varying vec3 vOutputDirection;

			uniform sampler2D envMap;
			uniform int samples;
			uniform float weights[ n ];
			uniform bool latitudinal;
			uniform float dTheta;
			uniform float mipInt;
			uniform vec3 poleAxis;

			#define ENVMAP_TYPE_CUBE_UV
			#include <cube_uv_reflection_fragment>

			vec3 getSample( float theta, vec3 axis ) {

				float cosTheta = cos( theta );
				// Rodrigues' axis-angle rotation
				vec3 sampleDirection = vOutputDirection * cosTheta
					+ cross( axis, vOutputDirection ) * sin( theta )
					+ axis * dot( axis, vOutputDirection ) * ( 1.0 - cosTheta );

				return bilinearCubeUV( envMap, sampleDirection, mipInt );

			}

			void main() {

				vec3 axis = latitudinal ? poleAxis : cross( poleAxis, vOutputDirection );

				if ( all( equal( axis, vec3( 0.0 ) ) ) ) {

					axis = vec3( vOutputDirection.z, 0.0, - vOutputDirection.x );

				}

				axis = normalize( axis );

				gl_FragColor = vec4( 0.0, 0.0, 0.0, 1.0 );
				gl_FragColor.rgb += weights[ 0 ] * getSample( 0.0, axis );

				for ( int i = 1; i < n; i++ ) {

					if ( i >= samples ) {

						break;

					}

					float theta = dTheta * float( i );
					gl_FragColor.rgb += weights[ i ] * getSample( -1.0 * theta, axis );
					gl_FragColor.rgb += weights[ i ] * getSample( theta, axis );

				}

			}
		`,blending:ri,depthTest:!1,depthWrite:!1})}d(cw,"_getBlurShader");function tA(){return new Yt({name:"EquirectangularToCubeUV",uniforms:{envMap:{value:null}},vertexShader:Bu(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			varying vec3 vOutputDirection;

			uniform sampler2D envMap;

			#include <common>

			void main() {

				vec3 outputDirection = normalize( vOutputDirection );
				vec2 uv = equirectUv( outputDirection );

				gl_FragColor = vec4( texture2D ( envMap, uv ).rgb, 1.0 );

			}
		`,blending:ri,depthTest:!1,depthWrite:!1})}d(tA,"_getEquirectMaterial");function nA(){return new Yt({name:"CubemapToCubeUV",uniforms:{envMap:{value:null},flipEnvMap:{value:-1}},vertexShader:Bu(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			uniform float flipEnvMap;

			varying vec3 vOutputDirection;

			uniform samplerCube envMap;

			void main() {

				gl_FragColor = textureCube( envMap, vec3( flipEnvMap * vOutputDirection.x, vOutputDirection.yz ) );

			}
		`,blending:ri,depthTest:!1,depthWrite:!1})}d(nA,"_getCubemapMaterial");function Bu(){return`

		precision mediump float;
		precision mediump int;

		attribute float faceIndex;

		varying vec3 vOutputDirection;

		// RH coordinate system; PMREM face-indexing convention
		vec3 getDirection( vec2 uv, float face ) {

			uv = 2.0 * uv - 1.0;

			vec3 direction = vec3( uv, 1.0 );

			if ( face == 0.0 ) {

				direction = direction.zyx; // ( 1, v, u ) pos x

			} else if ( face == 1.0 ) {

				direction = direction.xzy;
				direction.xz *= -1.0; // ( -u, 1, -v ) pos y

			} else if ( face == 2.0 ) {

				direction.x *= -1.0; // ( -u, v, 1 ) pos z

			} else if ( face == 3.0 ) {

				direction = direction.zyx;
				direction.xz *= -1.0; // ( -1, v, -u ) neg x

			} else if ( face == 4.0 ) {

				direction = direction.xzy;
				direction.xy *= -1.0; // ( -u, -1, v ) neg y

			} else if ( face == 5.0 ) {

				direction.z *= -1.0; // ( u, v, -1 ) neg z

			}

			return direction;

		}

		void main() {

			vOutputDirection = getDirection( uv, faceIndex );
			gl_Position = vec4( position, 1.0 );

		}
	`}d(Bu,"_getCommonVertexShader");function hw(o){let e=new WeakMap,t=null;function n(a){if(a&&a.isTexture){let l=a.mapping,c=l===So||l===$h,h=l===ir||l===sr;if(c||h)if(a.isRenderTargetTexture&&a.needsPMREMUpdate===!0){a.needsPMREMUpdate=!1;let u=e.get(a);return t===null&&(t=new bl(o)),u=c?t.fromEquirectangular(a,u):t.fromCubemap(a,u),e.set(a,u),u.texture}else{if(e.has(a))return e.get(a).texture;{let u=a.image;if(c&&u&&u.height>0||h&&u&&i(u)){t===null&&(t=new bl(o));let f=c?t.fromEquirectangular(a):t.fromCubemap(a);return e.set(a,f),a.addEventListener("dispose",s),f.texture}else return null}}}return a}d(n,"get");function i(a){let l=0,c=6;for(let h=0;h<c;h++)a[h]!==void 0&&l++;return l===c}d(i,"isCubeTextureComplete");function s(a){let l=a.target;l.removeEventListener("dispose",s);let c=e.get(l);c!==void 0&&(e.delete(l),c.dispose())}d(s,"onTextureDispose");function r(){e=new WeakMap,t!==null&&(t.dispose(),t=null)}return d(r,"dispose"),{get:n,dispose:r}}d(hw,"WebGLCubeUVMaps");function uw(o){let e={};function t(n){if(e[n]!==void 0)return e[n];let i;switch(n){case"WEBGL_depth_texture":i=o.getExtension("WEBGL_depth_texture")||o.getExtension("MOZ_WEBGL_depth_texture")||o.getExtension("WEBKIT_WEBGL_depth_texture");break;case"EXT_texture_filter_anisotropic":i=o.getExtension("EXT_texture_filter_anisotropic")||o.getExtension("MOZ_EXT_texture_filter_anisotropic")||o.getExtension("WEBKIT_EXT_texture_filter_anisotropic");break;case"WEBGL_compressed_texture_s3tc":i=o.getExtension("WEBGL_compressed_texture_s3tc")||o.getExtension("MOZ_WEBGL_compressed_texture_s3tc")||o.getExtension("WEBKIT_WEBGL_compressed_texture_s3tc");break;case"WEBGL_compressed_texture_pvrtc":i=o.getExtension("WEBGL_compressed_texture_pvrtc")||o.getExtension("WEBKIT_WEBGL_compressed_texture_pvrtc");break;default:i=o.getExtension(n)}return e[n]=i,i}return d(t,"getExtension"),{has:d(function(n){return t(n)!==null},"has"),init:d(function(n){n.isWebGL2?t("EXT_color_buffer_float"):(t("WEBGL_depth_texture"),t("OES_texture_float"),t("OES_texture_half_float"),t("OES_texture_half_float_linear"),t("OES_standard_derivatives"),t("OES_element_index_uint"),t("OES_vertex_array_object"),t("ANGLE_instanced_arrays")),t("OES_texture_float_linear"),t("EXT_color_buffer_half_float"),t("WEBGL_multisampled_render_to_texture")},"init"),get:d(function(n){let i=t(n);return i===null&&console.warn("THREE.WebGLRenderer: "+n+" extension not supported."),i},"get")}}d(uw,"WebGLExtensions");function dw(o,e,t,n){let i={},s=new WeakMap;function r(u){let f=u.target;f.index!==null&&e.remove(f.index);for(let g in f.attributes)e.remove(f.attributes[g]);f.removeEventListener("dispose",r),delete i[f.id];let p=s.get(f);p&&(e.remove(p),s.delete(f)),n.releaseStatesOfGeometry(f),f.isInstancedBufferGeometry===!0&&delete f._maxInstanceCount,t.memory.geometries--}d(r,"onGeometryDispose");function a(u,f){return i[f.id]===!0||(f.addEventListener("dispose",r),i[f.id]=!0,t.memory.geometries++),f}d(a,"get");function l(u){let f=u.attributes;for(let g in f)e.update(f[g],34962);let p=u.morphAttributes;for(let g in p){let A=p[g];for(let m=0,_=A.length;m<_;m++)e.update(A[m],34962)}}d(l,"update");function c(u){let f=[],p=u.index,g=u.attributes.position,A=0;if(p!==null){let E=p.array;A=p.version;for(let x=0,y=E.length;x<y;x+=3){let w=E[x+0],I=E[x+1],S=E[x+2];f.push(w,I,I,S,S,w)}}else{let E=g.array;A=g.version;for(let x=0,y=E.length/3-1;x<y;x+=3){let w=x+0,I=x+1,S=x+2;f.push(w,I,I,S,S,w)}}let m=new(qA(f)?El:vl)(f,1);m.version=A;let _=s.get(u);_&&e.remove(_),s.set(u,m)}d(c,"updateWireframeAttribute");function h(u){let f=s.get(u);if(f){let p=u.index;p!==null&&f.version<p.version&&c(u)}else c(u);return s.get(u)}return d(h,"getWireframeAttribute"),{get:a,update:l,getWireframeAttribute:h}}d(dw,"WebGLGeometries");function fw(o,e,t,n){let i=n.isWebGL2,s;function r(f){s=f}d(r,"setMode");let a,l;function c(f){a=f.type,l=f.bytesPerElement}d(c,"setIndex");function h(f,p){o.drawElements(s,p,a,f*l),t.update(p,s,1)}d(h,"render");function u(f,p,g){if(g===0)return;let A,m;if(i)A=o,m="drawElementsInstanced";else if(A=e.get("ANGLE_instanced_arrays"),m="drawElementsInstancedANGLE",A===null){console.error("THREE.WebGLIndexedBufferRenderer: using THREE.InstancedBufferGeometry but hardware does not support extension ANGLE_instanced_arrays.");return}A[m](s,p,a,f*l,g),t.update(p,s,g)}d(u,"renderInstances"),this.setMode=r,this.setIndex=c,this.render=h,this.renderInstances=u}d(fw,"WebGLIndexedBufferRenderer");function pw(o){let e={geometries:0,textures:0},t={frame:0,calls:0,triangles:0,points:0,lines:0};function n(s,r,a){switch(t.calls++,r){case 4:t.triangles+=a*(s/3);break;case 1:t.lines+=a*(s/2);break;case 3:t.lines+=a*(s-1);break;case 2:t.lines+=a*s;break;case 0:t.points+=a*s;break;default:console.error("THREE.WebGLInfo: Unknown draw mode:",r);break}}d(n,"update");function i(){t.frame++,t.calls=0,t.triangles=0,t.points=0,t.lines=0}return d(i,"reset"),{memory:e,render:t,programs:null,autoReset:!0,reset:i,update:n}}d(pw,"WebGLInfo");function Aw(o,e){return o[0]-e[0]}d(Aw,"numericalSort");function mw(o,e){return Math.abs(e[1])-Math.abs(o[1])}d(mw,"absNumericalSort");function gw(o,e,t){let n={},i=new Float32Array(8),s=new WeakMap,r=new nt,a=[];for(let c=0;c<8;c++)a[c]=[c,0];function l(c,h,u,f){let p=c.morphTargetInfluences;if(e.isWebGL2===!0){let g=h.morphAttributes.position||h.morphAttributes.normal||h.morphAttributes.color,A=g!==void 0?g.length:0,m=s.get(h);if(m===void 0||m.count!==A){let Q=function(){O.dispose(),s.delete(h),h.removeEventListener("dispose",Q)};d(Q,"disposeTexture"),m!==void 0&&m.texture.dispose();let x=h.morphAttributes.position!==void 0,y=h.morphAttributes.normal!==void 0,w=h.morphAttributes.color!==void 0,I=h.morphAttributes.position||[],S=h.morphAttributes.normal||[],v=h.morphAttributes.color||[],b=0;x===!0&&(b=1),y===!0&&(b=2),w===!0&&(b=3);let R=h.attributes.position.count*b,N=1;R>e.maxTextureSize&&(N=Math.ceil(R/e.maxTextureSize),R=e.maxTextureSize);let z=new Float32Array(R*N*4*A),O=new xl(z,R,N,A);O.type=Ut,O.needsUpdate=!0;let D=b*4;for(let q=0;q<A;q++){let H=I[q],k=S[q],j=v[q],Z=R*N*4*q;for(let fe=0;fe<H.count;fe++){let V=fe*D;x===!0&&(r.fromBufferAttribute(H,fe),z[Z+V+0]=r.x,z[Z+V+1]=r.y,z[Z+V+2]=r.z,z[Z+V+3]=0),y===!0&&(r.fromBufferAttribute(k,fe),z[Z+V+4]=r.x,z[Z+V+5]=r.y,z[Z+V+6]=r.z,z[Z+V+7]=0),w===!0&&(r.fromBufferAttribute(j,fe),z[Z+V+8]=r.x,z[Z+V+9]=r.y,z[Z+V+10]=r.z,z[Z+V+11]=j.itemSize===4?r.w:1)}}m={count:A,texture:O,size:new Be(R,N)},s.set(h,m),h.addEventListener("dispose",Q)}let _=0;for(let x=0;x<p.length;x++)_+=p[x];let E=h.morphTargetsRelative?1:1-_;f.getUniforms().setValue(o,"morphTargetBaseInfluence",E),f.getUniforms().setValue(o,"morphTargetInfluences",p),f.getUniforms().setValue(o,"morphTargetsTexture",m.texture,t),f.getUniforms().setValue(o,"morphTargetsTextureSize",m.size)}else{let g=p===void 0?0:p.length,A=n[h.id];if(A===void 0||A.length!==g){A=[];for(let y=0;y<g;y++)A[y]=[y,0];n[h.id]=A}for(let y=0;y<g;y++){let w=A[y];w[0]=y,w[1]=p[y]}A.sort(mw);for(let y=0;y<8;y++)y<g&&A[y][1]?(a[y][0]=A[y][0],a[y][1]=A[y][1]):(a[y][0]=Number.MAX_SAFE_INTEGER,a[y][1]=0);a.sort(Aw);let m=h.morphAttributes.position,_=h.morphAttributes.normal,E=0;for(let y=0;y<8;y++){let w=a[y],I=w[0],S=w[1];I!==Number.MAX_SAFE_INTEGER&&S?(m&&h.getAttribute("morphTarget"+y)!==m[I]&&h.setAttribute("morphTarget"+y,m[I]),_&&h.getAttribute("morphNormal"+y)!==_[I]&&h.setAttribute("morphNormal"+y,_[I]),i[y]=S,E+=S):(m&&h.hasAttribute("morphTarget"+y)===!0&&h.deleteAttribute("morphTarget"+y),_&&h.hasAttribute("morphNormal"+y)===!0&&h.deleteAttribute("morphNormal"+y),i[y]=0)}let x=h.morphTargetsRelative?1:1-E;f.getUniforms().setValue(o,"morphTargetBaseInfluence",x),f.getUniforms().setValue(o,"morphTargetInfluences",i)}}return d(l,"update"),{update:l}}d(gw,"WebGLMorphtargets");function _w(o,e,t,n){let i=new WeakMap;function s(l){let c=n.render.frame,h=l.geometry,u=e.get(l,h);return i.get(u)!==c&&(e.update(u),i.set(u,c)),l.isInstancedMesh&&(l.hasEventListener("dispose",a)===!1&&l.addEventListener("dispose",a),t.update(l.instanceMatrix,34962),l.instanceColor!==null&&t.update(l.instanceColor,34962)),u}d(s,"update");function r(){i=new WeakMap}d(r,"dispose");function a(l){let c=l.target;c.removeEventListener("dispose",a),t.remove(c.instanceMatrix),c.instanceColor!==null&&t.remove(c.instanceColor)}return d(a,"onInstancedMeshDispose"),{update:s,dispose:r}}d(_w,"WebGLObjects");var YA=new st,JA=new xl,jA=new Do,ZA=new Ml,iA=[],sA=[],rA=new Float32Array(16),oA=new Float32Array(9),aA=new Float32Array(4);function Er(o,e,t){let n=o[0];if(n<=0||n>0)return o;let i=e*t,s=iA[i];if(s===void 0&&(s=new Float32Array(i),iA[i]=s),e!==0){n.toArray(s,0);for(let r=1,a=0;r!==e;++r)a+=t,o[r].toArray(s,a)}return s}d(Er,"flatten");function bt(o,e){if(o.length!==e.length)return!1;for(let t=0,n=o.length;t<n;t++)if(o[t]!==e[t])return!1;return!0}d(bt,"arraysEqual");function It(o,e){for(let t=0,n=e.length;t<n;t++)o[t]=e[t]}d(It,"copyArray");function Hl(o,e){let t=sA[e];t===void 0&&(t=new Int32Array(e),sA[e]=t);for(let n=0;n!==e;++n)t[n]=o.allocateTextureUnit();return t}d(Hl,"allocTexUnits");function yw(o,e){let t=this.cache;t[0]!==e&&(o.uniform1f(this.addr,e),t[0]=e)}d(yw,"setValueV1f");function xw(o,e){let t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(o.uniform2f(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(bt(t,e))return;o.uniform2fv(this.addr,e),It(t,e)}}d(xw,"setValueV2f");function vw(o,e){let t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(o.uniform3f(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else if(e.r!==void 0)(t[0]!==e.r||t[1]!==e.g||t[2]!==e.b)&&(o.uniform3f(this.addr,e.r,e.g,e.b),t[0]=e.r,t[1]=e.g,t[2]=e.b);else{if(bt(t,e))return;o.uniform3fv(this.addr,e),It(t,e)}}d(vw,"setValueV3f");function Ew(o,e){let t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(o.uniform4f(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(bt(t,e))return;o.uniform4fv(this.addr,e),It(t,e)}}d(Ew,"setValueV4f");function ww(o,e){let t=this.cache,n=e.elements;if(n===void 0){if(bt(t,e))return;o.uniformMatrix2fv(this.addr,!1,e),It(t,e)}else{if(bt(t,n))return;aA.set(n),o.uniformMatrix2fv(this.addr,!1,aA),It(t,n)}}d(ww,"setValueM2");function Mw(o,e){let t=this.cache,n=e.elements;if(n===void 0){if(bt(t,e))return;o.uniformMatrix3fv(this.addr,!1,e),It(t,e)}else{if(bt(t,n))return;oA.set(n),o.uniformMatrix3fv(this.addr,!1,oA),It(t,n)}}d(Mw,"setValueM3");function bw(o,e){let t=this.cache,n=e.elements;if(n===void 0){if(bt(t,e))return;o.uniformMatrix4fv(this.addr,!1,e),It(t,e)}else{if(bt(t,n))return;rA.set(n),o.uniformMatrix4fv(this.addr,!1,rA),It(t,n)}}d(bw,"setValueM4");function Iw(o,e){let t=this.cache;t[0]!==e&&(o.uniform1i(this.addr,e),t[0]=e)}d(Iw,"setValueV1i");function Cw(o,e){let t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(o.uniform2i(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(bt(t,e))return;o.uniform2iv(this.addr,e),It(t,e)}}d(Cw,"setValueV2i");function Sw(o,e){let t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(o.uniform3i(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(bt(t,e))return;o.uniform3iv(this.addr,e),It(t,e)}}d(Sw,"setValueV3i");function Tw(o,e){let t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(o.uniform4i(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(bt(t,e))return;o.uniform4iv(this.addr,e),It(t,e)}}d(Tw,"setValueV4i");function Bw(o,e){let t=this.cache;t[0]!==e&&(o.uniform1ui(this.addr,e),t[0]=e)}d(Bw,"setValueV1ui");function Rw(o,e){let t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(o.uniform2ui(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(bt(t,e))return;o.uniform2uiv(this.addr,e),It(t,e)}}d(Rw,"setValueV2ui");function Dw(o,e){let t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(o.uniform3ui(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(bt(t,e))return;o.uniform3uiv(this.addr,e),It(t,e)}}d(Dw,"setValueV3ui");function Lw(o,e){let t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(o.uniform4ui(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(bt(t,e))return;o.uniform4uiv(this.addr,e),It(t,e)}}d(Lw,"setValueV4ui");function Pw(o,e,t){let n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(o.uniform1i(this.addr,i),n[0]=i),t.setTexture2D(e||YA,i)}d(Pw,"setValueT1");function Fw(o,e,t){let n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(o.uniform1i(this.addr,i),n[0]=i),t.setTexture3D(e||jA,i)}d(Fw,"setValueT3D1");function Ow(o,e,t){let n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(o.uniform1i(this.addr,i),n[0]=i),t.setTextureCube(e||ZA,i)}d(Ow,"setValueT6");function Nw(o,e,t){let n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(o.uniform1i(this.addr,i),n[0]=i),t.setTexture2DArray(e||JA,i)}d(Nw,"setValueT2DArray1");function Uw(o){switch(o){case 5126:return yw;case 35664:return xw;case 35665:return vw;case 35666:return Ew;case 35674:return ww;case 35675:return Mw;case 35676:return bw;case 5124:case 35670:return Iw;case 35667:case 35671:return Cw;case 35668:case 35672:return Sw;case 35669:case 35673:return Tw;case 5125:return Bw;case 36294:return Rw;case 36295:return Dw;case 36296:return Lw;case 35678:case 36198:case 36298:case 36306:case 35682:return Pw;case 35679:case 36299:case 36307:return Fw;case 35680:case 36300:case 36308:case 36293:return Ow;case 36289:case 36303:case 36311:case 36292:return Nw}}d(Uw,"getSingularSetter");function Qw(o,e){o.uniform1fv(this.addr,e)}d(Qw,"setValueV1fArray");function kw(o,e){let t=Er(e,this.size,2);o.uniform2fv(this.addr,t)}d(kw,"setValueV2fArray");function Gw(o,e){let t=Er(e,this.size,3);o.uniform3fv(this.addr,t)}d(Gw,"setValueV3fArray");function zw(o,e){let t=Er(e,this.size,4);o.uniform4fv(this.addr,t)}d(zw,"setValueV4fArray");function Vw(o,e){let t=Er(e,this.size,4);o.uniformMatrix2fv(this.addr,!1,t)}d(Vw,"setValueM2Array");function Hw(o,e){let t=Er(e,this.size,9);o.uniformMatrix3fv(this.addr,!1,t)}d(Hw,"setValueM3Array");function Ww(o,e){let t=Er(e,this.size,16);o.uniformMatrix4fv(this.addr,!1,t)}d(Ww,"setValueM4Array");function qw(o,e){o.uniform1iv(this.addr,e)}d(qw,"setValueV1iArray");function Kw(o,e){o.uniform2iv(this.addr,e)}d(Kw,"setValueV2iArray");function $w(o,e){o.uniform3iv(this.addr,e)}d($w,"setValueV3iArray");function Xw(o,e){o.uniform4iv(this.addr,e)}d(Xw,"setValueV4iArray");function Yw(o,e){o.uniform1uiv(this.addr,e)}d(Yw,"setValueV1uiArray");function Jw(o,e){o.uniform2uiv(this.addr,e)}d(Jw,"setValueV2uiArray");function jw(o,e){o.uniform3uiv(this.addr,e)}d(jw,"setValueV3uiArray");function Zw(o,e){o.uniform4uiv(this.addr,e)}d(Zw,"setValueV4uiArray");function eM(o,e,t){let n=this.cache,i=e.length,s=Hl(t,i);bt(n,s)||(o.uniform1iv(this.addr,s),It(n,s));for(let r=0;r!==i;++r)t.setTexture2D(e[r]||YA,s[r])}d(eM,"setValueT1Array");function tM(o,e,t){let n=this.cache,i=e.length,s=Hl(t,i);bt(n,s)||(o.uniform1iv(this.addr,s),It(n,s));for(let r=0;r!==i;++r)t.setTexture3D(e[r]||jA,s[r])}d(tM,"setValueT3DArray");function nM(o,e,t){let n=this.cache,i=e.length,s=Hl(t,i);bt(n,s)||(o.uniform1iv(this.addr,s),It(n,s));for(let r=0;r!==i;++r)t.setTextureCube(e[r]||ZA,s[r])}d(nM,"setValueT6Array");function iM(o,e,t){let n=this.cache,i=e.length,s=Hl(t,i);bt(n,s)||(o.uniform1iv(this.addr,s),It(n,s));for(let r=0;r!==i;++r)t.setTexture2DArray(e[r]||JA,s[r])}d(iM,"setValueT2DArrayArray");function sM(o){switch(o){case 5126:return Qw;case 35664:return kw;case 35665:return Gw;case 35666:return zw;case 35674:return Vw;case 35675:return Hw;case 35676:return Ww;case 5124:case 35670:return qw;case 35667:case 35671:return Kw;case 35668:case 35672:return $w;case 35669:case 35673:return Xw;case 5125:return Yw;case 36294:return Jw;case 36295:return jw;case 36296:return Zw;case 35678:case 36198:case 36298:case 36306:case 35682:return eM;case 35679:case 36299:case 36307:return tM;case 35680:case 36300:case 36308:case 36293:return nM;case 36289:case 36303:case 36311:case 36292:return iM}}d(sM,"getPureArraySetter");var jh=class{static{d(this,"SingleUniform")}constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.setValue=Uw(t.type)}},Zh=class{static{d(this,"PureArrayUniform")}constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.size=t.size,this.setValue=sM(t.type)}},eu=class{static{d(this,"StructuredUniform")}constructor(e){this.id=e,this.seq=[],this.map={}}setValue(e,t,n){let i=this.seq;for(let s=0,r=i.length;s!==r;++s){let a=i[s];a.setValue(e,t[a.id],n)}}},Vh=/(\w+)(\])?(\[|\.)?/g;function lA(o,e){o.seq.push(e),o.map[e.id]=e}d(lA,"addUniform");function rM(o,e,t){let n=o.name,i=n.length;for(Vh.lastIndex=0;;){let s=Vh.exec(n),r=Vh.lastIndex,a=s[1],l=s[2]==="]",c=s[3];if(l&&(a=a|0),c===void 0||c==="["&&r+2===i){lA(t,c===void 0?new jh(a,o,e):new Zh(a,o,e));break}else{let u=t.map[a];u===void 0&&(u=new eu(a),lA(t,u)),t=u}}}d(rM,"parseUniform");var nr=class{static{d(this,"WebGLUniforms")}constructor(e,t){this.seq=[],this.map={};let n=e.getProgramParameter(t,35718);for(let i=0;i<n;++i){let s=e.getActiveUniform(t,i),r=e.getUniformLocation(t,s.name);rM(s,r,this)}}setValue(e,t,n,i){let s=this.map[t];s!==void 0&&s.setValue(e,n,i)}setOptional(e,t,n){let i=t[n];i!==void 0&&this.setValue(e,n,i)}static upload(e,t,n,i){for(let s=0,r=t.length;s!==r;++s){let a=t[s],l=n[a.id];l.needsUpdate!==!1&&a.setValue(e,l.value,i)}}static seqWithValue(e,t){let n=[];for(let i=0,s=e.length;i!==s;++i){let r=e[i];r.id in t&&n.push(r)}return n}};function cA(o,e,t){let n=o.createShader(e);return o.shaderSource(n,t),o.compileShader(n),n}d(cA,"WebGLShader");var oM=0;function aM(o,e){let t=o.split(`
`),n=[],i=Math.max(e-6,0),s=Math.min(e+6,t.length);for(let r=i;r<s;r++){let a=r+1;n.push(`${a===e?">":" "} ${a}: ${t[r]}`)}return n.join(`
`)}d(aM,"handleSource");function lM(o){switch(o){case ft:return["Linear","( value )"];case Se:return["sRGB","( value )"];default:return console.warn("THREE.WebGLProgram: Unsupported encoding:",o),["Linear","( value )"]}}d(lM,"getEncodingComponents");function hA(o,e,t){let n=o.getShaderParameter(e,35713),i=o.getShaderInfoLog(e).trim();if(n&&i==="")return"";let s=/ERROR: 0:(\d+)/.exec(i);if(s){let r=parseInt(s[1]);return t.toUpperCase()+`

`+i+`

`+aM(o.getShaderSource(e),r)}else return i}d(hA,"getShaderErrors");function cM(o,e){let t=lM(e);return"vec4 "+o+"( vec4 value ) { return LinearTo"+t[0]+t[1]+"; }"}d(cM,"getTexelEncodingFunction");function hM(o,e){let t;switch(e){case Iy:t="Linear";break;case Cy:t="Reinhard";break;case Sy:t="OptimizedCineon";break;case bu:t="ACESFilmic";break;case Ty:t="Custom";break;default:console.warn("THREE.WebGLProgram: Unsupported toneMapping:",e),t="Linear"}return"vec3 "+o+"( vec3 color ) { return "+t+"ToneMapping( color ); }"}d(hM,"getToneMappingFunction");function uM(o){return[o.extensionDerivatives||o.envMapCubeUVHeight||o.bumpMap||o.tangentSpaceNormalMap||o.clearcoatNormalMap||o.flatShading||o.shaderID==="physical"?"#extension GL_OES_standard_derivatives : enable":"",(o.extensionFragDepth||o.logarithmicDepthBuffer)&&o.rendererExtensionFragDepth?"#extension GL_EXT_frag_depth : enable":"",o.extensionDrawBuffers&&o.rendererExtensionDrawBuffers?"#extension GL_EXT_draw_buffers : require":"",(o.extensionShaderTextureLOD||o.envMap||o.transmission)&&o.rendererExtensionShaderTextureLod?"#extension GL_EXT_shader_texture_lod : enable":""].filter(vo).join(`
`)}d(uM,"generateExtensions");function dM(o){let e=[];for(let t in o){let n=o[t];n!==!1&&e.push("#define "+t+" "+n)}return e.join(`
`)}d(dM,"generateDefines");function fM(o,e){let t={},n=o.getProgramParameter(e,35721);for(let i=0;i<n;i++){let s=o.getActiveAttrib(e,i),r=s.name,a=1;s.type===35674&&(a=2),s.type===35675&&(a=3),s.type===35676&&(a=4),t[r]={type:s.type,location:o.getAttribLocation(e,r),locationSize:a}}return t}d(fM,"fetchAttributeLocations");function vo(o){return o!==""}d(vo,"filterEmptyLine");function uA(o,e){let t=e.numSpotLightShadows+e.numSpotLightMaps-e.numSpotLightShadowsWithMaps;return o.replace(/NUM_DIR_LIGHTS/g,e.numDirLights).replace(/NUM_SPOT_LIGHTS/g,e.numSpotLights).replace(/NUM_SPOT_LIGHT_MAPS/g,e.numSpotLightMaps).replace(/NUM_SPOT_LIGHT_COORDS/g,t).replace(/NUM_RECT_AREA_LIGHTS/g,e.numRectAreaLights).replace(/NUM_POINT_LIGHTS/g,e.numPointLights).replace(/NUM_HEMI_LIGHTS/g,e.numHemiLights).replace(/NUM_DIR_LIGHT_SHADOWS/g,e.numDirLightShadows).replace(/NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS/g,e.numSpotLightShadowsWithMaps).replace(/NUM_SPOT_LIGHT_SHADOWS/g,e.numSpotLightShadows).replace(/NUM_POINT_LIGHT_SHADOWS/g,e.numPointLightShadows)}d(uA,"replaceLightNums");function dA(o,e){return o.replace(/NUM_CLIPPING_PLANES/g,e.numClippingPlanes).replace(/UNION_CLIPPING_PLANES/g,e.numClippingPlanes-e.numClipIntersection)}d(dA,"replaceClippingPlaneNums");var pM=/^[ \t]*#include +<([\w\d./]+)>/gm;function tu(o){return o.replace(pM,AM)}d(tu,"resolveIncludes");function AM(o,e){let t=Pe[e];if(t===void 0)throw new Error("Can not resolve #include <"+e+">");return tu(t)}d(AM,"includeReplacer");var mM=/#pragma unroll_loop_start\s+for\s*\(\s*int\s+i\s*=\s*(\d+)\s*;\s*i\s*<\s*(\d+)\s*;\s*i\s*\+\+\s*\)\s*{([\s\S]+?)}\s+#pragma unroll_loop_end/g;function fA(o){return o.replace(mM,gM)}d(fA,"unrollLoops");function gM(o,e,t,n){let i="";for(let s=parseInt(e);s<parseInt(t);s++)i+=n.replace(/\[\s*i\s*\]/g,"[ "+s+" ]").replace(/UNROLLED_LOOP_INDEX/g,s);return i}d(gM,"loopReplacer");function pA(o){let e="precision "+o.precision+` float;
precision `+o.precision+" int;";return o.precision==="highp"?e+=`
#define HIGH_PRECISION`:o.precision==="mediump"?e+=`
#define MEDIUM_PRECISION`:o.precision==="lowp"&&(e+=`
#define LOW_PRECISION`),e}d(pA,"generatePrecision");function _M(o){let e="SHADOWMAP_TYPE_BASIC";return o.shadowMapType===NA?e="SHADOWMAP_TYPE_PCF":o.shadowMapType===sy?e="SHADOWMAP_TYPE_PCF_SOFT":o.shadowMapType===xo&&(e="SHADOWMAP_TYPE_VSM"),e}d(_M,"generateShadowMapTypeDefine");function yM(o){let e="ENVMAP_TYPE_CUBE";if(o.envMap)switch(o.envMapMode){case ir:case sr:e="ENVMAP_TYPE_CUBE";break;case zl:e="ENVMAP_TYPE_CUBE_UV";break}return e}d(yM,"generateEnvMapTypeDefine");function xM(o){let e="ENVMAP_MODE_REFLECTION";if(o.envMap)switch(o.envMapMode){case sr:e="ENVMAP_MODE_REFRACTION";break}return e}d(xM,"generateEnvMapModeDefine");function vM(o){let e="ENVMAP_BLENDING_NONE";if(o.envMap)switch(o.combine){case kA:e="ENVMAP_BLENDING_MULTIPLY";break;case My:e="ENVMAP_BLENDING_MIX";break;case by:e="ENVMAP_BLENDING_ADD";break}return e}d(vM,"generateEnvMapBlendingDefine");function EM(o){let e=o.envMapCubeUVHeight;if(e===null)return null;let t=Math.log2(e)-2,n=1/e;return{texelWidth:1/(3*Math.max(Math.pow(2,t),7*16)),texelHeight:n,maxMip:t}}d(EM,"generateCubeUVSize");function wM(o,e,t,n){let i=o.getContext(),s=t.defines,r=t.vertexShader,a=t.fragmentShader,l=_M(t),c=yM(t),h=xM(t),u=vM(t),f=EM(t),p=t.isWebGL2?"":uM(t),g=dM(s),A=i.createProgram(),m,_,E=t.glslVersion?"#version "+t.glslVersion+`
`:"";t.isRawShaderMaterial?(m=[g].filter(vo).join(`
`),m.length>0&&(m+=`
`),_=[p,g].filter(vo).join(`
`),_.length>0&&(_+=`
`)):(m=[pA(t),"#define SHADER_NAME "+t.shaderName,g,t.instancing?"#define USE_INSTANCING":"",t.instancingColor?"#define USE_INSTANCING_COLOR":"",t.supportsVertexTextures?"#define VERTEX_TEXTURES":"",t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.map?"#define USE_MAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+h:"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMap&&t.objectSpaceNormalMap?"#define OBJECTSPACE_NORMALMAP":"",t.normalMap&&t.tangentSpaceNormalMap?"#define TANGENTSPACE_NORMALMAP":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.displacementMap&&t.supportsVertexTextures?"#define USE_DISPLACEMENTMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularIntensityMap?"#define USE_SPECULARINTENSITYMAP":"",t.specularColorMap?"#define USE_SPECULARCOLORMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.sheenColorMap?"#define USE_SHEENCOLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEENROUGHNESSMAP":"",t.vertexTangents?"#define USE_TANGENT":"",t.vertexColors?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUvs?"#define USE_UV":"",t.uvsVertexOnly?"#define UVS_VERTEX_ONLY":"",t.flatShading?"#define FLAT_SHADED":"",t.skinning?"#define USE_SKINNING":"",t.morphTargets?"#define USE_MORPHTARGETS":"",t.morphNormals&&t.flatShading===!1?"#define USE_MORPHNORMALS":"",t.morphColors&&t.isWebGL2?"#define USE_MORPHCOLORS":"",t.morphTargetsCount>0&&t.isWebGL2?"#define MORPHTARGETS_TEXTURE":"",t.morphTargetsCount>0&&t.isWebGL2?"#define MORPHTARGETS_TEXTURE_STRIDE "+t.morphTextureStride:"",t.morphTargetsCount>0&&t.isWebGL2?"#define MORPHTARGETS_COUNT "+t.morphTargetsCount:"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+l:"",t.sizeAttenuation?"#define USE_SIZEATTENUATION":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"",t.logarithmicDepthBuffer&&t.rendererExtensionFragDepth?"#define USE_LOGDEPTHBUF_EXT":"","uniform mat4 modelMatrix;","uniform mat4 modelViewMatrix;","uniform mat4 projectionMatrix;","uniform mat4 viewMatrix;","uniform mat3 normalMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;","#ifdef USE_INSTANCING","	attribute mat4 instanceMatrix;","#endif","#ifdef USE_INSTANCING_COLOR","	attribute vec3 instanceColor;","#endif","attribute vec3 position;","attribute vec3 normal;","attribute vec2 uv;","#ifdef USE_TANGENT","	attribute vec4 tangent;","#endif","#if defined( USE_COLOR_ALPHA )","	attribute vec4 color;","#elif defined( USE_COLOR )","	attribute vec3 color;","#endif","#if ( defined( USE_MORPHTARGETS ) && ! defined( MORPHTARGETS_TEXTURE ) )","	attribute vec3 morphTarget0;","	attribute vec3 morphTarget1;","	attribute vec3 morphTarget2;","	attribute vec3 morphTarget3;","	#ifdef USE_MORPHNORMALS","		attribute vec3 morphNormal0;","		attribute vec3 morphNormal1;","		attribute vec3 morphNormal2;","		attribute vec3 morphNormal3;","	#else","		attribute vec3 morphTarget4;","		attribute vec3 morphTarget5;","		attribute vec3 morphTarget6;","		attribute vec3 morphTarget7;","	#endif","#endif","#ifdef USE_SKINNING","	attribute vec4 skinIndex;","	attribute vec4 skinWeight;","#endif",`
`].filter(vo).join(`
`),_=[p,pA(t),"#define SHADER_NAME "+t.shaderName,g,t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.map?"#define USE_MAP":"",t.matcap?"#define USE_MATCAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+c:"",t.envMap?"#define "+h:"",t.envMap?"#define "+u:"",f?"#define CUBEUV_TEXEL_WIDTH "+f.texelWidth:"",f?"#define CUBEUV_TEXEL_HEIGHT "+f.texelHeight:"",f?"#define CUBEUV_MAX_MIP "+f.maxMip+".0":"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMap&&t.objectSpaceNormalMap?"#define OBJECTSPACE_NORMALMAP":"",t.normalMap&&t.tangentSpaceNormalMap?"#define TANGENTSPACE_NORMALMAP":"",t.clearcoat?"#define USE_CLEARCOAT":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.iridescence?"#define USE_IRIDESCENCE":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularIntensityMap?"#define USE_SPECULARINTENSITYMAP":"",t.specularColorMap?"#define USE_SPECULARCOLORMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaTest?"#define USE_ALPHATEST":"",t.sheen?"#define USE_SHEEN":"",t.sheenColorMap?"#define USE_SHEENCOLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEENROUGHNESSMAP":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.decodeVideoTexture?"#define DECODE_VIDEO_TEXTURE":"",t.vertexTangents?"#define USE_TANGENT":"",t.vertexColors||t.instancingColor?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUvs?"#define USE_UV":"",t.uvsVertexOnly?"#define UVS_VERTEX_ONLY":"",t.gradientMap?"#define USE_GRADIENTMAP":"",t.flatShading?"#define FLAT_SHADED":"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+l:"",t.premultipliedAlpha?"#define PREMULTIPLIED_ALPHA":"",t.physicallyCorrectLights?"#define PHYSICALLY_CORRECT_LIGHTS":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"",t.logarithmicDepthBuffer&&t.rendererExtensionFragDepth?"#define USE_LOGDEPTHBUF_EXT":"","uniform mat4 viewMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;",t.toneMapping!==qn?"#define TONE_MAPPING":"",t.toneMapping!==qn?Pe.tonemapping_pars_fragment:"",t.toneMapping!==qn?hM("toneMapping",t.toneMapping):"",t.dithering?"#define DITHERING":"",t.opaque?"#define OPAQUE":"",Pe.encodings_pars_fragment,cM("linearToOutputTexel",t.outputEncoding),t.useDepthPacking?"#define DEPTH_PACKING "+t.depthPacking:"",`
`].filter(vo).join(`
`)),r=tu(r),r=uA(r,t),r=dA(r,t),a=tu(a),a=uA(a,t),a=dA(a,t),r=fA(r),a=fA(a),t.isWebGL2&&t.isRawShaderMaterial!==!0&&(E=`#version 300 es
`,m=["precision mediump sampler2DArray;","#define attribute in","#define varying out","#define texture2D texture"].join(`
`)+`
`+m,_=["#define varying in",t.glslVersion===Qp?"":"layout(location = 0) out highp vec4 pc_fragColor;",t.glslVersion===Qp?"":"#define gl_FragColor pc_fragColor","#define gl_FragDepthEXT gl_FragDepth","#define texture2D texture","#define textureCube texture","#define texture2DProj textureProj","#define texture2DLodEXT textureLod","#define texture2DProjLodEXT textureProjLod","#define textureCubeLodEXT textureLod","#define texture2DGradEXT textureGrad","#define texture2DProjGradEXT textureProjGrad","#define textureCubeGradEXT textureGrad"].join(`
`)+`
`+_);let x=E+m+r,y=E+_+a,w=cA(i,35633,x),I=cA(i,35632,y);if(i.attachShader(A,w),i.attachShader(A,I),t.index0AttributeName!==void 0?i.bindAttribLocation(A,0,t.index0AttributeName):t.morphTargets===!0&&i.bindAttribLocation(A,0,"position"),i.linkProgram(A),o.debug.checkShaderErrors){let b=i.getProgramInfoLog(A).trim(),R=i.getShaderInfoLog(w).trim(),N=i.getShaderInfoLog(I).trim(),z=!0,O=!0;if(i.getProgramParameter(A,35714)===!1){z=!1;let D=hA(i,w,"vertex"),Q=hA(i,I,"fragment");console.error("THREE.WebGLProgram: Shader Error "+i.getError()+" - VALIDATE_STATUS "+i.getProgramParameter(A,35715)+`

Program Info Log: `+b+`
`+D+`
`+Q)}else b!==""?console.warn("THREE.WebGLProgram: Program Info Log:",b):(R===""||N==="")&&(O=!1);O&&(this.diagnostics={runnable:z,programLog:b,vertexShader:{log:R,prefix:m},fragmentShader:{log:N,prefix:_}})}i.deleteShader(w),i.deleteShader(I);let S;this.getUniforms=function(){return S===void 0&&(S=new nr(i,A)),S};let v;return this.getAttributes=function(){return v===void 0&&(v=fM(i,A)),v},this.destroy=function(){n.releaseStatesOfProgram(this),i.deleteProgram(A),this.program=void 0},this.name=t.shaderName,this.id=oM++,this.cacheKey=e,this.usedTimes=1,this.program=A,this.vertexShader=w,this.fragmentShader=I,this}d(wM,"WebGLProgram");var MM=0,nu=class{static{d(this,"WebGLShaderCache")}constructor(){this.shaderCache=new Map,this.materialCache=new Map}update(e){let t=e.vertexShader,n=e.fragmentShader,i=this._getShaderStage(t),s=this._getShaderStage(n),r=this._getShaderCacheForMaterial(e);return r.has(i)===!1&&(r.add(i),i.usedTimes++),r.has(s)===!1&&(r.add(s),s.usedTimes++),this}remove(e){let t=this.materialCache.get(e);for(let n of t)n.usedTimes--,n.usedTimes===0&&this.shaderCache.delete(n.code);return this.materialCache.delete(e),this}getVertexShaderID(e){return this._getShaderStage(e.vertexShader).id}getFragmentShaderID(e){return this._getShaderStage(e.fragmentShader).id}dispose(){this.shaderCache.clear(),this.materialCache.clear()}_getShaderCacheForMaterial(e){let t=this.materialCache,n=t.get(e);return n===void 0&&(n=new Set,t.set(e,n)),n}_getShaderStage(e){let t=this.shaderCache,n=t.get(e);return n===void 0&&(n=new iu(e),t.set(e,n)),n}},iu=class{static{d(this,"WebGLShaderStage")}constructor(e){this.id=MM++,this.code=e,this.usedTimes=0}};function bM(o,e,t,n,i,s,r){let a=new Lo,l=new nu,c=[],h=i.isWebGL2,u=i.logarithmicDepthBuffer,f=i.vertexTextures,p=i.precision,g={MeshDepthMaterial:"depth",MeshDistanceMaterial:"distanceRGBA",MeshNormalMaterial:"normal",MeshBasicMaterial:"basic",MeshLambertMaterial:"lambert",MeshPhongMaterial:"phong",MeshToonMaterial:"toon",MeshStandardMaterial:"physical",MeshPhysicalMaterial:"physical",MeshMatcapMaterial:"matcap",LineBasicMaterial:"basic",LineDashedMaterial:"dashed",PointsMaterial:"points",ShadowMaterial:"shadow",SpriteMaterial:"sprite"};function A(v,b,R,N,z){let O=N.fog,D=z.geometry,Q=v.isMeshStandardMaterial?N.environment:null,q=(v.isMeshStandardMaterial?t:e).get(v.envMap||Q),H=q&&q.mapping===zl?q.image.height:null,k=g[v.type];v.precision!==null&&(p=i.getMaxPrecision(v.precision),p!==v.precision&&console.warn("THREE.WebGLProgram.getParameters:",v.precision,"not supported, using",p,"instead."));let j=D.morphAttributes.position||D.morphAttributes.normal||D.morphAttributes.color,Z=j!==void 0?j.length:0,fe=0;D.morphAttributes.position!==void 0&&(fe=1),D.morphAttributes.normal!==void 0&&(fe=2),D.morphAttributes.color!==void 0&&(fe=3);let V,ee,re,ie;if(k){let $e=si[k];V=$e.vertexShader,ee=$e.fragmentShader}else V=v.vertexShader,ee=v.fragmentShader,l.update(v),re=l.getVertexShaderID(v),ie=l.getFragmentShaderID(v);let W=o.getRenderTarget(),Te=v.alphaTest>0,Ae=v.clearcoat>0,ge=v.iridescence>0;return{isWebGL2:h,shaderID:k,shaderName:v.type,vertexShader:V,fragmentShader:ee,defines:v.defines,customVertexShaderID:re,customFragmentShaderID:ie,isRawShaderMaterial:v.isRawShaderMaterial===!0,glslVersion:v.glslVersion,precision:p,instancing:z.isInstancedMesh===!0,instancingColor:z.isInstancedMesh===!0&&z.instanceColor!==null,supportsVertexTextures:f,outputEncoding:W===null?o.outputEncoding:W.isXRRenderTarget===!0?W.texture.encoding:ft,map:!!v.map,matcap:!!v.matcap,envMap:!!q,envMapMode:q&&q.mapping,envMapCubeUVHeight:H,lightMap:!!v.lightMap,aoMap:!!v.aoMap,emissiveMap:!!v.emissiveMap,bumpMap:!!v.bumpMap,normalMap:!!v.normalMap,objectSpaceNormalMap:v.normalMapType===Wy,tangentSpaceNormalMap:v.normalMapType===HA,decodeVideoTexture:!!v.map&&v.map.isVideoTexture===!0&&v.map.encoding===Se,clearcoat:Ae,clearcoatMap:Ae&&!!v.clearcoatMap,clearcoatRoughnessMap:Ae&&!!v.clearcoatRoughnessMap,clearcoatNormalMap:Ae&&!!v.clearcoatNormalMap,iridescence:ge,iridescenceMap:ge&&!!v.iridescenceMap,iridescenceThicknessMap:ge&&!!v.iridescenceThicknessMap,displacementMap:!!v.displacementMap,roughnessMap:!!v.roughnessMap,metalnessMap:!!v.metalnessMap,specularMap:!!v.specularMap,specularIntensityMap:!!v.specularIntensityMap,specularColorMap:!!v.specularColorMap,opaque:v.transparent===!1&&v.blending===er,alphaMap:!!v.alphaMap,alphaTest:Te,gradientMap:!!v.gradientMap,sheen:v.sheen>0,sheenColorMap:!!v.sheenColorMap,sheenRoughnessMap:!!v.sheenRoughnessMap,transmission:v.transmission>0,transmissionMap:!!v.transmissionMap,thicknessMap:!!v.thicknessMap,combine:v.combine,vertexTangents:!!v.normalMap&&!!D.attributes.tangent,vertexColors:v.vertexColors,vertexAlphas:v.vertexColors===!0&&!!D.attributes.color&&D.attributes.color.itemSize===4,vertexUvs:!!v.map||!!v.bumpMap||!!v.normalMap||!!v.specularMap||!!v.alphaMap||!!v.emissiveMap||!!v.roughnessMap||!!v.metalnessMap||!!v.clearcoatMap||!!v.clearcoatRoughnessMap||!!v.clearcoatNormalMap||!!v.iridescenceMap||!!v.iridescenceThicknessMap||!!v.displacementMap||!!v.transmissionMap||!!v.thicknessMap||!!v.specularIntensityMap||!!v.specularColorMap||!!v.sheenColorMap||!!v.sheenRoughnessMap,uvsVertexOnly:!(v.map||v.bumpMap||v.normalMap||v.specularMap||v.alphaMap||v.emissiveMap||v.roughnessMap||v.metalnessMap||v.clearcoatNormalMap||v.iridescenceMap||v.iridescenceThicknessMap||v.transmission>0||v.transmissionMap||v.thicknessMap||v.specularIntensityMap||v.specularColorMap||v.sheen>0||v.sheenColorMap||v.sheenRoughnessMap)&&!!v.displacementMap,fog:!!O,useFog:v.fog===!0,fogExp2:O&&O.isFogExp2,flatShading:!!v.flatShading,sizeAttenuation:v.sizeAttenuation,logarithmicDepthBuffer:u,skinning:z.isSkinnedMesh===!0,morphTargets:D.morphAttributes.position!==void 0,morphNormals:D.morphAttributes.normal!==void 0,morphColors:D.morphAttributes.color!==void 0,morphTargetsCount:Z,morphTextureStride:fe,numDirLights:b.directional.length,numPointLights:b.point.length,numSpotLights:b.spot.length,numSpotLightMaps:b.spotLightMap.length,numRectAreaLights:b.rectArea.length,numHemiLights:b.hemi.length,numDirLightShadows:b.directionalShadowMap.length,numPointLightShadows:b.pointShadowMap.length,numSpotLightShadows:b.spotShadowMap.length,numSpotLightShadowsWithMaps:b.numSpotLightShadowsWithMaps,numClippingPlanes:r.numPlanes,numClipIntersection:r.numIntersection,dithering:v.dithering,shadowMapEnabled:o.shadowMap.enabled&&R.length>0,shadowMapType:o.shadowMap.type,toneMapping:v.toneMapped?o.toneMapping:qn,physicallyCorrectLights:o.physicallyCorrectLights,premultipliedAlpha:v.premultipliedAlpha,doubleSided:v.side===Et,flipSided:v.side===dt,useDepthPacking:!!v.depthPacking,depthPacking:v.depthPacking||0,index0AttributeName:v.index0AttributeName,extensionDerivatives:v.extensions&&v.extensions.derivatives,extensionFragDepth:v.extensions&&v.extensions.fragDepth,extensionDrawBuffers:v.extensions&&v.extensions.drawBuffers,extensionShaderTextureLOD:v.extensions&&v.extensions.shaderTextureLOD,rendererExtensionFragDepth:h||n.has("EXT_frag_depth"),rendererExtensionDrawBuffers:h||n.has("WEBGL_draw_buffers"),rendererExtensionShaderTextureLod:h||n.has("EXT_shader_texture_lod"),customProgramCacheKey:v.customProgramCacheKey()}}d(A,"getParameters");function m(v){let b=[];if(v.shaderID?b.push(v.shaderID):(b.push(v.customVertexShaderID),b.push(v.customFragmentShaderID)),v.defines!==void 0)for(let R in v.defines)b.push(R),b.push(v.defines[R]);return v.isRawShaderMaterial===!1&&(_(b,v),E(b,v),b.push(o.outputEncoding)),b.push(v.customProgramCacheKey),b.join()}d(m,"getProgramCacheKey");function _(v,b){v.push(b.precision),v.push(b.outputEncoding),v.push(b.envMapMode),v.push(b.envMapCubeUVHeight),v.push(b.combine),v.push(b.vertexUvs),v.push(b.fogExp2),v.push(b.sizeAttenuation),v.push(b.morphTargetsCount),v.push(b.morphAttributeCount),v.push(b.numDirLights),v.push(b.numPointLights),v.push(b.numSpotLights),v.push(b.numSpotLightMaps),v.push(b.numHemiLights),v.push(b.numRectAreaLights),v.push(b.numDirLightShadows),v.push(b.numPointLightShadows),v.push(b.numSpotLightShadows),v.push(b.numSpotLightShadowsWithMaps),v.push(b.shadowMapType),v.push(b.toneMapping),v.push(b.numClippingPlanes),v.push(b.numClipIntersection),v.push(b.depthPacking)}d(_,"getProgramCacheKeyParameters");function E(v,b){a.disableAll(),b.isWebGL2&&a.enable(0),b.supportsVertexTextures&&a.enable(1),b.instancing&&a.enable(2),b.instancingColor&&a.enable(3),b.map&&a.enable(4),b.matcap&&a.enable(5),b.envMap&&a.enable(6),b.lightMap&&a.enable(7),b.aoMap&&a.enable(8),b.emissiveMap&&a.enable(9),b.bumpMap&&a.enable(10),b.normalMap&&a.enable(11),b.objectSpaceNormalMap&&a.enable(12),b.tangentSpaceNormalMap&&a.enable(13),b.clearcoat&&a.enable(14),b.clearcoatMap&&a.enable(15),b.clearcoatRoughnessMap&&a.enable(16),b.clearcoatNormalMap&&a.enable(17),b.iridescence&&a.enable(18),b.iridescenceMap&&a.enable(19),b.iridescenceThicknessMap&&a.enable(20),b.displacementMap&&a.enable(21),b.specularMap&&a.enable(22),b.roughnessMap&&a.enable(23),b.metalnessMap&&a.enable(24),b.gradientMap&&a.enable(25),b.alphaMap&&a.enable(26),b.alphaTest&&a.enable(27),b.vertexColors&&a.enable(28),b.vertexAlphas&&a.enable(29),b.vertexUvs&&a.enable(30),b.vertexTangents&&a.enable(31),b.uvsVertexOnly&&a.enable(32),v.push(a.mask),a.disableAll(),b.fog&&a.enable(0),b.useFog&&a.enable(1),b.flatShading&&a.enable(2),b.logarithmicDepthBuffer&&a.enable(3),b.skinning&&a.enable(4),b.morphTargets&&a.enable(5),b.morphNormals&&a.enable(6),b.morphColors&&a.enable(7),b.premultipliedAlpha&&a.enable(8),b.shadowMapEnabled&&a.enable(9),b.physicallyCorrectLights&&a.enable(10),b.doubleSided&&a.enable(11),b.flipSided&&a.enable(12),b.useDepthPacking&&a.enable(13),b.dithering&&a.enable(14),b.specularIntensityMap&&a.enable(15),b.specularColorMap&&a.enable(16),b.transmission&&a.enable(17),b.transmissionMap&&a.enable(18),b.thicknessMap&&a.enable(19),b.sheen&&a.enable(20),b.sheenColorMap&&a.enable(21),b.sheenRoughnessMap&&a.enable(22),b.decodeVideoTexture&&a.enable(23),b.opaque&&a.enable(24),v.push(a.mask)}d(E,"getProgramCacheKeyBooleans");function x(v){let b=g[v.type],R;if(b){let N=si[b];R=_x.clone(N.uniforms)}else R=v.uniforms;return R}d(x,"getUniforms");function y(v,b){let R;for(let N=0,z=c.length;N<z;N++){let O=c[N];if(O.cacheKey===b){R=O,++R.usedTimes;break}}return R===void 0&&(R=new wM(o,b,v,s),c.push(R)),R}d(y,"acquireProgram");function w(v){if(--v.usedTimes===0){let b=c.indexOf(v);c[b]=c[c.length-1],c.pop(),v.destroy()}}d(w,"releaseProgram");function I(v){l.remove(v)}d(I,"releaseShaderCache");function S(){l.dispose()}return d(S,"dispose"),{getParameters:A,getProgramCacheKey:m,getUniforms:x,acquireProgram:y,releaseProgram:w,releaseShaderCache:I,programs:c,dispose:S}}d(bM,"WebGLPrograms");function IM(){let o=new WeakMap;function e(s){let r=o.get(s);return r===void 0&&(r={},o.set(s,r)),r}d(e,"get");function t(s){o.delete(s)}d(t,"remove");function n(s,r,a){o.get(s)[r]=a}d(n,"update");function i(){o=new WeakMap}return d(i,"dispose"),{get:e,remove:t,update:n,dispose:i}}d(IM,"WebGLProperties");function CM(o,e){return o.groupOrder!==e.groupOrder?o.groupOrder-e.groupOrder:o.renderOrder!==e.renderOrder?o.renderOrder-e.renderOrder:o.material.id!==e.material.id?o.material.id-e.material.id:o.z!==e.z?o.z-e.z:o.id-e.id}d(CM,"painterSortStable");function AA(o,e){return o.groupOrder!==e.groupOrder?o.groupOrder-e.groupOrder:o.renderOrder!==e.renderOrder?o.renderOrder-e.renderOrder:o.z!==e.z?e.z-o.z:o.id-e.id}d(AA,"reversePainterSortStable");function mA(){let o=[],e=0,t=[],n=[],i=[];function s(){e=0,t.length=0,n.length=0,i.length=0}d(s,"init");function r(u,f,p,g,A,m){let _=o[e];return _===void 0?(_={id:u.id,object:u,geometry:f,material:p,groupOrder:g,renderOrder:u.renderOrder,z:A,group:m},o[e]=_):(_.id=u.id,_.object=u,_.geometry=f,_.material=p,_.groupOrder=g,_.renderOrder=u.renderOrder,_.z=A,_.group=m),e++,_}d(r,"getNextRenderItem");function a(u,f,p,g,A,m){let _=r(u,f,p,g,A,m);p.transmission>0?n.push(_):p.transparent===!0?i.push(_):t.push(_)}d(a,"push");function l(u,f,p,g,A,m){let _=r(u,f,p,g,A,m);p.transmission>0?n.unshift(_):p.transparent===!0?i.unshift(_):t.unshift(_)}d(l,"unshift");function c(u,f){t.length>1&&t.sort(u||CM),n.length>1&&n.sort(f||AA),i.length>1&&i.sort(f||AA)}d(c,"sort");function h(){for(let u=e,f=o.length;u<f;u++){let p=o[u];if(p.id===null)break;p.id=null,p.object=null,p.geometry=null,p.material=null,p.group=null}}return d(h,"finish"),{opaque:t,transmissive:n,transparent:i,init:s,push:a,unshift:l,finish:h,sort:c}}d(mA,"WebGLRenderList");function SM(){let o=new WeakMap;function e(n,i){let s=o.get(n),r;return s===void 0?(r=new mA,o.set(n,[r])):i>=s.length?(r=new mA,s.push(r)):r=s[i],r}d(e,"get");function t(){o=new WeakMap}return d(t,"dispose"),{get:e,dispose:t}}d(SM,"WebGLRenderLists");function TM(){let o={};return{get:d(function(e){if(o[e.id]!==void 0)return o[e.id];let t;switch(e.type){case"DirectionalLight":t={direction:new B,color:new Me};break;case"SpotLight":t={position:new B,direction:new B,color:new Me,distance:0,coneCos:0,penumbraCos:0,decay:0};break;case"PointLight":t={position:new B,color:new Me,distance:0,decay:0};break;case"HemisphereLight":t={direction:new B,skyColor:new Me,groundColor:new Me};break;case"RectAreaLight":t={color:new Me,position:new B,halfWidth:new B,halfHeight:new B};break}return o[e.id]=t,t},"get")}}d(TM,"UniformsCache");function BM(){let o={};return{get:d(function(e){if(o[e.id]!==void 0)return o[e.id];let t;switch(e.type){case"DirectionalLight":t={shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Be};break;case"SpotLight":t={shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Be};break;case"PointLight":t={shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Be,shadowCameraNear:1,shadowCameraFar:1e3};break}return o[e.id]=t,t},"get")}}d(BM,"ShadowUniformsCache");var RM=0;function DM(o,e){return(e.castShadow?2:0)-(o.castShadow?2:0)+(e.map?1:0)-(o.map?1:0)}d(DM,"shadowCastingAndTexturingLightsFirst");function LM(o,e){let t=new TM,n=BM(),i={version:0,hash:{directionalLength:-1,pointLength:-1,spotLength:-1,rectAreaLength:-1,hemiLength:-1,numDirectionalShadows:-1,numPointShadows:-1,numSpotShadows:-1,numSpotMaps:-1},ambient:[0,0,0],probe:[],directional:[],directionalShadow:[],directionalShadowMap:[],directionalShadowMatrix:[],spot:[],spotLightMap:[],spotShadow:[],spotShadowMap:[],spotLightMatrix:[],rectArea:[],rectAreaLTC1:null,rectAreaLTC2:null,point:[],pointShadow:[],pointShadowMap:[],pointShadowMatrix:[],hemi:[],numSpotLightShadowsWithMaps:0};for(let h=0;h<9;h++)i.probe.push(new B);let s=new B,r=new Ie,a=new Ie;function l(h,u){let f=0,p=0,g=0;for(let N=0;N<9;N++)i.probe[N].set(0,0,0);let A=0,m=0,_=0,E=0,x=0,y=0,w=0,I=0,S=0,v=0;h.sort(DM);let b=u!==!0?Math.PI:1;for(let N=0,z=h.length;N<z;N++){let O=h[N],D=O.color,Q=O.intensity,q=O.distance,H=O.shadow&&O.shadow.map?O.shadow.map.texture:null;if(O.isAmbientLight)f+=D.r*Q*b,p+=D.g*Q*b,g+=D.b*Q*b;else if(O.isLightProbe)for(let k=0;k<9;k++)i.probe[k].addScaledVector(O.sh.coefficients[k],Q);else if(O.isDirectionalLight){let k=t.get(O);if(k.color.copy(O.color).multiplyScalar(O.intensity*b),O.castShadow){let j=O.shadow,Z=n.get(O);Z.shadowBias=j.bias,Z.shadowNormalBias=j.normalBias,Z.shadowRadius=j.radius,Z.shadowMapSize=j.mapSize,i.directionalShadow[A]=Z,i.directionalShadowMap[A]=H,i.directionalShadowMatrix[A]=O.shadow.matrix,y++}i.directional[A]=k,A++}else if(O.isSpotLight){let k=t.get(O);k.position.setFromMatrixPosition(O.matrixWorld),k.color.copy(D).multiplyScalar(Q*b),k.distance=q,k.coneCos=Math.cos(O.angle),k.penumbraCos=Math.cos(O.angle*(1-O.penumbra)),k.decay=O.decay,i.spot[_]=k;let j=O.shadow;if(O.map&&(i.spotLightMap[S]=O.map,S++,j.updateMatrices(O),O.castShadow&&v++),i.spotLightMatrix[_]=j.matrix,O.castShadow){let Z=n.get(O);Z.shadowBias=j.bias,Z.shadowNormalBias=j.normalBias,Z.shadowRadius=j.radius,Z.shadowMapSize=j.mapSize,i.spotShadow[_]=Z,i.spotShadowMap[_]=H,I++}_++}else if(O.isRectAreaLight){let k=t.get(O);k.color.copy(D).multiplyScalar(Q),k.halfWidth.set(O.width*.5,0,0),k.halfHeight.set(0,O.height*.5,0),i.rectArea[E]=k,E++}else if(O.isPointLight){let k=t.get(O);if(k.color.copy(O.color).multiplyScalar(O.intensity*b),k.distance=O.distance,k.decay=O.decay,O.castShadow){let j=O.shadow,Z=n.get(O);Z.shadowBias=j.bias,Z.shadowNormalBias=j.normalBias,Z.shadowRadius=j.radius,Z.shadowMapSize=j.mapSize,Z.shadowCameraNear=j.camera.near,Z.shadowCameraFar=j.camera.far,i.pointShadow[m]=Z,i.pointShadowMap[m]=H,i.pointShadowMatrix[m]=O.shadow.matrix,w++}i.point[m]=k,m++}else if(O.isHemisphereLight){let k=t.get(O);k.skyColor.copy(O.color).multiplyScalar(Q*b),k.groundColor.copy(O.groundColor).multiplyScalar(Q*b),i.hemi[x]=k,x++}}E>0&&(e.isWebGL2||o.has("OES_texture_float_linear")===!0?(i.rectAreaLTC1=le.LTC_FLOAT_1,i.rectAreaLTC2=le.LTC_FLOAT_2):o.has("OES_texture_half_float_linear")===!0?(i.rectAreaLTC1=le.LTC_HALF_1,i.rectAreaLTC2=le.LTC_HALF_2):console.error("THREE.WebGLRenderer: Unable to use RectAreaLight. Missing WebGL extensions.")),i.ambient[0]=f,i.ambient[1]=p,i.ambient[2]=g;let R=i.hash;(R.directionalLength!==A||R.pointLength!==m||R.spotLength!==_||R.rectAreaLength!==E||R.hemiLength!==x||R.numDirectionalShadows!==y||R.numPointShadows!==w||R.numSpotShadows!==I||R.numSpotMaps!==S)&&(i.directional.length=A,i.spot.length=_,i.rectArea.length=E,i.point.length=m,i.hemi.length=x,i.directionalShadow.length=y,i.directionalShadowMap.length=y,i.pointShadow.length=w,i.pointShadowMap.length=w,i.spotShadow.length=I,i.spotShadowMap.length=I,i.directionalShadowMatrix.length=y,i.pointShadowMatrix.length=w,i.spotLightMatrix.length=I+S-v,i.spotLightMap.length=S,i.numSpotLightShadowsWithMaps=v,R.directionalLength=A,R.pointLength=m,R.spotLength=_,R.rectAreaLength=E,R.hemiLength=x,R.numDirectionalShadows=y,R.numPointShadows=w,R.numSpotShadows=I,R.numSpotMaps=S,i.version=RM++)}d(l,"setup");function c(h,u){let f=0,p=0,g=0,A=0,m=0,_=u.matrixWorldInverse;for(let E=0,x=h.length;E<x;E++){let y=h[E];if(y.isDirectionalLight){let w=i.directional[f];w.direction.setFromMatrixPosition(y.matrixWorld),s.setFromMatrixPosition(y.target.matrixWorld),w.direction.sub(s),w.direction.transformDirection(_),f++}else if(y.isSpotLight){let w=i.spot[g];w.position.setFromMatrixPosition(y.matrixWorld),w.position.applyMatrix4(_),w.direction.setFromMatrixPosition(y.matrixWorld),s.setFromMatrixPosition(y.target.matrixWorld),w.direction.sub(s),w.direction.transformDirection(_),g++}else if(y.isRectAreaLight){let w=i.rectArea[A];w.position.setFromMatrixPosition(y.matrixWorld),w.position.applyMatrix4(_),a.identity(),r.copy(y.matrixWorld),r.premultiply(_),a.extractRotation(r),w.halfWidth.set(y.width*.5,0,0),w.halfHeight.set(0,y.height*.5,0),w.halfWidth.applyMatrix4(a),w.halfHeight.applyMatrix4(a),A++}else if(y.isPointLight){let w=i.point[p];w.position.setFromMatrixPosition(y.matrixWorld),w.position.applyMatrix4(_),p++}else if(y.isHemisphereLight){let w=i.hemi[m];w.direction.setFromMatrixPosition(y.matrixWorld),w.direction.transformDirection(_),m++}}}return d(c,"setupView"),{setup:l,setupView:c,state:i}}d(LM,"WebGLLights");function gA(o,e){let t=new LM(o,e),n=[],i=[];function s(){n.length=0,i.length=0}d(s,"init");function r(u){n.push(u)}d(r,"pushLight");function a(u){i.push(u)}d(a,"pushShadow");function l(u){t.setup(n,u)}d(l,"setupLights");function c(u){t.setupView(n,u)}return d(c,"setupLightsView"),{init:s,state:{lightsArray:n,shadowsArray:i,lights:t},setupLights:l,setupLightsView:c,pushLight:r,pushShadow:a}}d(gA,"WebGLRenderState");function PM(o,e){let t=new WeakMap;function n(s,r=0){let a=t.get(s),l;return a===void 0?(l=new gA(o,e),t.set(s,[l])):r>=a.length?(l=new gA(o,e),a.push(l)):l=a[r],l}d(n,"get");function i(){t=new WeakMap}return d(i,"dispose"),{get:n,dispose:i}}d(PM,"WebGLRenderStates");var Fo=class extends sn{static{d(this,"MeshDepthMaterial")}constructor(e){super(),this.isMeshDepthMaterial=!0,this.type="MeshDepthMaterial",this.depthPacking=Vy,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.wireframe=!1,this.wireframeLinewidth=1,this.setValues(e)}copy(e){return super.copy(e),this.depthPacking=e.depthPacking,this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this}},su=class extends sn{static{d(this,"MeshDistanceMaterial")}constructor(e){super(),this.isMeshDistanceMaterial=!0,this.type="MeshDistanceMaterial",this.referencePosition=new B,this.nearDistance=1,this.farDistance=1e3,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.setValues(e)}copy(e){return super.copy(e),this.referencePosition.copy(e.referencePosition),this.nearDistance=e.nearDistance,this.farDistance=e.farDistance,this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this}},FM=`void main() {
	gl_Position = vec4( position, 1.0 );
}`,OM=`uniform sampler2D shadow_pass;
uniform vec2 resolution;
uniform float radius;
#include <packing>
void main() {
	const float samples = float( VSM_SAMPLES );
	float mean = 0.0;
	float squared_mean = 0.0;
	float uvStride = samples <= 1.0 ? 0.0 : 2.0 / ( samples - 1.0 );
	float uvStart = samples <= 1.0 ? 0.0 : - 1.0;
	for ( float i = 0.0; i < samples; i ++ ) {
		float uvOffset = uvStart + i * uvStride;
		#ifdef HORIZONTAL_PASS
			vec2 distribution = unpackRGBATo2Half( texture2D( shadow_pass, ( gl_FragCoord.xy + vec2( uvOffset, 0.0 ) * radius ) / resolution ) );
			mean += distribution.x;
			squared_mean += distribution.y * distribution.y + distribution.x * distribution.x;
		#else
			float depth = unpackRGBAToDepth( texture2D( shadow_pass, ( gl_FragCoord.xy + vec2( 0.0, uvOffset ) * radius ) / resolution ) );
			mean += depth;
			squared_mean += depth * depth;
		#endif
	}
	mean = mean / samples;
	squared_mean = squared_mean / samples;
	float std_dev = sqrt( squared_mean - mean * mean );
	gl_FragColor = pack2HalfToRGBA( vec2( mean, std_dev ) );
}`;function NM(o,e,t){let n=new Po,i=new Be,s=new Be,r=new nt,a=new Fo({depthPacking:Hy}),l=new su,c={},h=t.maxTextureSize,u={[fn]:dt,[dt]:fn,[Et]:Et},f=new Yt({defines:{VSM_SAMPLES:8},uniforms:{shadow_pass:{value:null},resolution:{value:new Be},radius:{value:4}},vertexShader:FM,fragmentShader:OM}),p=f.clone();p.defines.HORIZONTAL_PASS=1;let g=new kt;g.setAttribute("position",new je(new Float32Array([-1,-1,.5,3,-1,.5,-1,3,.5]),3));let A=new pe(g,f),m=this;this.enabled=!1,this.autoUpdate=!0,this.needsUpdate=!1,this.type=NA,this.render=function(y,w,I){if(m.enabled===!1||m.autoUpdate===!1&&m.needsUpdate===!1||y.length===0)return;let S=o.getRenderTarget(),v=o.getActiveCubeFace(),b=o.getActiveMipmapLevel(),R=o.state;R.setBlending(ri),R.buffers.color.setClear(1,1,1,1),R.buffers.depth.setTest(!0),R.setScissorTest(!1);for(let N=0,z=y.length;N<z;N++){let O=y[N],D=O.shadow;if(D===void 0){console.warn("THREE.WebGLShadowMap:",O,"has no shadow.");continue}if(D.autoUpdate===!1&&D.needsUpdate===!1)continue;i.copy(D.mapSize);let Q=D.getFrameExtents();if(i.multiply(Q),s.copy(D.mapSize),(i.x>h||i.y>h)&&(i.x>h&&(s.x=Math.floor(h/Q.x),i.x=s.x*Q.x,D.mapSize.x=s.x),i.y>h&&(s.y=Math.floor(h/Q.y),i.y=s.y*Q.y,D.mapSize.y=s.y)),D.map===null){let H=this.type!==xo?{minFilter:ct,magFilter:ct}:{};D.map=new Xt(i.x,i.y,H),D.map.texture.name=O.name+".shadowMap",D.camera.updateProjectionMatrix()}o.setRenderTarget(D.map),o.clear();let q=D.getViewportCount();for(let H=0;H<q;H++){let k=D.getViewport(H);r.set(s.x*k.x,s.y*k.y,s.x*k.z,s.y*k.w),R.viewport(r),D.updateMatrices(O,H),n=D.getFrustum(),x(w,I,D.camera,O,this.type)}D.isPointLightShadow!==!0&&this.type===xo&&_(D,I),D.needsUpdate=!1}m.needsUpdate=!1,o.setRenderTarget(S,v,b)};function _(y,w){let I=e.update(A);f.defines.VSM_SAMPLES!==y.blurSamples&&(f.defines.VSM_SAMPLES=y.blurSamples,p.defines.VSM_SAMPLES=y.blurSamples,f.needsUpdate=!0,p.needsUpdate=!0),y.mapPass===null&&(y.mapPass=new Xt(i.x,i.y)),f.uniforms.shadow_pass.value=y.map.texture,f.uniforms.resolution.value=y.mapSize,f.uniforms.radius.value=y.radius,o.setRenderTarget(y.mapPass),o.clear(),o.renderBufferDirect(w,null,I,f,A,null),p.uniforms.shadow_pass.value=y.mapPass.texture,p.uniforms.resolution.value=y.mapSize,p.uniforms.radius.value=y.radius,o.setRenderTarget(y.map),o.clear(),o.renderBufferDirect(w,null,I,p,A,null)}d(_,"VSMPass");function E(y,w,I,S,v,b){let R=null,N=I.isPointLight===!0?y.customDistanceMaterial:y.customDepthMaterial;if(N!==void 0)R=N;else if(R=I.isPointLight===!0?l:a,o.localClippingEnabled&&w.clipShadows===!0&&Array.isArray(w.clippingPlanes)&&w.clippingPlanes.length!==0||w.displacementMap&&w.displacementScale!==0||w.alphaMap&&w.alphaTest>0||w.map&&w.alphaTest>0){let z=R.uuid,O=w.uuid,D=c[z];D===void 0&&(D={},c[z]=D);let Q=D[O];Q===void 0&&(Q=R.clone(),D[O]=Q),R=Q}return R.visible=w.visible,R.wireframe=w.wireframe,b===xo?R.side=w.shadowSide!==null?w.shadowSide:w.side:R.side=w.shadowSide!==null?w.shadowSide:u[w.side],R.alphaMap=w.alphaMap,R.alphaTest=w.alphaTest,R.map=w.map,R.clipShadows=w.clipShadows,R.clippingPlanes=w.clippingPlanes,R.clipIntersection=w.clipIntersection,R.displacementMap=w.displacementMap,R.displacementScale=w.displacementScale,R.displacementBias=w.displacementBias,R.wireframeLinewidth=w.wireframeLinewidth,R.linewidth=w.linewidth,I.isPointLight===!0&&R.isMeshDistanceMaterial===!0&&(R.referencePosition.setFromMatrixPosition(I.matrixWorld),R.nearDistance=S,R.farDistance=v),R}d(E,"getDepthMaterial");function x(y,w,I,S,v){if(y.visible===!1)return;if(y.layers.test(w.layers)&&(y.isMesh||y.isLine||y.isPoints)&&(y.castShadow||y.receiveShadow&&v===xo)&&(!y.frustumCulled||n.intersectsObject(y))){y.modelViewMatrix.multiplyMatrices(I.matrixWorldInverse,y.matrixWorld);let N=e.update(y),z=y.material;if(Array.isArray(z)){let O=N.groups;for(let D=0,Q=O.length;D<Q;D++){let q=O[D],H=z[q.materialIndex];if(H&&H.visible){let k=E(y,H,S,I.near,I.far,v);o.renderBufferDirect(I,null,N,k,y,q)}}}else if(z.visible){let O=E(y,z,S,I.near,I.far,v);o.renderBufferDirect(I,null,N,O,y,null)}}let R=y.children;for(let N=0,z=R.length;N<z;N++)x(R[N],w,I,S,v)}d(x,"renderObject")}d(NM,"WebGLShadowMap");function UM(o,e,t){let n=t.isWebGL2;function i(){let F=!1,K=new nt,te=null,de=new nt(0,0,0,0);return{setMask:d(function(_e){te!==_e&&!F&&(o.colorMask(_e,_e,_e,_e),te=_e)},"setMask"),setLocked:d(function(_e){F=_e},"setLocked"),setClear:d(function(_e,Ke,Bt,Wt,ls){ls===!0&&(_e*=Wt,Ke*=Wt,Bt*=Wt),K.set(_e,Ke,Bt,Wt),de.equals(K)===!1&&(o.clearColor(_e,Ke,Bt,Wt),de.copy(K))},"setClear"),reset:d(function(){F=!1,te=null,de.set(-1,0,0,0)},"reset")}}d(i,"ColorBuffer");function s(){let F=!1,K=null,te=null,de=null;return{setTest:d(function(_e){_e?Te(2929):Ae(2929)},"setTest"),setMask:d(function(_e){K!==_e&&!F&&(o.depthMask(_e),K=_e)},"setMask"),setFunc:d(function(_e){if(te!==_e){switch(_e){case gy:o.depthFunc(512);break;case _y:o.depthFunc(519);break;case yy:o.depthFunc(513);break;case Kh:o.depthFunc(515);break;case xy:o.depthFunc(514);break;case vy:o.depthFunc(518);break;case Ey:o.depthFunc(516);break;case wy:o.depthFunc(517);break;default:o.depthFunc(515)}te=_e}},"setFunc"),setLocked:d(function(_e){F=_e},"setLocked"),setClear:d(function(_e){de!==_e&&(o.clearDepth(_e),de=_e)},"setClear"),reset:d(function(){F=!1,K=null,te=null,de=null},"reset")}}d(s,"DepthBuffer");function r(){let F=!1,K=null,te=null,de=null,_e=null,Ke=null,Bt=null,Wt=null,ls=null;return{setTest:d(function(at){F||(at?Te(2960):Ae(2960))},"setTest"),setMask:d(function(at){K!==at&&!F&&(o.stencilMask(at),K=at)},"setMask"),setFunc:d(function(at,ui,Dn){(te!==at||de!==ui||_e!==Dn)&&(o.stencilFunc(at,ui,Dn),te=at,de=ui,_e=Dn)},"setFunc"),setOp:d(function(at,ui,Dn){(Ke!==at||Bt!==ui||Wt!==Dn)&&(o.stencilOp(at,ui,Dn),Ke=at,Bt=ui,Wt=Dn)},"setOp"),setLocked:d(function(at){F=at},"setLocked"),setClear:d(function(at){ls!==at&&(o.clearStencil(at),ls=at)},"setClear"),reset:d(function(){F=!1,K=null,te=null,de=null,_e=null,Ke=null,Bt=null,Wt=null,ls=null},"reset")}}d(r,"StencilBuffer");let a=new i,l=new s,c=new r,h=new WeakMap,u=new WeakMap,f={},p={},g=new WeakMap,A=[],m=null,_=!1,E=null,x=null,y=null,w=null,I=null,S=null,v=null,b=!1,R=null,N=null,z=null,O=null,D=null,Q=o.getParameter(35661),q=!1,H=0,k=o.getParameter(7938);k.indexOf("WebGL")!==-1?(H=parseFloat(/^WebGL (\d)/.exec(k)[1]),q=H>=1):k.indexOf("OpenGL ES")!==-1&&(H=parseFloat(/^OpenGL ES (\d)/.exec(k)[1]),q=H>=2);let j=null,Z={},fe=o.getParameter(3088),V=o.getParameter(2978),ee=new nt().fromArray(fe),re=new nt().fromArray(V);function ie(F,K,te){let de=new Uint8Array(4),_e=o.createTexture();o.bindTexture(F,_e),o.texParameteri(F,10241,9728),o.texParameteri(F,10240,9728);for(let Ke=0;Ke<te;Ke++)o.texImage2D(K+Ke,0,6408,1,1,0,6408,5121,de);return _e}d(ie,"createTexture");let W={};W[3553]=ie(3553,3553,1),W[34067]=ie(34067,34069,6),a.setClear(0,0,0,1),l.setClear(1),c.setClear(0),Te(2929),l.setFunc(Kh),Ht(!1),Rn(Ap),Te(2884),yt(ri);function Te(F){f[F]!==!0&&(o.enable(F),f[F]=!0)}d(Te,"enable");function Ae(F){f[F]!==!1&&(o.disable(F),f[F]=!1)}d(Ae,"disable");function ge(F,K){return p[F]!==K?(o.bindFramebuffer(F,K),p[F]=K,n&&(F===36009&&(p[36160]=K),F===36160&&(p[36009]=K)),!0):!1}d(ge,"bindFramebuffer");function ce(F,K){let te=A,de=!1;if(F)if(te=g.get(K),te===void 0&&(te=[],g.set(K,te)),F.isWebGLMultipleRenderTargets){let _e=F.texture;if(te.length!==_e.length||te[0]!==36064){for(let Ke=0,Bt=_e.length;Ke<Bt;Ke++)te[Ke]=36064+Ke;te.length=_e.length,de=!0}}else te[0]!==36064&&(te[0]=36064,de=!0);else te[0]!==1029&&(te[0]=1029,de=!0);de&&(t.isWebGL2?o.drawBuffers(te):e.get("WEBGL_draw_buffers").drawBuffersWEBGL(te))}d(ce,"drawBuffers");function $e(F){return m!==F?(o.useProgram(F),m=F,!0):!1}d($e,"useProgram");let Le={[Ys]:32774,[oy]:32778,[ay]:32779};if(n)Le[yp]=32775,Le[xp]=32776;else{let F=e.get("EXT_blend_minmax");F!==null&&(Le[yp]=F.MIN_EXT,Le[xp]=F.MAX_EXT)}let Ce={[ly]:0,[cy]:1,[hy]:768,[UA]:770,[my]:776,[py]:774,[dy]:772,[uy]:769,[QA]:771,[Ay]:775,[fy]:773};function yt(F,K,te,de,_e,Ke,Bt,Wt){if(F===ri){_===!0&&(Ae(3042),_=!1);return}if(_===!1&&(Te(3042),_=!0),F!==ry){if(F!==E||Wt!==b){if((x!==Ys||I!==Ys)&&(o.blendEquation(32774),x=Ys,I=Ys),Wt)switch(F){case er:o.blendFuncSeparate(1,771,1,771);break;case mp:o.blendFunc(1,1);break;case gp:o.blendFuncSeparate(0,769,0,1);break;case _p:o.blendFuncSeparate(0,768,0,770);break;default:console.error("THREE.WebGLState: Invalid blending: ",F);break}else switch(F){case er:o.blendFuncSeparate(770,771,1,771);break;case mp:o.blendFunc(770,1);break;case gp:o.blendFuncSeparate(0,769,0,1);break;case _p:o.blendFunc(0,768);break;default:console.error("THREE.WebGLState: Invalid blending: ",F);break}y=null,w=null,S=null,v=null,E=F,b=Wt}return}_e=_e||K,Ke=Ke||te,Bt=Bt||de,(K!==x||_e!==I)&&(o.blendEquationSeparate(Le[K],Le[_e]),x=K,I=_e),(te!==y||de!==w||Ke!==S||Bt!==v)&&(o.blendFuncSeparate(Ce[te],Ce[de],Ce[Ke],Ce[Bt]),y=te,w=de,S=Ke,v=Bt),E=F,b=!1}d(yt,"setBlending");function Bn(F,K){F.side===Et?Ae(2884):Te(2884);let te=F.side===dt;K&&(te=!te),Ht(te),F.blending===er&&F.transparent===!1?yt(ri):yt(F.blending,F.blendEquation,F.blendSrc,F.blendDst,F.blendEquationAlpha,F.blendSrcAlpha,F.blendDstAlpha,F.premultipliedAlpha),l.setFunc(F.depthFunc),l.setTest(F.depthTest),l.setMask(F.depthWrite),a.setMask(F.colorWrite);let de=F.stencilWrite;c.setTest(de),de&&(c.setMask(F.stencilWriteMask),c.setFunc(F.stencilFunc,F.stencilRef,F.stencilFuncMask),c.setOp(F.stencilFail,F.stencilZFail,F.stencilZPass)),Xe(F.polygonOffset,F.polygonOffsetFactor,F.polygonOffsetUnits),F.alphaToCoverage===!0?Te(32926):Ae(32926)}d(Bn,"setMaterial");function Ht(F){R!==F&&(F?o.frontFace(2304):o.frontFace(2305),R=F)}d(Ht,"setFlipSided");function Rn(F){F!==ny?(Te(2884),F!==N&&(F===Ap?o.cullFace(1029):F===iy?o.cullFace(1028):o.cullFace(1032))):Ae(2884),N=F}d(Rn,"setCullFace");function xt(F){F!==z&&(q&&o.lineWidth(F),z=F)}d(xt,"setLineWidth");function Xe(F,K,te){F?(Te(32823),(O!==K||D!==te)&&(o.polygonOffset(K,te),O=K,D=te)):Ae(32823)}d(Xe,"setPolygonOffset");function hi(F){F?Te(3089):Ae(3089)}d(hi,"setScissorTest");function zn(F){F===void 0&&(F=33984+Q-1),j!==F&&(o.activeTexture(F),j=F)}d(zn,"activeTexture");function T(F,K,te){te===void 0&&(j===null?te=33984+Q-1:te=j);let de=Z[te];de===void 0&&(de={type:void 0,texture:void 0},Z[te]=de),(de.type!==F||de.texture!==K)&&(j!==te&&(o.activeTexture(te),j=te),o.bindTexture(F,K||W[F]),de.type=F,de.texture=K)}d(T,"bindTexture");function M(){let F=Z[j];F!==void 0&&F.type!==void 0&&(o.bindTexture(F.type,null),F.type=void 0,F.texture=void 0)}d(M,"unbindTexture");function X(){try{o.compressedTexImage2D.apply(o,arguments)}catch(F){console.error("THREE.WebGLState:",F)}}d(X,"compressedTexImage2D");function se(){try{o.compressedTexImage3D.apply(o,arguments)}catch(F){console.error("THREE.WebGLState:",F)}}d(se,"compressedTexImage3D");function ae(){try{o.texSubImage2D.apply(o,arguments)}catch(F){console.error("THREE.WebGLState:",F)}}d(ae,"texSubImage2D");function he(){try{o.texSubImage3D.apply(o,arguments)}catch(F){console.error("THREE.WebGLState:",F)}}d(he,"texSubImage3D");function Re(){try{o.compressedTexSubImage2D.apply(o,arguments)}catch(F){console.error("THREE.WebGLState:",F)}}d(Re,"compressedTexSubImage2D");function ue(){try{o.compressedTexSubImage3D.apply(o,arguments)}catch(F){console.error("THREE.WebGLState:",F)}}d(ue,"compressedTexSubImage3D");function J(){try{o.texStorage2D.apply(o,arguments)}catch(F){console.error("THREE.WebGLState:",F)}}d(J,"texStorage2D");function Ee(){try{o.texStorage3D.apply(o,arguments)}catch(F){console.error("THREE.WebGLState:",F)}}d(Ee,"texStorage3D");function be(){try{o.texImage2D.apply(o,arguments)}catch(F){console.error("THREE.WebGLState:",F)}}d(be,"texImage2D");function me(){try{o.texImage3D.apply(o,arguments)}catch(F){console.error("THREE.WebGLState:",F)}}d(me,"texImage3D");function we(F){ee.equals(F)===!1&&(o.scissor(F.x,F.y,F.z,F.w),ee.copy(F))}d(we,"scissor");function xe(F){re.equals(F)===!1&&(o.viewport(F.x,F.y,F.z,F.w),re.copy(F))}d(xe,"viewport");function Ve(F,K){let te=u.get(K);te===void 0&&(te=new WeakMap,u.set(K,te));let de=te.get(F);de===void 0&&(de=o.getUniformBlockIndex(K,F.name),te.set(F,de))}d(Ve,"updateUBOMapping");function ot(F,K){let de=u.get(K).get(F);h.get(K)!==de&&(o.uniformBlockBinding(K,de,F.__bindingPointIndex),h.set(K,de))}d(ot,"uniformBlockBinding");function Tt(){o.disable(3042),o.disable(2884),o.disable(2929),o.disable(32823),o.disable(3089),o.disable(2960),o.disable(32926),o.blendEquation(32774),o.blendFunc(1,0),o.blendFuncSeparate(1,0,1,0),o.colorMask(!0,!0,!0,!0),o.clearColor(0,0,0,0),o.depthMask(!0),o.depthFunc(513),o.clearDepth(1),o.stencilMask(4294967295),o.stencilFunc(519,0,4294967295),o.stencilOp(7680,7680,7680),o.clearStencil(0),o.cullFace(1029),o.frontFace(2305),o.polygonOffset(0,0),o.activeTexture(33984),o.bindFramebuffer(36160,null),n===!0&&(o.bindFramebuffer(36009,null),o.bindFramebuffer(36008,null)),o.useProgram(null),o.lineWidth(1),o.scissor(0,0,o.canvas.width,o.canvas.height),o.viewport(0,0,o.canvas.width,o.canvas.height),f={},j=null,Z={},p={},g=new WeakMap,A=[],m=null,_=!1,E=null,x=null,y=null,w=null,I=null,S=null,v=null,b=!1,R=null,N=null,z=null,O=null,D=null,ee.set(0,0,o.canvas.width,o.canvas.height),re.set(0,0,o.canvas.width,o.canvas.height),a.reset(),l.reset(),c.reset()}return d(Tt,"reset"),{buffers:{color:a,depth:l,stencil:c},enable:Te,disable:Ae,bindFramebuffer:ge,drawBuffers:ce,useProgram:$e,setBlending:yt,setMaterial:Bn,setFlipSided:Ht,setCullFace:Rn,setLineWidth:xt,setPolygonOffset:Xe,setScissorTest:hi,activeTexture:zn,bindTexture:T,unbindTexture:M,compressedTexImage2D:X,compressedTexImage3D:se,texImage2D:be,texImage3D:me,updateUBOMapping:Ve,uniformBlockBinding:ot,texStorage2D:J,texStorage3D:Ee,texSubImage2D:ae,texSubImage3D:he,compressedTexSubImage2D:Re,compressedTexSubImage3D:ue,scissor:we,viewport:xe,reset:Tt}}d(UM,"WebGLState");function QM(o,e,t,n,i,s,r){let a=i.isWebGL2,l=i.maxTextures,c=i.maxCubemapSize,h=i.maxTextureSize,u=i.maxSamples,f=e.has("WEBGL_multisampled_render_to_texture")?e.get("WEBGL_multisampled_render_to_texture"):null,p=typeof navigator>"u"?!1:/OculusBrowser/g.test(navigator.userAgent),g=new WeakMap,A,m=new WeakMap,_=!1;try{_=typeof OffscreenCanvas<"u"&&new OffscreenCanvas(1,1).getContext("2d")!==null}catch{}function E(T,M){return _?new OffscreenCanvas(T,M):Ro("canvas")}d(E,"createCanvas");function x(T,M,X,se){let ae=1;if((T.width>se||T.height>se)&&(ae=se/Math.max(T.width,T.height)),ae<1||M===!0)if(typeof HTMLImageElement<"u"&&T instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&T instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&T instanceof ImageBitmap){let he=M?_l:Math.floor,Re=he(ae*T.width),ue=he(ae*T.height);A===void 0&&(A=E(Re,ue));let J=X?E(Re,ue):A;return J.width=Re,J.height=ue,J.getContext("2d").drawImage(T,0,0,Re,ue),console.warn("THREE.WebGLRenderer: Texture has been resized from ("+T.width+"x"+T.height+") to ("+Re+"x"+ue+")."),J}else return"data"in T&&console.warn("THREE.WebGLRenderer: Image in DataTexture is too big ("+T.width+"x"+T.height+")."),T;return T}d(x,"resizeImage");function y(T){return Jh(T.width)&&Jh(T.height)}d(y,"isPowerOfTwo$1");function w(T){return a?!1:T.wrapS!==Lt||T.wrapT!==Lt||T.minFilter!==ct&&T.minFilter!==Je}d(w,"textureNeedsPowerOfTwo");function I(T,M){return T.generateMipmaps&&M&&T.minFilter!==ct&&T.minFilter!==Je}d(I,"textureNeedsGenerateMipmaps");function S(T){o.generateMipmap(T)}d(S,"generateMipmap");function v(T,M,X,se,ae=!1){if(a===!1)return M;if(T!==null){if(o[T]!==void 0)return o[T];console.warn("THREE.WebGLRenderer: Attempt to use non-existing WebGL internal format '"+T+"'")}let he=M;return M===6403&&(X===5126&&(he=33326),X===5131&&(he=33325),X===5121&&(he=33321)),M===33319&&(X===5126&&(he=33328),X===5131&&(he=33327),X===5121&&(he=33323)),M===6408&&(X===5126&&(he=34836),X===5131&&(he=34842),X===5121&&(he=se===Se&&ae===!1?35907:32856),X===32819&&(he=32854),X===32820&&(he=32855)),(he===33325||he===33326||he===33327||he===33328||he===34842||he===34836)&&e.get("EXT_color_buffer_float"),he}d(v,"getInternalFormat");function b(T,M,X){return I(T,X)===!0||T.isFramebufferTexture&&T.minFilter!==ct&&T.minFilter!==Je?Math.log2(Math.max(M.width,M.height))+1:T.mipmaps!==void 0&&T.mipmaps.length>0?T.mipmaps.length:T.isCompressedTexture&&Array.isArray(T.image)?M.mipmaps.length:1}d(b,"getMipLevels");function R(T){return T===ct||T===rr||T===_s?9728:9729}d(R,"filterFallback");function N(T){let M=T.target;M.removeEventListener("dispose",N),O(M),M.isVideoTexture&&g.delete(M)}d(N,"onTextureDispose");function z(T){let M=T.target;M.removeEventListener("dispose",z),Q(M)}d(z,"onRenderTargetDispose");function O(T){let M=n.get(T);if(M.__webglInit===void 0)return;let X=T.source,se=m.get(X);if(se){let ae=se[M.__cacheKey];ae.usedTimes--,ae.usedTimes===0&&D(T),Object.keys(se).length===0&&m.delete(X)}n.remove(T)}d(O,"deallocateTexture");function D(T){let M=n.get(T);o.deleteTexture(M.__webglTexture);let X=T.source,se=m.get(X);delete se[M.__cacheKey],r.memory.textures--}d(D,"deleteTexture");function Q(T){let M=T.texture,X=n.get(T),se=n.get(M);if(se.__webglTexture!==void 0&&(o.deleteTexture(se.__webglTexture),r.memory.textures--),T.depthTexture&&T.depthTexture.dispose(),T.isWebGLCubeRenderTarget)for(let ae=0;ae<6;ae++)o.deleteFramebuffer(X.__webglFramebuffer[ae]),X.__webglDepthbuffer&&o.deleteRenderbuffer(X.__webglDepthbuffer[ae]);else{if(o.deleteFramebuffer(X.__webglFramebuffer),X.__webglDepthbuffer&&o.deleteRenderbuffer(X.__webglDepthbuffer),X.__webglMultisampledFramebuffer&&o.deleteFramebuffer(X.__webglMultisampledFramebuffer),X.__webglColorRenderbuffer)for(let ae=0;ae<X.__webglColorRenderbuffer.length;ae++)X.__webglColorRenderbuffer[ae]&&o.deleteRenderbuffer(X.__webglColorRenderbuffer[ae]);X.__webglDepthRenderbuffer&&o.deleteRenderbuffer(X.__webglDepthRenderbuffer)}if(T.isWebGLMultipleRenderTargets)for(let ae=0,he=M.length;ae<he;ae++){let Re=n.get(M[ae]);Re.__webglTexture&&(o.deleteTexture(Re.__webglTexture),r.memory.textures--),n.remove(M[ae])}n.remove(M),n.remove(T)}d(Q,"deallocateRenderTarget");let q=0;function H(){q=0}d(H,"resetTextureUnits");function k(){let T=q;return T>=l&&console.warn("THREE.WebGLTextures: Trying to use "+T+" texture units while this GPU supports only "+l),q+=1,T}d(k,"allocateTextureUnit");function j(T){let M=[];return M.push(T.wrapS),M.push(T.wrapT),M.push(T.wrapR||0),M.push(T.magFilter),M.push(T.minFilter),M.push(T.anisotropy),M.push(T.internalFormat),M.push(T.format),M.push(T.type),M.push(T.generateMipmaps),M.push(T.premultiplyAlpha),M.push(T.flipY),M.push(T.unpackAlignment),M.push(T.encoding),M.join()}d(j,"getTextureCacheKey");function Z(T,M){let X=n.get(T);if(T.isVideoTexture&&hi(T),T.isRenderTargetTexture===!1&&T.version>0&&X.__version!==T.version){let se=T.image;if(se===null)console.warn("THREE.WebGLRenderer: Texture marked for update but no image data found.");else if(se.complete===!1)console.warn("THREE.WebGLRenderer: Texture marked for update but image is incomplete");else{Ae(X,T,M);return}}t.bindTexture(3553,X.__webglTexture,33984+M)}d(Z,"setTexture2D");function fe(T,M){let X=n.get(T);if(T.version>0&&X.__version!==T.version){Ae(X,T,M);return}t.bindTexture(35866,X.__webglTexture,33984+M)}d(fe,"setTexture2DArray");function V(T,M){let X=n.get(T);if(T.version>0&&X.__version!==T.version){Ae(X,T,M);return}t.bindTexture(32879,X.__webglTexture,33984+M)}d(V,"setTexture3D");function ee(T,M){let X=n.get(T);if(T.version>0&&X.__version!==T.version){ge(X,T,M);return}t.bindTexture(34067,X.__webglTexture,33984+M)}d(ee,"setTextureCube");let re={[Pn]:10497,[Lt]:33071,[vs]:33648},ie={[ct]:9728,[rr]:9984,[_s]:9986,[Je]:9729,[Wo]:9985,[wn]:9987};function W(T,M,X){if(X?(o.texParameteri(T,10242,re[M.wrapS]),o.texParameteri(T,10243,re[M.wrapT]),(T===32879||T===35866)&&o.texParameteri(T,32882,re[M.wrapR]),o.texParameteri(T,10240,ie[M.magFilter]),o.texParameteri(T,10241,ie[M.minFilter])):(o.texParameteri(T,10242,33071),o.texParameteri(T,10243,33071),(T===32879||T===35866)&&o.texParameteri(T,32882,33071),(M.wrapS!==Lt||M.wrapT!==Lt)&&console.warn("THREE.WebGLRenderer: Texture is not power of two. Texture.wrapS and Texture.wrapT should be set to THREE.ClampToEdgeWrapping."),o.texParameteri(T,10240,R(M.magFilter)),o.texParameteri(T,10241,R(M.minFilter)),M.minFilter!==ct&&M.minFilter!==Je&&console.warn("THREE.WebGLRenderer: Texture is not power of two. Texture.minFilter should be set to THREE.NearestFilter or THREE.LinearFilter.")),e.has("EXT_texture_filter_anisotropic")===!0){let se=e.get("EXT_texture_filter_anisotropic");if(M.magFilter===ct||M.minFilter!==_s&&M.minFilter!==wn||M.type===Ut&&e.has("OES_texture_float_linear")===!1||a===!1&&M.type===Pt&&e.has("OES_texture_half_float_linear")===!1)return;(M.anisotropy>1||n.get(M).__currentAnisotropy)&&(o.texParameterf(T,se.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(M.anisotropy,i.getMaxAnisotropy())),n.get(M).__currentAnisotropy=M.anisotropy)}}d(W,"setTextureParameters");function Te(T,M){let X=!1;T.__webglInit===void 0&&(T.__webglInit=!0,M.addEventListener("dispose",N));let se=M.source,ae=m.get(se);ae===void 0&&(ae={},m.set(se,ae));let he=j(M);if(he!==T.__cacheKey){ae[he]===void 0&&(ae[he]={texture:o.createTexture(),usedTimes:0},r.memory.textures++,X=!0),ae[he].usedTimes++;let Re=ae[T.__cacheKey];Re!==void 0&&(ae[T.__cacheKey].usedTimes--,Re.usedTimes===0&&D(M)),T.__cacheKey=he,T.__webglTexture=ae[he].texture}return X}d(Te,"initTexture");function Ae(T,M,X){let se=3553;(M.isDataArrayTexture||M.isCompressedArrayTexture)&&(se=35866),M.isData3DTexture&&(se=32879);let ae=Te(T,M),he=M.source;t.bindTexture(se,T.__webglTexture,33984+X);let Re=n.get(he);if(he.version!==Re.__version||ae===!0){t.activeTexture(33984+X),o.pixelStorei(37440,M.flipY),o.pixelStorei(37441,M.premultiplyAlpha),o.pixelStorei(3317,M.unpackAlignment),o.pixelStorei(37443,0);let ue=w(M)&&y(M.image)===!1,J=x(M.image,ue,!1,h);J=zn(M,J);let Ee=y(J)||a,be=s.convert(M.format,M.encoding),me=s.convert(M.type),we=v(M.internalFormat,be,me,M.encoding,M.isVideoTexture);W(se,M,Ee);let xe,Ve=M.mipmaps,ot=a&&M.isVideoTexture!==!0,Tt=Re.__version===void 0||ae===!0,F=b(M,J,Ee);if(M.isDepthTexture)we=6402,a?M.type===Ut?we=36012:M.type===gs?we=33190:M.type===tr?we=35056:we=33189:M.type===Ut&&console.error("WebGLRenderer: Floating point depth texture requires WebGL2."),M.format===ys&&we===6402&&M.type!==zA&&M.type!==gs&&(console.warn("THREE.WebGLRenderer: Use UnsignedShortType or UnsignedIntType for DepthFormat DepthTexture."),M.type=gs,me=s.convert(M.type)),M.format===or&&we===6402&&(we=34041,M.type!==tr&&(console.warn("THREE.WebGLRenderer: Use UnsignedInt248Type for DepthStencilFormat DepthTexture."),M.type=tr,me=s.convert(M.type))),Tt&&(ot?t.texStorage2D(3553,1,we,J.width,J.height):t.texImage2D(3553,0,we,J.width,J.height,0,be,me,null));else if(M.isDataTexture)if(Ve.length>0&&Ee){ot&&Tt&&t.texStorage2D(3553,F,we,Ve[0].width,Ve[0].height);for(let K=0,te=Ve.length;K<te;K++)xe=Ve[K],ot?t.texSubImage2D(3553,K,0,0,xe.width,xe.height,be,me,xe.data):t.texImage2D(3553,K,we,xe.width,xe.height,0,be,me,xe.data);M.generateMipmaps=!1}else ot?(Tt&&t.texStorage2D(3553,F,we,J.width,J.height),t.texSubImage2D(3553,0,0,0,J.width,J.height,be,me,J.data)):t.texImage2D(3553,0,we,J.width,J.height,0,be,me,J.data);else if(M.isCompressedTexture)if(M.isCompressedArrayTexture){ot&&Tt&&t.texStorage3D(35866,F,we,Ve[0].width,Ve[0].height,J.depth);for(let K=0,te=Ve.length;K<te;K++)xe=Ve[K],M.format!==lt?be!==null?ot?t.compressedTexSubImage3D(35866,K,0,0,0,xe.width,xe.height,J.depth,be,xe.data,0,0):t.compressedTexImage3D(35866,K,we,xe.width,xe.height,J.depth,0,xe.data,0,0):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()"):ot?t.texSubImage3D(35866,K,0,0,0,xe.width,xe.height,J.depth,be,me,xe.data):t.texImage3D(35866,K,we,xe.width,xe.height,J.depth,0,be,me,xe.data)}else{ot&&Tt&&t.texStorage2D(3553,F,we,Ve[0].width,Ve[0].height);for(let K=0,te=Ve.length;K<te;K++)xe=Ve[K],M.format!==lt?be!==null?ot?t.compressedTexSubImage2D(3553,K,0,0,xe.width,xe.height,be,xe.data):t.compressedTexImage2D(3553,K,we,xe.width,xe.height,0,xe.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()"):ot?t.texSubImage2D(3553,K,0,0,xe.width,xe.height,be,me,xe.data):t.texImage2D(3553,K,we,xe.width,xe.height,0,be,me,xe.data)}else if(M.isDataArrayTexture)ot?(Tt&&t.texStorage3D(35866,F,we,J.width,J.height,J.depth),t.texSubImage3D(35866,0,0,0,0,J.width,J.height,J.depth,be,me,J.data)):t.texImage3D(35866,0,we,J.width,J.height,J.depth,0,be,me,J.data);else if(M.isData3DTexture)ot?(Tt&&t.texStorage3D(32879,F,we,J.width,J.height,J.depth),t.texSubImage3D(32879,0,0,0,0,J.width,J.height,J.depth,be,me,J.data)):t.texImage3D(32879,0,we,J.width,J.height,J.depth,0,be,me,J.data);else if(M.isFramebufferTexture){if(Tt)if(ot)t.texStorage2D(3553,F,we,J.width,J.height);else{let K=J.width,te=J.height;for(let de=0;de<F;de++)t.texImage2D(3553,de,we,K,te,0,be,me,null),K>>=1,te>>=1}}else if(Ve.length>0&&Ee){ot&&Tt&&t.texStorage2D(3553,F,we,Ve[0].width,Ve[0].height);for(let K=0,te=Ve.length;K<te;K++)xe=Ve[K],ot?t.texSubImage2D(3553,K,0,0,be,me,xe):t.texImage2D(3553,K,we,be,me,xe);M.generateMipmaps=!1}else ot?(Tt&&t.texStorage2D(3553,F,we,J.width,J.height),t.texSubImage2D(3553,0,0,0,be,me,J)):t.texImage2D(3553,0,we,be,me,J);I(M,Ee)&&S(se),Re.__version=he.version,M.onUpdate&&M.onUpdate(M)}T.__version=M.version}d(Ae,"uploadTexture");function ge(T,M,X){if(M.image.length!==6)return;let se=Te(T,M),ae=M.source;t.bindTexture(34067,T.__webglTexture,33984+X);let he=n.get(ae);if(ae.version!==he.__version||se===!0){t.activeTexture(33984+X),o.pixelStorei(37440,M.flipY),o.pixelStorei(37441,M.premultiplyAlpha),o.pixelStorei(3317,M.unpackAlignment),o.pixelStorei(37443,0);let Re=M.isCompressedTexture||M.image[0].isCompressedTexture,ue=M.image[0]&&M.image[0].isDataTexture,J=[];for(let K=0;K<6;K++)!Re&&!ue?J[K]=x(M.image[K],!1,!0,c):J[K]=ue?M.image[K].image:M.image[K],J[K]=zn(M,J[K]);let Ee=J[0],be=y(Ee)||a,me=s.convert(M.format,M.encoding),we=s.convert(M.type),xe=v(M.internalFormat,me,we,M.encoding),Ve=a&&M.isVideoTexture!==!0,ot=he.__version===void 0||se===!0,Tt=b(M,Ee,be);W(34067,M,be);let F;if(Re){Ve&&ot&&t.texStorage2D(34067,Tt,xe,Ee.width,Ee.height);for(let K=0;K<6;K++){F=J[K].mipmaps;for(let te=0;te<F.length;te++){let de=F[te];M.format!==lt?me!==null?Ve?t.compressedTexSubImage2D(34069+K,te,0,0,de.width,de.height,me,de.data):t.compressedTexImage2D(34069+K,te,xe,de.width,de.height,0,de.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .setTextureCube()"):Ve?t.texSubImage2D(34069+K,te,0,0,de.width,de.height,me,we,de.data):t.texImage2D(34069+K,te,xe,de.width,de.height,0,me,we,de.data)}}}else{F=M.mipmaps,Ve&&ot&&(F.length>0&&Tt++,t.texStorage2D(34067,Tt,xe,J[0].width,J[0].height));for(let K=0;K<6;K++)if(ue){Ve?t.texSubImage2D(34069+K,0,0,0,J[K].width,J[K].height,me,we,J[K].data):t.texImage2D(34069+K,0,xe,J[K].width,J[K].height,0,me,we,J[K].data);for(let te=0;te<F.length;te++){let _e=F[te].image[K].image;Ve?t.texSubImage2D(34069+K,te+1,0,0,_e.width,_e.height,me,we,_e.data):t.texImage2D(34069+K,te+1,xe,_e.width,_e.height,0,me,we,_e.data)}}else{Ve?t.texSubImage2D(34069+K,0,0,0,me,we,J[K]):t.texImage2D(34069+K,0,xe,me,we,J[K]);for(let te=0;te<F.length;te++){let de=F[te];Ve?t.texSubImage2D(34069+K,te+1,0,0,me,we,de.image[K]):t.texImage2D(34069+K,te+1,xe,me,we,de.image[K])}}}I(M,be)&&S(34067),he.__version=ae.version,M.onUpdate&&M.onUpdate(M)}T.__version=M.version}d(ge,"uploadCubeTexture");function ce(T,M,X,se,ae){let he=s.convert(X.format,X.encoding),Re=s.convert(X.type),ue=v(X.internalFormat,he,Re,X.encoding);n.get(M).__hasExternalTextures||(ae===32879||ae===35866?t.texImage3D(ae,0,ue,M.width,M.height,M.depth,0,he,Re,null):t.texImage2D(ae,0,ue,M.width,M.height,0,he,Re,null)),t.bindFramebuffer(36160,T),Xe(M)?f.framebufferTexture2DMultisampleEXT(36160,se,ae,n.get(X).__webglTexture,0,xt(M)):(ae===3553||ae>=34069&&ae<=34074)&&o.framebufferTexture2D(36160,se,ae,n.get(X).__webglTexture,0),t.bindFramebuffer(36160,null)}d(ce,"setupFrameBufferTexture");function $e(T,M,X){if(o.bindRenderbuffer(36161,T),M.depthBuffer&&!M.stencilBuffer){let se=33189;if(X||Xe(M)){let ae=M.depthTexture;ae&&ae.isDepthTexture&&(ae.type===Ut?se=36012:ae.type===gs&&(se=33190));let he=xt(M);Xe(M)?f.renderbufferStorageMultisampleEXT(36161,he,se,M.width,M.height):o.renderbufferStorageMultisample(36161,he,se,M.width,M.height)}else o.renderbufferStorage(36161,se,M.width,M.height);o.framebufferRenderbuffer(36160,36096,36161,T)}else if(M.depthBuffer&&M.stencilBuffer){let se=xt(M);X&&Xe(M)===!1?o.renderbufferStorageMultisample(36161,se,35056,M.width,M.height):Xe(M)?f.renderbufferStorageMultisampleEXT(36161,se,35056,M.width,M.height):o.renderbufferStorage(36161,34041,M.width,M.height),o.framebufferRenderbuffer(36160,33306,36161,T)}else{let se=M.isWebGLMultipleRenderTargets===!0?M.texture:[M.texture];for(let ae=0;ae<se.length;ae++){let he=se[ae],Re=s.convert(he.format,he.encoding),ue=s.convert(he.type),J=v(he.internalFormat,Re,ue,he.encoding),Ee=xt(M);X&&Xe(M)===!1?o.renderbufferStorageMultisample(36161,Ee,J,M.width,M.height):Xe(M)?f.renderbufferStorageMultisampleEXT(36161,Ee,J,M.width,M.height):o.renderbufferStorage(36161,J,M.width,M.height)}}o.bindRenderbuffer(36161,null)}d($e,"setupRenderBufferStorage");function Le(T,M){if(M&&M.isWebGLCubeRenderTarget)throw new Error("Depth Texture with cube render targets is not supported");if(t.bindFramebuffer(36160,T),!(M.depthTexture&&M.depthTexture.isDepthTexture))throw new Error("renderTarget.depthTexture must be an instance of THREE.DepthTexture");(!n.get(M.depthTexture).__webglTexture||M.depthTexture.image.width!==M.width||M.depthTexture.image.height!==M.height)&&(M.depthTexture.image.width=M.width,M.depthTexture.image.height=M.height,M.depthTexture.needsUpdate=!0),Z(M.depthTexture,0);let se=n.get(M.depthTexture).__webglTexture,ae=xt(M);if(M.depthTexture.format===ys)Xe(M)?f.framebufferTexture2DMultisampleEXT(36160,36096,3553,se,0,ae):o.framebufferTexture2D(36160,36096,3553,se,0);else if(M.depthTexture.format===or)Xe(M)?f.framebufferTexture2DMultisampleEXT(36160,33306,3553,se,0,ae):o.framebufferTexture2D(36160,33306,3553,se,0);else throw new Error("Unknown depthTexture format")}d(Le,"setupDepthTexture");function Ce(T){let M=n.get(T),X=T.isWebGLCubeRenderTarget===!0;if(T.depthTexture&&!M.__autoAllocateDepthBuffer){if(X)throw new Error("target.depthTexture not supported in Cube render targets");Le(M.__webglFramebuffer,T)}else if(X){M.__webglDepthbuffer=[];for(let se=0;se<6;se++)t.bindFramebuffer(36160,M.__webglFramebuffer[se]),M.__webglDepthbuffer[se]=o.createRenderbuffer(),$e(M.__webglDepthbuffer[se],T,!1)}else t.bindFramebuffer(36160,M.__webglFramebuffer),M.__webglDepthbuffer=o.createRenderbuffer(),$e(M.__webglDepthbuffer,T,!1);t.bindFramebuffer(36160,null)}d(Ce,"setupDepthRenderbuffer");function yt(T,M,X){let se=n.get(T);M!==void 0&&ce(se.__webglFramebuffer,T,T.texture,36064,3553),X!==void 0&&Ce(T)}d(yt,"rebindTextures");function Bn(T){let M=T.texture,X=n.get(T),se=n.get(M);T.addEventListener("dispose",z),T.isWebGLMultipleRenderTargets!==!0&&(se.__webglTexture===void 0&&(se.__webglTexture=o.createTexture()),se.__version=M.version,r.memory.textures++);let ae=T.isWebGLCubeRenderTarget===!0,he=T.isWebGLMultipleRenderTargets===!0,Re=y(T)||a;if(ae){X.__webglFramebuffer=[];for(let ue=0;ue<6;ue++)X.__webglFramebuffer[ue]=o.createFramebuffer()}else{if(X.__webglFramebuffer=o.createFramebuffer(),he)if(i.drawBuffers){let ue=T.texture;for(let J=0,Ee=ue.length;J<Ee;J++){let be=n.get(ue[J]);be.__webglTexture===void 0&&(be.__webglTexture=o.createTexture(),r.memory.textures++)}}else console.warn("THREE.WebGLRenderer: WebGLMultipleRenderTargets can only be used with WebGL2 or WEBGL_draw_buffers extension.");if(a&&T.samples>0&&Xe(T)===!1){let ue=he?M:[M];X.__webglMultisampledFramebuffer=o.createFramebuffer(),X.__webglColorRenderbuffer=[],t.bindFramebuffer(36160,X.__webglMultisampledFramebuffer);for(let J=0;J<ue.length;J++){let Ee=ue[J];X.__webglColorRenderbuffer[J]=o.createRenderbuffer(),o.bindRenderbuffer(36161,X.__webglColorRenderbuffer[J]);let be=s.convert(Ee.format,Ee.encoding),me=s.convert(Ee.type),we=v(Ee.internalFormat,be,me,Ee.encoding,T.isXRRenderTarget===!0),xe=xt(T);o.renderbufferStorageMultisample(36161,xe,we,T.width,T.height),o.framebufferRenderbuffer(36160,36064+J,36161,X.__webglColorRenderbuffer[J])}o.bindRenderbuffer(36161,null),T.depthBuffer&&(X.__webglDepthRenderbuffer=o.createRenderbuffer(),$e(X.__webglDepthRenderbuffer,T,!0)),t.bindFramebuffer(36160,null)}}if(ae){t.bindTexture(34067,se.__webglTexture),W(34067,M,Re);for(let ue=0;ue<6;ue++)ce(X.__webglFramebuffer[ue],T,M,36064,34069+ue);I(M,Re)&&S(34067),t.unbindTexture()}else if(he){let ue=T.texture;for(let J=0,Ee=ue.length;J<Ee;J++){let be=ue[J],me=n.get(be);t.bindTexture(3553,me.__webglTexture),W(3553,be,Re),ce(X.__webglFramebuffer,T,be,36064+J,3553),I(be,Re)&&S(3553)}t.unbindTexture()}else{let ue=3553;(T.isWebGL3DRenderTarget||T.isWebGLArrayRenderTarget)&&(a?ue=T.isWebGL3DRenderTarget?32879:35866:console.error("THREE.WebGLTextures: THREE.Data3DTexture and THREE.DataArrayTexture only supported with WebGL2.")),t.bindTexture(ue,se.__webglTexture),W(ue,M,Re),ce(X.__webglFramebuffer,T,M,36064,ue),I(M,Re)&&S(ue),t.unbindTexture()}T.depthBuffer&&Ce(T)}d(Bn,"setupRenderTarget");function Ht(T){let M=y(T)||a,X=T.isWebGLMultipleRenderTargets===!0?T.texture:[T.texture];for(let se=0,ae=X.length;se<ae;se++){let he=X[se];if(I(he,M)){let Re=T.isWebGLCubeRenderTarget?34067:3553,ue=n.get(he).__webglTexture;t.bindTexture(Re,ue),S(Re),t.unbindTexture()}}}d(Ht,"updateRenderTargetMipmap");function Rn(T){if(a&&T.samples>0&&Xe(T)===!1){let M=T.isWebGLMultipleRenderTargets?T.texture:[T.texture],X=T.width,se=T.height,ae=16384,he=[],Re=T.stencilBuffer?33306:36096,ue=n.get(T),J=T.isWebGLMultipleRenderTargets===!0;if(J)for(let Ee=0;Ee<M.length;Ee++)t.bindFramebuffer(36160,ue.__webglMultisampledFramebuffer),o.framebufferRenderbuffer(36160,36064+Ee,36161,null),t.bindFramebuffer(36160,ue.__webglFramebuffer),o.framebufferTexture2D(36009,36064+Ee,3553,null,0);t.bindFramebuffer(36008,ue.__webglMultisampledFramebuffer),t.bindFramebuffer(36009,ue.__webglFramebuffer);for(let Ee=0;Ee<M.length;Ee++){he.push(36064+Ee),T.depthBuffer&&he.push(Re);let be=ue.__ignoreDepthValues!==void 0?ue.__ignoreDepthValues:!1;if(be===!1&&(T.depthBuffer&&(ae|=256),T.stencilBuffer&&(ae|=1024)),J&&o.framebufferRenderbuffer(36008,36064,36161,ue.__webglColorRenderbuffer[Ee]),be===!0&&(o.invalidateFramebuffer(36008,[Re]),o.invalidateFramebuffer(36009,[Re])),J){let me=n.get(M[Ee]).__webglTexture;o.framebufferTexture2D(36009,36064,3553,me,0)}o.blitFramebuffer(0,0,X,se,0,0,X,se,ae,9728),p&&o.invalidateFramebuffer(36008,he)}if(t.bindFramebuffer(36008,null),t.bindFramebuffer(36009,null),J)for(let Ee=0;Ee<M.length;Ee++){t.bindFramebuffer(36160,ue.__webglMultisampledFramebuffer),o.framebufferRenderbuffer(36160,36064+Ee,36161,ue.__webglColorRenderbuffer[Ee]);let be=n.get(M[Ee]).__webglTexture;t.bindFramebuffer(36160,ue.__webglFramebuffer),o.framebufferTexture2D(36009,36064+Ee,3553,be,0)}t.bindFramebuffer(36009,ue.__webglMultisampledFramebuffer)}}d(Rn,"updateMultisampleRenderTarget");function xt(T){return Math.min(u,T.samples)}d(xt,"getRenderTargetSamples");function Xe(T){let M=n.get(T);return a&&T.samples>0&&e.has("WEBGL_multisampled_render_to_texture")===!0&&M.__useRenderToTexture!==!1}d(Xe,"useMultisampledRTT");function hi(T){let M=r.render.frame;g.get(T)!==M&&(g.set(T,M),T.update())}d(hi,"updateVideoTexture");function zn(T,M){let X=T.encoding,se=T.format,ae=T.type;return T.isCompressedTexture===!0||T.isVideoTexture===!0||T.format===Yh||X!==ft&&(X===Se?a===!1?e.has("EXT_sRGB")===!0&&se===lt?(T.format=Yh,T.minFilter=Je,T.generateMipmaps=!1):M=yl.sRGBToLinear(M):(se!==lt||ae!==$t)&&console.warn("THREE.WebGLTextures: sRGB encoded textures have to use RGBAFormat and UnsignedByteType."):console.error("THREE.WebGLTextures: Unsupported texture encoding:",X)),M}d(zn,"verifyColorSpace"),this.allocateTextureUnit=k,this.resetTextureUnits=H,this.setTexture2D=Z,this.setTexture2DArray=fe,this.setTexture3D=V,this.setTextureCube=ee,this.rebindTextures=yt,this.setupRenderTarget=Bn,this.updateRenderTargetMipmap=Ht,this.updateMultisampleRenderTarget=Rn,this.setupDepthRenderbuffer=Ce,this.setupFrameBufferTexture=ce,this.useMultisampledRTT=Xe}d(QM,"WebGLTextures");function kM(o,e,t){let n=t.isWebGL2;function i(s,r=null){let a;if(s===$t)return 5121;if(s===Ly)return 32819;if(s===Py)return 32820;if(s===By)return 5120;if(s===Ry)return 5122;if(s===zA)return 5123;if(s===Dy)return 5124;if(s===gs)return 5125;if(s===Ut)return 5126;if(s===Pt)return n?5131:(a=e.get("OES_texture_half_float"),a!==null?a.HALF_FLOAT_OES:null);if(s===Fy)return 6406;if(s===lt)return 6408;if(s===Oy)return 6409;if(s===Ny)return 6410;if(s===ys)return 6402;if(s===or)return 34041;if(s===Yh)return a=e.get("EXT_sRGB"),a!==null?a.SRGB_ALPHA_EXT:null;if(s===yr)return 6403;if(s===Uy)return 36244;if(s===xr)return 33319;if(s===Qy)return 33320;if(s===ky)return 36249;if(s===Eo||s===gh||s===_h||s===wo)if(r===Se)if(a=e.get("WEBGL_compressed_texture_s3tc_srgb"),a!==null){if(s===Eo)return a.COMPRESSED_SRGB_S3TC_DXT1_EXT;if(s===gh)return a.COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT;if(s===_h)return a.COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT;if(s===wo)return a.COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT}else return null;else if(a=e.get("WEBGL_compressed_texture_s3tc"),a!==null){if(s===Eo)return a.COMPRESSED_RGB_S3TC_DXT1_EXT;if(s===gh)return a.COMPRESSED_RGBA_S3TC_DXT1_EXT;if(s===_h)return a.COMPRESSED_RGBA_S3TC_DXT3_EXT;if(s===wo)return a.COMPRESSED_RGBA_S3TC_DXT5_EXT}else return null;if(s===dl||s===vp||s===fl||s===Ep)if(a=e.get("WEBGL_compressed_texture_pvrtc"),a!==null){if(s===dl)return a.COMPRESSED_RGB_PVRTC_4BPPV1_IMG;if(s===vp)return a.COMPRESSED_RGB_PVRTC_2BPPV1_IMG;if(s===fl)return a.COMPRESSED_RGBA_PVRTC_4BPPV1_IMG;if(s===Ep)return a.COMPRESSED_RGBA_PVRTC_2BPPV1_IMG}else return null;if(s===Iu)return a=e.get("WEBGL_compressed_texture_etc1"),a!==null?a.COMPRESSED_RGB_ETC1_WEBGL:null;if(s===pl||s===Al)if(a=e.get("WEBGL_compressed_texture_etc"),a!==null){if(s===pl)return r===Se?a.COMPRESSED_SRGB8_ETC2:a.COMPRESSED_RGB8_ETC2;if(s===Al)return r===Se?a.COMPRESSED_SRGB8_ALPHA8_ETC2_EAC:a.COMPRESSED_RGBA8_ETC2_EAC}else return null;if(s===ml||s===wp||s===Mp||s===bp||s===Ip||s===Cp||s===Sp||s===Tp||s===Bp||s===Rp||s===Dp||s===Lp||s===Pp||s===Fp)if(a=e.get("WEBGL_compressed_texture_astc"),a!==null){if(s===ml)return r===Se?a.COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR:a.COMPRESSED_RGBA_ASTC_4x4_KHR;if(s===wp)return r===Se?a.COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR:a.COMPRESSED_RGBA_ASTC_5x4_KHR;if(s===Mp)return r===Se?a.COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR:a.COMPRESSED_RGBA_ASTC_5x5_KHR;if(s===bp)return r===Se?a.COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR:a.COMPRESSED_RGBA_ASTC_6x5_KHR;if(s===Ip)return r===Se?a.COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR:a.COMPRESSED_RGBA_ASTC_6x6_KHR;if(s===Cp)return r===Se?a.COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR:a.COMPRESSED_RGBA_ASTC_8x5_KHR;if(s===Sp)return r===Se?a.COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR:a.COMPRESSED_RGBA_ASTC_8x6_KHR;if(s===Tp)return r===Se?a.COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR:a.COMPRESSED_RGBA_ASTC_8x8_KHR;if(s===Bp)return r===Se?a.COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR:a.COMPRESSED_RGBA_ASTC_10x5_KHR;if(s===Rp)return r===Se?a.COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR:a.COMPRESSED_RGBA_ASTC_10x6_KHR;if(s===Dp)return r===Se?a.COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR:a.COMPRESSED_RGBA_ASTC_10x8_KHR;if(s===Lp)return r===Se?a.COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR:a.COMPRESSED_RGBA_ASTC_10x10_KHR;if(s===Pp)return r===Se?a.COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR:a.COMPRESSED_RGBA_ASTC_12x10_KHR;if(s===Fp)return r===Se?a.COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR:a.COMPRESSED_RGBA_ASTC_12x12_KHR}else return null;if(s===Mo)if(a=e.get("EXT_texture_compression_bptc"),a!==null){if(s===Mo)return r===Se?a.COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT:a.COMPRESSED_RGBA_BPTC_UNORM_EXT}else return null;if(s===Gy||s===Op||s===Np||s===Up)if(a=e.get("EXT_texture_compression_rgtc"),a!==null){if(s===Mo)return a.COMPRESSED_RED_RGTC1_EXT;if(s===Op)return a.COMPRESSED_SIGNED_RED_RGTC1_EXT;if(s===Np)return a.COMPRESSED_RED_GREEN_RGTC2_EXT;if(s===Up)return a.COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT}else return null;return s===tr?n?34042:(a=e.get("WEBGL_depth_texture"),a!==null?a.UNSIGNED_INT_24_8_WEBGL:null):o[s]!==void 0?o[s]:null}return d(i,"convert"),{convert:i}}d(kM,"WebGLUtils");var ru=class extends ht{static{d(this,"ArrayCamera")}constructor(e=[]){super(),this.isArrayCamera=!0,this.cameras=e}},En=class extends Ze{static{d(this,"Group")}constructor(){super(),this.isGroup=!0,this.type="Group"}},GM={type:"move"},Co=class{static{d(this,"WebXRController")}constructor(){this._targetRay=null,this._grip=null,this._hand=null}getHandSpace(){return this._hand===null&&(this._hand=new En,this._hand.matrixAutoUpdate=!1,this._hand.visible=!1,this._hand.joints={},this._hand.inputState={pinching:!1}),this._hand}getTargetRaySpace(){return this._targetRay===null&&(this._targetRay=new En,this._targetRay.matrixAutoUpdate=!1,this._targetRay.visible=!1,this._targetRay.hasLinearVelocity=!1,this._targetRay.linearVelocity=new B,this._targetRay.hasAngularVelocity=!1,this._targetRay.angularVelocity=new B),this._targetRay}getGripSpace(){return this._grip===null&&(this._grip=new En,this._grip.matrixAutoUpdate=!1,this._grip.visible=!1,this._grip.hasLinearVelocity=!1,this._grip.linearVelocity=new B,this._grip.hasAngularVelocity=!1,this._grip.angularVelocity=new B),this._grip}dispatchEvent(e){return this._targetRay!==null&&this._targetRay.dispatchEvent(e),this._grip!==null&&this._grip.dispatchEvent(e),this._hand!==null&&this._hand.dispatchEvent(e),this}connect(e){if(e&&e.hand){let t=this._hand;if(t)for(let n of e.hand.values())this._getHandJoint(t,n)}return this.dispatchEvent({type:"connected",data:e}),this}disconnect(e){return this.dispatchEvent({type:"disconnected",data:e}),this._targetRay!==null&&(this._targetRay.visible=!1),this._grip!==null&&(this._grip.visible=!1),this._hand!==null&&(this._hand.visible=!1),this}update(e,t,n){let i=null,s=null,r=null,a=this._targetRay,l=this._grip,c=this._hand;if(e&&t.session.visibilityState!=="visible-blurred"){if(c&&e.hand){r=!0;for(let A of e.hand.values()){let m=t.getJointPose(A,n),_=this._getHandJoint(c,A);m!==null&&(_.matrix.fromArray(m.transform.matrix),_.matrix.decompose(_.position,_.rotation,_.scale),_.jointRadius=m.radius),_.visible=m!==null}let h=c.joints["index-finger-tip"],u=c.joints["thumb-tip"],f=h.position.distanceTo(u.position),p=.02,g=.005;c.inputState.pinching&&f>p+g?(c.inputState.pinching=!1,this.dispatchEvent({type:"pinchend",handedness:e.handedness,target:this})):!c.inputState.pinching&&f<=p-g&&(c.inputState.pinching=!0,this.dispatchEvent({type:"pinchstart",handedness:e.handedness,target:this}))}else l!==null&&e.gripSpace&&(s=t.getPose(e.gripSpace,n),s!==null&&(l.matrix.fromArray(s.transform.matrix),l.matrix.decompose(l.position,l.rotation,l.scale),s.linearVelocity?(l.hasLinearVelocity=!0,l.linearVelocity.copy(s.linearVelocity)):l.hasLinearVelocity=!1,s.angularVelocity?(l.hasAngularVelocity=!0,l.angularVelocity.copy(s.angularVelocity)):l.hasAngularVelocity=!1));a!==null&&(i=t.getPose(e.targetRaySpace,n),i===null&&s!==null&&(i=s),i!==null&&(a.matrix.fromArray(i.transform.matrix),a.matrix.decompose(a.position,a.rotation,a.scale),i.linearVelocity?(a.hasLinearVelocity=!0,a.linearVelocity.copy(i.linearVelocity)):a.hasLinearVelocity=!1,i.angularVelocity?(a.hasAngularVelocity=!0,a.angularVelocity.copy(i.angularVelocity)):a.hasAngularVelocity=!1,this.dispatchEvent(GM)))}return a!==null&&(a.visible=i!==null),l!==null&&(l.visible=s!==null),c!==null&&(c.visible=r!==null),this}_getHandJoint(e,t){if(e.joints[t.jointName]===void 0){let n=new En;n.matrixAutoUpdate=!1,n.visible=!1,e.joints[t.jointName]=n,e.add(n)}return e.joints[t.jointName]}},ou=class extends st{static{d(this,"DepthTexture")}constructor(e,t,n,i,s,r,a,l,c,h){if(h=h!==void 0?h:ys,h!==ys&&h!==or)throw new Error("DepthTexture format must be either THREE.DepthFormat or THREE.DepthStencilFormat");n===void 0&&h===ys&&(n=gs),n===void 0&&h===or&&(n=tr),super(null,i,s,r,a,l,h,n,c),this.isDepthTexture=!0,this.image={width:e,height:t},this.magFilter=a!==void 0?a:ct,this.minFilter=l!==void 0?l:ct,this.flipY=!1,this.generateMipmaps=!1}},au=class extends Mt{static{d(this,"WebXRManager")}constructor(e,t){super();let n=this,i=null,s=1,r=null,a="local-floor",l=1,c=null,h=null,u=null,f=null,p=null,g=null,A=t.getContextAttributes(),m=null,_=null,E=[],x=[],y=new Set,w=new Map,I=new ht;I.layers.enable(1),I.viewport=new nt;let S=new ht;S.layers.enable(2),S.viewport=new nt;let v=[I,S],b=new ru;b.layers.enable(1),b.layers.enable(2);let R=null,N=null;this.cameraAutoUpdate=!0,this.enabled=!1,this.isPresenting=!1,this.getController=function(V){let ee=E[V];return ee===void 0&&(ee=new Co,E[V]=ee),ee.getTargetRaySpace()},this.getControllerGrip=function(V){let ee=E[V];return ee===void 0&&(ee=new Co,E[V]=ee),ee.getGripSpace()},this.getHand=function(V){let ee=E[V];return ee===void 0&&(ee=new Co,E[V]=ee),ee.getHandSpace()};function z(V){let ee=x.indexOf(V.inputSource);if(ee===-1)return;let re=E[ee];re!==void 0&&re.dispatchEvent({type:V.type,data:V.inputSource})}d(z,"onSessionEvent");function O(){i.removeEventListener("select",z),i.removeEventListener("selectstart",z),i.removeEventListener("selectend",z),i.removeEventListener("squeeze",z),i.removeEventListener("squeezestart",z),i.removeEventListener("squeezeend",z),i.removeEventListener("end",O),i.removeEventListener("inputsourceschange",D);for(let V=0;V<E.length;V++){let ee=x[V];ee!==null&&(x[V]=null,E[V].disconnect(ee))}R=null,N=null,e.setRenderTarget(m),p=null,f=null,u=null,i=null,_=null,fe.stop(),n.isPresenting=!1,n.dispatchEvent({type:"sessionend"})}d(O,"onSessionEnd"),this.setFramebufferScaleFactor=function(V){s=V,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change framebuffer scale while presenting.")},this.setReferenceSpaceType=function(V){a=V,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change reference space type while presenting.")},this.getReferenceSpace=function(){return c||r},this.setReferenceSpace=function(V){c=V},this.getBaseLayer=function(){return f!==null?f:p},this.getBinding=function(){return u},this.getFrame=function(){return g},this.getSession=function(){return i},this.setSession=async function(V){if(i=V,i!==null){if(m=e.getRenderTarget(),i.addEventListener("select",z),i.addEventListener("selectstart",z),i.addEventListener("selectend",z),i.addEventListener("squeeze",z),i.addEventListener("squeezestart",z),i.addEventListener("squeezeend",z),i.addEventListener("end",O),i.addEventListener("inputsourceschange",D),A.xrCompatible!==!0&&await t.makeXRCompatible(),i.renderState.layers===void 0||e.capabilities.isWebGL2===!1){let ee={antialias:i.renderState.layers===void 0?A.antialias:!0,alpha:A.alpha,depth:A.depth,stencil:A.stencil,framebufferScaleFactor:s};p=new XRWebGLLayer(i,t,ee),i.updateRenderState({baseLayer:p}),_=new Xt(p.framebufferWidth,p.framebufferHeight,{format:lt,type:$t,encoding:e.outputEncoding,stencilBuffer:A.stencil})}else{let ee=null,re=null,ie=null;A.depth&&(ie=A.stencil?35056:33190,ee=A.stencil?or:ys,re=A.stencil?tr:gs);let W={colorFormat:32856,depthFormat:ie,scaleFactor:s};u=new XRWebGLBinding(i,t),f=u.createProjectionLayer(W),i.updateRenderState({layers:[f]}),_=new Xt(f.textureWidth,f.textureHeight,{format:lt,type:$t,depthTexture:new ou(f.textureWidth,f.textureHeight,re,void 0,void 0,void 0,void 0,void 0,void 0,ee),stencilBuffer:A.stencil,encoding:e.outputEncoding,samples:A.antialias?4:0});let Te=e.properties.get(_);Te.__ignoreDepthValues=f.ignoreDepthValues}_.isXRRenderTarget=!0,this.setFoveation(l),c=null,r=await i.requestReferenceSpace(a),fe.setContext(i),fe.start(),n.isPresenting=!0,n.dispatchEvent({type:"sessionstart"})}};function D(V){for(let ee=0;ee<V.removed.length;ee++){let re=V.removed[ee],ie=x.indexOf(re);ie>=0&&(x[ie]=null,E[ie].disconnect(re))}for(let ee=0;ee<V.added.length;ee++){let re=V.added[ee],ie=x.indexOf(re);if(ie===-1){for(let Te=0;Te<E.length;Te++)if(Te>=x.length){x.push(re),ie=Te;break}else if(x[Te]===null){x[Te]=re,ie=Te;break}if(ie===-1)break}let W=E[ie];W&&W.connect(re)}}d(D,"onInputSourcesChange");let Q=new B,q=new B;function H(V,ee,re){Q.setFromMatrixPosition(ee.matrixWorld),q.setFromMatrixPosition(re.matrixWorld);let ie=Q.distanceTo(q),W=ee.projectionMatrix.elements,Te=re.projectionMatrix.elements,Ae=W[14]/(W[10]-1),ge=W[14]/(W[10]+1),ce=(W[9]+1)/W[5],$e=(W[9]-1)/W[5],Le=(W[8]-1)/W[0],Ce=(Te[8]+1)/Te[0],yt=Ae*Le,Bn=Ae*Ce,Ht=ie/(-Le+Ce),Rn=Ht*-Le;ee.matrixWorld.decompose(V.position,V.quaternion,V.scale),V.translateX(Rn),V.translateZ(Ht),V.matrixWorld.compose(V.position,V.quaternion,V.scale),V.matrixWorldInverse.copy(V.matrixWorld).invert();let xt=Ae+Ht,Xe=ge+Ht,hi=yt-Rn,zn=Bn+(ie-Rn),T=ce*ge/Xe*xt,M=$e*ge/Xe*xt;V.projectionMatrix.makePerspective(hi,zn,T,M,xt,Xe)}d(H,"setProjectionFromUnion");function k(V,ee){ee===null?V.matrixWorld.copy(V.matrix):V.matrixWorld.multiplyMatrices(ee.matrixWorld,V.matrix),V.matrixWorldInverse.copy(V.matrixWorld).invert()}d(k,"updateCamera"),this.updateCamera=function(V){if(i===null)return;b.near=S.near=I.near=V.near,b.far=S.far=I.far=V.far,(R!==b.near||N!==b.far)&&(i.updateRenderState({depthNear:b.near,depthFar:b.far}),R=b.near,N=b.far);let ee=V.parent,re=b.cameras;k(b,ee);for(let W=0;W<re.length;W++)k(re[W],ee);b.matrixWorld.decompose(b.position,b.quaternion,b.scale),V.matrix.copy(b.matrix),V.matrix.decompose(V.position,V.quaternion,V.scale);let ie=V.children;for(let W=0,Te=ie.length;W<Te;W++)ie[W].updateMatrixWorld(!0);re.length===2?H(b,I,S):b.projectionMatrix.copy(I.projectionMatrix)},this.getCamera=function(){return b},this.getFoveation=function(){if(!(f===null&&p===null))return l},this.setFoveation=function(V){l=V,f!==null&&(f.fixedFoveation=V),p!==null&&p.fixedFoveation!==void 0&&(p.fixedFoveation=V)},this.getPlanes=function(){return y};let j=null;function Z(V,ee){if(h=ee.getViewerPose(c||r),g=ee,h!==null){let re=h.views;p!==null&&(e.setRenderTargetFramebuffer(_,p.framebuffer),e.setRenderTarget(_));let ie=!1;re.length!==b.cameras.length&&(b.cameras.length=0,ie=!0);for(let W=0;W<re.length;W++){let Te=re[W],Ae=null;if(p!==null)Ae=p.getViewport(Te);else{let ce=u.getViewSubImage(f,Te);Ae=ce.viewport,W===0&&(e.setRenderTargetTextures(_,ce.colorTexture,f.ignoreDepthValues?void 0:ce.depthStencilTexture),e.setRenderTarget(_))}let ge=v[W];ge===void 0&&(ge=new ht,ge.layers.enable(W),ge.viewport=new nt,v[W]=ge),ge.matrix.fromArray(Te.transform.matrix),ge.projectionMatrix.fromArray(Te.projectionMatrix),ge.viewport.set(Ae.x,Ae.y,Ae.width,Ae.height),W===0&&b.matrix.copy(ge.matrix),ie===!0&&b.cameras.push(ge)}}for(let re=0;re<E.length;re++){let ie=x[re],W=E[re];ie!==null&&W!==void 0&&W.update(ie,ee,c||r)}if(j&&j(V,ee),ee.detectedPlanes){n.dispatchEvent({type:"planesdetected",data:ee.detectedPlanes});let re=null;for(let ie of y)ee.detectedPlanes.has(ie)||(re===null&&(re=[]),re.push(ie));if(re!==null)for(let ie of re)y.delete(ie),w.delete(ie),n.dispatchEvent({type:"planeremoved",data:ie});for(let ie of ee.detectedPlanes)if(!y.has(ie))y.add(ie),w.set(ie,ee.lastChangedTime),n.dispatchEvent({type:"planeadded",data:ie});else{let W=w.get(ie);ie.lastChangedTime>W&&(w.set(ie,ie.lastChangedTime),n.dispatchEvent({type:"planechanged",data:ie}))}}g=null}d(Z,"onAnimationFrame");let fe=new XA;fe.setAnimationLoop(Z),this.setAnimationLoop=function(V){j=V},this.dispose=function(){}}};function zM(o,e){function t(A,m){m.color.getRGB(A.fogColor.value,$A(o)),m.isFog?(A.fogNear.value=m.near,A.fogFar.value=m.far):m.isFogExp2&&(A.fogDensity.value=m.density)}d(t,"refreshFogUniforms");function n(A,m,_,E,x){m.isMeshBasicMaterial||m.isMeshLambertMaterial?i(A,m):m.isMeshToonMaterial?(i(A,m),h(A,m)):m.isMeshPhongMaterial?(i(A,m),c(A,m)):m.isMeshStandardMaterial?(i(A,m),u(A,m),m.isMeshPhysicalMaterial&&f(A,m,x)):m.isMeshMatcapMaterial?(i(A,m),p(A,m)):m.isMeshDepthMaterial?i(A,m):m.isMeshDistanceMaterial?(i(A,m),g(A,m)):m.isMeshNormalMaterial?i(A,m):m.isLineBasicMaterial?(s(A,m),m.isLineDashedMaterial&&r(A,m)):m.isPointsMaterial?a(A,m,_,E):m.isSpriteMaterial?l(A,m):m.isShadowMaterial?(A.color.value.copy(m.color),A.opacity.value=m.opacity):m.isShaderMaterial&&(m.uniformsNeedUpdate=!1)}d(n,"refreshMaterialUniforms");function i(A,m){A.opacity.value=m.opacity,m.color&&A.diffuse.value.copy(m.color),m.emissive&&A.emissive.value.copy(m.emissive).multiplyScalar(m.emissiveIntensity),m.map&&(A.map.value=m.map),m.alphaMap&&(A.alphaMap.value=m.alphaMap),m.bumpMap&&(A.bumpMap.value=m.bumpMap,A.bumpScale.value=m.bumpScale,m.side===dt&&(A.bumpScale.value*=-1)),m.displacementMap&&(A.displacementMap.value=m.displacementMap,A.displacementScale.value=m.displacementScale,A.displacementBias.value=m.displacementBias),m.emissiveMap&&(A.emissiveMap.value=m.emissiveMap),m.normalMap&&(A.normalMap.value=m.normalMap,A.normalScale.value.copy(m.normalScale),m.side===dt&&A.normalScale.value.negate()),m.specularMap&&(A.specularMap.value=m.specularMap),m.alphaTest>0&&(A.alphaTest.value=m.alphaTest);let _=e.get(m).envMap;if(_&&(A.envMap.value=_,A.flipEnvMap.value=_.isCubeTexture&&_.isRenderTargetTexture===!1?-1:1,A.reflectivity.value=m.reflectivity,A.ior.value=m.ior,A.refractionRatio.value=m.refractionRatio),m.lightMap){A.lightMap.value=m.lightMap;let y=o.physicallyCorrectLights!==!0?Math.PI:1;A.lightMapIntensity.value=m.lightMapIntensity*y}m.aoMap&&(A.aoMap.value=m.aoMap,A.aoMapIntensity.value=m.aoMapIntensity);let E;m.map?E=m.map:m.specularMap?E=m.specularMap:m.displacementMap?E=m.displacementMap:m.normalMap?E=m.normalMap:m.bumpMap?E=m.bumpMap:m.roughnessMap?E=m.roughnessMap:m.metalnessMap?E=m.metalnessMap:m.alphaMap?E=m.alphaMap:m.emissiveMap?E=m.emissiveMap:m.clearcoatMap?E=m.clearcoatMap:m.clearcoatNormalMap?E=m.clearcoatNormalMap:m.clearcoatRoughnessMap?E=m.clearcoatRoughnessMap:m.iridescenceMap?E=m.iridescenceMap:m.iridescenceThicknessMap?E=m.iridescenceThicknessMap:m.specularIntensityMap?E=m.specularIntensityMap:m.specularColorMap?E=m.specularColorMap:m.transmissionMap?E=m.transmissionMap:m.thicknessMap?E=m.thicknessMap:m.sheenColorMap?E=m.sheenColorMap:m.sheenRoughnessMap&&(E=m.sheenRoughnessMap),E!==void 0&&(E.isWebGLRenderTarget&&(E=E.texture),E.matrixAutoUpdate===!0&&E.updateMatrix(),A.uvTransform.value.copy(E.matrix));let x;m.aoMap?x=m.aoMap:m.lightMap&&(x=m.lightMap),x!==void 0&&(x.isWebGLRenderTarget&&(x=x.texture),x.matrixAutoUpdate===!0&&x.updateMatrix(),A.uv2Transform.value.copy(x.matrix))}d(i,"refreshUniformsCommon");function s(A,m){A.diffuse.value.copy(m.color),A.opacity.value=m.opacity}d(s,"refreshUniformsLine");function r(A,m){A.dashSize.value=m.dashSize,A.totalSize.value=m.dashSize+m.gapSize,A.scale.value=m.scale}d(r,"refreshUniformsDash");function a(A,m,_,E){A.diffuse.value.copy(m.color),A.opacity.value=m.opacity,A.size.value=m.size*_,A.scale.value=E*.5,m.map&&(A.map.value=m.map),m.alphaMap&&(A.alphaMap.value=m.alphaMap),m.alphaTest>0&&(A.alphaTest.value=m.alphaTest);let x;m.map?x=m.map:m.alphaMap&&(x=m.alphaMap),x!==void 0&&(x.matrixAutoUpdate===!0&&x.updateMatrix(),A.uvTransform.value.copy(x.matrix))}d(a,"refreshUniformsPoints");function l(A,m){A.diffuse.value.copy(m.color),A.opacity.value=m.opacity,A.rotation.value=m.rotation,m.map&&(A.map.value=m.map),m.alphaMap&&(A.alphaMap.value=m.alphaMap),m.alphaTest>0&&(A.alphaTest.value=m.alphaTest);let _;m.map?_=m.map:m.alphaMap&&(_=m.alphaMap),_!==void 0&&(_.matrixAutoUpdate===!0&&_.updateMatrix(),A.uvTransform.value.copy(_.matrix))}d(l,"refreshUniformsSprites");function c(A,m){A.specular.value.copy(m.specular),A.shininess.value=Math.max(m.shininess,1e-4)}d(c,"refreshUniformsPhong");function h(A,m){m.gradientMap&&(A.gradientMap.value=m.gradientMap)}d(h,"refreshUniformsToon");function u(A,m){A.roughness.value=m.roughness,A.metalness.value=m.metalness,m.roughnessMap&&(A.roughnessMap.value=m.roughnessMap),m.metalnessMap&&(A.metalnessMap.value=m.metalnessMap),e.get(m).envMap&&(A.envMapIntensity.value=m.envMapIntensity)}d(u,"refreshUniformsStandard");function f(A,m,_){A.ior.value=m.ior,m.sheen>0&&(A.sheenColor.value.copy(m.sheenColor).multiplyScalar(m.sheen),A.sheenRoughness.value=m.sheenRoughness,m.sheenColorMap&&(A.sheenColorMap.value=m.sheenColorMap),m.sheenRoughnessMap&&(A.sheenRoughnessMap.value=m.sheenRoughnessMap)),m.clearcoat>0&&(A.clearcoat.value=m.clearcoat,A.clearcoatRoughness.value=m.clearcoatRoughness,m.clearcoatMap&&(A.clearcoatMap.value=m.clearcoatMap),m.clearcoatRoughnessMap&&(A.clearcoatRoughnessMap.value=m.clearcoatRoughnessMap),m.clearcoatNormalMap&&(A.clearcoatNormalScale.value.copy(m.clearcoatNormalScale),A.clearcoatNormalMap.value=m.clearcoatNormalMap,m.side===dt&&A.clearcoatNormalScale.value.negate())),m.iridescence>0&&(A.iridescence.value=m.iridescence,A.iridescenceIOR.value=m.iridescenceIOR,A.iridescenceThicknessMinimum.value=m.iridescenceThicknessRange[0],A.iridescenceThicknessMaximum.value=m.iridescenceThicknessRange[1],m.iridescenceMap&&(A.iridescenceMap.value=m.iridescenceMap),m.iridescenceThicknessMap&&(A.iridescenceThicknessMap.value=m.iridescenceThicknessMap)),m.transmission>0&&(A.transmission.value=m.transmission,A.transmissionSamplerMap.value=_.texture,A.transmissionSamplerSize.value.set(_.width,_.height),m.transmissionMap&&(A.transmissionMap.value=m.transmissionMap),A.thickness.value=m.thickness,m.thicknessMap&&(A.thicknessMap.value=m.thicknessMap),A.attenuationDistance.value=m.attenuationDistance,A.attenuationColor.value.copy(m.attenuationColor)),A.specularIntensity.value=m.specularIntensity,A.specularColor.value.copy(m.specularColor),m.specularIntensityMap&&(A.specularIntensityMap.value=m.specularIntensityMap),m.specularColorMap&&(A.specularColorMap.value=m.specularColorMap)}d(f,"refreshUniformsPhysical");function p(A,m){m.matcap&&(A.matcap.value=m.matcap)}d(p,"refreshUniformsMatcap");function g(A,m){A.referencePosition.value.copy(m.referencePosition),A.nearDistance.value=m.nearDistance,A.farDistance.value=m.farDistance}return d(g,"refreshUniformsDistance"),{refreshFogUniforms:t,refreshMaterialUniforms:n}}d(zM,"WebGLMaterials");function VM(o,e,t,n){let i={},s={},r=[],a=t.isWebGL2?o.getParameter(35375):0;function l(E,x){let y=x.program;n.uniformBlockBinding(E,y)}d(l,"bind");function c(E,x){let y=i[E.id];y===void 0&&(g(E),y=h(E),i[E.id]=y,E.addEventListener("dispose",m));let w=x.program;n.updateUBOMapping(E,w);let I=e.render.frame;s[E.id]!==I&&(f(E),s[E.id]=I)}d(c,"update");function h(E){let x=u();E.__bindingPointIndex=x;let y=o.createBuffer(),w=E.__size,I=E.usage;return o.bindBuffer(35345,y),o.bufferData(35345,w,I),o.bindBuffer(35345,null),o.bindBufferBase(35345,x,y),y}d(h,"createBuffer");function u(){for(let E=0;E<a;E++)if(r.indexOf(E)===-1)return r.push(E),E;return console.error("THREE.WebGLRenderer: Maximum number of simultaneously usable uniforms groups reached."),0}d(u,"allocateBindingPointIndex");function f(E){let x=i[E.id],y=E.uniforms,w=E.__cache;o.bindBuffer(35345,x);for(let I=0,S=y.length;I<S;I++){let v=y[I];if(p(v,I,w)===!0){let b=v.__offset,R=Array.isArray(v.value)?v.value:[v.value],N=0;for(let z=0;z<R.length;z++){let O=R[z],D=A(O);typeof O=="number"?(v.__data[0]=O,o.bufferSubData(35345,b+N,v.__data)):O.isMatrix3?(v.__data[0]=O.elements[0],v.__data[1]=O.elements[1],v.__data[2]=O.elements[2],v.__data[3]=O.elements[0],v.__data[4]=O.elements[3],v.__data[5]=O.elements[4],v.__data[6]=O.elements[5],v.__data[7]=O.elements[0],v.__data[8]=O.elements[6],v.__data[9]=O.elements[7],v.__data[10]=O.elements[8],v.__data[11]=O.elements[0]):(O.toArray(v.__data,N),N+=D.storage/Float32Array.BYTES_PER_ELEMENT)}o.bufferSubData(35345,b,v.__data)}}o.bindBuffer(35345,null)}d(f,"updateBufferData");function p(E,x,y){let w=E.value;if(y[x]===void 0){if(typeof w=="number")y[x]=w;else{let I=Array.isArray(w)?w:[w],S=[];for(let v=0;v<I.length;v++)S.push(I[v].clone());y[x]=S}return!0}else if(typeof w=="number"){if(y[x]!==w)return y[x]=w,!0}else{let I=Array.isArray(y[x])?y[x]:[y[x]],S=Array.isArray(w)?w:[w];for(let v=0;v<I.length;v++){let b=I[v];if(b.equals(S[v])===!1)return b.copy(S[v]),!0}}return!1}d(p,"hasUniformChanged");function g(E){let x=E.uniforms,y=0,w=16,I=0;for(let S=0,v=x.length;S<v;S++){let b=x[S],R={boundary:0,storage:0},N=Array.isArray(b.value)?b.value:[b.value];for(let z=0,O=N.length;z<O;z++){let D=N[z],Q=A(D);R.boundary+=Q.boundary,R.storage+=Q.storage}if(b.__data=new Float32Array(R.storage/Float32Array.BYTES_PER_ELEMENT),b.__offset=y,S>0){I=y%w;let z=w-I;I!==0&&z-R.boundary<0&&(y+=w-I,b.__offset=y)}y+=R.storage}return I=y%w,I>0&&(y+=w-I),E.__size=y,E.__cache={},this}d(g,"prepareUniformsGroup");function A(E){let x={boundary:0,storage:0};return typeof E=="number"?(x.boundary=4,x.storage=4):E.isVector2?(x.boundary=8,x.storage=8):E.isVector3||E.isColor?(x.boundary=16,x.storage=12):E.isVector4?(x.boundary=16,x.storage=16):E.isMatrix3?(x.boundary=48,x.storage=48):E.isMatrix4?(x.boundary=64,x.storage=64):E.isTexture?console.warn("THREE.WebGLRenderer: Texture samplers can not be part of an uniforms group."):console.warn("THREE.WebGLRenderer: Unsupported uniform value type.",E),x}d(A,"getUniformSize");function m(E){let x=E.target;x.removeEventListener("dispose",m);let y=r.indexOf(x.__bindingPointIndex);r.splice(y,1),o.deleteBuffer(i[x.id]),delete i[x.id],delete s[x.id]}d(m,"onUniformsGroupsDispose");function _(){for(let E in i)o.deleteBuffer(i[E]);r=[],i={},s={}}return d(_,"dispose"),{bind:l,update:c,dispose:_}}d(VM,"WebGLUniformsGroups");function HM(){let o=Ro("canvas");return o.style.display="block",o}d(HM,"createCanvasElement");function Ru(o={}){this.isWebGLRenderer=!0;let e=o.canvas!==void 0?o.canvas:HM(),t=o.context!==void 0?o.context:null,n=o.depth!==void 0?o.depth:!0,i=o.stencil!==void 0?o.stencil:!0,s=o.antialias!==void 0?o.antialias:!1,r=o.premultipliedAlpha!==void 0?o.premultipliedAlpha:!0,a=o.preserveDrawingBuffer!==void 0?o.preserveDrawingBuffer:!1,l=o.powerPreference!==void 0?o.powerPreference:"default",c=o.failIfMajorPerformanceCaveat!==void 0?o.failIfMajorPerformanceCaveat:!1,h;t!==null?h=t.getContextAttributes().alpha:h=o.alpha!==void 0?o.alpha:!1;let u=null,f=null,p=[],g=[];this.domElement=e,this.debug={checkShaderErrors:!0},this.autoClear=!0,this.autoClearColor=!0,this.autoClearDepth=!0,this.autoClearStencil=!0,this.sortObjects=!0,this.clippingPlanes=[],this.localClippingEnabled=!1,this.outputEncoding=ft,this.physicallyCorrectLights=!1,this.toneMapping=qn,this.toneMappingExposure=1;let A=this,m=!1,_=0,E=0,x=null,y=-1,w=null,I=new nt,S=new nt,v=null,b=e.width,R=e.height,N=1,z=null,O=null,D=new nt(0,0,b,R),Q=new nt(0,0,b,R),q=!1,H=new Po,k=!1,j=!1,Z=null,fe=new Ie,V=new Be,ee=new B,re={background:null,fog:null,environment:null,overrideMaterial:null,isScene:!0};function ie(){return x===null?N:1}d(ie,"getTargetPixelRatio");let W=t;function Te(C,G){for(let $=0;$<C.length;$++){let U=C[$],Y=e.getContext(U,G);if(Y!==null)return Y}return null}d(Te,"getContext");try{let C={alpha:!0,depth:n,stencil:i,antialias:s,premultipliedAlpha:r,preserveDrawingBuffer:a,powerPreference:l,failIfMajorPerformanceCaveat:c};if("setAttribute"in e&&e.setAttribute("data-engine",`three.js r${Mu}`),e.addEventListener("webglcontextlost",we,!1),e.addEventListener("webglcontextrestored",xe,!1),e.addEventListener("webglcontextcreationerror",Ve,!1),W===null){let G=["webgl2","webgl","experimental-webgl"];if(A.isWebGL1Renderer===!0&&G.shift(),W=Te(G,C),W===null)throw Te(G)?new Error("Error creating WebGL context with your selected attributes."):new Error("Error creating WebGL context.")}W.getShaderPrecisionFormat===void 0&&(W.getShaderPrecisionFormat=function(){return{rangeMin:1,rangeMax:1,precision:1}})}catch(C){throw console.error("THREE.WebGLRenderer: "+C.message),C}let Ae,ge,ce,$e,Le,Ce,yt,Bn,Ht,Rn,xt,Xe,hi,zn,T,M,X,se,ae,he,Re,ue,J,Ee;function be(){Ae=new uw(W),ge=new rw(W,Ae,o),Ae.init(ge),ue=new kM(W,Ae,ge),ce=new UM(W,Ae,ge),$e=new pw,Le=new IM,Ce=new QM(W,Ae,ce,Le,ge,ue,$e),yt=new aw(A),Bn=new hw(A),Ht=new wx(W,ge),J=new iw(W,Ae,Ht,ge),Rn=new dw(W,Ht,$e,J),xt=new _w(W,Rn,Ht,$e),ae=new gw(W,ge,Ce),M=new ow(Le),Xe=new bM(A,yt,Bn,Ae,ge,J,M),hi=new zM(A,Le),zn=new SM,T=new PM(Ae,ge),se=new nw(A,yt,Bn,ce,xt,h,r),X=new NM(A,xt,ge),Ee=new VM(W,$e,ge,ce),he=new sw(W,Ae,$e,ge),Re=new fw(W,Ae,$e,ge),$e.programs=Xe.programs,A.capabilities=ge,A.extensions=Ae,A.properties=Le,A.renderLists=zn,A.shadowMap=X,A.state=ce,A.info=$e}d(be,"initGLContext"),be();let me=new au(A,W);this.xr=me,this.getContext=function(){return W},this.getContextAttributes=function(){return W.getContextAttributes()},this.forceContextLoss=function(){let C=Ae.get("WEBGL_lose_context");C&&C.loseContext()},this.forceContextRestore=function(){let C=Ae.get("WEBGL_lose_context");C&&C.restoreContext()},this.getPixelRatio=function(){return N},this.setPixelRatio=function(C){C!==void 0&&(N=C,this.setSize(b,R,!1))},this.getSize=function(C){return C.set(b,R)},this.setSize=function(C,G,$){if(me.isPresenting){console.warn("THREE.WebGLRenderer: Can't change size while VR device is presenting.");return}b=C,R=G,e.width=Math.floor(C*N),e.height=Math.floor(G*N),$!==!1&&(e.style.width=C+"px",e.style.height=G+"px"),this.setViewport(0,0,C,G)},this.getDrawingBufferSize=function(C){return C.set(b*N,R*N).floor()},this.setDrawingBufferSize=function(C,G,$){b=C,R=G,N=$,e.width=Math.floor(C*$),e.height=Math.floor(G*$),this.setViewport(0,0,C,G)},this.getCurrentViewport=function(C){return C.copy(I)},this.getViewport=function(C){return C.copy(D)},this.setViewport=function(C,G,$,U){C.isVector4?D.set(C.x,C.y,C.z,C.w):D.set(C,G,$,U),ce.viewport(I.copy(D).multiplyScalar(N).floor())},this.getScissor=function(C){return C.copy(Q)},this.setScissor=function(C,G,$,U){C.isVector4?Q.set(C.x,C.y,C.z,C.w):Q.set(C,G,$,U),ce.scissor(S.copy(Q).multiplyScalar(N).floor())},this.getScissorTest=function(){return q},this.setScissorTest=function(C){ce.setScissorTest(q=C)},this.setOpaqueSort=function(C){z=C},this.setTransparentSort=function(C){O=C},this.getClearColor=function(C){return C.copy(se.getClearColor())},this.setClearColor=function(){se.setClearColor.apply(se,arguments)},this.getClearAlpha=function(){return se.getClearAlpha()},this.setClearAlpha=function(){se.setClearAlpha.apply(se,arguments)},this.clear=function(C=!0,G=!0,$=!0){let U=0;C&&(U|=16384),G&&(U|=256),$&&(U|=1024),W.clear(U)},this.clearColor=function(){this.clear(!0,!1,!1)},this.clearDepth=function(){this.clear(!1,!0,!1)},this.clearStencil=function(){this.clear(!1,!1,!0)},this.dispose=function(){e.removeEventListener("webglcontextlost",we,!1),e.removeEventListener("webglcontextrestored",xe,!1),e.removeEventListener("webglcontextcreationerror",Ve,!1),zn.dispose(),T.dispose(),Le.dispose(),yt.dispose(),Bn.dispose(),xt.dispose(),J.dispose(),Ee.dispose(),Xe.dispose(),me.dispose(),me.removeEventListener("sessionstart",de),me.removeEventListener("sessionend",_e),Z&&(Z.dispose(),Z=null),Ke.stop()};function we(C){C.preventDefault(),console.log("THREE.WebGLRenderer: Context Lost."),m=!0}d(we,"onContextLost");function xe(){console.log("THREE.WebGLRenderer: Context Restored."),m=!1;let C=$e.autoReset,G=X.enabled,$=X.autoUpdate,U=X.needsUpdate,Y=X.type;be(),$e.autoReset=C,X.enabled=G,X.autoUpdate=$,X.needsUpdate=U,X.type=Y}d(xe,"onContextRestore");function Ve(C){console.error("THREE.WebGLRenderer: A WebGL context could not be created. Reason: ",C.statusMessage)}d(Ve,"onContextCreationError");function ot(C){let G=C.target;G.removeEventListener("dispose",ot),Tt(G)}d(ot,"onMaterialDispose");function Tt(C){F(C),Le.remove(C)}d(Tt,"deallocateMaterial");function F(C){let G=Le.get(C).programs;G!==void 0&&(G.forEach(function($){Xe.releaseProgram($)}),C.isShaderMaterial&&Xe.releaseShaderCache(C))}d(F,"releaseMaterialProgramReferences"),this.renderBufferDirect=function(C,G,$,U,Y,ve){G===null&&(G=re);let De=Y.isMesh&&Y.matrixWorld.determinant()<0,Fe=J_(C,G,$,U,Y);ce.setMaterial(U,De);let Oe=$.index,He=1;U.wireframe===!0&&(Oe=Rn.getWireframeAttribute($),He=2);let Qe=$.drawRange,ke=$.attributes.position,At=Qe.start*He,_n=(Qe.start+Qe.count)*He;ve!==null&&(At=Math.max(At,ve.start*He),_n=Math.min(_n,(ve.start+ve.count)*He)),Oe!==null?(At=Math.max(At,0),_n=Math.min(_n,Oe.count)):ke!=null&&(At=Math.max(At,0),_n=Math.min(_n,ke.count));let di=_n-At;if(di<0||di===1/0)return;J.setup(Y,U,Fe,$,Oe);let cs,mt=he;if(Oe!==null&&(cs=Ht.get(Oe),mt=Re,mt.setIndex(cs)),Y.isMesh)U.wireframe===!0?(ce.setLineWidth(U.wireframeLinewidth*ie()),mt.setMode(1)):mt.setMode(4);else if(Y.isLine){let Ge=U.linewidth;Ge===void 0&&(Ge=1),ce.setLineWidth(Ge*ie()),Y.isLineSegments?mt.setMode(1):Y.isLineLoop?mt.setMode(2):mt.setMode(3)}else Y.isPoints?mt.setMode(0):Y.isSprite&&mt.setMode(4);if(Y.isInstancedMesh)mt.renderInstances(At,di,Y.count);else if($.isInstancedBufferGeometry){let Ge=$._maxInstanceCount!==void 0?$._maxInstanceCount:1/0,dh=Math.min($.instanceCount,Ge);mt.renderInstances(At,di,dh)}else mt.render(At,di)},this.compile=function(C,G){function $(U,Y,ve){U.transparent===!0&&U.side===Et&&U.forceSinglePass===!1?(U.side=dt,U.needsUpdate=!0,Dn(U,Y,ve),U.side=fn,U.needsUpdate=!0,Dn(U,Y,ve),U.side=Et):Dn(U,Y,ve)}d($,"prepare"),f=T.get(C),f.init(),g.push(f),C.traverseVisible(function(U){U.isLight&&U.layers.test(G.layers)&&(f.pushLight(U),U.castShadow&&f.pushShadow(U))}),f.setupLights(A.physicallyCorrectLights),C.traverse(function(U){let Y=U.material;if(Y)if(Array.isArray(Y))for(let ve=0;ve<Y.length;ve++){let De=Y[ve];$(De,C,U)}else $(Y,C,U)}),g.pop(),f=null};let K=null;function te(C){K&&K(C)}d(te,"onAnimationFrame");function de(){Ke.stop()}d(de,"onXRSessionStart");function _e(){Ke.start()}d(_e,"onXRSessionEnd");let Ke=new XA;Ke.setAnimationLoop(te),typeof self<"u"&&Ke.setContext(self),this.setAnimationLoop=function(C){K=C,me.setAnimationLoop(C),C===null?Ke.stop():Ke.start()},me.addEventListener("sessionstart",de),me.addEventListener("sessionend",_e),this.render=function(C,G){if(G!==void 0&&G.isCamera!==!0){console.error("THREE.WebGLRenderer.render: camera is not an instance of THREE.Camera.");return}if(m===!0)return;C.matrixWorldAutoUpdate===!0&&C.updateMatrixWorld(),G.parent===null&&G.matrixWorldAutoUpdate===!0&&G.updateMatrixWorld(),me.enabled===!0&&me.isPresenting===!0&&(me.cameraAutoUpdate===!0&&me.updateCamera(G),G=me.getCamera()),C.isScene===!0&&C.onBeforeRender(A,C,G,x),f=T.get(C,g.length),f.init(),g.push(f),fe.multiplyMatrices(G.projectionMatrix,G.matrixWorldInverse),H.setFromProjectionMatrix(fe),j=this.localClippingEnabled,k=M.init(this.clippingPlanes,j),u=zn.get(C,p.length),u.init(),p.push(u),Bt(C,G,0,A.sortObjects),u.finish(),A.sortObjects===!0&&u.sort(z,O),k===!0&&M.beginShadows();let $=f.state.shadowsArray;if(X.render($,C,G),k===!0&&M.endShadows(),this.info.autoReset===!0&&this.info.reset(),se.render(u,C),f.setupLights(A.physicallyCorrectLights),G.isArrayCamera){let U=G.cameras;for(let Y=0,ve=U.length;Y<ve;Y++){let De=U[Y];Wt(u,C,De,De.viewport)}}else Wt(u,C,G);x!==null&&(Ce.updateMultisampleRenderTarget(x),Ce.updateRenderTargetMipmap(x)),C.isScene===!0&&C.onAfterRender(A,C,G),J.resetDefaultState(),y=-1,w=null,g.pop(),g.length>0?f=g[g.length-1]:f=null,p.pop(),p.length>0?u=p[p.length-1]:u=null};function Bt(C,G,$,U){if(C.visible===!1)return;if(C.layers.test(G.layers)){if(C.isGroup)$=C.renderOrder;else if(C.isLOD)C.autoUpdate===!0&&C.update(G);else if(C.isLight)f.pushLight(C),C.castShadow&&f.pushShadow(C);else if(C.isSprite){if(!C.frustumCulled||H.intersectsSprite(C)){U&&ee.setFromMatrixPosition(C.matrixWorld).applyMatrix4(fe);let De=xt.update(C),Fe=C.material;Fe.visible&&u.push(C,De,Fe,$,ee.z,null)}}else if((C.isMesh||C.isLine||C.isPoints)&&(C.isSkinnedMesh&&C.skeleton.frame!==$e.render.frame&&(C.skeleton.update(),C.skeleton.frame=$e.render.frame),!C.frustumCulled||H.intersectsObject(C))){U&&ee.setFromMatrixPosition(C.matrixWorld).applyMatrix4(fe);let De=xt.update(C),Fe=C.material;if(Array.isArray(Fe)){let Oe=De.groups;for(let He=0,Qe=Oe.length;He<Qe;He++){let ke=Oe[He],At=Fe[ke.materialIndex];At&&At.visible&&u.push(C,De,At,$,ee.z,ke)}}else Fe.visible&&u.push(C,De,Fe,$,ee.z,null)}}let ve=C.children;for(let De=0,Fe=ve.length;De<Fe;De++)Bt(ve[De],G,$,U)}d(Bt,"projectObject");function Wt(C,G,$,U){let Y=C.opaque,ve=C.transmissive,De=C.transparent;f.setupLightsView($),k===!0&&M.setGlobalState(A.clippingPlanes,$),ve.length>0&&ls(Y,G,$),U&&ce.viewport(I.copy(U)),Y.length>0&&at(Y,G,$),ve.length>0&&at(ve,G,$),De.length>0&&at(De,G,$),ce.buffers.depth.setTest(!0),ce.buffers.depth.setMask(!0),ce.buffers.color.setMask(!0),ce.setPolygonOffset(!1)}d(Wt,"renderScene");function ls(C,G,$){let U=ge.isWebGL2;Z===null&&(Z=new Xt(1,1,{generateMipmaps:!0,type:Ae.has("EXT_color_buffer_half_float")?Pt:$t,minFilter:wn,samples:U&&s===!0?4:0})),A.getDrawingBufferSize(V),U?Z.setSize(V.x,V.y):Z.setSize(_l(V.x),_l(V.y));let Y=A.getRenderTarget();A.setRenderTarget(Z),A.clear();let ve=A.toneMapping;A.toneMapping=qn,at(C,G,$),A.toneMapping=ve,Ce.updateMultisampleRenderTarget(Z),Ce.updateRenderTargetMipmap(Z),A.setRenderTarget(Y)}d(ls,"renderTransmissionPass");function at(C,G,$){let U=G.isScene===!0?G.overrideMaterial:null;for(let Y=0,ve=C.length;Y<ve;Y++){let De=C[Y],Fe=De.object,Oe=De.geometry,He=U===null?De.material:U,Qe=De.group;Fe.layers.test($.layers)&&ui(Fe,G,$,Oe,He,Qe)}}d(at,"renderObjects");function ui(C,G,$,U,Y,ve){C.onBeforeRender(A,G,$,U,Y,ve),C.modelViewMatrix.multiplyMatrices($.matrixWorldInverse,C.matrixWorld),C.normalMatrix.getNormalMatrix(C.modelViewMatrix),Y.onBeforeRender(A,G,$,U,C,ve),Y.transparent===!0&&Y.side===Et&&Y.forceSinglePass===!1?(Y.side=dt,Y.needsUpdate=!0,A.renderBufferDirect($,G,U,Y,C,ve),Y.side=fn,Y.needsUpdate=!0,A.renderBufferDirect($,G,U,Y,C,ve),Y.side=Et):A.renderBufferDirect($,G,U,Y,C,ve),C.onAfterRender(A,G,$,U,Y,ve)}d(ui,"renderObject");function Dn(C,G,$){G.isScene!==!0&&(G=re);let U=Le.get(C),Y=f.state.lights,ve=f.state.shadowsArray,De=Y.state.version,Fe=Xe.getParameters(C,Y.state,ve,G,$),Oe=Xe.getProgramCacheKey(Fe),He=U.programs;U.environment=C.isMeshStandardMaterial?G.environment:null,U.fog=G.fog,U.envMap=(C.isMeshStandardMaterial?Bn:yt).get(C.envMap||U.environment),He===void 0&&(C.addEventListener("dispose",ot),He=new Map,U.programs=He);let Qe=He.get(Oe);if(Qe!==void 0){if(U.currentProgram===Qe&&U.lightsStateVersion===De)return dp(C,Fe),Qe}else Fe.uniforms=Xe.getUniforms(C),C.onBuild($,Fe,A),C.onBeforeCompile(Fe,A),Qe=Xe.acquireProgram(Fe,Oe),He.set(Oe,Qe),U.uniforms=Fe.uniforms;let ke=U.uniforms;(!C.isShaderMaterial&&!C.isRawShaderMaterial||C.clipping===!0)&&(ke.clippingPlanes=M.uniform),dp(C,Fe),U.needsLights=Z_(C),U.lightsStateVersion=De,U.needsLights&&(ke.ambientLightColor.value=Y.state.ambient,ke.lightProbe.value=Y.state.probe,ke.directionalLights.value=Y.state.directional,ke.directionalLightShadows.value=Y.state.directionalShadow,ke.spotLights.value=Y.state.spot,ke.spotLightShadows.value=Y.state.spotShadow,ke.rectAreaLights.value=Y.state.rectArea,ke.ltc_1.value=Y.state.rectAreaLTC1,ke.ltc_2.value=Y.state.rectAreaLTC2,ke.pointLights.value=Y.state.point,ke.pointLightShadows.value=Y.state.pointShadow,ke.hemisphereLights.value=Y.state.hemi,ke.directionalShadowMap.value=Y.state.directionalShadowMap,ke.directionalShadowMatrix.value=Y.state.directionalShadowMatrix,ke.spotShadowMap.value=Y.state.spotShadowMap,ke.spotLightMatrix.value=Y.state.spotLightMatrix,ke.spotLightMap.value=Y.state.spotLightMap,ke.pointShadowMap.value=Y.state.pointShadowMap,ke.pointShadowMatrix.value=Y.state.pointShadowMatrix);let At=Qe.getUniforms(),_n=nr.seqWithValue(At.seq,ke);return U.currentProgram=Qe,U.uniformsList=_n,Qe}d(Dn,"getProgram");function dp(C,G){let $=Le.get(C);$.outputEncoding=G.outputEncoding,$.instancing=G.instancing,$.skinning=G.skinning,$.morphTargets=G.morphTargets,$.morphNormals=G.morphNormals,$.morphColors=G.morphColors,$.morphTargetsCount=G.morphTargetsCount,$.numClippingPlanes=G.numClippingPlanes,$.numIntersection=G.numClipIntersection,$.vertexAlphas=G.vertexAlphas,$.vertexTangents=G.vertexTangents,$.toneMapping=G.toneMapping}d(dp,"updateCommonMaterialProperties");function J_(C,G,$,U,Y){G.isScene!==!0&&(G=re),Ce.resetTextureUnits();let ve=G.fog,De=U.isMeshStandardMaterial?G.environment:null,Fe=x===null?A.outputEncoding:x.isXRRenderTarget===!0?x.texture.encoding:ft,Oe=(U.isMeshStandardMaterial?Bn:yt).get(U.envMap||De),He=U.vertexColors===!0&&!!$.attributes.color&&$.attributes.color.itemSize===4,Qe=!!U.normalMap&&!!$.attributes.tangent,ke=!!$.morphAttributes.position,At=!!$.morphAttributes.normal,_n=!!$.morphAttributes.color,di=U.toneMapped?A.toneMapping:qn,cs=$.morphAttributes.position||$.morphAttributes.normal||$.morphAttributes.color,mt=cs!==void 0?cs.length:0,Ge=Le.get(U),dh=f.state.lights;if(k===!0&&(j===!0||C!==w)){let yn=C===w&&U.id===y;M.setState(U,C,yn)}let Rt=!1;U.version===Ge.__version?(Ge.needsLights&&Ge.lightsStateVersion!==dh.state.version||Ge.outputEncoding!==Fe||Y.isInstancedMesh&&Ge.instancing===!1||!Y.isInstancedMesh&&Ge.instancing===!0||Y.isSkinnedMesh&&Ge.skinning===!1||!Y.isSkinnedMesh&&Ge.skinning===!0||Ge.envMap!==Oe||U.fog===!0&&Ge.fog!==ve||Ge.numClippingPlanes!==void 0&&(Ge.numClippingPlanes!==M.numPlanes||Ge.numIntersection!==M.numIntersection)||Ge.vertexAlphas!==He||Ge.vertexTangents!==Qe||Ge.morphTargets!==ke||Ge.morphNormals!==At||Ge.morphColors!==_n||Ge.toneMapping!==di||ge.isWebGL2===!0&&Ge.morphTargetsCount!==mt)&&(Rt=!0):(Rt=!0,Ge.__version=U.version);let hs=Ge.currentProgram;Rt===!0&&(hs=Dn(U,G,Y));let fp=!1,lo=!1,fh=!1,Zt=hs.getUniforms(),us=Ge.uniforms;if(ce.useProgram(hs.program)&&(fp=!0,lo=!0,fh=!0),U.id!==y&&(y=U.id,lo=!0),fp||w!==C){if(Zt.setValue(W,"projectionMatrix",C.projectionMatrix),ge.logarithmicDepthBuffer&&Zt.setValue(W,"logDepthBufFC",2/(Math.log(C.far+1)/Math.LN2)),w!==C&&(w=C,lo=!0,fh=!0),U.isShaderMaterial||U.isMeshPhongMaterial||U.isMeshToonMaterial||U.isMeshStandardMaterial||U.envMap){let yn=Zt.map.cameraPosition;yn!==void 0&&yn.setValue(W,ee.setFromMatrixPosition(C.matrixWorld))}(U.isMeshPhongMaterial||U.isMeshToonMaterial||U.isMeshLambertMaterial||U.isMeshBasicMaterial||U.isMeshStandardMaterial||U.isShaderMaterial)&&Zt.setValue(W,"isOrthographic",C.isOrthographicCamera===!0),(U.isMeshPhongMaterial||U.isMeshToonMaterial||U.isMeshLambertMaterial||U.isMeshBasicMaterial||U.isMeshStandardMaterial||U.isShaderMaterial||U.isShadowMaterial||Y.isSkinnedMesh)&&Zt.setValue(W,"viewMatrix",C.matrixWorldInverse)}if(Y.isSkinnedMesh){Zt.setOptional(W,Y,"bindMatrix"),Zt.setOptional(W,Y,"bindMatrixInverse");let yn=Y.skeleton;yn&&(ge.floatVertexTextures?(yn.boneTexture===null&&yn.computeBoneTexture(),Zt.setValue(W,"boneTexture",yn.boneTexture,Ce),Zt.setValue(W,"boneTextureSize",yn.boneTextureSize)):console.warn("THREE.WebGLRenderer: SkinnedMesh can only be used with WebGL 2. With WebGL 1 OES_texture_float and vertex textures support is required."))}let ph=$.morphAttributes;if((ph.position!==void 0||ph.normal!==void 0||ph.color!==void 0&&ge.isWebGL2===!0)&&ae.update(Y,$,U,hs),(lo||Ge.receiveShadow!==Y.receiveShadow)&&(Ge.receiveShadow=Y.receiveShadow,Zt.setValue(W,"receiveShadow",Y.receiveShadow)),U.isMeshGouraudMaterial&&U.envMap!==null&&(us.envMap.value=Oe,us.flipEnvMap.value=Oe.isCubeTexture&&Oe.isRenderTargetTexture===!1?-1:1),lo&&(Zt.setValue(W,"toneMappingExposure",A.toneMappingExposure),Ge.needsLights&&j_(us,fh),ve&&U.fog===!0&&hi.refreshFogUniforms(us,ve),hi.refreshMaterialUniforms(us,U,N,R,Z),nr.upload(W,Ge.uniformsList,us,Ce)),U.isShaderMaterial&&U.uniformsNeedUpdate===!0&&(nr.upload(W,Ge.uniformsList,us,Ce),U.uniformsNeedUpdate=!1),U.isSpriteMaterial&&Zt.setValue(W,"center",Y.center),Zt.setValue(W,"modelViewMatrix",Y.modelViewMatrix),Zt.setValue(W,"normalMatrix",Y.normalMatrix),Zt.setValue(W,"modelMatrix",Y.matrixWorld),U.isShaderMaterial||U.isRawShaderMaterial){let yn=U.uniformsGroups;for(let Ah=0,ey=yn.length;Ah<ey;Ah++)if(ge.isWebGL2){let pp=yn[Ah];Ee.update(pp,hs),Ee.bind(pp,hs)}else console.warn("THREE.WebGLRenderer: Uniform Buffer Objects can only be used with WebGL 2.")}return hs}d(J_,"setProgram");function j_(C,G){C.ambientLightColor.needsUpdate=G,C.lightProbe.needsUpdate=G,C.directionalLights.needsUpdate=G,C.directionalLightShadows.needsUpdate=G,C.pointLights.needsUpdate=G,C.pointLightShadows.needsUpdate=G,C.spotLights.needsUpdate=G,C.spotLightShadows.needsUpdate=G,C.rectAreaLights.needsUpdate=G,C.hemisphereLights.needsUpdate=G}d(j_,"markUniformsLightsNeedsUpdate");function Z_(C){return C.isMeshLambertMaterial||C.isMeshToonMaterial||C.isMeshPhongMaterial||C.isMeshStandardMaterial||C.isShadowMaterial||C.isShaderMaterial&&C.lights===!0}d(Z_,"materialNeedsLights"),this.getActiveCubeFace=function(){return _},this.getActiveMipmapLevel=function(){return E},this.getRenderTarget=function(){return x},this.setRenderTargetTextures=function(C,G,$){Le.get(C.texture).__webglTexture=G,Le.get(C.depthTexture).__webglTexture=$;let U=Le.get(C);U.__hasExternalTextures=!0,U.__hasExternalTextures&&(U.__autoAllocateDepthBuffer=$===void 0,U.__autoAllocateDepthBuffer||Ae.has("WEBGL_multisampled_render_to_texture")===!0&&(console.warn("THREE.WebGLRenderer: Render-to-texture extension was disabled because an external texture was provided"),U.__useRenderToTexture=!1))},this.setRenderTargetFramebuffer=function(C,G){let $=Le.get(C);$.__webglFramebuffer=G,$.__useDefaultFramebuffer=G===void 0},this.setRenderTarget=function(C,G=0,$=0){x=C,_=G,E=$;let U=!0,Y=null,ve=!1,De=!1;if(C){let Oe=Le.get(C);Oe.__useDefaultFramebuffer!==void 0?(ce.bindFramebuffer(36160,null),U=!1):Oe.__webglFramebuffer===void 0?Ce.setupRenderTarget(C):Oe.__hasExternalTextures&&Ce.rebindTextures(C,Le.get(C.texture).__webglTexture,Le.get(C.depthTexture).__webglTexture);let He=C.texture;(He.isData3DTexture||He.isDataArrayTexture||He.isCompressedArrayTexture)&&(De=!0);let Qe=Le.get(C).__webglFramebuffer;C.isWebGLCubeRenderTarget?(Y=Qe[G],ve=!0):ge.isWebGL2&&C.samples>0&&Ce.useMultisampledRTT(C)===!1?Y=Le.get(C).__webglMultisampledFramebuffer:Y=Qe,I.copy(C.viewport),S.copy(C.scissor),v=C.scissorTest}else I.copy(D).multiplyScalar(N).floor(),S.copy(Q).multiplyScalar(N).floor(),v=q;if(ce.bindFramebuffer(36160,Y)&&ge.drawBuffers&&U&&ce.drawBuffers(C,Y),ce.viewport(I),ce.scissor(S),ce.setScissorTest(v),ve){let Oe=Le.get(C.texture);W.framebufferTexture2D(36160,36064,34069+G,Oe.__webglTexture,$)}else if(De){let Oe=Le.get(C.texture),He=G||0;W.framebufferTextureLayer(36160,36064,Oe.__webglTexture,$||0,He)}y=-1},this.readRenderTargetPixels=function(C,G,$,U,Y,ve,De){if(!(C&&C.isWebGLRenderTarget)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");return}let Fe=Le.get(C).__webglFramebuffer;if(C.isWebGLCubeRenderTarget&&De!==void 0&&(Fe=Fe[De]),Fe){ce.bindFramebuffer(36160,Fe);try{let Oe=C.texture,He=Oe.format,Qe=Oe.type;if(He!==lt&&ue.convert(He)!==W.getParameter(35739)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in RGBA or implementation defined format.");return}let ke=Qe===Pt&&(Ae.has("EXT_color_buffer_half_float")||ge.isWebGL2&&Ae.has("EXT_color_buffer_float"));if(Qe!==$t&&ue.convert(Qe)!==W.getParameter(35738)&&!(Qe===Ut&&(ge.isWebGL2||Ae.has("OES_texture_float")||Ae.has("WEBGL_color_buffer_float")))&&!ke){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in UnsignedByteType or implementation defined type.");return}G>=0&&G<=C.width-U&&$>=0&&$<=C.height-Y&&W.readPixels(G,$,U,Y,ue.convert(He),ue.convert(Qe),ve)}finally{let Oe=x!==null?Le.get(x).__webglFramebuffer:null;ce.bindFramebuffer(36160,Oe)}}},this.copyFramebufferToTexture=function(C,G,$=0){let U=Math.pow(2,-$),Y=Math.floor(G.image.width*U),ve=Math.floor(G.image.height*U);Ce.setTexture2D(G,0),W.copyTexSubImage2D(3553,$,0,0,C.x,C.y,Y,ve),ce.unbindTexture()},this.copyTextureToTexture=function(C,G,$,U=0){let Y=G.image.width,ve=G.image.height,De=ue.convert($.format),Fe=ue.convert($.type);Ce.setTexture2D($,0),W.pixelStorei(37440,$.flipY),W.pixelStorei(37441,$.premultiplyAlpha),W.pixelStorei(3317,$.unpackAlignment),G.isDataTexture?W.texSubImage2D(3553,U,C.x,C.y,Y,ve,De,Fe,G.image.data):G.isCompressedTexture?W.compressedTexSubImage2D(3553,U,C.x,C.y,G.mipmaps[0].width,G.mipmaps[0].height,De,G.mipmaps[0].data):W.texSubImage2D(3553,U,C.x,C.y,De,Fe,G.image),U===0&&$.generateMipmaps&&W.generateMipmap(3553),ce.unbindTexture()},this.copyTextureToTexture3D=function(C,G,$,U,Y=0){if(A.isWebGL1Renderer){console.warn("THREE.WebGLRenderer.copyTextureToTexture3D: can only be used with WebGL2.");return}let ve=C.max.x-C.min.x+1,De=C.max.y-C.min.y+1,Fe=C.max.z-C.min.z+1,Oe=ue.convert(U.format),He=ue.convert(U.type),Qe;if(U.isData3DTexture)Ce.setTexture3D(U,0),Qe=32879;else if(U.isDataArrayTexture)Ce.setTexture2DArray(U,0),Qe=35866;else{console.warn("THREE.WebGLRenderer.copyTextureToTexture3D: only supports THREE.DataTexture3D and THREE.DataTexture2DArray.");return}W.pixelStorei(37440,U.flipY),W.pixelStorei(37441,U.premultiplyAlpha),W.pixelStorei(3317,U.unpackAlignment);let ke=W.getParameter(3314),At=W.getParameter(32878),_n=W.getParameter(3316),di=W.getParameter(3315),cs=W.getParameter(32877),mt=$.isCompressedTexture?$.mipmaps[0]:$.image;W.pixelStorei(3314,mt.width),W.pixelStorei(32878,mt.height),W.pixelStorei(3316,C.min.x),W.pixelStorei(3315,C.min.y),W.pixelStorei(32877,C.min.z),$.isDataTexture||$.isData3DTexture?W.texSubImage3D(Qe,Y,G.x,G.y,G.z,ve,De,Fe,Oe,He,mt.data):$.isCompressedArrayTexture?(console.warn("THREE.WebGLRenderer.copyTextureToTexture3D: untested support for compressed srcTexture."),W.compressedTexSubImage3D(Qe,Y,G.x,G.y,G.z,ve,De,Fe,Oe,mt.data)):W.texSubImage3D(Qe,Y,G.x,G.y,G.z,ve,De,Fe,Oe,He,mt),W.pixelStorei(3314,ke),W.pixelStorei(32878,At),W.pixelStorei(3316,_n),W.pixelStorei(3315,di),W.pixelStorei(32877,cs),Y===0&&U.generateMipmaps&&W.generateMipmap(Qe),ce.unbindTexture()},this.initTexture=function(C){C.isCubeTexture?Ce.setTextureCube(C,0):C.isData3DTexture?Ce.setTexture3D(C,0):C.isDataArrayTexture||C.isCompressedArrayTexture?Ce.setTexture2DArray(C,0):Ce.setTexture2D(C,0),ce.unbindTexture()},this.resetState=function(){_=0,E=0,x=null,ce.reset(),J.reset()},typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}d(Ru,"WebGLRenderer");var lu=class extends Ru{static{d(this,"WebGL1Renderer")}};lu.prototype.isWebGL1Renderer=!0;var Gt=class extends Ze{static{d(this,"Scene")}constructor(){super(),this.isScene=!0,this.type="Scene",this.background=null,this.environment=null,this.fog=null,this.backgroundBlurriness=0,this.backgroundIntensity=1,this.overrideMaterial=null,typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}copy(e,t){return super.copy(e,t),e.background!==null&&(this.background=e.background.clone()),e.environment!==null&&(this.environment=e.environment.clone()),e.fog!==null&&(this.fog=e.fog.clone()),this.backgroundBlurriness=e.backgroundBlurriness,this.backgroundIntensity=e.backgroundIntensity,e.overrideMaterial!==null&&(this.overrideMaterial=e.overrideMaterial.clone()),this.matrixAutoUpdate=e.matrixAutoUpdate,this}toJSON(e){let t=super.toJSON(e);return this.fog!==null&&(t.object.fog=this.fog.toJSON()),this.backgroundBlurriness>0&&(t.object.backgroundBlurriness=this.backgroundBlurriness),this.backgroundIntensity!==1&&(t.object.backgroundIntensity=this.backgroundIntensity),t}get autoUpdate(){return console.warn("THREE.Scene: autoUpdate was renamed to matrixWorldAutoUpdate in r144."),this.matrixWorldAutoUpdate}set autoUpdate(e){console.warn("THREE.Scene: autoUpdate was renamed to matrixWorldAutoUpdate in r144."),this.matrixWorldAutoUpdate=e}},Oo=class{static{d(this,"InterleavedBuffer")}constructor(e,t){this.isInterleavedBuffer=!0,this.array=e,this.stride=t,this.count=e!==void 0?e.length/t:0,this.usage=Xh,this.updateRange={offset:0,count:-1},this.version=0,this.uuid=Kn()}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}setUsage(e){return this.usage=e,this}copy(e){return this.array=new e.array.constructor(e.array),this.count=e.count,this.stride=e.stride,this.usage=e.usage,this}copyAt(e,t,n){e*=this.stride,n*=t.stride;for(let i=0,s=this.stride;i<s;i++)this.array[e+i]=t.array[n+i];return this}set(e,t=0){return this.array.set(e,t),this}clone(e){e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=Kn()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=this.array.slice(0).buffer);let t=new this.array.constructor(e.arrayBuffers[this.array.buffer._uuid]),n=new this.constructor(t,this.stride);return n.setUsage(this.usage),n}onUpload(e){return this.onUploadCallback=e,this}toJSON(e){return e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=Kn()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=Array.from(new Uint32Array(this.array.buffer))),{uuid:this.uuid,buffer:this.array.buffer._uuid,type:this.array.constructor.name,stride:this.stride}}},tn=new B,No=class o{static{d(this,"InterleavedBufferAttribute")}constructor(e,t,n,i=!1){this.isInterleavedBufferAttribute=!0,this.name="",this.data=e,this.itemSize=t,this.offset=n,this.normalized=i}get count(){return this.data.count}get array(){return this.data.array}set needsUpdate(e){this.data.needsUpdate=e}applyMatrix4(e){for(let t=0,n=this.data.count;t<n;t++)tn.fromBufferAttribute(this,t),tn.applyMatrix4(e),this.setXYZ(t,tn.x,tn.y,tn.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)tn.fromBufferAttribute(this,t),tn.applyNormalMatrix(e),this.setXYZ(t,tn.x,tn.y,tn.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)tn.fromBufferAttribute(this,t),tn.transformDirection(e),this.setXYZ(t,tn.x,tn.y,tn.z);return this}setX(e,t){return this.normalized&&(t=tt(t,this.array)),this.data.array[e*this.data.stride+this.offset]=t,this}setY(e,t){return this.normalized&&(t=tt(t,this.array)),this.data.array[e*this.data.stride+this.offset+1]=t,this}setZ(e,t){return this.normalized&&(t=tt(t,this.array)),this.data.array[e*this.data.stride+this.offset+2]=t,this}setW(e,t){return this.normalized&&(t=tt(t,this.array)),this.data.array[e*this.data.stride+this.offset+3]=t,this}getX(e){let t=this.data.array[e*this.data.stride+this.offset];return this.normalized&&(t=vi(t,this.array)),t}getY(e){let t=this.data.array[e*this.data.stride+this.offset+1];return this.normalized&&(t=vi(t,this.array)),t}getZ(e){let t=this.data.array[e*this.data.stride+this.offset+2];return this.normalized&&(t=vi(t,this.array)),t}getW(e){let t=this.data.array[e*this.data.stride+this.offset+3];return this.normalized&&(t=vi(t,this.array)),t}setXY(e,t,n){return e=e*this.data.stride+this.offset,this.normalized&&(t=tt(t,this.array),n=tt(n,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this}setXYZ(e,t,n,i){return e=e*this.data.stride+this.offset,this.normalized&&(t=tt(t,this.array),n=tt(n,this.array),i=tt(i,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=i,this}setXYZW(e,t,n,i,s){return e=e*this.data.stride+this.offset,this.normalized&&(t=tt(t,this.array),n=tt(n,this.array),i=tt(i,this.array),s=tt(s,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=i,this.data.array[e+3]=s,this}clone(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.clone(): Cloning an interleaved buffer attribute will de-interleave buffer data.");let t=[];for(let n=0;n<this.count;n++){let i=n*this.data.stride+this.offset;for(let s=0;s<this.itemSize;s++)t.push(this.data.array[i+s])}return new je(new this.array.constructor(t),this.itemSize,this.normalized)}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.clone(e)),new o(e.interleavedBuffers[this.data.uuid],this.itemSize,this.offset,this.normalized)}toJSON(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.toJSON(): Serializing an interleaved buffer attribute will de-interleave buffer data.");let t=[];for(let n=0;n<this.count;n++){let i=n*this.data.stride+this.offset;for(let s=0;s<this.itemSize;s++)t.push(this.data.array[i+s])}return{itemSize:this.itemSize,type:this.array.constructor.name,array:t,normalized:this.normalized}}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.toJSON(e)),{isInterleavedBufferAttribute:!0,itemSize:this.itemSize,data:this.data.uuid,offset:this.offset,normalized:this.normalized}}};var _A=new B,yA=new nt,xA=new nt,WM=new B,vA=new Ie,Il=class extends pe{static{d(this,"SkinnedMesh")}constructor(e,t){super(e,t),this.isSkinnedMesh=!0,this.type="SkinnedMesh",this.bindMode="attached",this.bindMatrix=new Ie,this.bindMatrixInverse=new Ie}copy(e,t){return super.copy(e,t),this.bindMode=e.bindMode,this.bindMatrix.copy(e.bindMatrix),this.bindMatrixInverse.copy(e.bindMatrixInverse),this.skeleton=e.skeleton,this}bind(e,t){this.skeleton=e,t===void 0&&(this.updateMatrixWorld(!0),this.skeleton.calculateInverses(),t=this.matrixWorld),this.bindMatrix.copy(t),this.bindMatrixInverse.copy(t).invert()}pose(){this.skeleton.pose()}normalizeSkinWeights(){let e=new nt,t=this.geometry.attributes.skinWeight;for(let n=0,i=t.count;n<i;n++){e.fromBufferAttribute(t,n);let s=1/e.manhattanLength();s!==1/0?e.multiplyScalar(s):e.set(1,0,0,0),t.setXYZW(n,e.x,e.y,e.z,e.w)}}updateMatrixWorld(e){super.updateMatrixWorld(e),this.bindMode==="attached"?this.bindMatrixInverse.copy(this.matrixWorld).invert():this.bindMode==="detached"?this.bindMatrixInverse.copy(this.bindMatrix).invert():console.warn("THREE.SkinnedMesh: Unrecognized bindMode: "+this.bindMode)}boneTransform(e,t){let n=this.skeleton,i=this.geometry;yA.fromBufferAttribute(i.attributes.skinIndex,e),xA.fromBufferAttribute(i.attributes.skinWeight,e),_A.copy(t).applyMatrix4(this.bindMatrix),t.set(0,0,0);for(let s=0;s<4;s++){let r=xA.getComponent(s);if(r!==0){let a=yA.getComponent(s);vA.multiplyMatrices(n.bones[a].matrixWorld,n.boneInverses[a]),t.addScaledVector(WM.copy(_A).applyMatrix4(vA),r)}}return t.applyMatrix4(this.bindMatrixInverse)}},Uo=class extends Ze{static{d(this,"Bone")}constructor(){super(),this.isBone=!0,this.type="Bone"}},ur=class extends st{static{d(this,"DataTexture")}constructor(e=null,t=1,n=1,i,s,r,a,l,c=ct,h=ct,u,f){super(null,r,a,l,c,h,i,s,u,f),this.isDataTexture=!0,this.image={data:e,width:t,height:n},this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}},EA=new Ie,qM=new Ie,Cl=class o{static{d(this,"Skeleton")}constructor(e=[],t=[]){this.uuid=Kn(),this.bones=e.slice(0),this.boneInverses=t,this.boneMatrices=null,this.boneTexture=null,this.boneTextureSize=0,this.frame=-1,this.init()}init(){let e=this.bones,t=this.boneInverses;if(this.boneMatrices=new Float32Array(e.length*16),t.length===0)this.calculateInverses();else if(e.length!==t.length){console.warn("THREE.Skeleton: Number of inverse bone matrices does not match amount of bones."),this.boneInverses=[];for(let n=0,i=this.bones.length;n<i;n++)this.boneInverses.push(new Ie)}}calculateInverses(){this.boneInverses.length=0;for(let e=0,t=this.bones.length;e<t;e++){let n=new Ie;this.bones[e]&&n.copy(this.bones[e].matrixWorld).invert(),this.boneInverses.push(n)}}pose(){for(let e=0,t=this.bones.length;e<t;e++){let n=this.bones[e];n&&n.matrixWorld.copy(this.boneInverses[e]).invert()}for(let e=0,t=this.bones.length;e<t;e++){let n=this.bones[e];n&&(n.parent&&n.parent.isBone?(n.matrix.copy(n.parent.matrixWorld).invert(),n.matrix.multiply(n.matrixWorld)):n.matrix.copy(n.matrixWorld),n.matrix.decompose(n.position,n.quaternion,n.scale))}}update(){let e=this.bones,t=this.boneInverses,n=this.boneMatrices,i=this.boneTexture;for(let s=0,r=e.length;s<r;s++){let a=e[s]?e[s].matrixWorld:qM;EA.multiplyMatrices(a,t[s]),EA.toArray(n,s*16)}i!==null&&(i.needsUpdate=!0)}clone(){return new o(this.bones,this.boneInverses)}computeBoneTexture(){let e=Math.sqrt(this.bones.length*4);e=WA(e),e=Math.max(e,4);let t=new Float32Array(e*e*4);t.set(this.boneMatrices);let n=new ur(t,e,e,lt,Ut);return n.needsUpdate=!0,this.boneMatrices=t,this.boneTexture=n,this.boneTextureSize=e,this}getBoneByName(e){for(let t=0,n=this.bones.length;t<n;t++){let i=this.bones[t];if(i.name===e)return i}}dispose(){this.boneTexture!==null&&(this.boneTexture.dispose(),this.boneTexture=null)}fromJSON(e,t){this.uuid=e.uuid;for(let n=0,i=e.bones.length;n<i;n++){let s=e.bones[n],r=t[s];r===void 0&&(console.warn("THREE.Skeleton: No bone found with UUID:",s),r=new Uo),this.bones.push(r),this.boneInverses.push(new Ie().fromArray(e.boneInverses[n]))}return this.init(),this}toJSON(){let e={metadata:{version:4.5,type:"Skeleton",generator:"Skeleton.toJSON"},bones:[],boneInverses:[]};e.uuid=this.uuid;let t=this.bones,n=this.boneInverses;for(let i=0,s=t.length;i<s;i++){let r=t[i];e.bones.push(r.uuid);let a=n[i];e.boneInverses.push(a.toArray())}return e}},Qo=class extends je{static{d(this,"InstancedBufferAttribute")}constructor(e,t,n,i=1){super(e,t,n),this.isInstancedBufferAttribute=!0,this.meshPerAttribute=i}copy(e){return super.copy(e),this.meshPerAttribute=e.meshPerAttribute,this}toJSON(){let e=super.toJSON();return e.meshPerAttribute=this.meshPerAttribute,e.isInstancedBufferAttribute=!0,e}},wA=new Ie,MA=new Ie,ol=[],KM=new Ie,_o=new pe,Sl=class extends pe{static{d(this,"InstancedMesh")}constructor(e,t,n){super(e,t),this.isInstancedMesh=!0,this.instanceMatrix=new Qo(new Float32Array(n*16),16),this.instanceColor=null,this.count=n,this.frustumCulled=!1;for(let i=0;i<n;i++)this.setMatrixAt(i,KM)}copy(e,t){return super.copy(e,t),this.instanceMatrix.copy(e.instanceMatrix),e.instanceColor!==null&&(this.instanceColor=e.instanceColor.clone()),this.count=e.count,this}getColorAt(e,t){t.fromArray(this.instanceColor.array,e*3)}getMatrixAt(e,t){t.fromArray(this.instanceMatrix.array,e*16)}raycast(e,t){let n=this.matrixWorld,i=this.count;if(_o.geometry=this.geometry,_o.material=this.material,_o.material!==void 0)for(let s=0;s<i;s++){this.getMatrixAt(s,wA),MA.multiplyMatrices(n,wA),_o.matrixWorld=MA,_o.raycast(e,ol);for(let r=0,a=ol.length;r<a;r++){let l=ol[r];l.instanceId=s,l.object=this,t.push(l)}ol.length=0}}setColorAt(e,t){this.instanceColor===null&&(this.instanceColor=new Qo(new Float32Array(this.instanceMatrix.count*3),3)),t.toArray(this.instanceColor.array,e*3)}setMatrixAt(e,t){t.toArray(this.instanceMatrix.array,e*16)}updateMorphTargets(){}dispose(){this.dispatchEvent({type:"dispose"})}},ko=class extends sn{static{d(this,"LineBasicMaterial")}constructor(e){super(),this.isLineBasicMaterial=!0,this.type="LineBasicMaterial",this.color=new Me(16777215),this.linewidth=1,this.linecap="round",this.linejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.linewidth=e.linewidth,this.linecap=e.linecap,this.linejoin=e.linejoin,this.fog=e.fog,this}},bA=new B,IA=new B,CA=new Ie,Hh=new lr,al=new Mn,dr=class extends Ze{static{d(this,"Line")}constructor(e=new kt,t=new ko){super(),this.isLine=!0,this.type="Line",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=e.material,this.geometry=e.geometry,this}computeLineDistances(){let e=this.geometry;if(e.index===null){let t=e.attributes.position,n=[0];for(let i=1,s=t.count;i<s;i++)bA.fromBufferAttribute(t,i-1),IA.fromBufferAttribute(t,i),n[i]=n[i-1],n[i]+=bA.distanceTo(IA);e.setAttribute("lineDistance",new dn(n,1))}else console.warn("THREE.Line.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}raycast(e,t){let n=this.geometry,i=this.matrixWorld,s=e.params.Line.threshold,r=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),al.copy(n.boundingSphere),al.applyMatrix4(i),al.radius+=s,e.ray.intersectsSphere(al)===!1)return;CA.copy(i).invert(),Hh.copy(e.ray).applyMatrix4(CA);let a=s/((this.scale.x+this.scale.y+this.scale.z)/3),l=a*a,c=new B,h=new B,u=new B,f=new B,p=this.isLineSegments?2:1,g=n.index,m=n.attributes.position;if(g!==null){let _=Math.max(0,r.start),E=Math.min(g.count,r.start+r.count);for(let x=_,y=E-1;x<y;x+=p){let w=g.getX(x),I=g.getX(x+1);if(c.fromBufferAttribute(m,w),h.fromBufferAttribute(m,I),Hh.distanceSqToSegment(c,h,f,u)>l)continue;f.applyMatrix4(this.matrixWorld);let v=e.ray.origin.distanceTo(f);v<e.near||v>e.far||t.push({distance:v,point:u.clone().applyMatrix4(this.matrixWorld),index:x,face:null,faceIndex:null,object:this})}}else{let _=Math.max(0,r.start),E=Math.min(m.count,r.start+r.count);for(let x=_,y=E-1;x<y;x+=p){if(c.fromBufferAttribute(m,x),h.fromBufferAttribute(m,x+1),Hh.distanceSqToSegment(c,h,f,u)>l)continue;f.applyMatrix4(this.matrixWorld);let I=e.ray.origin.distanceTo(f);I<e.near||I>e.far||t.push({distance:I,point:u.clone().applyMatrix4(this.matrixWorld),index:x,face:null,faceIndex:null,object:this})}}}updateMorphTargets(){let t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){let i=t[n[0]];if(i!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let s=0,r=i.length;s<r;s++){let a=i[s].name||String(s);this.morphTargetInfluences.push(0),this.morphTargetDictionary[a]=s}}}}},SA=new B,TA=new B,Tl=class extends dr{static{d(this,"LineSegments")}constructor(e,t){super(e,t),this.isLineSegments=!0,this.type="LineSegments"}computeLineDistances(){let e=this.geometry;if(e.index===null){let t=e.attributes.position,n=[];for(let i=0,s=t.count;i<s;i+=2)SA.fromBufferAttribute(t,i),TA.fromBufferAttribute(t,i+1),n[i]=i===0?0:n[i-1],n[i+1]=n[i]+SA.distanceTo(TA);e.setAttribute("lineDistance",new dn(n,1))}else console.warn("THREE.LineSegments.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}},Bl=class extends dr{static{d(this,"LineLoop")}constructor(e,t){super(e,t),this.isLineLoop=!0,this.type="LineLoop"}},Go=class extends sn{static{d(this,"PointsMaterial")}constructor(e){super(),this.isPointsMaterial=!0,this.type="PointsMaterial",this.color=new Me(16777215),this.map=null,this.alphaMap=null,this.size=1,this.sizeAttenuation=!0,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.alphaMap=e.alphaMap,this.size=e.size,this.sizeAttenuation=e.sizeAttenuation,this.fog=e.fog,this}},BA=new Ie,cu=new lr,ll=new Mn,cl=new B,Rl=class extends Ze{static{d(this,"Points")}constructor(e=new kt,t=new Go){super(),this.isPoints=!0,this.type="Points",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=e.material,this.geometry=e.geometry,this}raycast(e,t){let n=this.geometry,i=this.matrixWorld,s=e.params.Points.threshold,r=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),ll.copy(n.boundingSphere),ll.applyMatrix4(i),ll.radius+=s,e.ray.intersectsSphere(ll)===!1)return;BA.copy(i).invert(),cu.copy(e.ray).applyMatrix4(BA);let a=s/((this.scale.x+this.scale.y+this.scale.z)/3),l=a*a,c=n.index,u=n.attributes.position;if(c!==null){let f=Math.max(0,r.start),p=Math.min(c.count,r.start+r.count);for(let g=f,A=p;g<A;g++){let m=c.getX(g);cl.fromBufferAttribute(u,m),RA(cl,m,l,i,e,t,this)}}else{let f=Math.max(0,r.start),p=Math.min(u.count,r.start+r.count);for(let g=f,A=p;g<A;g++)cl.fromBufferAttribute(u,g),RA(cl,g,l,i,e,t,this)}}updateMorphTargets(){let t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){let i=t[n[0]];if(i!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let s=0,r=i.length;s<r;s++){let a=i[s].name||String(s);this.morphTargetInfluences.push(0),this.morphTargetDictionary[a]=s}}}}};function RA(o,e,t,n,i,s,r){let a=cu.distanceSqToPoint(o);if(a<t){let l=new B;cu.closestPointToPoint(o,l),l.applyMatrix4(n);let c=i.ray.origin.distanceTo(l);if(c<i.near||c>i.far)return;s.push({distance:c,distanceToRay:Math.sqrt(a),point:l,index:e,face:null,object:r})}}d(RA,"testPoint");var Dl=class extends st{static{d(this,"VideoTexture")}constructor(e,t,n,i,s,r,a,l,c){super(e,t,n,i,s,r,a,l,c),this.isVideoTexture=!0,this.minFilter=r!==void 0?r:Je,this.magFilter=s!==void 0?s:Je,this.generateMipmaps=!1;let h=this;function u(){h.needsUpdate=!0,e.requestVideoFrameCallback(u)}d(u,"updateVideo"),"requestVideoFrameCallback"in e&&e.requestVideoFrameCallback(u)}clone(){return new this.constructor(this.image).copy(this)}update(){let e=this.image;"requestVideoFrameCallback"in e===!1&&e.readyState>=e.HAVE_CURRENT_DATA&&(this.needsUpdate=!0)}};var zo=class extends st{static{d(this,"CompressedTexture")}constructor(e,t,n,i,s,r,a,l,c,h,u,f){super(null,r,a,l,c,h,i,s,u,f),this.isCompressedTexture=!0,this.image={width:t,height:n},this.mipmaps=e,this.flipY=!1,this.generateMipmaps=!1}},Ll=class extends zo{static{d(this,"CompressedArrayTexture")}constructor(e,t,n,i,s,r){super(e,t,n,s,r),this.isCompressedArrayTexture=!0,this.image.depth=i,this.wrapR=Lt}},Vo=class extends st{static{d(this,"CanvasTexture")}constructor(e,t,n,i,s,r,a,l,c){super(e,t,n,i,s,r,a,l,c),this.isCanvasTexture=!0,this.needsUpdate=!0}};var On=class extends sn{static{d(this,"MeshStandardMaterial")}constructor(e){super(),this.isMeshStandardMaterial=!0,this.defines={STANDARD:""},this.type="MeshStandardMaterial",this.color=new Me(16777215),this.roughness=1,this.metalness=0,this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.emissive=new Me(0),this.emissiveIntensity=1,this.emissiveMap=null,this.bumpMap=null,this.bumpScale=1,this.normalMap=null,this.normalMapType=HA,this.normalScale=new Be(1,1),this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.roughnessMap=null,this.metalnessMap=null,this.alphaMap=null,this.envMap=null,this.envMapIntensity=1,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.flatShading=!1,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.defines={STANDARD:""},this.color.copy(e.color),this.roughness=e.roughness,this.metalness=e.metalness,this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.emissive.copy(e.emissive),this.emissiveMap=e.emissiveMap,this.emissiveIntensity=e.emissiveIntensity,this.bumpMap=e.bumpMap,this.bumpScale=e.bumpScale,this.normalMap=e.normalMap,this.normalMapType=e.normalMapType,this.normalScale.copy(e.normalScale),this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.roughnessMap=e.roughnessMap,this.metalnessMap=e.metalnessMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapIntensity=e.envMapIntensity,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.flatShading=e.flatShading,this.fog=e.fog,this}},oi=class extends On{static{d(this,"MeshPhysicalMaterial")}constructor(e){super(),this.isMeshPhysicalMaterial=!0,this.defines={STANDARD:"",PHYSICAL:""},this.type="MeshPhysicalMaterial",this.clearcoatMap=null,this.clearcoatRoughness=0,this.clearcoatRoughnessMap=null,this.clearcoatNormalScale=new Be(1,1),this.clearcoatNormalMap=null,this.ior=1.5,Object.defineProperty(this,"reflectivity",{get:d(function(){return Nt(2.5*(this.ior-1)/(this.ior+1),0,1)},"get"),set:d(function(t){this.ior=(1+.4*t)/(1-.4*t)},"set")}),this.iridescenceMap=null,this.iridescenceIOR=1.3,this.iridescenceThicknessRange=[100,400],this.iridescenceThicknessMap=null,this.sheenColor=new Me(0),this.sheenColorMap=null,this.sheenRoughness=1,this.sheenRoughnessMap=null,this.transmissionMap=null,this.thickness=0,this.thicknessMap=null,this.attenuationDistance=1/0,this.attenuationColor=new Me(1,1,1),this.specularIntensity=1,this.specularIntensityMap=null,this.specularColor=new Me(1,1,1),this.specularColorMap=null,this._sheen=0,this._clearcoat=0,this._iridescence=0,this._transmission=0,this.setValues(e)}get sheen(){return this._sheen}set sheen(e){this._sheen>0!=e>0&&this.version++,this._sheen=e}get clearcoat(){return this._clearcoat}set clearcoat(e){this._clearcoat>0!=e>0&&this.version++,this._clearcoat=e}get iridescence(){return this._iridescence}set iridescence(e){this._iridescence>0!=e>0&&this.version++,this._iridescence=e}get transmission(){return this._transmission}set transmission(e){this._transmission>0!=e>0&&this.version++,this._transmission=e}copy(e){return super.copy(e),this.defines={STANDARD:"",PHYSICAL:""},this.clearcoat=e.clearcoat,this.clearcoatMap=e.clearcoatMap,this.clearcoatRoughness=e.clearcoatRoughness,this.clearcoatRoughnessMap=e.clearcoatRoughnessMap,this.clearcoatNormalMap=e.clearcoatNormalMap,this.clearcoatNormalScale.copy(e.clearcoatNormalScale),this.ior=e.ior,this.iridescence=e.iridescence,this.iridescenceMap=e.iridescenceMap,this.iridescenceIOR=e.iridescenceIOR,this.iridescenceThicknessRange=[...e.iridescenceThicknessRange],this.iridescenceThicknessMap=e.iridescenceThicknessMap,this.sheen=e.sheen,this.sheenColor.copy(e.sheenColor),this.sheenColorMap=e.sheenColorMap,this.sheenRoughness=e.sheenRoughness,this.sheenRoughnessMap=e.sheenRoughnessMap,this.transmission=e.transmission,this.transmissionMap=e.transmissionMap,this.thickness=e.thickness,this.thicknessMap=e.thicknessMap,this.attenuationDistance=e.attenuationDistance,this.attenuationColor.copy(e.attenuationColor),this.specularIntensity=e.specularIntensity,this.specularIntensityMap=e.specularIntensityMap,this.specularColor.copy(e.specularColor),this.specularColorMap=e.specularColorMap,this}};function Gi(o,e,t){return em(o)?new o.constructor(o.subarray(e,t!==void 0?t:o.length)):o.slice(e,t)}d(Gi,"arraySlice");function hl(o,e,t){return!o||!t&&o.constructor===e?o:typeof e.BYTES_PER_ELEMENT=="number"?new e(o):Array.prototype.slice.call(o)}d(hl,"convertArray");function em(o){return ArrayBuffer.isView(o)&&!(o instanceof DataView)}d(em,"isTypedArray");function $M(o){function e(i,s){return o[i]-o[s]}d(e,"compareTime");let t=o.length,n=new Array(t);for(let i=0;i!==t;++i)n[i]=i;return n.sort(e),n}d($M,"getKeyframeOrder");function DA(o,e,t){let n=o.length,i=new o.constructor(n);for(let s=0,r=0;r!==n;++s){let a=t[s]*e;for(let l=0;l!==e;++l)i[r++]=o[a+l]}return i}d(DA,"sortedArray");function tm(o,e,t,n){let i=1,s=o[0];for(;s!==void 0&&s[n]===void 0;)s=o[i++];if(s===void 0)return;let r=s[n];if(r!==void 0)if(Array.isArray(r))do r=s[n],r!==void 0&&(e.push(s.time),t.push.apply(t,r)),s=o[i++];while(s!==void 0);else if(r.toArray!==void 0)do r=s[n],r!==void 0&&(e.push(s.time),r.toArray(t,t.length)),s=o[i++];while(s!==void 0);else do r=s[n],r!==void 0&&(e.push(s.time),t.push(r)),s=o[i++];while(s!==void 0)}d(tm,"flattenJSON");var Hi=class{static{d(this,"Interpolant")}constructor(e,t,n,i){this.parameterPositions=e,this._cachedIndex=0,this.resultBuffer=i!==void 0?i:new t.constructor(n),this.sampleValues=t,this.valueSize=n,this.settings=null,this.DefaultSettings_={}}evaluate(e){let t=this.parameterPositions,n=this._cachedIndex,i=t[n],s=t[n-1];e:{t:{let r;n:{i:if(!(e<i)){for(let a=n+2;;){if(i===void 0){if(e<s)break i;return n=t.length,this._cachedIndex=n,this.copySampleValue_(n-1)}if(n===a)break;if(s=i,i=t[++n],e<i)break t}r=t.length;break n}if(!(e>=s)){let a=t[1];e<a&&(n=2,s=a);for(let l=n-2;;){if(s===void 0)return this._cachedIndex=0,this.copySampleValue_(0);if(n===l)break;if(i=s,s=t[--n-1],e>=s)break t}r=n,n=0;break n}break e}for(;n<r;){let a=n+r>>>1;e<t[a]?r=a:n=a+1}if(i=t[n],s=t[n-1],s===void 0)return this._cachedIndex=0,this.copySampleValue_(0);if(i===void 0)return n=t.length,this._cachedIndex=n,this.copySampleValue_(n-1)}this._cachedIndex=n,this.intervalChanged_(n,s,i)}return this.interpolate_(n,s,e,i)}getSettings_(){return this.settings||this.DefaultSettings_}copySampleValue_(e){let t=this.resultBuffer,n=this.sampleValues,i=this.valueSize,s=e*i;for(let r=0;r!==i;++r)t[r]=n[s+r];return t}interpolate_(){throw new Error("call to abstract method")}intervalChanged_(){}},hu=class extends Hi{static{d(this,"CubicInterpolant")}constructor(e,t,n,i){super(e,t,n,i),this._weightPrev=-0,this._offsetPrev=-0,this._weightNext=-0,this._offsetNext=-0,this.DefaultSettings_={endingStart:Js,endingEnd:Js}}intervalChanged_(e,t,n){let i=this.parameterPositions,s=e-2,r=e+1,a=i[s],l=i[r];if(a===void 0)switch(this.getSettings_().endingStart){case js:s=e,a=2*t-n;break;case gl:s=i.length-2,a=t+i[s]-i[s+1];break;default:s=e,a=n}if(l===void 0)switch(this.getSettings_().endingEnd){case js:r=e,l=2*n-t;break;case gl:r=1,l=n+i[1]-i[0];break;default:r=e-1,l=t}let c=(n-t)*.5,h=this.valueSize;this._weightPrev=c/(t-a),this._weightNext=c/(l-n),this._offsetPrev=s*h,this._offsetNext=r*h}interpolate_(e,t,n,i){let s=this.resultBuffer,r=this.sampleValues,a=this.valueSize,l=e*a,c=l-a,h=this._offsetPrev,u=this._offsetNext,f=this._weightPrev,p=this._weightNext,g=(n-t)/(i-t),A=g*g,m=A*g,_=-f*m+2*f*A-f*g,E=(1+f)*m+(-1.5-2*f)*A+(-.5+f)*g+1,x=(-1-p)*m+(1.5+p)*A+.5*g,y=p*m-p*A;for(let w=0;w!==a;++w)s[w]=_*r[h+w]+E*r[c+w]+x*r[l+w]+y*r[u+w];return s}},Pl=class extends Hi{static{d(this,"LinearInterpolant")}constructor(e,t,n,i){super(e,t,n,i)}interpolate_(e,t,n,i){let s=this.resultBuffer,r=this.sampleValues,a=this.valueSize,l=e*a,c=l-a,h=(n-t)/(i-t),u=1-h;for(let f=0;f!==a;++f)s[f]=r[c+f]*u+r[l+f]*h;return s}},uu=class extends Hi{static{d(this,"DiscreteInterpolant")}constructor(e,t,n,i){super(e,t,n,i)}interpolate_(e){return this.copySampleValue_(e-1)}},Nn=class{static{d(this,"KeyframeTrack")}constructor(e,t,n,i){if(e===void 0)throw new Error("THREE.KeyframeTrack: track name is undefined");if(t===void 0||t.length===0)throw new Error("THREE.KeyframeTrack: no keyframes in track named "+e);this.name=e,this.times=hl(t,this.TimeBufferType),this.values=hl(n,this.ValueBufferType),this.setInterpolation(i||this.DefaultInterpolation)}static toJSON(e){let t=e.constructor,n;if(t.toJSON!==this.toJSON)n=t.toJSON(e);else{n={name:e.name,times:hl(e.times,Array),values:hl(e.values,Array)};let i=e.getInterpolation();i!==e.DefaultInterpolation&&(n.interpolation=i)}return n.type=e.ValueTypeName,n}InterpolantFactoryMethodDiscrete(e){return new uu(this.times,this.values,this.getValueSize(),e)}InterpolantFactoryMethodLinear(e){return new Pl(this.times,this.values,this.getValueSize(),e)}InterpolantFactoryMethodSmooth(e){return new hu(this.times,this.values,this.getValueSize(),e)}setInterpolation(e){let t;switch(e){case zi:t=this.InterpolantFactoryMethodDiscrete;break;case wi:t=this.InterpolantFactoryMethodLinear;break;case yh:t=this.InterpolantFactoryMethodSmooth;break}if(t===void 0){let n="unsupported interpolation for "+this.ValueTypeName+" keyframe track named "+this.name;if(this.createInterpolant===void 0)if(e!==this.DefaultInterpolation)this.setInterpolation(this.DefaultInterpolation);else throw new Error(n);return console.warn("THREE.KeyframeTrack:",n),this}return this.createInterpolant=t,this}getInterpolation(){switch(this.createInterpolant){case this.InterpolantFactoryMethodDiscrete:return zi;case this.InterpolantFactoryMethodLinear:return wi;case this.InterpolantFactoryMethodSmooth:return yh}}getValueSize(){return this.values.length/this.times.length}shift(e){if(e!==0){let t=this.times;for(let n=0,i=t.length;n!==i;++n)t[n]+=e}return this}scale(e){if(e!==1){let t=this.times;for(let n=0,i=t.length;n!==i;++n)t[n]*=e}return this}trim(e,t){let n=this.times,i=n.length,s=0,r=i-1;for(;s!==i&&n[s]<e;)++s;for(;r!==-1&&n[r]>t;)--r;if(++r,s!==0||r!==i){s>=r&&(r=Math.max(r,1),s=r-1);let a=this.getValueSize();this.times=Gi(n,s,r),this.values=Gi(this.values,s*a,r*a)}return this}validate(){let e=!0,t=this.getValueSize();t-Math.floor(t)!==0&&(console.error("THREE.KeyframeTrack: Invalid value size in track.",this),e=!1);let n=this.times,i=this.values,s=n.length;s===0&&(console.error("THREE.KeyframeTrack: Track is empty.",this),e=!1);let r=null;for(let a=0;a!==s;a++){let l=n[a];if(typeof l=="number"&&isNaN(l)){console.error("THREE.KeyframeTrack: Time is not a valid number.",this,a,l),e=!1;break}if(r!==null&&r>l){console.error("THREE.KeyframeTrack: Out of order keys.",this,a,l,r),e=!1;break}r=l}if(i!==void 0&&em(i))for(let a=0,l=i.length;a!==l;++a){let c=i[a];if(isNaN(c)){console.error("THREE.KeyframeTrack: Value is not a valid number.",this,a,c),e=!1;break}}return e}optimize(){let e=Gi(this.times),t=Gi(this.values),n=this.getValueSize(),i=this.getInterpolation()===yh,s=e.length-1,r=1;for(let a=1;a<s;++a){let l=!1,c=e[a],h=e[a+1];if(c!==h&&(a!==1||c!==e[0]))if(i)l=!0;else{let u=a*n,f=u-n,p=u+n;for(let g=0;g!==n;++g){let A=t[u+g];if(A!==t[f+g]||A!==t[p+g]){l=!0;break}}}if(l){if(a!==r){e[r]=e[a];let u=a*n,f=r*n;for(let p=0;p!==n;++p)t[f+p]=t[u+p]}++r}}if(s>0){e[r]=e[s];for(let a=s*n,l=r*n,c=0;c!==n;++c)t[l+c]=t[a+c];++r}return r!==e.length?(this.times=Gi(e,0,r),this.values=Gi(t,0,r*n)):(this.times=e,this.values=t),this}clone(){let e=Gi(this.times,0),t=Gi(this.values,0),n=this.constructor,i=new n(this.name,e,t);return i.createInterpolant=this.createInterpolant,i}};Nn.prototype.TimeBufferType=Float32Array;Nn.prototype.ValueBufferType=Float32Array;Nn.prototype.DefaultInterpolation=wi;var Wi=class extends Nn{static{d(this,"BooleanKeyframeTrack")}};Wi.prototype.ValueTypeName="bool";Wi.prototype.ValueBufferType=Array;Wi.prototype.DefaultInterpolation=zi;Wi.prototype.InterpolantFactoryMethodLinear=void 0;Wi.prototype.InterpolantFactoryMethodSmooth=void 0;var Fl=class extends Nn{static{d(this,"ColorKeyframeTrack")}};Fl.prototype.ValueTypeName="color";var qi=class extends Nn{static{d(this,"NumberKeyframeTrack")}};qi.prototype.ValueTypeName="number";var du=class extends Hi{static{d(this,"QuaternionLinearInterpolant")}constructor(e,t,n,i){super(e,t,n,i)}interpolate_(e,t,n,i){let s=this.resultBuffer,r=this.sampleValues,a=this.valueSize,l=(n-t)/(i-t),c=e*a;for(let h=c+a;c!==h;c+=4)Kt.slerpFlat(s,0,r,c-a,r,c,l);return s}},ai=class extends Nn{static{d(this,"QuaternionKeyframeTrack")}InterpolantFactoryMethodLinear(e){return new du(this.times,this.values,this.getValueSize(),e)}};ai.prototype.ValueTypeName="quaternion";ai.prototype.DefaultInterpolation=wi;ai.prototype.InterpolantFactoryMethodSmooth=void 0;var Ki=class extends Nn{static{d(this,"StringKeyframeTrack")}};Ki.prototype.ValueTypeName="string";Ki.prototype.ValueBufferType=Array;Ki.prototype.DefaultInterpolation=zi;Ki.prototype.InterpolantFactoryMethodLinear=void 0;Ki.prototype.InterpolantFactoryMethodSmooth=void 0;var $i=class extends Nn{static{d(this,"VectorKeyframeTrack")}};$i.prototype.ValueTypeName="vector";var fr=class{static{d(this,"AnimationClip")}constructor(e,t=-1,n,i=Su){this.name=e,this.tracks=n,this.duration=t,this.blendMode=i,this.uuid=Kn(),this.duration<0&&this.resetDuration()}static parse(e){let t=[],n=e.tracks,i=1/(e.fps||1);for(let r=0,a=n.length;r!==a;++r)t.push(YM(n[r]).scale(i));let s=new this(e.name,e.duration,t,e.blendMode);return s.uuid=e.uuid,s}static toJSON(e){let t=[],n=e.tracks,i={name:e.name,duration:e.duration,tracks:t,uuid:e.uuid,blendMode:e.blendMode};for(let s=0,r=n.length;s!==r;++s)t.push(Nn.toJSON(n[s]));return i}static CreateFromMorphTargetSequence(e,t,n,i){let s=t.length,r=[];for(let a=0;a<s;a++){let l=[],c=[];l.push((a+s-1)%s,a,(a+1)%s),c.push(0,1,0);let h=$M(l);l=DA(l,1,h),c=DA(c,1,h),!i&&l[0]===0&&(l.push(s),c.push(c[0])),r.push(new qi(".morphTargetInfluences["+t[a].name+"]",l,c).scale(1/n))}return new this(e,-1,r)}static findByName(e,t){let n=e;if(!Array.isArray(e)){let i=e;n=i.geometry&&i.geometry.animations||i.animations}for(let i=0;i<n.length;i++)if(n[i].name===t)return n[i];return null}static CreateClipsFromMorphTargetSequences(e,t,n){let i={},s=/^([\w-]*?)([\d]+)$/;for(let a=0,l=e.length;a<l;a++){let c=e[a],h=c.name.match(s);if(h&&h.length>1){let u=h[1],f=i[u];f||(i[u]=f=[]),f.push(c)}}let r=[];for(let a in i)r.push(this.CreateFromMorphTargetSequence(a,i[a],t,n));return r}static parseAnimation(e,t){if(!e)return console.error("THREE.AnimationClip: No animation in JSONLoader data."),null;let n=d(function(u,f,p,g,A){if(p.length!==0){let m=[],_=[];tm(p,m,_,g),m.length!==0&&A.push(new u(f,m,_))}},"addNonemptyTrack"),i=[],s=e.name||"default",r=e.fps||30,a=e.blendMode,l=e.length||-1,c=e.hierarchy||[];for(let u=0;u<c.length;u++){let f=c[u].keys;if(!(!f||f.length===0))if(f[0].morphTargets){let p={},g;for(g=0;g<f.length;g++)if(f[g].morphTargets)for(let A=0;A<f[g].morphTargets.length;A++)p[f[g].morphTargets[A]]=-1;for(let A in p){let m=[],_=[];for(let E=0;E!==f[g].morphTargets.length;++E){let x=f[g];m.push(x.time),_.push(x.morphTarget===A?1:0)}i.push(new qi(".morphTargetInfluence["+A+"]",m,_))}l=p.length*r}else{let p=".bones["+t[u].name+"]";n($i,p+".position",f,"pos",i),n(ai,p+".quaternion",f,"rot",i),n($i,p+".scale",f,"scl",i)}}return i.length===0?null:new this(s,l,i,a)}resetDuration(){let e=this.tracks,t=0;for(let n=0,i=e.length;n!==i;++n){let s=this.tracks[n];t=Math.max(t,s.times[s.times.length-1])}return this.duration=t,this}trim(){for(let e=0;e<this.tracks.length;e++)this.tracks[e].trim(0,this.duration);return this}validate(){let e=!0;for(let t=0;t<this.tracks.length;t++)e=e&&this.tracks[t].validate();return e}optimize(){for(let e=0;e<this.tracks.length;e++)this.tracks[e].optimize();return this}clone(){let e=[];for(let t=0;t<this.tracks.length;t++)e.push(this.tracks[t].clone());return new this.constructor(this.name,this.duration,e,this.blendMode)}toJSON(){return this.constructor.toJSON(this)}};function XM(o){switch(o.toLowerCase()){case"scalar":case"double":case"float":case"number":case"integer":return qi;case"vector":case"vector2":case"vector3":case"vector4":return $i;case"color":return Fl;case"quaternion":return ai;case"bool":case"boolean":return Wi;case"string":return Ki}throw new Error("THREE.KeyframeTrack: Unsupported typeName: "+o)}d(XM,"getTrackTypeForValueTypeName");function YM(o){if(o.type===void 0)throw new Error("THREE.KeyframeTrack: track type undefined, can not parse");let e=XM(o.type);if(o.times===void 0){let t=[],n=[];tm(o.keys,t,n,"value"),o.times=t,o.values=n}return e.parse!==void 0?e.parse(o):new e(o.name,o.times,o.values,o.interpolation)}d(YM,"parseKeyframeTrack");var pr={enabled:!1,files:{},add:d(function(o,e){this.enabled!==!1&&(this.files[o]=e)},"add"),get:d(function(o){if(this.enabled!==!1)return this.files[o]},"get"),remove:d(function(o){delete this.files[o]},"remove"),clear:d(function(){this.files={}},"clear")},fu=class{static{d(this,"LoadingManager")}constructor(e,t,n){let i=this,s=!1,r=0,a=0,l,c=[];this.onStart=void 0,this.onLoad=e,this.onProgress=t,this.onError=n,this.itemStart=function(h){a++,s===!1&&i.onStart!==void 0&&i.onStart(h,r,a),s=!0},this.itemEnd=function(h){r++,i.onProgress!==void 0&&i.onProgress(h,r,a),r===a&&(s=!1,i.onLoad!==void 0&&i.onLoad())},this.itemError=function(h){i.onError!==void 0&&i.onError(h)},this.resolveURL=function(h){return l?l(h):h},this.setURLModifier=function(h){return l=h,this},this.addHandler=function(h,u){return c.push(h,u),this},this.removeHandler=function(h){let u=c.indexOf(h);return u!==-1&&c.splice(u,2),this},this.getHandler=function(h){for(let u=0,f=c.length;u<f;u+=2){let p=c[u],g=c[u+1];if(p.global&&(p.lastIndex=0),p.test(h))return g}return null}}},JM=new fu,pn=class{static{d(this,"Loader")}constructor(e){this.manager=e!==void 0?e:JM,this.crossOrigin="anonymous",this.withCredentials=!1,this.path="",this.resourcePath="",this.requestHeader={}}load(){}loadAsync(e,t){let n=this;return new Promise(function(i,s){n.load(e,i,t,s)})}parse(){}setCrossOrigin(e){return this.crossOrigin=e,this}setWithCredentials(e){return this.withCredentials=e,this}setPath(e){return this.path=e,this}setResourcePath(e){return this.resourcePath=e,this}setRequestHeader(e){return this.requestHeader=e,this}},_i={},pu=class extends Error{static{d(this,"HttpError")}constructor(e,t){super(e),this.response=t}},An=class extends pn{static{d(this,"FileLoader")}constructor(e){super(e)}load(e,t,n,i){e===void 0&&(e=""),this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);let s=pr.get(e);if(s!==void 0)return this.manager.itemStart(e),setTimeout(()=>{t&&t(s),this.manager.itemEnd(e)},0),s;if(_i[e]!==void 0){_i[e].push({onLoad:t,onProgress:n,onError:i});return}_i[e]=[],_i[e].push({onLoad:t,onProgress:n,onError:i});let r=new Request(e,{headers:new Headers(this.requestHeader),credentials:this.withCredentials?"include":"same-origin"}),a=this.mimeType,l=this.responseType;fetch(r).then(c=>{if(c.status===200||c.status===0){if(c.status===0&&console.warn("THREE.FileLoader: HTTP Status 0 received."),typeof ReadableStream>"u"||c.body===void 0||c.body.getReader===void 0)return c;let h=_i[e],u=c.body.getReader(),f=c.headers.get("Content-Length")||c.headers.get("X-File-Size"),p=f?parseInt(f):0,g=p!==0,A=0,m=new ReadableStream({start(_){E();function E(){u.read().then(({done:x,value:y})=>{if(x)_.close();else{A+=y.byteLength;let w=new ProgressEvent("progress",{lengthComputable:g,loaded:A,total:p});for(let I=0,S=h.length;I<S;I++){let v=h[I];v.onProgress&&v.onProgress(w)}_.enqueue(y),E()}})}d(E,"readData")}});return new Response(m)}else throw new pu(`fetch for "${c.url}" responded with ${c.status}: ${c.statusText}`,c)}).then(c=>{switch(l){case"arraybuffer":return c.arrayBuffer();case"blob":return c.blob();case"document":return c.text().then(h=>new DOMParser().parseFromString(h,a));case"json":return c.json();default:if(a===void 0)return c.text();{let u=/charset="?([^;"\s]*)"?/i.exec(a),f=u&&u[1]?u[1].toLowerCase():void 0,p=new TextDecoder(f);return c.arrayBuffer().then(g=>p.decode(g))}}}).then(c=>{pr.add(e,c);let h=_i[e];delete _i[e];for(let u=0,f=h.length;u<f;u++){let p=h[u];p.onLoad&&p.onLoad(c)}}).catch(c=>{let h=_i[e];if(h===void 0)throw this.manager.itemError(e),c;delete _i[e];for(let u=0,f=h.length;u<f;u++){let p=h[u];p.onError&&p.onError(c)}this.manager.itemError(e)}).finally(()=>{this.manager.itemEnd(e)}),this.manager.itemStart(e)}setResponseType(e){return this.responseType=e,this}setMimeType(e){return this.mimeType=e,this}};var Au=class extends pn{static{d(this,"ImageLoader")}constructor(e){super(e)}load(e,t,n,i){this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);let s=this,r=pr.get(e);if(r!==void 0)return s.manager.itemStart(e),setTimeout(function(){t&&t(r),s.manager.itemEnd(e)},0),r;let a=Ro("img");function l(){h(),pr.add(e,this),t&&t(this),s.manager.itemEnd(e)}d(l,"onImageLoad");function c(u){h(),i&&i(u),s.manager.itemError(e),s.manager.itemEnd(e)}d(c,"onImageError");function h(){a.removeEventListener("load",l,!1),a.removeEventListener("error",c,!1)}return d(h,"removeEventListeners"),a.addEventListener("load",l,!1),a.addEventListener("error",c,!1),e.slice(0,5)!=="data:"&&this.crossOrigin!==void 0&&(a.crossOrigin=this.crossOrigin),s.manager.itemStart(e),a.src=e,a}};var Ol=class extends pn{static{d(this,"DataTextureLoader")}constructor(e){super(e)}load(e,t,n,i){let s=this,r=new ur,a=new An(this.manager);return a.setResponseType("arraybuffer"),a.setRequestHeader(this.requestHeader),a.setPath(this.path),a.setWithCredentials(s.withCredentials),a.load(e,function(l){let c=s.parse(l);c&&(c.image!==void 0?r.image=c.image:c.data!==void 0&&(r.image.width=c.width,r.image.height=c.height,r.image.data=c.data),r.wrapS=c.wrapS!==void 0?c.wrapS:Lt,r.wrapT=c.wrapT!==void 0?c.wrapT:Lt,r.magFilter=c.magFilter!==void 0?c.magFilter:Je,r.minFilter=c.minFilter!==void 0?c.minFilter:Je,r.anisotropy=c.anisotropy!==void 0?c.anisotropy:1,c.encoding!==void 0&&(r.encoding=c.encoding),c.flipY!==void 0&&(r.flipY=c.flipY),c.format!==void 0&&(r.format=c.format),c.type!==void 0&&(r.type=c.type),c.mipmaps!==void 0&&(r.mipmaps=c.mipmaps,r.minFilter=wn),c.mipmapCount===1&&(r.minFilter=Je),c.generateMipmaps!==void 0&&(r.generateMipmaps=c.generateMipmaps),r.needsUpdate=!0,t&&t(r,c))},n,i),r}},Ar=class extends pn{static{d(this,"TextureLoader")}constructor(e){super(e)}load(e,t,n,i){let s=new st,r=new Au(this.manager);return r.setCrossOrigin(this.crossOrigin),r.setPath(this.path),r.load(e,function(a){s.image=a,s.needsUpdate=!0,t!==void 0&&t(s)},n,i),s}},mr=class extends Ze{static{d(this,"Light")}constructor(e,t=1){super(),this.isLight=!0,this.type="Light",this.color=new Me(e),this.intensity=t}dispose(){}copy(e,t){return super.copy(e,t),this.color.copy(e.color),this.intensity=e.intensity,this}toJSON(e){let t=super.toJSON(e);return t.object.color=this.color.getHex(),t.object.intensity=this.intensity,this.groundColor!==void 0&&(t.object.groundColor=this.groundColor.getHex()),this.distance!==void 0&&(t.object.distance=this.distance),this.angle!==void 0&&(t.object.angle=this.angle),this.decay!==void 0&&(t.object.decay=this.decay),this.penumbra!==void 0&&(t.object.penumbra=this.penumbra),this.shadow!==void 0&&(t.object.shadow=this.shadow.toJSON()),t}};var Wh=new Ie,LA=new B,PA=new B,Ho=class{static{d(this,"LightShadow")}constructor(e){this.camera=e,this.bias=0,this.normalBias=0,this.radius=1,this.blurSamples=8,this.mapSize=new Be(512,512),this.map=null,this.mapPass=null,this.matrix=new Ie,this.autoUpdate=!0,this.needsUpdate=!1,this._frustum=new Po,this._frameExtents=new Be(1,1),this._viewportCount=1,this._viewports=[new nt(0,0,1,1)]}getViewportCount(){return this._viewportCount}getFrustum(){return this._frustum}updateMatrices(e){let t=this.camera,n=this.matrix;LA.setFromMatrixPosition(e.matrixWorld),t.position.copy(LA),PA.setFromMatrixPosition(e.target.matrixWorld),t.lookAt(PA),t.updateMatrixWorld(),Wh.multiplyMatrices(t.projectionMatrix,t.matrixWorldInverse),this._frustum.setFromProjectionMatrix(Wh),n.set(.5,0,0,.5,0,.5,0,.5,0,0,.5,.5,0,0,0,1),n.multiply(Wh)}getViewport(e){return this._viewports[e]}getFrameExtents(){return this._frameExtents}dispose(){this.map&&this.map.dispose(),this.mapPass&&this.mapPass.dispose()}copy(e){return this.camera=e.camera.clone(),this.bias=e.bias,this.radius=e.radius,this.mapSize.copy(e.mapSize),this}clone(){return new this.constructor().copy(this)}toJSON(){let e={};return this.bias!==0&&(e.bias=this.bias),this.normalBias!==0&&(e.normalBias=this.normalBias),this.radius!==1&&(e.radius=this.radius),(this.mapSize.x!==512||this.mapSize.y!==512)&&(e.mapSize=this.mapSize.toArray()),e.camera=this.camera.toJSON(!1).object,delete e.camera.matrix,e}},mu=class extends Ho{static{d(this,"SpotLightShadow")}constructor(){super(new ht(50,1,.5,500)),this.isSpotLightShadow=!0,this.focus=1}updateMatrices(e){let t=this.camera,n=Bo*2*e.angle*this.focus,i=this.mapSize.width/this.mapSize.height,s=e.distance||t.far;(n!==t.fov||i!==t.aspect||s!==t.far)&&(t.fov=n,t.aspect=i,t.far=s,t.updateProjectionMatrix()),super.updateMatrices(e)}copy(e){return super.copy(e),this.focus=e.focus,this}},Nl=class extends mr{static{d(this,"SpotLight")}constructor(e,t,n=0,i=Math.PI/3,s=0,r=2){super(e,t),this.isSpotLight=!0,this.type="SpotLight",this.position.copy(Ze.DEFAULT_UP),this.updateMatrix(),this.target=new Ze,this.distance=n,this.angle=i,this.penumbra=s,this.decay=r,this.map=null,this.shadow=new mu}get power(){return this.intensity*Math.PI}set power(e){this.intensity=e/Math.PI}dispose(){this.shadow.dispose()}copy(e,t){return super.copy(e,t),this.distance=e.distance,this.angle=e.angle,this.penumbra=e.penumbra,this.decay=e.decay,this.target=e.target.clone(),this.shadow=e.shadow.clone(),this}},FA=new Ie,yo=new B,qh=new B,gu=class extends Ho{static{d(this,"PointLightShadow")}constructor(){super(new ht(90,1,.5,500)),this.isPointLightShadow=!0,this._frameExtents=new Be(4,2),this._viewportCount=6,this._viewports=[new nt(2,1,1,1),new nt(0,1,1,1),new nt(3,1,1,1),new nt(1,1,1,1),new nt(3,0,1,1),new nt(1,0,1,1)],this._cubeDirections=[new B(1,0,0),new B(-1,0,0),new B(0,0,1),new B(0,0,-1),new B(0,1,0),new B(0,-1,0)],this._cubeUps=[new B(0,1,0),new B(0,1,0),new B(0,1,0),new B(0,1,0),new B(0,0,1),new B(0,0,-1)]}updateMatrices(e,t=0){let n=this.camera,i=this.matrix,s=e.distance||n.far;s!==n.far&&(n.far=s,n.updateProjectionMatrix()),yo.setFromMatrixPosition(e.matrixWorld),n.position.copy(yo),qh.copy(n.position),qh.add(this._cubeDirections[t]),n.up.copy(this._cubeUps[t]),n.lookAt(qh),n.updateMatrixWorld(),i.makeTranslation(-yo.x,-yo.y,-yo.z),FA.multiplyMatrices(n.projectionMatrix,n.matrixWorldInverse),this._frustum.setFromProjectionMatrix(FA)}},Xi=class extends mr{static{d(this,"PointLight")}constructor(e,t,n=0,i=2){super(e,t),this.isPointLight=!0,this.type="PointLight",this.distance=n,this.decay=i,this.shadow=new gu}get power(){return this.intensity*4*Math.PI}set power(e){this.intensity=e/(4*Math.PI)}dispose(){this.shadow.dispose()}copy(e,t){return super.copy(e,t),this.distance=e.distance,this.decay=e.decay,this.shadow=e.shadow.clone(),this}},_u=class extends Ho{static{d(this,"DirectionalLightShadow")}constructor(){super(new Fn(-5,5,5,-5,.5,500)),this.isDirectionalLightShadow=!0}},gr=class extends mr{static{d(this,"DirectionalLight")}constructor(e,t){super(e,t),this.isDirectionalLight=!0,this.type="DirectionalLight",this.position.copy(Ze.DEFAULT_UP),this.updateMatrix(),this.target=new Ze,this.shadow=new _u}dispose(){this.shadow.dispose()}copy(e){return super.copy(e),this.target=e.target.clone(),this.shadow=e.shadow.clone(),this}};var yu=class{static{d(this,"SphericalHarmonics3")}constructor(){this.isSphericalHarmonics3=!0,this.coefficients=[];for(let e=0;e<9;e++)this.coefficients.push(new B)}set(e){for(let t=0;t<9;t++)this.coefficients[t].copy(e[t]);return this}zero(){for(let e=0;e<9;e++)this.coefficients[e].set(0,0,0);return this}getAt(e,t){let n=e.x,i=e.y,s=e.z,r=this.coefficients;return t.copy(r[0]).multiplyScalar(.282095),t.addScaledVector(r[1],.488603*i),t.addScaledVector(r[2],.488603*s),t.addScaledVector(r[3],.488603*n),t.addScaledVector(r[4],1.092548*(n*i)),t.addScaledVector(r[5],1.092548*(i*s)),t.addScaledVector(r[6],.315392*(3*s*s-1)),t.addScaledVector(r[7],1.092548*(n*s)),t.addScaledVector(r[8],.546274*(n*n-i*i)),t}getIrradianceAt(e,t){let n=e.x,i=e.y,s=e.z,r=this.coefficients;return t.copy(r[0]).multiplyScalar(.886227),t.addScaledVector(r[1],2*.511664*i),t.addScaledVector(r[2],2*.511664*s),t.addScaledVector(r[3],2*.511664*n),t.addScaledVector(r[4],2*.429043*n*i),t.addScaledVector(r[5],2*.429043*i*s),t.addScaledVector(r[6],.743125*s*s-.247708),t.addScaledVector(r[7],2*.429043*n*s),t.addScaledVector(r[8],.429043*(n*n-i*i)),t}add(e){for(let t=0;t<9;t++)this.coefficients[t].add(e.coefficients[t]);return this}addScaledSH(e,t){for(let n=0;n<9;n++)this.coefficients[n].addScaledVector(e.coefficients[n],t);return this}scale(e){for(let t=0;t<9;t++)this.coefficients[t].multiplyScalar(e);return this}lerp(e,t){for(let n=0;n<9;n++)this.coefficients[n].lerp(e.coefficients[n],t);return this}equals(e){for(let t=0;t<9;t++)if(!this.coefficients[t].equals(e.coefficients[t]))return!1;return!0}copy(e){return this.set(e.coefficients)}clone(){return new this.constructor().copy(this)}fromArray(e,t=0){let n=this.coefficients;for(let i=0;i<9;i++)n[i].fromArray(e,t+i*3);return this}toArray(e=[],t=0){let n=this.coefficients;for(let i=0;i<9;i++)n[i].toArray(e,t+i*3);return e}static getBasisAt(e,t){let n=e.x,i=e.y,s=e.z;t[0]=.282095,t[1]=.488603*i,t[2]=.488603*s,t[3]=.488603*n,t[4]=1.092548*n*i,t[5]=1.092548*i*s,t[6]=.315392*(3*s*s-1),t[7]=1.092548*n*s,t[8]=.546274*(n*n-i*i)}},Ul=class extends mr{static{d(this,"LightProbe")}constructor(e=new yu,t=1){super(void 0,t),this.isLightProbe=!0,this.sh=e}copy(e){return super.copy(e),this.sh.copy(e.sh),this}fromJSON(e){return this.intensity=e.intensity,this.sh.fromArray(e.sh),this}toJSON(e){let t=super.toJSON(e);return t.object.sh=this.sh.toArray(),t}};var _r=class{static{d(this,"LoaderUtils")}static decodeText(e){if(typeof TextDecoder<"u")return new TextDecoder().decode(e);let t="";for(let n=0,i=e.length;n<i;n++)t+=String.fromCharCode(e[n]);try{return decodeURIComponent(escape(t))}catch{return t}}static extractUrlBase(e){let t=e.lastIndexOf("/");return t===-1?"./":e.slice(0,t+1)}static resolveURL(e,t){return typeof e!="string"||e===""?"":(/^https?:\/\//i.test(t)&&/^\//.test(e)&&(t=t.replace(/(^https?:\/\/[^\/]+).*/i,"$1")),/^(https?:)?\/\//i.test(e)||/^data:.*,.*$/i.test(e)||/^blob:.*$/i.test(e)?e:t+e)}};var Ql=class extends pn{static{d(this,"ImageBitmapLoader")}constructor(e){super(e),this.isImageBitmapLoader=!0,typeof createImageBitmap>"u"&&console.warn("THREE.ImageBitmapLoader: createImageBitmap() not supported."),typeof fetch>"u"&&console.warn("THREE.ImageBitmapLoader: fetch() not supported."),this.options={premultiplyAlpha:"none"}}setOptions(e){return this.options=e,this}load(e,t,n,i){e===void 0&&(e=""),this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);let s=this,r=pr.get(e);if(r!==void 0)return s.manager.itemStart(e),setTimeout(function(){t&&t(r),s.manager.itemEnd(e)},0),r;let a={};a.credentials=this.crossOrigin==="anonymous"?"same-origin":"include",a.headers=this.requestHeader,fetch(e,a).then(function(l){return l.blob()}).then(function(l){return createImageBitmap(l,Object.assign(s.options,{colorSpaceConversion:"none"}))}).then(function(l){pr.add(e,l),t&&t(l),s.manager.itemEnd(e)}).catch(function(l){i&&i(l),s.manager.itemError(e),s.manager.itemEnd(e)}),s.manager.itemStart(e)}};var xu=class{static{d(this,"PropertyMixer")}constructor(e,t,n){this.binding=e,this.valueSize=n;let i,s,r;switch(t){case"quaternion":i=this._slerp,s=this._slerpAdditive,r=this._setAdditiveIdentityQuaternion,this.buffer=new Float64Array(n*6),this._workIndex=5;break;case"string":case"bool":i=this._select,s=this._select,r=this._setAdditiveIdentityOther,this.buffer=new Array(n*5);break;default:i=this._lerp,s=this._lerpAdditive,r=this._setAdditiveIdentityNumeric,this.buffer=new Float64Array(n*5)}this._mixBufferRegion=i,this._mixBufferRegionAdditive=s,this._setIdentity=r,this._origIndex=3,this._addIndex=4,this.cumulativeWeight=0,this.cumulativeWeightAdditive=0,this.useCount=0,this.referenceCount=0}accumulate(e,t){let n=this.buffer,i=this.valueSize,s=e*i+i,r=this.cumulativeWeight;if(r===0){for(let a=0;a!==i;++a)n[s+a]=n[a];r=t}else{r+=t;let a=t/r;this._mixBufferRegion(n,s,0,a,i)}this.cumulativeWeight=r}accumulateAdditive(e){let t=this.buffer,n=this.valueSize,i=n*this._addIndex;this.cumulativeWeightAdditive===0&&this._setIdentity(),this._mixBufferRegionAdditive(t,i,0,e,n),this.cumulativeWeightAdditive+=e}apply(e){let t=this.valueSize,n=this.buffer,i=e*t+t,s=this.cumulativeWeight,r=this.cumulativeWeightAdditive,a=this.binding;if(this.cumulativeWeight=0,this.cumulativeWeightAdditive=0,s<1){let l=t*this._origIndex;this._mixBufferRegion(n,i,l,1-s,t)}r>0&&this._mixBufferRegionAdditive(n,i,this._addIndex*t,1,t);for(let l=t,c=t+t;l!==c;++l)if(n[l]!==n[l+t]){a.setValue(n,i);break}}saveOriginalState(){let e=this.binding,t=this.buffer,n=this.valueSize,i=n*this._origIndex;e.getValue(t,i);for(let s=n,r=i;s!==r;++s)t[s]=t[i+s%n];this._setIdentity(),this.cumulativeWeight=0,this.cumulativeWeightAdditive=0}restoreOriginalState(){let e=this.valueSize*3;this.binding.setValue(this.buffer,e)}_setAdditiveIdentityNumeric(){let e=this._addIndex*this.valueSize,t=e+this.valueSize;for(let n=e;n<t;n++)this.buffer[n]=0}_setAdditiveIdentityQuaternion(){this._setAdditiveIdentityNumeric(),this.buffer[this._addIndex*this.valueSize+3]=1}_setAdditiveIdentityOther(){let e=this._origIndex*this.valueSize,t=this._addIndex*this.valueSize;for(let n=0;n<this.valueSize;n++)this.buffer[t+n]=this.buffer[e+n]}_select(e,t,n,i,s){if(i>=.5)for(let r=0;r!==s;++r)e[t+r]=e[n+r]}_slerp(e,t,n,i){Kt.slerpFlat(e,t,e,t,e,n,i)}_slerpAdditive(e,t,n,i,s){let r=this._workIndex*s;Kt.multiplyQuaternionsFlat(e,r,e,t,e,n),Kt.slerpFlat(e,t,e,t,e,r,i)}_lerp(e,t,n,i,s){let r=1-i;for(let a=0;a!==s;++a){let l=t+a;e[l]=e[l]*r+e[n+a]*i}}_lerpAdditive(e,t,n,i,s){for(let r=0;r!==s;++r){let a=t+r;e[a]=e[a]+e[n+r]*i}}},Du="\\[\\]\\.:\\/",jM=new RegExp("["+Du+"]","g"),Lu="[^"+Du+"]",ZM="[^"+Du.replace("\\.","")+"]",eb=/((?:WC+[\/:])*)/.source.replace("WC",Lu),tb=/(WCOD+)?/.source.replace("WCOD",ZM),nb=/(?:\.(WC+)(?:\[(.+)\])?)?/.source.replace("WC",Lu),ib=/\.(WC+)(?:\[(.+)\])?/.source.replace("WC",Lu),sb=new RegExp("^"+eb+tb+nb+ib+"$"),rb=["material","materials","bones","map"],vu=class{static{d(this,"Composite")}constructor(e,t,n){let i=n||We.parseTrackName(t);this._targetGroup=e,this._bindings=e.subscribe_(t,i)}getValue(e,t){this.bind();let n=this._targetGroup.nCachedObjects_,i=this._bindings[n];i!==void 0&&i.getValue(e,t)}setValue(e,t){let n=this._bindings;for(let i=this._targetGroup.nCachedObjects_,s=n.length;i!==s;++i)n[i].setValue(e,t)}bind(){let e=this._bindings;for(let t=this._targetGroup.nCachedObjects_,n=e.length;t!==n;++t)e[t].bind()}unbind(){let e=this._bindings;for(let t=this._targetGroup.nCachedObjects_,n=e.length;t!==n;++t)e[t].unbind()}},We=class o{static{d(this,"PropertyBinding")}constructor(e,t,n){this.path=t,this.parsedPath=n||o.parseTrackName(t),this.node=o.findNode(e,this.parsedPath.nodeName)||e,this.rootNode=e,this.getValue=this._getValue_unbound,this.setValue=this._setValue_unbound}static create(e,t,n){return e&&e.isAnimationObjectGroup?new o.Composite(e,t,n):new o(e,t,n)}static sanitizeNodeName(e){return e.replace(/\s/g,"_").replace(jM,"")}static parseTrackName(e){let t=sb.exec(e);if(t===null)throw new Error("PropertyBinding: Cannot parse trackName: "+e);let n={nodeName:t[2],objectName:t[3],objectIndex:t[4],propertyName:t[5],propertyIndex:t[6]},i=n.nodeName&&n.nodeName.lastIndexOf(".");if(i!==void 0&&i!==-1){let s=n.nodeName.substring(i+1);rb.indexOf(s)!==-1&&(n.nodeName=n.nodeName.substring(0,i),n.objectName=s)}if(n.propertyName===null||n.propertyName.length===0)throw new Error("PropertyBinding: can not parse propertyName from trackName: "+e);return n}static findNode(e,t){if(t===void 0||t===""||t==="."||t===-1||t===e.name||t===e.uuid)return e;if(e.skeleton){let n=e.skeleton.getBoneByName(t);if(n!==void 0)return n}if(e.children){let n=d(function(s){for(let r=0;r<s.length;r++){let a=s[r];if(a.name===t||a.uuid===t)return a;let l=n(a.children);if(l)return l}return null},"searchNodeSubtree"),i=n(e.children);if(i)return i}return null}_getValue_unavailable(){}_setValue_unavailable(){}_getValue_direct(e,t){e[t]=this.targetObject[this.propertyName]}_getValue_array(e,t){let n=this.resolvedProperty;for(let i=0,s=n.length;i!==s;++i)e[t++]=n[i]}_getValue_arrayElement(e,t){e[t]=this.resolvedProperty[this.propertyIndex]}_getValue_toArray(e,t){this.resolvedProperty.toArray(e,t)}_setValue_direct(e,t){this.targetObject[this.propertyName]=e[t]}_setValue_direct_setNeedsUpdate(e,t){this.targetObject[this.propertyName]=e[t],this.targetObject.needsUpdate=!0}_setValue_direct_setMatrixWorldNeedsUpdate(e,t){this.targetObject[this.propertyName]=e[t],this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_array(e,t){let n=this.resolvedProperty;for(let i=0,s=n.length;i!==s;++i)n[i]=e[t++]}_setValue_array_setNeedsUpdate(e,t){let n=this.resolvedProperty;for(let i=0,s=n.length;i!==s;++i)n[i]=e[t++];this.targetObject.needsUpdate=!0}_setValue_array_setMatrixWorldNeedsUpdate(e,t){let n=this.resolvedProperty;for(let i=0,s=n.length;i!==s;++i)n[i]=e[t++];this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_arrayElement(e,t){this.resolvedProperty[this.propertyIndex]=e[t]}_setValue_arrayElement_setNeedsUpdate(e,t){this.resolvedProperty[this.propertyIndex]=e[t],this.targetObject.needsUpdate=!0}_setValue_arrayElement_setMatrixWorldNeedsUpdate(e,t){this.resolvedProperty[this.propertyIndex]=e[t],this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_fromArray(e,t){this.resolvedProperty.fromArray(e,t)}_setValue_fromArray_setNeedsUpdate(e,t){this.resolvedProperty.fromArray(e,t),this.targetObject.needsUpdate=!0}_setValue_fromArray_setMatrixWorldNeedsUpdate(e,t){this.resolvedProperty.fromArray(e,t),this.targetObject.matrixWorldNeedsUpdate=!0}_getValue_unbound(e,t){this.bind(),this.getValue(e,t)}_setValue_unbound(e,t){this.bind(),this.setValue(e,t)}bind(){let e=this.node,t=this.parsedPath,n=t.objectName,i=t.propertyName,s=t.propertyIndex;if(e||(e=o.findNode(this.rootNode,t.nodeName)||this.rootNode,this.node=e),this.getValue=this._getValue_unavailable,this.setValue=this._setValue_unavailable,!e){console.error("THREE.PropertyBinding: Trying to update node for track: "+this.path+" but it wasn't found.");return}if(n){let c=t.objectIndex;switch(n){case"materials":if(!e.material){console.error("THREE.PropertyBinding: Can not bind to material as node does not have a material.",this);return}if(!e.material.materials){console.error("THREE.PropertyBinding: Can not bind to material.materials as node.material does not have a materials array.",this);return}e=e.material.materials;break;case"bones":if(!e.skeleton){console.error("THREE.PropertyBinding: Can not bind to bones as node does not have a skeleton.",this);return}e=e.skeleton.bones;for(let h=0;h<e.length;h++)if(e[h].name===c){c=h;break}break;case"map":if("map"in e){e=e.map;break}if(!e.material){console.error("THREE.PropertyBinding: Can not bind to material as node does not have a material.",this);return}if(!e.material.map){console.error("THREE.PropertyBinding: Can not bind to material.map as node.material does not have a map.",this);return}e=e.material.map;break;default:if(e[n]===void 0){console.error("THREE.PropertyBinding: Can not bind to objectName of node undefined.",this);return}e=e[n]}if(c!==void 0){if(e[c]===void 0){console.error("THREE.PropertyBinding: Trying to bind to objectIndex of objectName, but is undefined.",this,e);return}e=e[c]}}let r=e[i];if(r===void 0){let c=t.nodeName;console.error("THREE.PropertyBinding: Trying to update property for track: "+c+"."+i+" but it wasn't found.",e);return}let a=this.Versioning.None;this.targetObject=e,e.needsUpdate!==void 0?a=this.Versioning.NeedsUpdate:e.matrixWorldNeedsUpdate!==void 0&&(a=this.Versioning.MatrixWorldNeedsUpdate);let l=this.BindingType.Direct;if(s!==void 0){if(i==="morphTargetInfluences"){if(!e.geometry){console.error("THREE.PropertyBinding: Can not bind to morphTargetInfluences because node does not have a geometry.",this);return}if(!e.geometry.morphAttributes){console.error("THREE.PropertyBinding: Can not bind to morphTargetInfluences because node does not have a geometry.morphAttributes.",this);return}e.morphTargetDictionary[s]!==void 0&&(s=e.morphTargetDictionary[s])}l=this.BindingType.ArrayElement,this.resolvedProperty=r,this.propertyIndex=s}else r.fromArray!==void 0&&r.toArray!==void 0?(l=this.BindingType.HasFromToArray,this.resolvedProperty=r):Array.isArray(r)?(l=this.BindingType.EntireArray,this.resolvedProperty=r):this.propertyName=i;this.getValue=this.GetterByBindingType[l],this.setValue=this.SetterByBindingTypeAndVersioning[l][a]}unbind(){this.node=null,this.getValue=this._getValue_unbound,this.setValue=this._setValue_unbound}};We.Composite=vu;We.prototype.BindingType={Direct:0,EntireArray:1,ArrayElement:2,HasFromToArray:3};We.prototype.Versioning={None:0,NeedsUpdate:1,MatrixWorldNeedsUpdate:2};We.prototype.GetterByBindingType=[We.prototype._getValue_direct,We.prototype._getValue_array,We.prototype._getValue_arrayElement,We.prototype._getValue_toArray];We.prototype.SetterByBindingTypeAndVersioning=[[We.prototype._setValue_direct,We.prototype._setValue_direct_setNeedsUpdate,We.prototype._setValue_direct_setMatrixWorldNeedsUpdate],[We.prototype._setValue_array,We.prototype._setValue_array_setNeedsUpdate,We.prototype._setValue_array_setMatrixWorldNeedsUpdate],[We.prototype._setValue_arrayElement,We.prototype._setValue_arrayElement_setNeedsUpdate,We.prototype._setValue_arrayElement_setMatrixWorldNeedsUpdate],[We.prototype._setValue_fromArray,We.prototype._setValue_fromArray_setNeedsUpdate,We.prototype._setValue_fromArray_setMatrixWorldNeedsUpdate]];var Eu=class{static{d(this,"AnimationAction")}constructor(e,t,n=null,i=t.blendMode){this._mixer=e,this._clip=t,this._localRoot=n,this.blendMode=i;let s=t.tracks,r=s.length,a=new Array(r),l={endingStart:Js,endingEnd:Js};for(let c=0;c!==r;++c){let h=s[c].createInterpolant(null);a[c]=h,h.settings=l}this._interpolantSettings=l,this._interpolants=a,this._propertyBindings=new Array(r),this._cacheIndex=null,this._byClipCacheIndex=null,this._timeScaleInterpolant=null,this._weightInterpolant=null,this.loop=qo,this._loopCount=-1,this._startTime=null,this.time=0,this.timeScale=1,this._effectiveTimeScale=1,this.weight=1,this._effectiveWeight=1,this.repetitions=1/0,this.paused=!1,this.enabled=!0,this.clampWhenFinished=!1,this.zeroSlopeAtStart=!0,this.zeroSlopeAtEnd=!0}play(){return this._mixer._activateAction(this),this}stop(){return this._mixer._deactivateAction(this),this.reset()}reset(){return this.paused=!1,this.enabled=!0,this.time=0,this._loopCount=-1,this._startTime=null,this.stopFading().stopWarping()}isRunning(){return this.enabled&&!this.paused&&this.timeScale!==0&&this._startTime===null&&this._mixer._isActiveAction(this)}isScheduled(){return this._mixer._isActiveAction(this)}startAt(e){return this._startTime=e,this}setLoop(e,t){return this.loop=e,this.repetitions=t,this}setEffectiveWeight(e){return this.weight=e,this._effectiveWeight=this.enabled?e:0,this.stopFading()}getEffectiveWeight(){return this._effectiveWeight}fadeIn(e){return this._scheduleFading(e,0,1)}fadeOut(e){return this._scheduleFading(e,1,0)}crossFadeFrom(e,t,n){if(e.fadeOut(t),this.fadeIn(t),n){let i=this._clip.duration,s=e._clip.duration,r=s/i,a=i/s;e.warp(1,r,t),this.warp(a,1,t)}return this}crossFadeTo(e,t,n){return e.crossFadeFrom(this,t,n)}stopFading(){let e=this._weightInterpolant;return e!==null&&(this._weightInterpolant=null,this._mixer._takeBackControlInterpolant(e)),this}setEffectiveTimeScale(e){return this.timeScale=e,this._effectiveTimeScale=this.paused?0:e,this.stopWarping()}getEffectiveTimeScale(){return this._effectiveTimeScale}setDuration(e){return this.timeScale=this._clip.duration/e,this.stopWarping()}syncWith(e){return this.time=e.time,this.timeScale=e.timeScale,this.stopWarping()}halt(e){return this.warp(this._effectiveTimeScale,0,e)}warp(e,t,n){let i=this._mixer,s=i.time,r=this.timeScale,a=this._timeScaleInterpolant;a===null&&(a=i._lendControlInterpolant(),this._timeScaleInterpolant=a);let l=a.parameterPositions,c=a.sampleValues;return l[0]=s,l[1]=s+n,c[0]=e/r,c[1]=t/r,this}stopWarping(){let e=this._timeScaleInterpolant;return e!==null&&(this._timeScaleInterpolant=null,this._mixer._takeBackControlInterpolant(e)),this}getMixer(){return this._mixer}getClip(){return this._clip}getRoot(){return this._localRoot||this._mixer._root}_update(e,t,n,i){if(!this.enabled){this._updateWeight(e);return}let s=this._startTime;if(s!==null){let l=(e-s)*n;l<0||n===0?t=0:(this._startTime=null,t=n*l)}t*=this._updateTimeScale(e);let r=this._updateTime(t),a=this._updateWeight(e);if(a>0){let l=this._interpolants,c=this._propertyBindings;switch(this.blendMode){case zy:for(let h=0,u=l.length;h!==u;++h)l[h].evaluate(r),c[h].accumulateAdditive(a);break;case Su:default:for(let h=0,u=l.length;h!==u;++h)l[h].evaluate(r),c[h].accumulate(i,a)}}}_updateWeight(e){let t=0;if(this.enabled){t=this.weight;let n=this._weightInterpolant;if(n!==null){let i=n.evaluate(e)[0];t*=i,e>n.parameterPositions[1]&&(this.stopFading(),i===0&&(this.enabled=!1))}}return this._effectiveWeight=t,t}_updateTimeScale(e){let t=0;if(!this.paused){t=this.timeScale;let n=this._timeScaleInterpolant;if(n!==null){let i=n.evaluate(e)[0];t*=i,e>n.parameterPositions[1]&&(this.stopWarping(),t===0?this.paused=!0:this.timeScale=t)}}return this._effectiveTimeScale=t,t}_updateTime(e){let t=this._clip.duration,n=this.loop,i=this.time+e,s=this._loopCount,r=n===Ko;if(e===0)return s===-1?i:r&&(s&1)===1?t-i:i;if(n===Cu){s===-1&&(this._loopCount=0,this._setEndings(!0,!0,!1));e:{if(i>=t)i=t;else if(i<0)i=0;else{this.time=i;break e}this.clampWhenFinished?this.paused=!0:this.enabled=!1,this.time=i,this._mixer.dispatchEvent({type:"finished",action:this,direction:e<0?-1:1})}}else{if(s===-1&&(e>=0?(s=0,this._setEndings(!0,this.repetitions===0,r)):this._setEndings(this.repetitions===0,!0,r)),i>=t||i<0){let a=Math.floor(i/t);i-=t*a,s+=Math.abs(a);let l=this.repetitions-s;if(l<=0)this.clampWhenFinished?this.paused=!0:this.enabled=!1,i=e>0?t:0,this.time=i,this._mixer.dispatchEvent({type:"finished",action:this,direction:e>0?1:-1});else{if(l===1){let c=e<0;this._setEndings(c,!c,r)}else this._setEndings(!1,!1,r);this._loopCount=s,this.time=i,this._mixer.dispatchEvent({type:"loop",action:this,loopDelta:a})}}else this.time=i;if(r&&(s&1)===1)return t-i}return i}_setEndings(e,t,n){let i=this._interpolantSettings;n?(i.endingStart=js,i.endingEnd=js):(e?i.endingStart=this.zeroSlopeAtStart?js:Js:i.endingStart=gl,t?i.endingEnd=this.zeroSlopeAtEnd?js:Js:i.endingEnd=gl)}_scheduleFading(e,t,n){let i=this._mixer,s=i.time,r=this._weightInterpolant;r===null&&(r=i._lendControlInterpolant(),this._weightInterpolant=r);let a=r.parameterPositions,l=r.sampleValues;return a[0]=s,l[0]=t,a[1]=s+e,l[1]=n,this}},ob=new Float32Array(1),kl=class extends Mt{static{d(this,"AnimationMixer")}constructor(e){super(),this._root=e,this._initMemoryManager(),this._accuIndex=0,this.time=0,this.timeScale=1}_bindAction(e,t){let n=e._localRoot||this._root,i=e._clip.tracks,s=i.length,r=e._propertyBindings,a=e._interpolants,l=n.uuid,c=this._bindingsByRootAndName,h=c[l];h===void 0&&(h={},c[l]=h);for(let u=0;u!==s;++u){let f=i[u],p=f.name,g=h[p];if(g!==void 0)++g.referenceCount,r[u]=g;else{if(g=r[u],g!==void 0){g._cacheIndex===null&&(++g.referenceCount,this._addInactiveBinding(g,l,p));continue}let A=t&&t._propertyBindings[u].binding.parsedPath;g=new xu(We.create(n,p,A),f.ValueTypeName,f.getValueSize()),++g.referenceCount,this._addInactiveBinding(g,l,p),r[u]=g}a[u].resultBuffer=g.buffer}}_activateAction(e){if(!this._isActiveAction(e)){if(e._cacheIndex===null){let n=(e._localRoot||this._root).uuid,i=e._clip.uuid,s=this._actionsByClip[i];this._bindAction(e,s&&s.knownActions[0]),this._addInactiveAction(e,i,n)}let t=e._propertyBindings;for(let n=0,i=t.length;n!==i;++n){let s=t[n];s.useCount++===0&&(this._lendBinding(s),s.saveOriginalState())}this._lendAction(e)}}_deactivateAction(e){if(this._isActiveAction(e)){let t=e._propertyBindings;for(let n=0,i=t.length;n!==i;++n){let s=t[n];--s.useCount===0&&(s.restoreOriginalState(),this._takeBackBinding(s))}this._takeBackAction(e)}}_initMemoryManager(){this._actions=[],this._nActiveActions=0,this._actionsByClip={},this._bindings=[],this._nActiveBindings=0,this._bindingsByRootAndName={},this._controlInterpolants=[],this._nActiveControlInterpolants=0;let e=this;this.stats={actions:{get total(){return e._actions.length},get inUse(){return e._nActiveActions}},bindings:{get total(){return e._bindings.length},get inUse(){return e._nActiveBindings}},controlInterpolants:{get total(){return e._controlInterpolants.length},get inUse(){return e._nActiveControlInterpolants}}}}_isActiveAction(e){let t=e._cacheIndex;return t!==null&&t<this._nActiveActions}_addInactiveAction(e,t,n){let i=this._actions,s=this._actionsByClip,r=s[t];if(r===void 0)r={knownActions:[e],actionByRoot:{}},e._byClipCacheIndex=0,s[t]=r;else{let a=r.knownActions;e._byClipCacheIndex=a.length,a.push(e)}e._cacheIndex=i.length,i.push(e),r.actionByRoot[n]=e}_removeInactiveAction(e){let t=this._actions,n=t[t.length-1],i=e._cacheIndex;n._cacheIndex=i,t[i]=n,t.pop(),e._cacheIndex=null;let s=e._clip.uuid,r=this._actionsByClip,a=r[s],l=a.knownActions,c=l[l.length-1],h=e._byClipCacheIndex;c._byClipCacheIndex=h,l[h]=c,l.pop(),e._byClipCacheIndex=null;let u=a.actionByRoot,f=(e._localRoot||this._root).uuid;delete u[f],l.length===0&&delete r[s],this._removeInactiveBindingsForAction(e)}_removeInactiveBindingsForAction(e){let t=e._propertyBindings;for(let n=0,i=t.length;n!==i;++n){let s=t[n];--s.referenceCount===0&&this._removeInactiveBinding(s)}}_lendAction(e){let t=this._actions,n=e._cacheIndex,i=this._nActiveActions++,s=t[i];e._cacheIndex=i,t[i]=e,s._cacheIndex=n,t[n]=s}_takeBackAction(e){let t=this._actions,n=e._cacheIndex,i=--this._nActiveActions,s=t[i];e._cacheIndex=i,t[i]=e,s._cacheIndex=n,t[n]=s}_addInactiveBinding(e,t,n){let i=this._bindingsByRootAndName,s=this._bindings,r=i[t];r===void 0&&(r={},i[t]=r),r[n]=e,e._cacheIndex=s.length,s.push(e)}_removeInactiveBinding(e){let t=this._bindings,n=e.binding,i=n.rootNode.uuid,s=n.path,r=this._bindingsByRootAndName,a=r[i],l=t[t.length-1],c=e._cacheIndex;l._cacheIndex=c,t[c]=l,t.pop(),delete a[s],Object.keys(a).length===0&&delete r[i]}_lendBinding(e){let t=this._bindings,n=e._cacheIndex,i=this._nActiveBindings++,s=t[i];e._cacheIndex=i,t[i]=e,s._cacheIndex=n,t[n]=s}_takeBackBinding(e){let t=this._bindings,n=e._cacheIndex,i=--this._nActiveBindings,s=t[i];e._cacheIndex=i,t[i]=e,s._cacheIndex=n,t[n]=s}_lendControlInterpolant(){let e=this._controlInterpolants,t=this._nActiveControlInterpolants++,n=e[t];return n===void 0&&(n=new Pl(new Float32Array(2),new Float32Array(2),1,ob),n.__cacheIndex=t,e[t]=n),n}_takeBackControlInterpolant(e){let t=this._controlInterpolants,n=e.__cacheIndex,i=--this._nActiveControlInterpolants,s=t[i];e.__cacheIndex=i,t[i]=e,s.__cacheIndex=n,t[n]=s}clipAction(e,t,n){let i=t||this._root,s=i.uuid,r=typeof e=="string"?fr.findByName(i,e):e,a=r!==null?r.uuid:e,l=this._actionsByClip[a],c=null;if(n===void 0&&(r!==null?n=r.blendMode:n=Su),l!==void 0){let u=l.actionByRoot[s];if(u!==void 0&&u.blendMode===n)return u;c=l.knownActions[0],r===null&&(r=c._clip)}if(r===null)return null;let h=new Eu(this,r,t,n);return this._bindAction(h,c),this._addInactiveAction(h,a,s),h}existingAction(e,t){let n=t||this._root,i=n.uuid,s=typeof e=="string"?fr.findByName(n,e):e,r=s?s.uuid:e,a=this._actionsByClip[r];return a!==void 0&&a.actionByRoot[i]||null}stopAllAction(){let e=this._actions,t=this._nActiveActions;for(let n=t-1;n>=0;--n)e[n].stop();return this}update(e){e*=this.timeScale;let t=this._actions,n=this._nActiveActions,i=this.time+=e,s=Math.sign(e),r=this._accuIndex^=1;for(let c=0;c!==n;++c)t[c]._update(i,e,s,r);let a=this._bindings,l=this._nActiveBindings;for(let c=0;c!==l;++c)a[c].apply(r);return this}setTime(e){this.time=0;for(let t=0;t<this._actions.length;t++)this._actions[t].time=0;return this.update(e)}getRoot(){return this._root}uncacheClip(e){let t=this._actions,n=e.uuid,i=this._actionsByClip,s=i[n];if(s!==void 0){let r=s.knownActions;for(let a=0,l=r.length;a!==l;++a){let c=r[a];this._deactivateAction(c);let h=c._cacheIndex,u=t[t.length-1];c._cacheIndex=null,c._byClipCacheIndex=null,u._cacheIndex=h,t[h]=u,t.pop(),this._removeInactiveBindingsForAction(c)}delete i[n]}}uncacheRoot(e){let t=e.uuid,n=this._actionsByClip;for(let r in n){let a=n[r].actionByRoot,l=a[t];l!==void 0&&(this._deactivateAction(l),this._removeInactiveAction(l))}let i=this._bindingsByRootAndName,s=i[t];if(s!==void 0)for(let r in s){let a=s[r];a.restoreOriginalState(),this._removeInactiveBinding(a)}}uncacheAction(e,t){let n=this.existingAction(e,t);n!==null&&(this._deactivateAction(n),this._removeInactiveAction(n))}};var Gl=class{static{d(this,"Raycaster")}constructor(e,t,n=0,i=1/0){this.ray=new lr(e,t),this.near=n,this.far=i,this.camera=null,this.layers=new Lo,this.params={Mesh:{},Line:{threshold:1},LOD:{},Points:{threshold:1},Sprite:{}}}set(e,t){this.ray.set(e,t)}setFromCamera(e,t){t.isPerspectiveCamera?(this.ray.origin.setFromMatrixPosition(t.matrixWorld),this.ray.direction.set(e.x,e.y,.5).unproject(t).sub(this.ray.origin).normalize(),this.camera=t):t.isOrthographicCamera?(this.ray.origin.set(e.x,e.y,(t.near+t.far)/(t.near-t.far)).unproject(t),this.ray.direction.set(0,0,-1).transformDirection(t.matrixWorld),this.camera=t):console.error("THREE.Raycaster: Unsupported camera type: "+t.type)}intersectObject(e,t=!0,n=[]){return wu(e,this,n,t),n.sort(OA),n}intersectObjects(e,t=!0,n=[]){for(let i=0,s=e.length;i<s;i++)wu(e[i],this,n,t);return n.sort(OA),n}};function OA(o,e){return o.distance-e.distance}d(OA,"ascSort");function wu(o,e,t,n){if(o.layers.test(e.layers)&&o.raycast(e,t),n===!0){let i=o.children;for(let s=0,r=i.length;s<r;s++)wu(i[s],e,t,!0)}}d(wu,"intersectObject");var Yi=class{static{d(this,"Spherical")}constructor(e=1,t=0,n=0){return this.radius=e,this.phi=t,this.theta=n,this}set(e,t,n){return this.radius=e,this.phi=t,this.theta=n,this}copy(e){return this.radius=e.radius,this.phi=e.phi,this.theta=e.theta,this}makeSafe(){return this.phi=Math.max(1e-6,Math.min(Math.PI-1e-6,this.phi)),this}setFromVector3(e){return this.setFromCartesianCoords(e.x,e.y,e.z)}setFromCartesianCoords(e,t,n){return this.radius=Math.sqrt(e*e+t*t+n*n),this.radius===0?(this.theta=0,this.phi=0):(this.theta=Math.atan2(e,n),this.phi=Math.acos(Nt(t/this.radius,-1,1))),this}clone(){return new this.constructor().copy(this)}};var xi=ab();function ab(){let o=new ArrayBuffer(4),e=new Float32Array(o),t=new Uint32Array(o),n=new Uint32Array(512),i=new Uint32Array(512);for(let l=0;l<256;++l){let c=l-127;c<-27?(n[l]=0,n[l|256]=32768,i[l]=24,i[l|256]=24):c<-14?(n[l]=1024>>-c-14,n[l|256]=1024>>-c-14|32768,i[l]=-c-1,i[l|256]=-c-1):c<=15?(n[l]=c+15<<10,n[l|256]=c+15<<10|32768,i[l]=13,i[l|256]=13):c<128?(n[l]=31744,n[l|256]=64512,i[l]=24,i[l|256]=24):(n[l]=31744,n[l|256]=64512,i[l]=13,i[l|256]=13)}let s=new Uint32Array(2048),r=new Uint32Array(64),a=new Uint32Array(64);for(let l=1;l<1024;++l){let c=l<<13,h=0;for(;!(c&8388608);)c<<=1,h-=8388608;c&=-8388609,h+=947912704,s[l]=c|h}for(let l=1024;l<2048;++l)s[l]=939524096+(l-1024<<13);for(let l=1;l<31;++l)r[l]=l<<23;r[31]=1199570944,r[32]=2147483648;for(let l=33;l<63;++l)r[l]=2147483648+(l-32<<23);r[63]=3347054592;for(let l=1;l<64;++l)l!==32&&(a[l]=1024);return{floatView:e,uint32View:t,baseTable:n,shiftTable:i,mantissaTable:s,exponentTable:r,offsetTable:a}}d(ab,"_generateTables");function lb(o){Math.abs(o)>65504&&console.warn("THREE.DataUtils.toHalfFloat(): Value out of range."),o=Nt(o,-65504,65504),xi.floatView[0]=o;let e=xi.uint32View[0],t=e>>23&511;return xi.baseTable[t]+((e&8388607)>>xi.shiftTable[t])}d(lb,"toHalfFloat");function cb(o){let e=o>>10;return xi.uint32View[0]=xi.mantissaTable[xi.offsetTable[e]+(o&1023)]+xi.exponentTable[e],xi.floatView[0]}d(cb,"fromHalfFloat");var Xo=Object.freeze({__proto__:null,fromHalfFloat:cb,toHalfFloat:lb});typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("register",{detail:{revision:Mu}}));typeof self<"u"&&(self.__THREE__?console.warn("WARNING: Multiple instances of Three.js being imported."):self.__THREE__=Mu);L();P();L();P();L();P();L();P();var Wl=self,Kl=Wl.ShadowRoot&&(Wl.ShadyCSS===void 0||Wl.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,im=Symbol(),nm=new WeakMap,ql=class{static{d(this,"o")}constructor(e,t,n){if(this._$cssResult$=!0,n!==im)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o,t=this.t;if(Kl&&e===void 0){let n=t!==void 0&&t.length===1;n&&(e=nm.get(t)),e===void 0&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),n&&nm.set(t,e))}return e}toString(){return this.cssText}},sm=d(o=>new ql(typeof o=="string"?o:o+"",void 0,im),"r");var Pu=d((o,e)=>{Kl?o.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet):e.forEach(t=>{let n=document.createElement("style"),i=Wl.litNonce;i!==void 0&&n.setAttribute("nonce",i),n.textContent=t.cssText,o.appendChild(n)})},"S"),$l=Kl?o=>o:o=>o instanceof CSSStyleSheet?(e=>{let t="";for(let n of e.cssRules)t+=n.cssText;return sm(t)})(o):o;var Fu,Xl=self,rm=Xl.trustedTypes,hb=rm?rm.emptyScript:"",om=Xl.reactiveElementPolyfillSupport,Nu={toAttribute(o,e){switch(e){case Boolean:o=o?hb:null;break;case Object:case Array:o=o==null?o:JSON.stringify(o)}return o},fromAttribute(o,e){let t=o;switch(e){case Boolean:t=o!==null;break;case Number:t=o===null?null:Number(o);break;case Object:case Array:try{t=JSON.parse(o)}catch{t=null}}return t}},am=d((o,e)=>e!==o&&(e==e||o==o),"a"),Ou={attribute:!0,type:String,converter:Nu,reflect:!1,hasChanged:am},Yn=class extends HTMLElement{static{d(this,"d")}constructor(){super(),this._$Ei=new Map,this.isUpdatePending=!1,this.hasUpdated=!1,this._$El=null,this.u()}static addInitializer(e){var t;this.finalize(),((t=this.h)!==null&&t!==void 0?t:this.h=[]).push(e)}static get observedAttributes(){this.finalize();let e=[];return this.elementProperties.forEach((t,n)=>{let i=this._$Ep(n,t);i!==void 0&&(this._$Ev.set(i,n),e.push(i))}),e}static createProperty(e,t=Ou){if(t.state&&(t.attribute=!1),this.finalize(),this.elementProperties.set(e,t),!t.noAccessor&&!this.prototype.hasOwnProperty(e)){let n=typeof e=="symbol"?Symbol():"__"+e,i=this.getPropertyDescriptor(e,n,t);i!==void 0&&Object.defineProperty(this.prototype,e,i)}}static getPropertyDescriptor(e,t,n){return{get(){return this[t]},set(i){let s=this[e];this[t]=i,this.requestUpdate(e,s,n)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)||Ou}static finalize(){if(this.hasOwnProperty("finalized"))return!1;this.finalized=!0;let e=Object.getPrototypeOf(this);if(e.finalize(),e.h!==void 0&&(this.h=[...e.h]),this.elementProperties=new Map(e.elementProperties),this._$Ev=new Map,this.hasOwnProperty("properties")){let t=this.properties,n=[...Object.getOwnPropertyNames(t),...Object.getOwnPropertySymbols(t)];for(let i of n)this.createProperty(i,t[i])}return this.elementStyles=this.finalizeStyles(this.styles),!0}static finalizeStyles(e){let t=[];if(Array.isArray(e)){let n=new Set(e.flat(1/0).reverse());for(let i of n)t.unshift($l(i))}else e!==void 0&&t.push($l(e));return t}static _$Ep(e,t){let n=t.attribute;return n===!1?void 0:typeof n=="string"?n:typeof e=="string"?e.toLowerCase():void 0}u(){var e;this._$E_=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$Eg(),this.requestUpdate(),(e=this.constructor.h)===null||e===void 0||e.forEach(t=>t(this))}addController(e){var t,n;((t=this._$ES)!==null&&t!==void 0?t:this._$ES=[]).push(e),this.renderRoot!==void 0&&this.isConnected&&((n=e.hostConnected)===null||n===void 0||n.call(e))}removeController(e){var t;(t=this._$ES)===null||t===void 0||t.splice(this._$ES.indexOf(e)>>>0,1)}_$Eg(){this.constructor.elementProperties.forEach((e,t)=>{this.hasOwnProperty(t)&&(this._$Ei.set(t,this[t]),delete this[t])})}createRenderRoot(){var e;let t=(e=this.shadowRoot)!==null&&e!==void 0?e:this.attachShadow(this.constructor.shadowRootOptions);return Pu(t,this.constructor.elementStyles),t}connectedCallback(){var e;this.renderRoot===void 0&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),(e=this._$ES)===null||e===void 0||e.forEach(t=>{var n;return(n=t.hostConnected)===null||n===void 0?void 0:n.call(t)})}enableUpdating(e){}disconnectedCallback(){var e;(e=this._$ES)===null||e===void 0||e.forEach(t=>{var n;return(n=t.hostDisconnected)===null||n===void 0?void 0:n.call(t)})}attributeChangedCallback(e,t,n){this._$AK(e,n)}_$EO(e,t,n=Ou){var i;let s=this.constructor._$Ep(e,n);if(s!==void 0&&n.reflect===!0){let r=(((i=n.converter)===null||i===void 0?void 0:i.toAttribute)!==void 0?n.converter:Nu).toAttribute(t,n.type);this._$El=e,r==null?this.removeAttribute(s):this.setAttribute(s,r),this._$El=null}}_$AK(e,t){var n;let i=this.constructor,s=i._$Ev.get(e);if(s!==void 0&&this._$El!==s){let r=i.getPropertyOptions(s),a=typeof r.converter=="function"?{fromAttribute:r.converter}:((n=r.converter)===null||n===void 0?void 0:n.fromAttribute)!==void 0?r.converter:Nu;this._$El=s,this[s]=a.fromAttribute(t,r.type),this._$El=null}}requestUpdate(e,t,n){let i=!0;e!==void 0&&(((n=n||this.constructor.getPropertyOptions(e)).hasChanged||am)(this[e],t)?(this._$AL.has(e)||this._$AL.set(e,t),n.reflect===!0&&this._$El!==e&&(this._$EC===void 0&&(this._$EC=new Map),this._$EC.set(e,n))):i=!1),!this.isUpdatePending&&i&&(this._$E_=this._$Ej())}async _$Ej(){this.isUpdatePending=!0;try{await this._$E_}catch(t){Promise.reject(t)}let e=this.scheduleUpdate();return e!=null&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){var e;if(!this.isUpdatePending)return;this.hasUpdated,this._$Ei&&(this._$Ei.forEach((i,s)=>this[s]=i),this._$Ei=void 0);let t=!1,n=this._$AL;try{t=this.shouldUpdate(n),t?(this.willUpdate(n),(e=this._$ES)===null||e===void 0||e.forEach(i=>{var s;return(s=i.hostUpdate)===null||s===void 0?void 0:s.call(i)}),this.update(n)):this._$Ek()}catch(i){throw t=!1,this._$Ek(),i}t&&this._$AE(n)}willUpdate(e){}_$AE(e){var t;(t=this._$ES)===null||t===void 0||t.forEach(n=>{var i;return(i=n.hostUpdated)===null||i===void 0?void 0:i.call(n)}),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$Ek(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$E_}shouldUpdate(e){return!0}update(e){this._$EC!==void 0&&(this._$EC.forEach((t,n)=>this._$EO(n,this[n],t)),this._$EC=void 0),this._$Ek()}updated(e){}firstUpdated(e){}};Yn.finalized=!0,Yn.elementProperties=new Map,Yn.elementStyles=[],Yn.shadowRootOptions={mode:"open"},om?.({ReactiveElement:Yn}),((Fu=Xl.reactiveElementVersions)!==null&&Fu!==void 0?Fu:Xl.reactiveElementVersions=[]).push("1.6.1");L();P();var Uu,Yl=self,Mr=Yl.trustedTypes,lm=Mr?Mr.createPolicy("lit-html",{createHTML:d(o=>o,"createHTML")}):void 0,Ji=`lit$${(Math.random()+"").slice(9)}$`,Am="?"+Ji,ub=`<${Am}>`,br=document,Jo=d((o="")=>br.createComment(o),"r"),jo=d(o=>o===null||typeof o!="object"&&typeof o!="function","d"),mm=Array.isArray,db=d(o=>mm(o)||typeof o?.[Symbol.iterator]=="function","c"),Yo=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,cm=/-->/g,hm=/>/g,ws=RegExp(`>|[ 	
\f\r](?:([^\\s"'>=/]+)([ 	
\f\r]*=[ 	
\f\r]*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),um=/'/g,dm=/"/g,gm=/^(?:script|style|textarea|title)$/i,_m=d(o=>(e,...t)=>({_$litType$:o,strings:e,values:t}),"g"),ji=_m(1),x1=_m(2),Ms=Symbol.for("lit-noChange"),Ot=Symbol.for("lit-nothing"),fm=new WeakMap,wr=br.createTreeWalker(br,129,null,!1),fb=d((o,e)=>{let t=o.length-1,n=[],i,s=e===2?"<svg>":"",r=Yo;for(let l=0;l<t;l++){let c=o[l],h,u,f=-1,p=0;for(;p<c.length&&(r.lastIndex=p,u=r.exec(c),u!==null);)p=r.lastIndex,r===Yo?u[1]==="!--"?r=cm:u[1]!==void 0?r=hm:u[2]!==void 0?(gm.test(u[2])&&(i=RegExp("</"+u[2],"g")),r=ws):u[3]!==void 0&&(r=ws):r===ws?u[0]===">"?(r=i??Yo,f=-1):u[1]===void 0?f=-2:(f=r.lastIndex-u[2].length,h=u[1],r=u[3]===void 0?ws:u[3]==='"'?dm:um):r===dm||r===um?r=ws:r===cm||r===hm?r=Yo:(r=ws,i=void 0);let g=r===ws&&o[l+1].startsWith("/>")?" ":"";s+=r===Yo?c+ub:f>=0?(n.push(h),c.slice(0,f)+"$lit$"+c.slice(f)+Ji+g):c+Ji+(f===-2?(n.push(void 0),l):g)}let a=s+(o[t]||"<?>")+(e===2?"</svg>":"");if(!Array.isArray(o)||!o.hasOwnProperty("raw"))throw Error("invalid template strings array");return[lm!==void 0?lm.createHTML(a):a,n]},"E"),Zo=class o{static{d(this,"C")}constructor({strings:e,_$litType$:t},n){let i;this.parts=[];let s=0,r=0,a=e.length-1,l=this.parts,[c,h]=fb(e,t);if(this.el=o.createElement(c,n),wr.currentNode=this.el.content,t===2){let u=this.el.content,f=u.firstChild;f.remove(),u.append(...f.childNodes)}for(;(i=wr.nextNode())!==null&&l.length<a;){if(i.nodeType===1){if(i.hasAttributes()){let u=[];for(let f of i.getAttributeNames())if(f.endsWith("$lit$")||f.startsWith(Ji)){let p=h[r++];if(u.push(f),p!==void 0){let g=i.getAttribute(p.toLowerCase()+"$lit$").split(Ji),A=/([.?@])?(.*)/.exec(p);l.push({type:1,index:s,name:A[2],strings:g,ctor:A[1]==="."?ku:A[1]==="?"?Gu:A[1]==="@"?zu:Cr})}else l.push({type:6,index:s})}for(let f of u)i.removeAttribute(f)}if(gm.test(i.tagName)){let u=i.textContent.split(Ji),f=u.length-1;if(f>0){i.textContent=Mr?Mr.emptyScript:"";for(let p=0;p<f;p++)i.append(u[p],Jo()),wr.nextNode(),l.push({type:2,index:++s});i.append(u[f],Jo())}}}else if(i.nodeType===8)if(i.data===Am)l.push({type:2,index:s});else{let u=-1;for(;(u=i.data.indexOf(Ji,u+1))!==-1;)l.push({type:7,index:s}),u+=Ji.length-1}s++}}static createElement(e,t){let n=br.createElement("template");return n.innerHTML=e,n}};function Ir(o,e,t=o,n){var i,s,r,a;if(e===Ms)return e;let l=n!==void 0?(i=t._$Co)===null||i===void 0?void 0:i[n]:t._$Cl,c=jo(e)?void 0:e._$litDirective$;return l?.constructor!==c&&((s=l?._$AO)===null||s===void 0||s.call(l,!1),c===void 0?l=void 0:(l=new c(o),l._$AT(o,t,n)),n!==void 0?((r=(a=t)._$Co)!==null&&r!==void 0?r:a._$Co=[])[n]=l:t._$Cl=l),l!==void 0&&(e=Ir(o,l._$AS(o,e.values),l,n)),e}d(Ir,"P");var Qu=class{static{d(this,"V")}constructor(e,t){this.u=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}v(e){var t;let{el:{content:n},parts:i}=this._$AD,s=((t=e?.creationScope)!==null&&t!==void 0?t:br).importNode(n,!0);wr.currentNode=s;let r=wr.nextNode(),a=0,l=0,c=i[0];for(;c!==void 0;){if(a===c.index){let h;c.type===2?h=new ea(r,r.nextSibling,this,e):c.type===1?h=new c.ctor(r,c.name,c.strings,this,e):c.type===6&&(h=new Vu(r,this,e)),this.u.push(h),c=i[++l]}a!==c?.index&&(r=wr.nextNode(),a++)}return s}p(e){let t=0;for(let n of this.u)n!==void 0&&(n.strings!==void 0?(n._$AI(e,n,t),t+=n.strings.length-2):n._$AI(e[t])),t++}},ea=class o{static{d(this,"N")}constructor(e,t,n,i){var s;this.type=2,this._$AH=Ot,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=n,this.options=i,this._$Cm=(s=i?.isConnected)===null||s===void 0||s}get _$AU(){var e,t;return(t=(e=this._$AM)===null||e===void 0?void 0:e._$AU)!==null&&t!==void 0?t:this._$Cm}get parentNode(){let e=this._$AA.parentNode,t=this._$AM;return t!==void 0&&e.nodeType===11&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=Ir(this,e,t),jo(e)?e===Ot||e==null||e===""?(this._$AH!==Ot&&this._$AR(),this._$AH=Ot):e!==this._$AH&&e!==Ms&&this.g(e):e._$litType$!==void 0?this.$(e):e.nodeType!==void 0?this.T(e):db(e)?this.k(e):this.g(e)}O(e,t=this._$AB){return this._$AA.parentNode.insertBefore(e,t)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}g(e){this._$AH!==Ot&&jo(this._$AH)?this._$AA.nextSibling.data=e:this.T(br.createTextNode(e)),this._$AH=e}$(e){var t;let{values:n,_$litType$:i}=e,s=typeof i=="number"?this._$AC(e):(i.el===void 0&&(i.el=Zo.createElement(i.h,this.options)),i);if(((t=this._$AH)===null||t===void 0?void 0:t._$AD)===s)this._$AH.p(n);else{let r=new Qu(s,this),a=r.v(this.options);r.p(n),this.T(a),this._$AH=r}}_$AC(e){let t=fm.get(e.strings);return t===void 0&&fm.set(e.strings,t=new Zo(e)),t}k(e){mm(this._$AH)||(this._$AH=[],this._$AR());let t=this._$AH,n,i=0;for(let s of e)i===t.length?t.push(n=new o(this.O(Jo()),this.O(Jo()),this,this.options)):n=t[i],n._$AI(s),i++;i<t.length&&(this._$AR(n&&n._$AB.nextSibling,i),t.length=i)}_$AR(e=this._$AA.nextSibling,t){var n;for((n=this._$AP)===null||n===void 0||n.call(this,!1,!0,t);e&&e!==this._$AB;){let i=e.nextSibling;e.remove(),e=i}}setConnected(e){var t;this._$AM===void 0&&(this._$Cm=e,(t=this._$AP)===null||t===void 0||t.call(this,e))}},Cr=class{static{d(this,"S")}constructor(e,t,n,i,s){this.type=1,this._$AH=Ot,this._$AN=void 0,this.element=e,this.name=t,this._$AM=i,this.options=s,n.length>2||n[0]!==""||n[1]!==""?(this._$AH=Array(n.length-1).fill(new String),this.strings=n):this._$AH=Ot}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(e,t=this,n,i){let s=this.strings,r=!1;if(s===void 0)e=Ir(this,e,t,0),r=!jo(e)||e!==this._$AH&&e!==Ms,r&&(this._$AH=e);else{let a=e,l,c;for(e=s[0],l=0;l<s.length-1;l++)c=Ir(this,a[n+l],t,l),c===Ms&&(c=this._$AH[l]),r||(r=!jo(c)||c!==this._$AH[l]),c===Ot?e=Ot:e!==Ot&&(e+=(c??"")+s[l+1]),this._$AH[l]=c}r&&!i&&this.j(e)}j(e){e===Ot?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}},ku=class extends Cr{static{d(this,"M")}constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===Ot?void 0:e}},pb=Mr?Mr.emptyScript:"",Gu=class extends Cr{static{d(this,"k")}constructor(){super(...arguments),this.type=4}j(e){e&&e!==Ot?this.element.setAttribute(this.name,pb):this.element.removeAttribute(this.name)}},zu=class extends Cr{static{d(this,"H")}constructor(e,t,n,i,s){super(e,t,n,i,s),this.type=5}_$AI(e,t=this){var n;if((e=(n=Ir(this,e,t,0))!==null&&n!==void 0?n:Ot)===Ms)return;let i=this._$AH,s=e===Ot&&i!==Ot||e.capture!==i.capture||e.once!==i.once||e.passive!==i.passive,r=e!==Ot&&(i===Ot||s);s&&this.element.removeEventListener(this.name,this,i),r&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){var t,n;typeof this._$AH=="function"?this._$AH.call((n=(t=this.options)===null||t===void 0?void 0:t.host)!==null&&n!==void 0?n:this.element,e):this._$AH.handleEvent(e)}},Vu=class{static{d(this,"I")}constructor(e,t,n){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=n}get _$AU(){return this._$AM._$AU}_$AI(e){Ir(this,e)}};var pm=Yl.litHtmlPolyfillSupport;pm?.(Zo,ea),((Uu=Yl.litHtmlVersions)!==null&&Uu!==void 0?Uu:Yl.litHtmlVersions=[]).push("2.6.1");var Jl=d((o,e,t)=>{var n,i;let s=(n=t?.renderBefore)!==null&&n!==void 0?n:e,r=s._$litPart$;if(r===void 0){let a=(i=t?.renderBefore)!==null&&i!==void 0?i:null;s._$litPart$=r=new ea(e.insertBefore(Jo(),a),a,void 0,t??{})}return r._$AI(o),r},"Z");L();P();var Hu,Wu;var Sr=class extends Yn{static{d(this,"s")}constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){var e,t;let n=super.createRenderRoot();return(e=(t=this.renderOptions).renderBefore)!==null&&e!==void 0||(t.renderBefore=n.firstChild),n}update(e){let t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=Jl(t,this.renderRoot,this.renderOptions)}connectedCallback(){var e;super.connectedCallback(),(e=this._$Do)===null||e===void 0||e.setConnected(!0)}disconnectedCallback(){var e;super.disconnectedCallback(),(e=this._$Do)===null||e===void 0||e.setConnected(!1)}render(){return Ms}};Sr.finalized=!0,Sr._$litElement$=!0,(Hu=globalThis.litElementHydrateSupport)===null||Hu===void 0||Hu.call(globalThis,{LitElement:Sr});var ym=globalThis.litElementPolyfillSupport;ym?.({LitElement:Sr});((Wu=globalThis.litElementVersions)!==null&&Wu!==void 0?Wu:globalThis.litElementVersions=[]).push("3.2.2");L();P();L();P();var qu=navigator.xr!=null&&self.XRSession!=null&&navigator.xr.isSessionSupported!=null,Ku=qu&&self.XRSession.prototype.requestHitTestSource!=null,jl=self.ResizeObserver!=null,Zl=self.IntersectionObserver!=null,ec=Ku,V1=(()=>{let o=navigator.userAgent||navigator.vendor||self.opera,e=!1;return(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(o)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(o.substr(0,4)))&&(e=!0),e})(),H1=/\bCrOS\b/.test(navigator.userAgent),Ab=/android/i.test(navigator.userAgent),xm=/iPad|iPhone|iPod/.test(navigator.userAgent)&&!self.MSStream||navigator.platform==="MacIntel"&&navigator.maxTouchPoints>1,W1=/Safari\//.test(navigator.userAgent),mb=/firefox/i.test(navigator.userAgent),gb=/OculusBrowser/.test(navigator.userAgent),q1=xm&&/CriOS\//.test(navigator.userAgent);var vm=Ab&&!mb&&!gb,_b=!!(self.webkit&&self.webkit.messageHandlers),$u=(()=>{if(xm){if(_b)return!!/CriOS\/|EdgiOS\/|FxiOS\/|GSA\/|DuckDuckGo\//.test(navigator.userAgent);{let o=document.createElement("a");return!!(o.relList&&o.relList.supports&&o.relList.supports("ar"))}}else return!1})();L();P();L();P();var tc=d(o=>o&&o!=="null"?yb(o):null,"deserializeUrl"),Xu=d(()=>{if(ec)return;let o=[];throw qu||o.push("WebXR Device API"),Ku||o.push("WebXR Hit Test API"),new Error(`The following APIs are required for AR, but are missing in this browser: ${o.join(", ")}`)},"assertIsArCandidate"),yb=d(o=>new URL(o,self.location.toString()).toString(),"toFullUrl"),Em=d((o,e)=>{let t=null,n=d((...i)=>{t==null&&(o(...i),t=self.setTimeout(()=>t=null,e))},"throttled");return n.flush=()=>{t!=null&&(self.clearTimeout(t),t=null)},n},"throttle"),Yu=d((o,e)=>{let t=null;return(...n)=>{t!=null&&self.clearTimeout(t),t=self.setTimeout(()=>{t=null,o(...n)},e)}},"debounce");var Jt=d((o,e,t)=>Math.max(e,Math.min(t,o)),"clamp"),xb=1,ta=(()=>{let o=(()=>{var e;if(!((e=document.documentElement.getAttribute("itemtype"))===null||e===void 0)&&e.includes("schema.org/SearchResultsPage"))return!0;let t=document.head!=null?Array.from(document.head.querySelectorAll("meta")):[];for(let n of t)if(n.name==="viewport")return!0;return!1})();return o||console.warn('No <meta name="viewport"> detected; <model-viewer> will cap pixel density at 1.'),()=>o?self.devicePixelRatio:xb})(),Ju=(()=>{let o="model-viewer-debug-mode",e=new RegExp(`[?&]${o}(&|$)`);return()=>self.ModelViewerElement&&self.ModelViewerElement.debugMode||self.location&&self.location.search&&self.location.search.match(e)})();var wm=d((o=0)=>new Promise(e=>setTimeout(e,o)),"timePasses"),Mm=d((o,e,t=null)=>new Promise(n=>{function i(s){(!t||t(s))&&(n(s),o.removeEventListener(e,i))}d(i,"handler"),o.addEventListener(e,i)}),"waitForEvent");var na=function(o,e,t,n){var i=arguments.length,s=i<3?e:n===null?n=Object.getOwnPropertyDescriptor(e,t):n,r;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")s=Reflect.decorate(o,e,t,n);else for(var a=o.length-1;a>=0;a--)(r=o[a])&&(s=(i<3?r(s):i>3?r(e,t,s):r(e,t))||s);return i>3&&s&&Object.defineProperty(e,t,s),s},vb=.5,Eb=0,wb=1,Mb=1,Tr=Symbol("currentEnvironmentMap"),Br=Symbol("currentBackground"),Rr=Symbol("updateEnvironment"),nc=Symbol("cancelEnvironmentUpdate"),bm=d(o=>{var e,t,n;class i extends o{static{d(this,"EnvironmentModelViewerElement")}constructor(){super(...arguments),this.environmentImage=null,this.skyboxImage=null,this.shadowIntensity=Eb,this.shadowSoftness=wb,this.exposure=Mb,this[e]=null,this[t]=null,this[n]=null}updated(r){super.updated(r),r.has("shadowIntensity")&&(this[oe].setShadowIntensity(this.shadowIntensity*vb),this[_t]()),r.has("shadowSoftness")&&(this[oe].setShadowSoftness(this.shadowSoftness),this[_t]()),r.has("exposure")&&(this[oe].exposure=this.exposure,this[_t]()),(r.has("environmentImage")||r.has("skyboxImage"))&&this[Mi]()&&this[Rr]()}hasBakedShadow(){return this[oe].bakedShadows.size>0}async[(e=Tr,t=Br,n=nc,Rr)](){let{skyboxImage:r,environmentImage:a}=this;this[nc]!=null&&(this[nc](),this[nc]=null);let{textureUtils:l}=this[Ne];if(l==null)return;let c=this[Jn].beginActivity();try{let{environmentMap:h,skybox:u}=await l.generateEnvironmentMapAndSkybox(tc(r),a,f=>c(Jt(f,0,1)));this[Tr]!==h&&(this[Tr]=h,this.dispatchEvent(new CustomEvent("environment-change"))),u!=null?this[Br]=u.name===h.name?h:u:this[Br]=null,this[oe].setEnvironmentAndSkybox(this[Tr],this[Br]),this[oe].dispatchEvent({type:"envmap-update"})}catch(h){if(h instanceof Error)throw this[oe].setEnvironmentAndSkybox(null,null),h}finally{c(1)}}}return na([ye({type:String,attribute:"environment-image"})],i.prototype,"environmentImage",void 0),na([ye({type:String,attribute:"skybox-image"})],i.prototype,"skyboxImage",void 0),na([ye({type:Number,attribute:"shadow-intensity"})],i.prototype,"shadowIntensity",void 0),na([ye({type:Number,attribute:"shadow-softness"})],i.prototype,"shadowSoftness",void 0),na([ye({type:Number})],i.prototype,"exposure",void 0),i},"EnvironmentMixin");L();P();L();P();var Im=ji`
<svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" viewBox="0 0 24 24" fill="#000000">
    <!-- NOTE(cdata): This SVG filter is a stop-gap until we can implement
         support for dynamic re-coloring of UI components -->
    <defs>
      <filter id="drop-shadow" x="-100%" y="-100%" width="300%" height="300%">
        <feGaussianBlur in="SourceAlpha" stdDeviation="1"/>
        <feOffset dx="0" dy="0" result="offsetblur"/>
        <feFlood flood-color="#000000"/>
        <feComposite in2="offsetblur" operator="in"/>
        <feMerge>
          <feMergeNode/>
          <feMergeNode in="SourceGraphic"/>
        </feMerge>
      </filter>
    </defs>
    <path filter="url(#drop-shadow)" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
    <path d="M0 0h24v24H0z" fill="none"/>
</svg>`;L();P();var Cm=ji`
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="25" height="36">
    <defs>
        <path id="A" d="M.001.232h24.997V36H.001z" />
    </defs>
    <g transform="translate(-11 -4)" fill="none" fill-rule="evenodd">
        <path fill-opacity="0" fill="#fff" d="M0 0h44v44H0z" />
        <g transform="translate(11 3)">
            <path d="M8.733 11.165c.04-1.108.766-2.027 1.743-2.307a2.54 2.54 0 0 1 .628-.089c.16 0 .314.017.463.044 1.088.2 1.9 1.092 1.9 2.16v8.88h1.26c2.943-1.39 5-4.45 5-8.025a9.01 9.01 0 0 0-1.9-5.56l-.43-.5c-.765-.838-1.683-1.522-2.712-2-1.057-.49-2.226-.77-3.46-.77s-2.4.278-3.46.77c-1.03.478-1.947 1.162-2.71 2l-.43.5a9.01 9.01 0 0 0-1.9 5.56 9.04 9.04 0 0 0 .094 1.305c.03.21.088.41.13.617l.136.624c.083.286.196.56.305.832l.124.333a8.78 8.78 0 0 0 .509.953l.065.122a8.69 8.69 0 0 0 3.521 3.191l1.11.537v-9.178z" fill-opacity=".5" fill="#e4e4e4" />
            <path d="M22.94 26.218l-2.76 7.74c-.172.485-.676.8-1.253.8H12.24c-1.606 0-3.092-.68-3.98-1.82-1.592-2.048-3.647-3.822-6.11-5.27-.095-.055-.15-.137-.152-.23-.004-.1.046-.196.193-.297.56-.393 1.234-.6 1.926-.6a3.43 3.43 0 0 1 .691.069l4.922.994V10.972c0-.663.615-1.203 1.37-1.203s1.373.54 1.373 1.203v9.882h2.953c.273 0 .533.073.757.21l6.257 3.874c.027.017.045.042.07.06.41.296.586.77.426 1.22M4.1 16.614c-.024-.04-.042-.083-.065-.122a8.69 8.69 0 0 1-.509-.953c-.048-.107-.08-.223-.124-.333l-.305-.832c-.058-.202-.09-.416-.136-.624l-.13-.617a9.03 9.03 0 0 1-.094-1.305c0-2.107.714-4.04 1.9-5.56l.43-.5c.764-.84 1.682-1.523 2.71-2 1.058-.49 2.226-.77 3.46-.77s2.402.28 3.46.77c1.03.477 1.947 1.16 2.712 2l.428.5a9 9 0 0 1 1.901 5.559c0 3.577-2.056 6.636-5 8.026h-1.26v-8.882c0-1.067-.822-1.96-1.9-2.16-.15-.028-.304-.044-.463-.044-.22 0-.427.037-.628.09-.977.28-1.703 1.198-1.743 2.306v9.178l-1.11-.537C6.18 19.098 4.96 18 4.1 16.614M22.97 24.09l-6.256-3.874c-.102-.063-.218-.098-.33-.144 2.683-1.8 4.354-4.855 4.354-8.243 0-.486-.037-.964-.104-1.43a9.97 9.97 0 0 0-1.57-4.128l-.295-.408-.066-.092a10.05 10.05 0 0 0-.949-1.078c-.342-.334-.708-.643-1.094-.922-1.155-.834-2.492-1.412-3.94-1.65l-.732-.088-.748-.03a9.29 9.29 0 0 0-1.482.119c-1.447.238-2.786.816-3.94 1.65a9.33 9.33 0 0 0-.813.686 9.59 9.59 0 0 0-.845.877l-.385.437-.36.5-.288.468-.418.778-.04.09c-.593 1.28-.93 2.71-.93 4.222 0 3.832 2.182 7.342 5.56 8.938l1.437.68v4.946L5 25.64a4.44 4.44 0 0 0-.888-.086c-.017 0-.034.003-.05.003-.252.004-.503.033-.75.08a5.08 5.08 0 0 0-.237.056c-.193.046-.382.107-.568.18-.075.03-.15.057-.225.1-.25.114-.494.244-.723.405a1.31 1.31 0 0 0-.566 1.122 1.28 1.28 0 0 0 .645 1.051C4 29.925 5.96 31.614 7.473 33.563a5.06 5.06 0 0 0 .434.491c1.086 1.082 2.656 1.713 4.326 1.715h6.697c.748-.001 1.43-.333 1.858-.872.142-.18.256-.38.336-.602l2.757-7.74c.094-.26.13-.53.112-.794s-.088-.52-.203-.76a2.19 2.19 0 0 0-.821-.91" fill-opacity=".6" fill="#000" />
            <path d="M22.444 24.94l-6.257-3.874a1.45 1.45 0 0 0-.757-.211h-2.953v-9.88c0-.663-.616-1.203-1.373-1.203s-1.37.54-1.37 1.203v16.643l-4.922-.994a3.44 3.44 0 0 0-.692-.069 3.35 3.35 0 0 0-1.925.598c-.147.102-.198.198-.194.298.004.094.058.176.153.23 2.462 1.448 4.517 3.22 6.11 5.27.887 1.14 2.373 1.82 3.98 1.82h6.686c.577 0 1.08-.326 1.253-.8l2.76-7.74c.16-.448-.017-.923-.426-1.22-.025-.02-.043-.043-.07-.06z" fill="#fff" />
            <g transform="translate(0 .769)">
                <mask id="B" fill="#fff">
                    <use xlink:href="#A" />
                </mask>
                <path d="M23.993 24.992a1.96 1.96 0 0 1-.111.794l-2.758 7.74c-.08.22-.194.423-.336.602-.427.54-1.11.87-1.857.872h-6.698c-1.67-.002-3.24-.633-4.326-1.715-.154-.154-.3-.318-.434-.49C5.96 30.846 4 29.157 1.646 27.773c-.385-.225-.626-.618-.645-1.05a1.31 1.31 0 0 1 .566-1.122 4.56 4.56 0 0 1 .723-.405l.225-.1a4.3 4.3 0 0 1 .568-.18l.237-.056c.248-.046.5-.075.75-.08.018 0 .034-.003.05-.003.303-.001.597.027.89.086l3.722.752V20.68l-1.436-.68c-3.377-1.596-5.56-5.106-5.56-8.938 0-1.51.336-2.94.93-4.222.015-.03.025-.06.04-.09.127-.267.268-.525.418-.778.093-.16.186-.316.288-.468.063-.095.133-.186.2-.277L3.773 5c.118-.155.26-.29.385-.437.266-.3.544-.604.845-.877a9.33 9.33 0 0 1 .813-.686C6.97 2.167 8.31 1.59 9.757 1.35a9.27 9.27 0 0 1 1.481-.119 8.82 8.82 0 0 1 .748.031c.247.02.49.05.733.088 1.448.238 2.786.816 3.94 1.65.387.28.752.588 1.094.922a9.94 9.94 0 0 1 .949 1.078l.066.092c.102.133.203.268.295.408a9.97 9.97 0 0 1 1.571 4.128c.066.467.103.945.103 1.43 0 3.388-1.67 6.453-4.353 8.243.11.046.227.08.33.144l6.256 3.874c.37.23.645.55.82.9.115.24.185.498.203.76m.697-1.195c-.265-.55-.677-1.007-1.194-1.326l-5.323-3.297c2.255-2.037 3.564-4.97 3.564-8.114 0-2.19-.637-4.304-1.84-6.114-.126-.188-.26-.37-.4-.552-.645-.848-1.402-1.6-2.252-2.204C15.472.91 13.393.232 11.238.232A10.21 10.21 0 0 0 5.23 2.19c-.848.614-1.606 1.356-2.253 2.205-.136.18-.272.363-.398.55C1.374 6.756.737 8.87.737 11.06c0 4.218 2.407 8.08 6.133 9.842l.863.41v3.092l-2.525-.51c-.356-.07-.717-.106-1.076-.106a5.45 5.45 0 0 0-3.14.996c-.653.46-1.022 1.202-.99 1.983a2.28 2.28 0 0 0 1.138 1.872c2.24 1.318 4.106 2.923 5.543 4.772 1.26 1.62 3.333 2.59 5.55 2.592h6.698c1.42-.001 2.68-.86 3.134-2.138l2.76-7.74c.272-.757.224-1.584-.134-2.325" fill-opacity=".05" fill="#000" mask="url(#B)" />
            </g>
        </g>
    </g>
</svg>`;L();P();var Sm=ji`
<svg version="1.1" id="view_x5F_in_x5F_AR_x5F_icon"
	 xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="24px" height="24px"
	 viewBox="0 0 24 24" enable-background="new 0 0 24 24" xml:space="preserve">
<rect id="Bounding_Box" x="0" y="0" fill="none" width="24" height="24"/>
<g id="Art_layer">
	<path d="M3,4c0-0.55,0.45-1,1-1h2V1H4C2.35,1,1,2.35,1,4v2h2V4z"/>
	<path d="M20,3c0.55,0,1,0.45,1,1v2h2V4c0-1.65-1.35-3-3-3h-2v2H20z"/>
	<path d="M4,21c-0.55,0-1-0.45-1-1v-2H1v2c0,1.65,1.35,3,3,3h2v-2H4z"/>
	<path d="M20,21c0.55,0,1-0.45,1-1v-2h2v2c0,1.65-1.35,3-3,3h-2v-2H20z"/>
	<g>
		<path d="M18.25,7.6l-5.5-3.18c-0.46-0.27-1.04-0.27-1.5,0L5.75,7.6C5.29,7.87,5,8.36,5,8.9v6.35c0,0.54,0.29,1.03,0.75,1.3
			l5.5,3.18c0.46,0.27,1.04,0.27,1.5,0l5.5-3.18c0.46-0.27,0.75-0.76,0.75-1.3V8.9C19,8.36,18.71,7.87,18.25,7.6z M7,14.96v-4.62
			l4,2.32v4.61L7,14.96z M12,10.93L8,8.61l4-2.31l4,2.31L12,10.93z M13,17.27v-4.61l4-2.32v4.62L13,17.27z"/>
	</g>
</g>
</svg>`;var bb=ji`
<style>
:host {
  display: block;
  position: relative;
  contain: strict;
  width: 300px;
  height: 150px;
}

/* NOTE: This rule set is our integration surface area with the
 * :focus-visible polyfill.
 *
 * @see https://github.com/WICG/focus-visible/pull/196 */
:host([data-js-focus-visible]:focus:not(.focus-visible)),
:host([data-js-focus-visible]) :focus:not(.focus-visible) {
  outline: none;
}

.container {
  position: relative;
  overflow: hidden;
}

.userInput {
  width: 100%;
  height: 100%;
  display: none;
  position: relative;
}

canvas {
  position: absolute;
  display: none;
  pointer-events: none;
  /* NOTE(cdata): Chrome 76 and below apparently have a bug
   * that causes our canvas not to display pixels unless it is
   * on its own render layer
   * @see https://github.com/google/model-viewer/pull/755#issuecomment-536597893
   */
  transform: translateZ(0);
}

.show {
  display: block;
}

/* Adapted from HTML5 Boilerplate
 *
 * @see https://github.com/h5bp/html5-boilerplate/blob/ceb4620c78fc82e13534fc44202a3f168754873f/dist/css/main.css#L122-L133 */
.screen-reader-only {
  border: 0;
  left: 0;
  top: 0;
  clip: rect(0, 0, 0, 0);
  height: 1px;
  margin: -1px;
  overflow: hidden;
  padding: 0;
  position: absolute;
  white-space: nowrap;
  width: 1px;
  pointer-events: none;
}

.slot {
  position: absolute;
  pointer-events: none;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.slot > * {
  pointer-events: initial;
}

.annotation-wrapper ::slotted(*) {
  opacity: var(--max-hotspot-opacity, 1);
  transition: opacity 0.3s;
}

.pointer-tumbling .annotation-wrapper ::slotted(*) {
  pointer-events: none;
}

.annotation-wrapper ::slotted(*) {
  pointer-events: initial;
}

.annotation-wrapper.hide ::slotted(*) {
  opacity: var(--min-hotspot-opacity, 0.25);
}

.slot.poster {
  display: none;
  background-color: inherit;
}

.slot.poster.show {
  display: inherit;
}

.slot.poster > * {
  pointer-events: initial;
}

.slot.poster:not(.show) > * {
  pointer-events: none;
}

#default-poster {
  width: 100%;
  height: 100%;
  /* The default poster is a <button> so we need to set display
   * to prevent it from being affected by text-align: */
  display: block;
  position: absolute;
  border: none;
  padding: 0;
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
  background-color: #fff0;
}

#default-progress-bar {
  display: block;
  position: relative;
  width: 100%;
  height: 100%;
  pointer-events: none;
  overflow: hidden;
}

#default-progress-bar > .bar {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: var(--progress-bar-height, 5px);
  background-color: var(--progress-bar-color, rgba(0, 0, 0, 0.4));
  transition: transform 0.09s;
  transform-origin: top left;
  transform: scaleX(0);
  overflow: hidden;
}

#default-progress-bar > .bar.hide {
  transition: opacity 0.3s 1s;
  opacity: 0;
}

.centered {
  align-items: center;
  justify-content: center;
}

.cover {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.slot.interaction-prompt {
  display: var(--interaction-prompt-display, flex);
  overflow: hidden;
  opacity: 0;
  will-change: opacity;
  transition: opacity 0.3s;
}

.slot.interaction-prompt.visible {
  opacity: 1;
}

.animated-container {
  will-change: transform, opacity;
  opacity: 0;
  transition: opacity 0.3s;
}

.slot.interaction-prompt > * {
  pointer-events: none;
}

.slot.ar-button {
  -moz-user-select: none;
  -webkit-tap-highlight-color: transparent;
  user-select: none;

  display: var(--ar-button-display, block);
}

.slot.ar-button:not(.enabled) {
  display: none;
}

.fab {
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  width: 40px;
  height: 40px;
  cursor: pointer;
  background-color: #fff;
  box-shadow: 0px 0px 4px rgba(0, 0, 0, 0.15);
  border-radius: 100px;
}

.fab > * {
  opacity: 0.87;
}

#default-ar-button {
  position: absolute;
  bottom: 16px;
  right: 16px;
  transform: scale(var(--ar-button-scale, 1));
  transform-origin: bottom right;
}

.slot.pan-target {
  display: block;
  position: absolute;
  width: 0;
  height: 0;
  left: 50%;
  top: 50%;
  transform: translate3d(-50%, -50%, 0);
  background-color: transparent;
  opacity: 0;
  transition: opacity 0.3s;
}

#default-pan-target {
  width: 6px;
  height: 6px;
  border-radius: 6px;
  border: 1px solid white;
  box-shadow: 0px 0px 2px 1px rgba(0, 0, 0, 0.8);
}

.slot.default {
  pointer-events: none;
}

.slot.progress-bar {
  pointer-events: none;
}

.slot.exit-webxr-ar-button {
  pointer-events: none;
}

.slot.exit-webxr-ar-button:not(.enabled) {
  display: none;
}

#default-exit-webxr-ar-button {
  display: flex;
  align-items: center;
  justify-content: center;
  position: absolute;
  top: env(safe-area-inset-top, 16px);
  right: 16px;
  width: 40px;
  height: 40px;
  box-sizing: border-box;
}

#default-exit-webxr-ar-button > svg {
  fill: #fff;
}
</style>
<div class="container">
  <div class="userInput" tabindex="0" role="img"
      aria-label="3D model">
      <div class="slot canvas">
        <slot name="canvas">
          <canvas></canvas>
        </slot>
      </div>

  </div>

  <!-- NOTE(cdata): We need to wrap slots because browsers without ShadowDOM
        will have their <slot> elements removed by ShadyCSS -->
  <div class="slot poster">
    <slot name="poster">
      <button type="button" id="default-poster" aria-hidden="true" aria-label="Loading 3D model"></button>
    </slot>
  </div>

  <div class="slot ar-button">
    <slot name="ar-button">
      <a id="default-ar-button" part="default-ar-button" class="fab"
          tabindex="2"
          aria-label="View in your space">
        ${Sm}
      </a>
    </slot>
  </div>

  <div class="slot pan-target">
    <slot name="pan-target">
      <div id="default-pan-target">
      </div>
    </slot>
  </div>

  <div class="slot interaction-prompt cover centered">
    <div id="prompt" class="animated-container">
      <slot name="interaction-prompt" aria-hidden="true">
        ${Cm}
      </slot>
    </div>
  </div>

  <div id="finger0" class="animated-container cover">
    <slot name="finger0" aria-hidden="true">
    </slot>
  </div>
  <div id="finger1" class="animated-container cover">
    <slot name="finger1" aria-hidden="true">
    </slot>
  </div>

  <div class="slot default">
    <slot></slot>

    <div class="slot progress-bar">
      <slot name="progress-bar">
        <div id="default-progress-bar" aria-hidden="true">
          <div class="bar" part="default-progress-bar"></div>
        </div>
      </slot>
    </div>

    <div class="slot exit-webxr-ar-button">
      <slot name="exit-webxr-ar-button">
        <a id="default-exit-webxr-ar-button" part="default-exit-webxr-ar-button"
            tabindex="3"
            aria-label="Exit AR"
            aria-hidden="true">
          ${Im}
        </a>
      </slot>
    </div>
  </div>
</div>
<div class="screen-reader-only" role="region" aria-label="Live announcements">
  <span id="status" role="status"></span>
</div>`,Tm=d(o=>{Jl(bb,o)},"makeTemplate");L();P();L();P();var ju=new WeakMap,ic=class extends pn{static{d(this,"DRACOLoader")}constructor(e){super(e),this.decoderPath="",this.decoderConfig={},this.decoderBinary=null,this.decoderPending=null,this.workerLimit=4,this.workerPool=[],this.workerNextTaskID=1,this.workerSourceURL="",this.defaultAttributeIDs={position:"POSITION",normal:"NORMAL",color:"COLOR",uv:"TEX_COORD"},this.defaultAttributeTypes={position:"Float32Array",normal:"Float32Array",color:"Float32Array",uv:"Float32Array"}}setDecoderPath(e){return this.decoderPath=e,this}setDecoderConfig(e){return this.decoderConfig=e,this}setWorkerLimit(e){return this.workerLimit=e,this}load(e,t,n,i){let s=new An(this.manager);s.setPath(this.path),s.setResponseType("arraybuffer"),s.setRequestHeader(this.requestHeader),s.setWithCredentials(this.withCredentials),s.load(e,r=>{this.decodeDracoFile(r,t).catch(i)},n,i)}decodeDracoFile(e,t,n,i){let s={attributeIDs:n||this.defaultAttributeIDs,attributeTypes:i||this.defaultAttributeTypes,useUniqueIDs:!!n};return this.decodeGeometry(e,s).then(t)}decodeGeometry(e,t){let n=JSON.stringify(t);if(ju.has(e)){let l=ju.get(e);if(l.key===n)return l.promise;if(e.byteLength===0)throw new Error("THREE.DRACOLoader: Unable to re-decode a buffer with different settings. Buffer has already been transferred.")}let i,s=this.workerNextTaskID++,r=e.byteLength,a=this._getWorker(s,r).then(l=>(i=l,new Promise((c,h)=>{i._callbacks[s]={resolve:c,reject:h},i.postMessage({type:"decode",id:s,taskConfig:t,buffer:e},[e])}))).then(l=>this._createGeometry(l.geometry));return a.catch(()=>!0).then(()=>{i&&s&&this._releaseTask(i,s)}),ju.set(e,{key:n,promise:a}),a}_createGeometry(e){let t=new kt;e.index&&t.setIndex(new je(e.index.array,1));for(let n=0;n<e.attributes.length;n++){let i=e.attributes[n],s=i.name,r=i.array,a=i.itemSize;t.setAttribute(s,new je(r,a))}return t}_loadLibrary(e,t){let n=new An(this.manager);return n.setPath(this.decoderPath),n.setResponseType(t),n.setWithCredentials(this.withCredentials),new Promise((i,s)=>{n.load(e,i,void 0,s)})}preload(){return this._initDecoder(),this}_initDecoder(){if(this.decoderPending)return this.decoderPending;let e=typeof WebAssembly!="object"||this.decoderConfig.type==="js",t=[];return e?t.push(this._loadLibrary("draco_decoder.js","text")):(t.push(this._loadLibrary("draco_wasm_wrapper.js","text")),t.push(this._loadLibrary("draco_decoder.wasm","arraybuffer"))),this.decoderPending=Promise.all(t).then(n=>{let i=n[0];e||(this.decoderConfig.wasmBinary=n[1]);let s=Ib.toString(),r=["/* draco decoder */",i,"","/* worker */",s.substring(s.indexOf("{")+1,s.lastIndexOf("}"))].join(`
`);this.workerSourceURL=URL.createObjectURL(new Blob([r]))}),this.decoderPending}_getWorker(e,t){return this._initDecoder().then(()=>{if(this.workerPool.length<this.workerLimit){let i=new Worker(this.workerSourceURL);i._callbacks={},i._taskCosts={},i._taskLoad=0,i.postMessage({type:"init",decoderConfig:this.decoderConfig}),i.onmessage=function(s){let r=s.data;switch(r.type){case"decode":i._callbacks[r.id].resolve(r);break;case"error":i._callbacks[r.id].reject(r);break;default:console.error('THREE.DRACOLoader: Unexpected message, "'+r.type+'"')}},this.workerPool.push(i)}else this.workerPool.sort(function(i,s){return i._taskLoad>s._taskLoad?-1:1});let n=this.workerPool[this.workerPool.length-1];return n._taskCosts[e]=t,n._taskLoad+=t,n})}_releaseTask(e,t){e._taskLoad-=e._taskCosts[t],delete e._callbacks[t],delete e._taskCosts[t]}debug(){console.log("Task load: ",this.workerPool.map(e=>e._taskLoad))}dispose(){for(let e=0;e<this.workerPool.length;++e)this.workerPool[e].terminate();return this.workerPool.length=0,this.workerSourceURL!==""&&URL.revokeObjectURL(this.workerSourceURL),this}};function Ib(){let o,e;onmessage=d(function(r){let a=r.data;switch(a.type){case"init":o=a.decoderConfig,e=new Promise(function(h){o.onModuleLoaded=function(u){h({draco:u})},DracoDecoderModule(o)});break;case"decode":let l=a.buffer,c=a.taskConfig;e.then(h=>{let u=h.draco,f=new u.Decoder,p=new u.DecoderBuffer;p.Init(new Int8Array(l),l.byteLength);try{let g=t(u,f,p,c),A=g.attributes.map(m=>m.array.buffer);g.index&&A.push(g.index.array.buffer),self.postMessage({type:"decode",id:a.id,geometry:g},A)}catch(g){console.error(g),self.postMessage({type:"error",id:a.id,error:g.message})}finally{u.destroy(p),u.destroy(f)}});break}},"onmessage");function t(r,a,l,c){let h=c.attributeIDs,u=c.attributeTypes,f,p,g=a.GetEncodedGeometryType(l);if(g===r.TRIANGULAR_MESH)f=new r.Mesh,p=a.DecodeBufferToMesh(l,f);else if(g===r.POINT_CLOUD)f=new r.PointCloud,p=a.DecodeBufferToPointCloud(l,f);else throw new Error("THREE.DRACOLoader: Unexpected geometry type.");if(!p.ok()||f.ptr===0)throw new Error("THREE.DRACOLoader: Decoding failed: "+p.error_msg());let A={index:null,attributes:[]};for(let m in h){let _=self[u[m]],E,x;if(c.useUniqueIDs)x=h[m],E=a.GetAttributeByUniqueId(f,x);else{if(x=a.GetAttributeId(f,r[h[m]]),x===-1)continue;E=a.GetAttribute(f,x)}A.attributes.push(i(r,a,f,m,_,E))}return g===r.TRIANGULAR_MESH&&(A.index=n(r,a,f)),r.destroy(f),A}d(t,"decodeGeometry");function n(r,a,l){let h=l.num_faces()*3,u=h*4,f=r._malloc(u);a.GetTrianglesUInt32Array(l,u,f);let p=new Uint32Array(r.HEAPF32.buffer,f,h).slice();return r._free(f),{array:p,itemSize:1}}d(n,"decodeIndex");function i(r,a,l,c,h,u){let f=u.num_components(),g=l.num_points()*f,A=g*h.BYTES_PER_ELEMENT,m=s(r,h),_=r._malloc(A);a.GetAttributeDataArrayForAllPoints(l,u,m,A,_);let E=new h(r.HEAPF32.buffer,_,g).slice();return r._free(_),{name:c,array:E,itemSize:f}}d(i,"decodeAttribute");function s(r,a){switch(a){case Float32Array:return r.DT_FLOAT32;case Int8Array:return r.DT_INT8;case Int16Array:return r.DT_INT16;case Int32Array:return r.DT_INT32;case Uint8Array:return r.DT_UINT8;case Uint16Array:return r.DT_UINT16;case Uint32Array:return r.DT_UINT32}}d(s,"getDracoDataType")}d(Ib,"DRACOWorker");L();P();L();P();function Zu(o,e){if(e===VA)return console.warn("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Geometry already defined as triangles."),o;if(e===$o||e===Vl){let t=o.getIndex();if(t===null){let r=[],a=o.getAttribute("position");if(a!==void 0){for(let l=0;l<a.count;l++)r.push(l);o.setIndex(r),t=o.getIndex()}else return console.error("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Undefined position attribute. Processing not possible."),o}let n=t.count-2,i=[];if(e===$o)for(let r=1;r<=n;r++)i.push(t.getX(0)),i.push(t.getX(r)),i.push(t.getX(r+1));else for(let r=0;r<n;r++)r%2===0?(i.push(t.getX(r)),i.push(t.getX(r+1)),i.push(t.getX(r+2))):(i.push(t.getX(r+2)),i.push(t.getX(r+1)),i.push(t.getX(r)));i.length/3!==n&&console.error("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Unable to generate correct amount of triangles.");let s=o.clone();return s.setIndex(i),s.clearGroups(),s}else return console.error("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Unknown draw mode:",e),o}d(Zu,"toTrianglesDrawMode");var sc=class extends pn{static{d(this,"GLTFLoader")}constructor(e){super(e),this.dracoLoader=null,this.ktx2Loader=null,this.meshoptDecoder=null,this.pluginCallbacks=[],this.register(function(t){return new rd(t)}),this.register(function(t){return new dd(t)}),this.register(function(t){return new fd(t)}),this.register(function(t){return new ad(t)}),this.register(function(t){return new ld(t)}),this.register(function(t){return new cd(t)}),this.register(function(t){return new hd(t)}),this.register(function(t){return new sd(t)}),this.register(function(t){return new ud(t)}),this.register(function(t){return new od(t)}),this.register(function(t){return new nd(t)}),this.register(function(t){return new pd(t)}),this.register(function(t){return new Ad(t)})}load(e,t,n,i){let s=this,r;this.resourcePath!==""?r=this.resourcePath:this.path!==""?r=this.path:r=_r.extractUrlBase(e),this.manager.itemStart(e);let a=d(function(c){i?i(c):console.error(c),s.manager.itemError(e),s.manager.itemEnd(e)},"_onError"),l=new An(this.manager);l.setPath(this.path),l.setResponseType("arraybuffer"),l.setRequestHeader(this.requestHeader),l.setWithCredentials(this.withCredentials),l.load(e,function(c){try{s.parse(c,r,function(h){t(h),s.manager.itemEnd(e)},a)}catch(h){a(h)}},n,a)}setDRACOLoader(e){return this.dracoLoader=e,this}setDDSLoader(){throw new Error('THREE.GLTFLoader: "MSFT_texture_dds" no longer supported. Please update to "KHR_texture_basisu".')}setKTX2Loader(e){return this.ktx2Loader=e,this}setMeshoptDecoder(e){return this.meshoptDecoder=e,this}register(e){return this.pluginCallbacks.indexOf(e)===-1&&this.pluginCallbacks.push(e),this}unregister(e){return this.pluginCallbacks.indexOf(e)!==-1&&this.pluginCallbacks.splice(this.pluginCallbacks.indexOf(e),1),this}parse(e,t,n,i){let s,r={},a={},l=new TextDecoder;if(typeof e=="string")s=JSON.parse(e);else if(e instanceof ArrayBuffer)if(l.decode(new Uint8Array(e,0,4))===Fm){try{r[ze.KHR_BINARY_GLTF]=new md(e)}catch(u){i&&i(u);return}s=JSON.parse(r[ze.KHR_BINARY_GLTF].content)}else s=JSON.parse(l.decode(e));else s=e;if(s.asset===void 0||s.asset.version[0]<2){i&&i(new Error("THREE.GLTFLoader: Unsupported asset. glTF versions >=2.0 are supported."));return}let c=new wd(s,{path:t||this.resourcePath||"",crossOrigin:this.crossOrigin,requestHeader:this.requestHeader,manager:this.manager,ktx2Loader:this.ktx2Loader,meshoptDecoder:this.meshoptDecoder});c.fileLoader.setRequestHeader(this.requestHeader);for(let h=0;h<this.pluginCallbacks.length;h++){let u=this.pluginCallbacks[h](c);a[u.name]=u,r[u.name]=!0}if(s.extensionsUsed)for(let h=0;h<s.extensionsUsed.length;++h){let u=s.extensionsUsed[h],f=s.extensionsRequired||[];switch(u){case ze.KHR_MATERIALS_UNLIT:r[u]=new id;break;case ze.KHR_DRACO_MESH_COMPRESSION:r[u]=new gd(s,this.dracoLoader);break;case ze.KHR_TEXTURE_TRANSFORM:r[u]=new _d;break;case ze.KHR_MESH_QUANTIZATION:r[u]=new yd;break;default:f.indexOf(u)>=0&&a[u]===void 0&&console.warn('THREE.GLTFLoader: Unknown extension "'+u+'".')}}c.setExtensions(r),c.setPlugins(a),c.parse(n,i)}parseAsync(e,t){let n=this;return new Promise(function(i,s){n.parse(e,t,i,s)})}};function Cb(){let o={};return{get:d(function(e){return o[e]},"get"),add:d(function(e,t){o[e]=t},"add"),remove:d(function(e){delete o[e]},"remove"),removeAll:d(function(){o={}},"removeAll")}}d(Cb,"GLTFRegistry");var ze={KHR_BINARY_GLTF:"KHR_binary_glTF",KHR_DRACO_MESH_COMPRESSION:"KHR_draco_mesh_compression",KHR_LIGHTS_PUNCTUAL:"KHR_lights_punctual",KHR_MATERIALS_CLEARCOAT:"KHR_materials_clearcoat",KHR_MATERIALS_IOR:"KHR_materials_ior",KHR_MATERIALS_SHEEN:"KHR_materials_sheen",KHR_MATERIALS_SPECULAR:"KHR_materials_specular",KHR_MATERIALS_TRANSMISSION:"KHR_materials_transmission",KHR_MATERIALS_IRIDESCENCE:"KHR_materials_iridescence",KHR_MATERIALS_UNLIT:"KHR_materials_unlit",KHR_MATERIALS_VOLUME:"KHR_materials_volume",KHR_TEXTURE_BASISU:"KHR_texture_basisu",KHR_TEXTURE_TRANSFORM:"KHR_texture_transform",KHR_MESH_QUANTIZATION:"KHR_mesh_quantization",KHR_MATERIALS_EMISSIVE_STRENGTH:"KHR_materials_emissive_strength",EXT_TEXTURE_WEBP:"EXT_texture_webp",EXT_MESHOPT_COMPRESSION:"EXT_meshopt_compression",EXT_MESH_GPU_INSTANCING:"EXT_mesh_gpu_instancing"},nd=class{static{d(this,"GLTFLightsExtension")}constructor(e){this.parser=e,this.name=ze.KHR_LIGHTS_PUNCTUAL,this.cache={refs:{},uses:{}}}_markDefs(){let e=this.parser,t=this.parser.json.nodes||[];for(let n=0,i=t.length;n<i;n++){let s=t[n];s.extensions&&s.extensions[this.name]&&s.extensions[this.name].light!==void 0&&e._addNodeRef(this.cache,s.extensions[this.name].light)}}_loadLight(e){let t=this.parser,n="light:"+e,i=t.cache.get(n);if(i)return i;let s=t.json,l=((s.extensions&&s.extensions[this.name]||{}).lights||[])[e],c,h=new Me(16777215);l.color!==void 0&&h.fromArray(l.color);let u=l.range!==void 0?l.range:0;switch(l.type){case"directional":c=new gr(h),c.target.position.set(0,0,-1),c.add(c.target);break;case"point":c=new Xi(h),c.distance=u;break;case"spot":c=new Nl(h),c.distance=u,l.spot=l.spot||{},l.spot.innerConeAngle=l.spot.innerConeAngle!==void 0?l.spot.innerConeAngle:0,l.spot.outerConeAngle=l.spot.outerConeAngle!==void 0?l.spot.outerConeAngle:Math.PI/4,c.angle=l.spot.outerConeAngle,c.penumbra=1-l.spot.innerConeAngle/l.spot.outerConeAngle,c.target.position.set(0,0,-1),c.add(c.target);break;default:throw new Error("THREE.GLTFLoader: Unexpected light type: "+l.type)}return c.position.set(0,0,0),c.decay=2,es(c,l),l.intensity!==void 0&&(c.intensity=l.intensity),c.name=t.createUniqueName(l.name||"light_"+e),i=Promise.resolve(c),t.cache.add(n,i),i}getDependency(e,t){if(e==="light")return this._loadLight(t)}createNodeAttachment(e){let t=this,n=this.parser,s=n.json.nodes[e],a=(s.extensions&&s.extensions[this.name]||{}).light;return a===void 0?null:this._loadLight(a).then(function(l){return n._getNodeRef(t.cache,a,l)})}},id=class{static{d(this,"GLTFMaterialsUnlitExtension")}constructor(){this.name=ze.KHR_MATERIALS_UNLIT}getMaterialType(){return Ft}extendParams(e,t,n){let i=[];e.color=new Me(1,1,1),e.opacity=1;let s=t.pbrMetallicRoughness;if(s){if(Array.isArray(s.baseColorFactor)){let r=s.baseColorFactor;e.color.fromArray(r),e.opacity=r[3]}s.baseColorTexture!==void 0&&i.push(n.assignTexture(e,"map",s.baseColorTexture,Se))}return Promise.all(i)}},sd=class{static{d(this,"GLTFMaterialsEmissiveStrengthExtension")}constructor(e){this.parser=e,this.name=ze.KHR_MATERIALS_EMISSIVE_STRENGTH}extendMaterialParams(e,t){let i=this.parser.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();let s=i.extensions[this.name].emissiveStrength;return s!==void 0&&(t.emissiveIntensity=s),Promise.resolve()}},rd=class{static{d(this,"GLTFMaterialsClearcoatExtension")}constructor(e){this.parser=e,this.name=ze.KHR_MATERIALS_CLEARCOAT}getMaterialType(e){let n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:oi}extendMaterialParams(e,t){let n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();let s=[],r=i.extensions[this.name];if(r.clearcoatFactor!==void 0&&(t.clearcoat=r.clearcoatFactor),r.clearcoatTexture!==void 0&&s.push(n.assignTexture(t,"clearcoatMap",r.clearcoatTexture)),r.clearcoatRoughnessFactor!==void 0&&(t.clearcoatRoughness=r.clearcoatRoughnessFactor),r.clearcoatRoughnessTexture!==void 0&&s.push(n.assignTexture(t,"clearcoatRoughnessMap",r.clearcoatRoughnessTexture)),r.clearcoatNormalTexture!==void 0&&(s.push(n.assignTexture(t,"clearcoatNormalMap",r.clearcoatNormalTexture)),r.clearcoatNormalTexture.scale!==void 0)){let a=r.clearcoatNormalTexture.scale;t.clearcoatNormalScale=new Be(a,a)}return Promise.all(s)}},od=class{static{d(this,"GLTFMaterialsIridescenceExtension")}constructor(e){this.parser=e,this.name=ze.KHR_MATERIALS_IRIDESCENCE}getMaterialType(e){let n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:oi}extendMaterialParams(e,t){let n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();let s=[],r=i.extensions[this.name];return r.iridescenceFactor!==void 0&&(t.iridescence=r.iridescenceFactor),r.iridescenceTexture!==void 0&&s.push(n.assignTexture(t,"iridescenceMap",r.iridescenceTexture)),r.iridescenceIor!==void 0&&(t.iridescenceIOR=r.iridescenceIor),t.iridescenceThicknessRange===void 0&&(t.iridescenceThicknessRange=[100,400]),r.iridescenceThicknessMinimum!==void 0&&(t.iridescenceThicknessRange[0]=r.iridescenceThicknessMinimum),r.iridescenceThicknessMaximum!==void 0&&(t.iridescenceThicknessRange[1]=r.iridescenceThicknessMaximum),r.iridescenceThicknessTexture!==void 0&&s.push(n.assignTexture(t,"iridescenceThicknessMap",r.iridescenceThicknessTexture)),Promise.all(s)}},ad=class{static{d(this,"GLTFMaterialsSheenExtension")}constructor(e){this.parser=e,this.name=ze.KHR_MATERIALS_SHEEN}getMaterialType(e){let n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:oi}extendMaterialParams(e,t){let n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();let s=[];t.sheenColor=new Me(0,0,0),t.sheenRoughness=0,t.sheen=1;let r=i.extensions[this.name];return r.sheenColorFactor!==void 0&&t.sheenColor.fromArray(r.sheenColorFactor),r.sheenRoughnessFactor!==void 0&&(t.sheenRoughness=r.sheenRoughnessFactor),r.sheenColorTexture!==void 0&&s.push(n.assignTexture(t,"sheenColorMap",r.sheenColorTexture,Se)),r.sheenRoughnessTexture!==void 0&&s.push(n.assignTexture(t,"sheenRoughnessMap",r.sheenRoughnessTexture)),Promise.all(s)}},ld=class{static{d(this,"GLTFMaterialsTransmissionExtension")}constructor(e){this.parser=e,this.name=ze.KHR_MATERIALS_TRANSMISSION}getMaterialType(e){let n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:oi}extendMaterialParams(e,t){let n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();let s=[],r=i.extensions[this.name];return r.transmissionFactor!==void 0&&(t.transmission=r.transmissionFactor),r.transmissionTexture!==void 0&&s.push(n.assignTexture(t,"transmissionMap",r.transmissionTexture)),Promise.all(s)}},cd=class{static{d(this,"GLTFMaterialsVolumeExtension")}constructor(e){this.parser=e,this.name=ze.KHR_MATERIALS_VOLUME}getMaterialType(e){let n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:oi}extendMaterialParams(e,t){let n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();let s=[],r=i.extensions[this.name];t.thickness=r.thicknessFactor!==void 0?r.thicknessFactor:0,r.thicknessTexture!==void 0&&s.push(n.assignTexture(t,"thicknessMap",r.thicknessTexture)),t.attenuationDistance=r.attenuationDistance||1/0;let a=r.attenuationColor||[1,1,1];return t.attenuationColor=new Me(a[0],a[1],a[2]),Promise.all(s)}},hd=class{static{d(this,"GLTFMaterialsIorExtension")}constructor(e){this.parser=e,this.name=ze.KHR_MATERIALS_IOR}getMaterialType(e){let n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:oi}extendMaterialParams(e,t){let i=this.parser.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();let s=i.extensions[this.name];return t.ior=s.ior!==void 0?s.ior:1.5,Promise.resolve()}},ud=class{static{d(this,"GLTFMaterialsSpecularExtension")}constructor(e){this.parser=e,this.name=ze.KHR_MATERIALS_SPECULAR}getMaterialType(e){let n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:oi}extendMaterialParams(e,t){let n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();let s=[],r=i.extensions[this.name];t.specularIntensity=r.specularFactor!==void 0?r.specularFactor:1,r.specularTexture!==void 0&&s.push(n.assignTexture(t,"specularIntensityMap",r.specularTexture));let a=r.specularColorFactor||[1,1,1];return t.specularColor=new Me(a[0],a[1],a[2]),r.specularColorTexture!==void 0&&s.push(n.assignTexture(t,"specularColorMap",r.specularColorTexture,Se)),Promise.all(s)}},dd=class{static{d(this,"GLTFTextureBasisUExtension")}constructor(e){this.parser=e,this.name=ze.KHR_TEXTURE_BASISU}loadTexture(e){let t=this.parser,n=t.json,i=n.textures[e];if(!i.extensions||!i.extensions[this.name])return null;let s=i.extensions[this.name],r=t.options.ktx2Loader;if(!r){if(n.extensionsRequired&&n.extensionsRequired.indexOf(this.name)>=0)throw new Error("THREE.GLTFLoader: setKTX2Loader must be called before loading KTX2 textures");return null}return t.loadTextureImage(e,s.source,r)}},fd=class{static{d(this,"GLTFTextureWebPExtension")}constructor(e){this.parser=e,this.name=ze.EXT_TEXTURE_WEBP,this.isSupported=null}loadTexture(e){let t=this.name,n=this.parser,i=n.json,s=i.textures[e];if(!s.extensions||!s.extensions[t])return null;let r=s.extensions[t],a=i.images[r.source],l=n.textureLoader;if(a.uri){let c=n.options.manager.getHandler(a.uri);c!==null&&(l=c)}return this.detectSupport().then(function(c){if(c)return n.loadTextureImage(e,r.source,l);if(i.extensionsRequired&&i.extensionsRequired.indexOf(t)>=0)throw new Error("THREE.GLTFLoader: WebP required by asset but unsupported.");return n.loadTexture(e)})}detectSupport(){return this.isSupported||(this.isSupported=new Promise(function(e){let t=new Image;t.src="data:image/webp;base64,UklGRiIAAABXRUJQVlA4IBYAAAAwAQCdASoBAAEADsD+JaQAA3AAAAAA",t.onload=t.onerror=function(){e(t.height===1)}})),this.isSupported}},pd=class{static{d(this,"GLTFMeshoptCompression")}constructor(e){this.name=ze.EXT_MESHOPT_COMPRESSION,this.parser=e}loadBufferView(e){let t=this.parser.json,n=t.bufferViews[e];if(n.extensions&&n.extensions[this.name]){let i=n.extensions[this.name],s=this.parser.getDependency("buffer",i.buffer),r=this.parser.options.meshoptDecoder;if(!r||!r.supported){if(t.extensionsRequired&&t.extensionsRequired.indexOf(this.name)>=0)throw new Error("THREE.GLTFLoader: setMeshoptDecoder must be called before loading compressed files");return null}return s.then(function(a){let l=i.byteOffset||0,c=i.byteLength||0,h=i.count,u=i.byteStride,f=new Uint8Array(a,l,c);return r.decodeGltfBufferAsync?r.decodeGltfBufferAsync(h,u,f,i.mode,i.filter).then(function(p){return p.buffer}):r.ready.then(function(){let p=new ArrayBuffer(h*u);return r.decodeGltfBuffer(new Uint8Array(p),h,u,f,i.mode,i.filter),p})})}else return null}},Ad=class{static{d(this,"GLTFMeshGpuInstancing")}constructor(e){this.name=ze.EXT_MESH_GPU_INSTANCING,this.parser=e}createNodeMesh(e){let t=this.parser.json,n=t.nodes[e];if(!n.extensions||!n.extensions[this.name]||n.mesh===void 0)return null;let i=t.meshes[n.mesh];for(let c of i.primitives)if(c.mode!==Un.TRIANGLES&&c.mode!==Un.TRIANGLE_STRIP&&c.mode!==Un.TRIANGLE_FAN&&c.mode!==void 0)return null;let r=n.extensions[this.name].attributes,a=[],l={};for(let c in r)a.push(this.parser.getDependency("accessor",r[c]).then(h=>(l[c]=h,l[c])));return a.length<1?null:(a.push(this.parser.createNodeMesh(e)),Promise.all(a).then(c=>{let h=c.pop(),u=h.isGroup?h.children:[h],f=c[0].count,p=[];for(let g of u){let A=new Ie,m=new B,_=new Kt,E=new B(1,1,1),x=new Sl(g.geometry,g.material,f);for(let y=0;y<f;y++)l.TRANSLATION&&m.fromBufferAttribute(l.TRANSLATION,y),l.ROTATION&&_.fromBufferAttribute(l.ROTATION,y),l.SCALE&&E.fromBufferAttribute(l.SCALE,y),x.setMatrixAt(y,A.compose(m,_,E));for(let y in l)y!=="TRANSLATION"&&y!=="ROTATION"&&y!=="SCALE"&&g.geometry.setAttribute(y,l[y]);Ze.prototype.copy.call(x,g),x.frustumCulled=!1,this.parser.assignFinalMaterial(x),p.push(x)}return h.isGroup?(h.clear(),h.add(...p),h):p[0]}))}},Fm="glTF",ia=12,Bm={JSON:1313821514,BIN:5130562},md=class{static{d(this,"GLTFBinaryExtension")}constructor(e){this.name=ze.KHR_BINARY_GLTF,this.content=null,this.body=null;let t=new DataView(e,0,ia),n=new TextDecoder;if(this.header={magic:n.decode(new Uint8Array(e.slice(0,4))),version:t.getUint32(4,!0),length:t.getUint32(8,!0)},this.header.magic!==Fm)throw new Error("THREE.GLTFLoader: Unsupported glTF-Binary header.");if(this.header.version<2)throw new Error("THREE.GLTFLoader: Legacy binary file detected.");let i=this.header.length-ia,s=new DataView(e,ia),r=0;for(;r<i;){let a=s.getUint32(r,!0);r+=4;let l=s.getUint32(r,!0);if(r+=4,l===Bm.JSON){let c=new Uint8Array(e,ia+r,a);this.content=n.decode(c)}else if(l===Bm.BIN){let c=ia+r;this.body=e.slice(c,c+a)}r+=a}if(this.content===null)throw new Error("THREE.GLTFLoader: JSON content not found.")}},gd=class{static{d(this,"GLTFDracoMeshCompressionExtension")}constructor(e,t){if(!t)throw new Error("THREE.GLTFLoader: No DRACOLoader instance provided.");this.name=ze.KHR_DRACO_MESH_COMPRESSION,this.json=e,this.dracoLoader=t,this.dracoLoader.preload()}decodePrimitive(e,t){let n=this.json,i=this.dracoLoader,s=e.extensions[this.name].bufferView,r=e.extensions[this.name].attributes,a={},l={},c={};for(let h in r){let u=vd[h]||h.toLowerCase();a[u]=r[h]}for(let h in e.attributes){let u=vd[h]||h.toLowerCase();if(r[h]!==void 0){let f=n.accessors[e.attributes[h]],p=Dr[f.componentType];c[u]=p.name,l[u]=f.normalized===!0}}return t.getDependency("bufferView",s).then(function(h){return new Promise(function(u){i.decodeDracoFile(h,function(f){for(let p in f.attributes){let g=f.attributes[p],A=l[p];A!==void 0&&(g.normalized=A)}u(f)},a,c)})})}},_d=class{static{d(this,"GLTFTextureTransformExtension")}constructor(){this.name=ze.KHR_TEXTURE_TRANSFORM}extendTexture(e,t){return t.texCoord!==void 0&&console.warn('THREE.GLTFLoader: Custom UV sets in "'+this.name+'" extension not yet supported.'),t.offset===void 0&&t.rotation===void 0&&t.scale===void 0||(e=e.clone(),t.offset!==void 0&&e.offset.fromArray(t.offset),t.rotation!==void 0&&(e.rotation=t.rotation),t.scale!==void 0&&e.repeat.fromArray(t.scale),e.needsUpdate=!0),e}},yd=class{static{d(this,"GLTFMeshQuantizationExtension")}constructor(){this.name=ze.KHR_MESH_QUANTIZATION}},rc=class extends Hi{static{d(this,"GLTFCubicSplineInterpolant")}constructor(e,t,n,i){super(e,t,n,i)}copySampleValue_(e){let t=this.resultBuffer,n=this.sampleValues,i=this.valueSize,s=e*i*3+i;for(let r=0;r!==i;r++)t[r]=n[s+r];return t}interpolate_(e,t,n,i){let s=this.resultBuffer,r=this.sampleValues,a=this.valueSize,l=a*2,c=a*3,h=i-t,u=(n-t)/h,f=u*u,p=f*u,g=e*c,A=g-c,m=-2*p+3*f,_=p-f,E=1-m,x=_-f+u;for(let y=0;y!==a;y++){let w=r[A+y+a],I=r[A+y+l]*h,S=r[g+y+a],v=r[g+y]*h;s[y]=E*w+x*I+m*S+_*v}return s}},Sb=new Kt,xd=class extends rc{static{d(this,"GLTFCubicSplineQuaternionInterpolant")}interpolate_(e,t,n,i){let s=super.interpolate_(e,t,n,i);return Sb.fromArray(s).normalize().toArray(s),s}},Un={FLOAT:5126,FLOAT_MAT3:35675,FLOAT_MAT4:35676,FLOAT_VEC2:35664,FLOAT_VEC3:35665,FLOAT_VEC4:35666,LINEAR:9729,REPEAT:10497,SAMPLER_2D:35678,POINTS:0,LINES:1,LINE_LOOP:2,LINE_STRIP:3,TRIANGLES:4,TRIANGLE_STRIP:5,TRIANGLE_FAN:6,UNSIGNED_BYTE:5121,UNSIGNED_SHORT:5123},Dr={5120:Int8Array,5121:Uint8Array,5122:Int16Array,5123:Uint16Array,5125:Uint32Array,5126:Float32Array},Rm={9728:ct,9729:Je,9984:rr,9985:Wo,9986:_s,9987:wn},Dm={33071:Lt,33648:vs,10497:Pn},ed={SCALAR:1,VEC2:2,VEC3:3,VEC4:4,MAT2:4,MAT3:9,MAT4:16},vd={POSITION:"position",NORMAL:"normal",TANGENT:"tangent",TEXCOORD_0:"uv",TEXCOORD_1:"uv2",COLOR_0:"color",WEIGHTS_0:"skinWeight",JOINTS_0:"skinIndex"},Zi={scale:"scale",translation:"position",rotation:"quaternion",weights:"morphTargetInfluences"},Tb={CUBICSPLINE:void 0,LINEAR:wi,STEP:zi},td={OPAQUE:"OPAQUE",MASK:"MASK",BLEND:"BLEND"};function Bb(o){return o.DefaultMaterial===void 0&&(o.DefaultMaterial=new On({color:16777215,emissive:0,metalness:1,roughness:1,transparent:!1,depthTest:!0,side:fn})),o.DefaultMaterial}d(Bb,"createDefaultMaterial");function sa(o,e,t){for(let n in t.extensions)o[n]===void 0&&(e.userData.gltfExtensions=e.userData.gltfExtensions||{},e.userData.gltfExtensions[n]=t.extensions[n])}d(sa,"addUnknownExtensionsToUserData");function es(o,e){e.extras!==void 0&&(typeof e.extras=="object"?Object.assign(o.userData,e.extras):console.warn("THREE.GLTFLoader: Ignoring primitive type .extras, "+e.extras))}d(es,"assignExtrasToUserData");function Rb(o,e,t){let n=!1,i=!1,s=!1;for(let c=0,h=e.length;c<h;c++){let u=e[c];if(u.POSITION!==void 0&&(n=!0),u.NORMAL!==void 0&&(i=!0),u.COLOR_0!==void 0&&(s=!0),n&&i&&s)break}if(!n&&!i&&!s)return Promise.resolve(o);let r=[],a=[],l=[];for(let c=0,h=e.length;c<h;c++){let u=e[c];if(n){let f=u.POSITION!==void 0?t.getDependency("accessor",u.POSITION):o.attributes.position;r.push(f)}if(i){let f=u.NORMAL!==void 0?t.getDependency("accessor",u.NORMAL):o.attributes.normal;a.push(f)}if(s){let f=u.COLOR_0!==void 0?t.getDependency("accessor",u.COLOR_0):o.attributes.color;l.push(f)}}return Promise.all([Promise.all(r),Promise.all(a),Promise.all(l)]).then(function(c){let h=c[0],u=c[1],f=c[2];return n&&(o.morphAttributes.position=h),i&&(o.morphAttributes.normal=u),s&&(o.morphAttributes.color=f),o.morphTargetsRelative=!0,o})}d(Rb,"addMorphTargets");function Db(o,e){if(o.updateMorphTargets(),e.weights!==void 0)for(let t=0,n=e.weights.length;t<n;t++)o.morphTargetInfluences[t]=e.weights[t];if(e.extras&&Array.isArray(e.extras.targetNames)){let t=e.extras.targetNames;if(o.morphTargetInfluences.length===t.length){o.morphTargetDictionary={};for(let n=0,i=t.length;n<i;n++)o.morphTargetDictionary[t[n]]=n}else console.warn("THREE.GLTFLoader: Invalid extras.targetNames length. Ignoring names.")}}d(Db,"updateMorphTargets");function Lb(o){let e=o.extensions&&o.extensions[ze.KHR_DRACO_MESH_COMPRESSION],t;return e?t="draco:"+e.bufferView+":"+e.indices+":"+Lm(e.attributes):t=o.indices+":"+Lm(o.attributes)+":"+o.mode,t}d(Lb,"createPrimitiveKey");function Lm(o){let e="",t=Object.keys(o).sort();for(let n=0,i=t.length;n<i;n++)e+=t[n]+":"+o[t[n]]+";";return e}d(Lm,"createAttributesKey");function Ed(o){switch(o){case Int8Array:return 1/127;case Uint8Array:return 1/255;case Int16Array:return 1/32767;case Uint16Array:return 1/65535;default:throw new Error("THREE.GLTFLoader: Unsupported normalized accessor component type.")}}d(Ed,"getNormalizedComponentScale");function Pb(o){return o.search(/\.jpe?g($|\?)/i)>0||o.search(/^data\:image\/jpeg/)===0?"image/jpeg":o.search(/\.webp($|\?)/i)>0||o.search(/^data\:image\/webp/)===0?"image/webp":"image/png"}d(Pb,"getImageURIMimeType");var Fb=new Ie,wd=class{static{d(this,"GLTFParser")}constructor(e={},t={}){this.json=e,this.extensions={},this.plugins={},this.options=t,this.cache=new Cb,this.associations=new Map,this.primitiveCache={},this.meshCache={refs:{},uses:{}},this.cameraCache={refs:{},uses:{}},this.lightCache={refs:{},uses:{}},this.sourceCache={},this.textureCache={},this.nodeNamesUsed={};let n=!1,i=!1,s=-1;typeof navigator<"u"&&(n=/^((?!chrome|android).)*safari/i.test(navigator.userAgent)===!0,i=navigator.userAgent.indexOf("Firefox")>-1,s=i?navigator.userAgent.match(/Firefox\/([0-9]+)\./)[1]:-1),typeof createImageBitmap>"u"||n||i&&s<98?this.textureLoader=new Ar(this.options.manager):this.textureLoader=new Ql(this.options.manager),this.textureLoader.setCrossOrigin(this.options.crossOrigin),this.textureLoader.setRequestHeader(this.options.requestHeader),this.fileLoader=new An(this.options.manager),this.fileLoader.setResponseType("arraybuffer"),this.options.crossOrigin==="use-credentials"&&this.fileLoader.setWithCredentials(!0)}setExtensions(e){this.extensions=e}setPlugins(e){this.plugins=e}parse(e,t){let n=this,i=this.json,s=this.extensions;this.cache.removeAll(),this._invokeAll(function(r){return r._markDefs&&r._markDefs()}),Promise.all(this._invokeAll(function(r){return r.beforeRoot&&r.beforeRoot()})).then(function(){return Promise.all([n.getDependencies("scene"),n.getDependencies("animation"),n.getDependencies("camera")])}).then(function(r){let a={scene:r[0][i.scene||0],scenes:r[0],animations:r[1],cameras:r[2],asset:i.asset,parser:n,userData:{}};sa(s,a,i),es(a,i),Promise.all(n._invokeAll(function(l){return l.afterRoot&&l.afterRoot(a)})).then(function(){e(a)})}).catch(t)}_markDefs(){let e=this.json.nodes||[],t=this.json.skins||[],n=this.json.meshes||[];for(let i=0,s=t.length;i<s;i++){let r=t[i].joints;for(let a=0,l=r.length;a<l;a++)e[r[a]].isBone=!0}for(let i=0,s=e.length;i<s;i++){let r=e[i];r.mesh!==void 0&&(this._addNodeRef(this.meshCache,r.mesh),r.skin!==void 0&&(n[r.mesh].isSkinnedMesh=!0)),r.camera!==void 0&&this._addNodeRef(this.cameraCache,r.camera)}}_addNodeRef(e,t){t!==void 0&&(e.refs[t]===void 0&&(e.refs[t]=e.uses[t]=0),e.refs[t]++)}_getNodeRef(e,t,n){if(e.refs[t]<=1)return n;let i=n.clone(),s=d((r,a)=>{let l=this.associations.get(r);l!=null&&this.associations.set(a,l);for(let[c,h]of r.children.entries())s(h,a.children[c])},"updateMappings");return s(n,i),i.name+="_instance_"+e.uses[t]++,i}_invokeOne(e){let t=Object.values(this.plugins);t.push(this);for(let n=0;n<t.length;n++){let i=e(t[n]);if(i)return i}return null}_invokeAll(e){let t=Object.values(this.plugins);t.unshift(this);let n=[];for(let i=0;i<t.length;i++){let s=e(t[i]);s&&n.push(s)}return n}getDependency(e,t){let n=e+":"+t,i=this.cache.get(n);if(!i){switch(e){case"scene":i=this.loadScene(t);break;case"node":i=this._invokeOne(function(s){return s.loadNode&&s.loadNode(t)});break;case"mesh":i=this._invokeOne(function(s){return s.loadMesh&&s.loadMesh(t)});break;case"accessor":i=this.loadAccessor(t);break;case"bufferView":i=this._invokeOne(function(s){return s.loadBufferView&&s.loadBufferView(t)});break;case"buffer":i=this.loadBuffer(t);break;case"material":i=this._invokeOne(function(s){return s.loadMaterial&&s.loadMaterial(t)});break;case"texture":i=this._invokeOne(function(s){return s.loadTexture&&s.loadTexture(t)});break;case"skin":i=this.loadSkin(t);break;case"animation":i=this._invokeOne(function(s){return s.loadAnimation&&s.loadAnimation(t)});break;case"camera":i=this.loadCamera(t);break;default:if(i=this._invokeOne(function(s){return s!=this&&s.getDependency&&s.getDependency(e,t)}),!i)throw new Error("Unknown type: "+e);break}this.cache.add(n,i)}return i}getDependencies(e){let t=this.cache.get(e);if(!t){let n=this,i=this.json[e+(e==="mesh"?"es":"s")]||[];t=Promise.all(i.map(function(s,r){return n.getDependency(e,r)})),this.cache.add(e,t)}return t}loadBuffer(e){let t=this.json.buffers[e],n=this.fileLoader;if(t.type&&t.type!=="arraybuffer")throw new Error("THREE.GLTFLoader: "+t.type+" buffer type is not supported.");if(t.uri===void 0&&e===0)return Promise.resolve(this.extensions[ze.KHR_BINARY_GLTF].body);let i=this.options;return new Promise(function(s,r){n.load(_r.resolveURL(t.uri,i.path),s,void 0,function(){r(new Error('THREE.GLTFLoader: Failed to load buffer "'+t.uri+'".'))})})}loadBufferView(e){let t=this.json.bufferViews[e];return this.getDependency("buffer",t.buffer).then(function(n){let i=t.byteLength||0,s=t.byteOffset||0;return n.slice(s,s+i)})}loadAccessor(e){let t=this,n=this.json,i=this.json.accessors[e];if(i.bufferView===void 0&&i.sparse===void 0){let r=ed[i.type],a=Dr[i.componentType],l=i.normalized===!0,c=new a(i.count*r);return Promise.resolve(new je(c,r,l))}let s=[];return i.bufferView!==void 0?s.push(this.getDependency("bufferView",i.bufferView)):s.push(null),i.sparse!==void 0&&(s.push(this.getDependency("bufferView",i.sparse.indices.bufferView)),s.push(this.getDependency("bufferView",i.sparse.values.bufferView))),Promise.all(s).then(function(r){let a=r[0],l=ed[i.type],c=Dr[i.componentType],h=c.BYTES_PER_ELEMENT,u=h*l,f=i.byteOffset||0,p=i.bufferView!==void 0?n.bufferViews[i.bufferView].byteStride:void 0,g=i.normalized===!0,A,m;if(p&&p!==u){let _=Math.floor(f/p),E="InterleavedBuffer:"+i.bufferView+":"+i.componentType+":"+_+":"+i.count,x=t.cache.get(E);x||(A=new c(a,_*p,i.count*p/h),x=new Oo(A,p/h),t.cache.add(E,x)),m=new No(x,l,f%p/h,g)}else a===null?A=new c(i.count*l):A=new c(a,f,i.count*l),m=new je(A,l,g);if(i.sparse!==void 0){let _=ed.SCALAR,E=Dr[i.sparse.indices.componentType],x=i.sparse.indices.byteOffset||0,y=i.sparse.values.byteOffset||0,w=new E(r[1],x,i.sparse.count*_),I=new c(r[2],y,i.sparse.count*l);a!==null&&(m=new je(m.array.slice(),m.itemSize,m.normalized));for(let S=0,v=w.length;S<v;S++){let b=w[S];if(m.setX(b,I[S*l]),l>=2&&m.setY(b,I[S*l+1]),l>=3&&m.setZ(b,I[S*l+2]),l>=4&&m.setW(b,I[S*l+3]),l>=5)throw new Error("THREE.GLTFLoader: Unsupported itemSize in sparse BufferAttribute.")}}return m})}loadTexture(e){let t=this.json,n=this.options,s=t.textures[e].source,r=t.images[s],a=this.textureLoader;if(r.uri){let l=n.manager.getHandler(r.uri);l!==null&&(a=l)}return this.loadTextureImage(e,s,a)}loadTextureImage(e,t,n){let i=this,s=this.json,r=s.textures[e],a=s.images[t],l=(a.uri||a.bufferView)+":"+r.sampler;if(this.textureCache[l])return this.textureCache[l];let c=this.loadImageSource(t,n).then(function(h){h.flipY=!1,h.name=r.name||a.name||"";let f=(s.samplers||{})[r.sampler]||{};return h.magFilter=Rm[f.magFilter]||Je,h.minFilter=Rm[f.minFilter]||wn,h.wrapS=Dm[f.wrapS]||Pn,h.wrapT=Dm[f.wrapT]||Pn,i.associations.set(h,{textures:e}),h}).catch(function(){return null});return this.textureCache[l]=c,c}loadImageSource(e,t){let n=this,i=this.json,s=this.options;if(this.sourceCache[e]!==void 0)return this.sourceCache[e].then(u=>u.clone());let r=i.images[e],a=self.URL||self.webkitURL,l=r.uri||"",c=!1;if(r.bufferView!==void 0)l=n.getDependency("bufferView",r.bufferView).then(function(u){c=!0;let f=new Blob([u],{type:r.mimeType});return l=a.createObjectURL(f),l});else if(r.uri===void 0)throw new Error("THREE.GLTFLoader: Image "+e+" is missing URI and bufferView");let h=Promise.resolve(l).then(function(u){return new Promise(function(f,p){let g=f;t.isImageBitmapLoader===!0&&(g=d(function(A){let m=new st(A);m.needsUpdate=!0,f(m)},"onLoad")),t.load(_r.resolveURL(u,s.path),g,void 0,p)})}).then(function(u){return c===!0&&a.revokeObjectURL(l),u.userData.mimeType=r.mimeType||Pb(r.uri),u}).catch(function(u){throw console.error("THREE.GLTFLoader: Couldn't load texture",l),u});return this.sourceCache[e]=h,h}assignTexture(e,t,n,i){let s=this;return this.getDependency("texture",n.index).then(function(r){if(!r)return null;if(n.texCoord!==void 0&&n.texCoord!=0&&!(t==="aoMap"&&n.texCoord==1)&&console.warn("THREE.GLTFLoader: Custom UV set "+n.texCoord+" for texture "+t+" not yet supported."),s.extensions[ze.KHR_TEXTURE_TRANSFORM]){let a=n.extensions!==void 0?n.extensions[ze.KHR_TEXTURE_TRANSFORM]:void 0;if(a){let l=s.associations.get(r);r=s.extensions[ze.KHR_TEXTURE_TRANSFORM].extendTexture(r,a),s.associations.set(r,l)}}return i!==void 0&&(r.encoding=i),e[t]=r,r})}assignFinalMaterial(e){let t=e.geometry,n=e.material,i=t.attributes.tangent===void 0,s=t.attributes.color!==void 0,r=t.attributes.normal===void 0;if(e.isPoints){let a="PointsMaterial:"+n.uuid,l=this.cache.get(a);l||(l=new Go,sn.prototype.copy.call(l,n),l.color.copy(n.color),l.map=n.map,l.sizeAttenuation=!1,this.cache.add(a,l)),n=l}else if(e.isLine){let a="LineBasicMaterial:"+n.uuid,l=this.cache.get(a);l||(l=new ko,sn.prototype.copy.call(l,n),l.color.copy(n.color),this.cache.add(a,l)),n=l}if(i||s||r){let a="ClonedMaterial:"+n.uuid+":";i&&(a+="derivative-tangents:"),s&&(a+="vertex-colors:"),r&&(a+="flat-shading:");let l=this.cache.get(a);l||(l=n.clone(),s&&(l.vertexColors=!0),r&&(l.flatShading=!0),i&&(l.normalScale&&(l.normalScale.y*=-1),l.clearcoatNormalScale&&(l.clearcoatNormalScale.y*=-1)),this.cache.add(a,l),this.associations.set(l,this.associations.get(n))),n=l}n.aoMap&&t.attributes.uv2===void 0&&t.attributes.uv!==void 0&&t.setAttribute("uv2",t.attributes.uv),e.material=n}getMaterialType(){return On}loadMaterial(e){let t=this,n=this.json,i=this.extensions,s=n.materials[e],r,a={},l=s.extensions||{},c=[];if(l[ze.KHR_MATERIALS_UNLIT]){let u=i[ze.KHR_MATERIALS_UNLIT];r=u.getMaterialType(),c.push(u.extendParams(a,s,t))}else{let u=s.pbrMetallicRoughness||{};if(a.color=new Me(1,1,1),a.opacity=1,Array.isArray(u.baseColorFactor)){let f=u.baseColorFactor;a.color.fromArray(f),a.opacity=f[3]}u.baseColorTexture!==void 0&&c.push(t.assignTexture(a,"map",u.baseColorTexture,Se)),a.metalness=u.metallicFactor!==void 0?u.metallicFactor:1,a.roughness=u.roughnessFactor!==void 0?u.roughnessFactor:1,u.metallicRoughnessTexture!==void 0&&(c.push(t.assignTexture(a,"metalnessMap",u.metallicRoughnessTexture)),c.push(t.assignTexture(a,"roughnessMap",u.metallicRoughnessTexture))),r=this._invokeOne(function(f){return f.getMaterialType&&f.getMaterialType(e)}),c.push(Promise.all(this._invokeAll(function(f){return f.extendMaterialParams&&f.extendMaterialParams(e,a)})))}s.doubleSided===!0&&(a.side=Et);let h=s.alphaMode||td.OPAQUE;if(h===td.BLEND?(a.transparent=!0,a.depthWrite=!1):(a.transparent=!1,h===td.MASK&&(a.alphaTest=s.alphaCutoff!==void 0?s.alphaCutoff:.5)),s.normalTexture!==void 0&&r!==Ft&&(c.push(t.assignTexture(a,"normalMap",s.normalTexture)),a.normalScale=new Be(1,1),s.normalTexture.scale!==void 0)){let u=s.normalTexture.scale;a.normalScale.set(u,u)}return s.occlusionTexture!==void 0&&r!==Ft&&(c.push(t.assignTexture(a,"aoMap",s.occlusionTexture)),s.occlusionTexture.strength!==void 0&&(a.aoMapIntensity=s.occlusionTexture.strength)),s.emissiveFactor!==void 0&&r!==Ft&&(a.emissive=new Me().fromArray(s.emissiveFactor)),s.emissiveTexture!==void 0&&r!==Ft&&c.push(t.assignTexture(a,"emissiveMap",s.emissiveTexture,Se)),Promise.all(c).then(function(){let u=new r(a);return s.name&&(u.name=s.name),es(u,s),t.associations.set(u,{materials:e}),s.extensions&&sa(i,u,s),u})}createUniqueName(e){let t=We.sanitizeNodeName(e||""),n=t;for(let i=1;this.nodeNamesUsed[n];++i)n=t+"_"+i;return this.nodeNamesUsed[n]=!0,n}loadGeometries(e){let t=this,n=this.extensions,i=this.primitiveCache;function s(a){return n[ze.KHR_DRACO_MESH_COMPRESSION].decodePrimitive(a,t).then(function(l){return Pm(l,a,t)})}d(s,"createDracoPrimitive");let r=[];for(let a=0,l=e.length;a<l;a++){let c=e[a],h=Lb(c),u=i[h];if(u)r.push(u.promise);else{let f;c.extensions&&c.extensions[ze.KHR_DRACO_MESH_COMPRESSION]?f=s(c):f=Pm(new kt,c,t),i[h]={primitive:c,promise:f},r.push(f)}}return Promise.all(r)}loadMesh(e){let t=this,n=this.json,i=this.extensions,s=n.meshes[e],r=s.primitives,a=[];for(let l=0,c=r.length;l<c;l++){let h=r[l].material===void 0?Bb(this.cache):this.getDependency("material",r[l].material);a.push(h)}return a.push(t.loadGeometries(r)),Promise.all(a).then(function(l){let c=l.slice(0,l.length-1),h=l[l.length-1],u=[];for(let p=0,g=h.length;p<g;p++){let A=h[p],m=r[p],_,E=c[p];if(m.mode===Un.TRIANGLES||m.mode===Un.TRIANGLE_STRIP||m.mode===Un.TRIANGLE_FAN||m.mode===void 0)_=s.isSkinnedMesh===!0?new Il(A,E):new pe(A,E),_.isSkinnedMesh===!0&&!_.geometry.attributes.skinWeight.normalized&&_.normalizeSkinWeights(),m.mode===Un.TRIANGLE_STRIP?_.geometry=Zu(_.geometry,Vl):m.mode===Un.TRIANGLE_FAN&&(_.geometry=Zu(_.geometry,$o));else if(m.mode===Un.LINES)_=new Tl(A,E);else if(m.mode===Un.LINE_STRIP)_=new dr(A,E);else if(m.mode===Un.LINE_LOOP)_=new Bl(A,E);else if(m.mode===Un.POINTS)_=new Rl(A,E);else throw new Error("THREE.GLTFLoader: Primitive mode unsupported: "+m.mode);Object.keys(_.geometry.morphAttributes).length>0&&Db(_,s),_.name=t.createUniqueName(s.name||"mesh_"+e),es(_,s),m.extensions&&sa(i,_,m),t.assignFinalMaterial(_),u.push(_)}for(let p=0,g=u.length;p<g;p++)t.associations.set(u[p],{meshes:e,primitives:p});if(u.length===1)return u[0];let f=new En;t.associations.set(f,{meshes:e});for(let p=0,g=u.length;p<g;p++)f.add(u[p]);return f})}loadCamera(e){let t,n=this.json.cameras[e],i=n[n.type];if(!i){console.warn("THREE.GLTFLoader: Missing camera parameters.");return}return n.type==="perspective"?t=new ht(vr.radToDeg(i.yfov),i.aspectRatio||1,i.znear||1,i.zfar||2e6):n.type==="orthographic"&&(t=new Fn(-i.xmag,i.xmag,i.ymag,-i.ymag,i.znear,i.zfar)),n.name&&(t.name=this.createUniqueName(n.name)),es(t,n),Promise.resolve(t)}loadSkin(e){let t=this.json.skins[e],n=[];for(let i=0,s=t.joints.length;i<s;i++)n.push(this.getDependency("node",t.joints[i]));return t.inverseBindMatrices!==void 0?n.push(this.getDependency("accessor",t.inverseBindMatrices)):n.push(null),Promise.all(n).then(function(i){let s=i.pop(),r=i,a=[],l=[];for(let c=0,h=r.length;c<h;c++){let u=r[c];if(u){a.push(u);let f=new Ie;s!==null&&f.fromArray(s.array,c*16),l.push(f)}else console.warn('THREE.GLTFLoader: Joint "%s" could not be found.',t.joints[c])}return new Cl(a,l)})}loadAnimation(e){let n=this.json.animations[e],i=[],s=[],r=[],a=[],l=[];for(let c=0,h=n.channels.length;c<h;c++){let u=n.channels[c],f=n.samplers[u.sampler],p=u.target,g=p.node,A=n.parameters!==void 0?n.parameters[f.input]:f.input,m=n.parameters!==void 0?n.parameters[f.output]:f.output;i.push(this.getDependency("node",g)),s.push(this.getDependency("accessor",A)),r.push(this.getDependency("accessor",m)),a.push(f),l.push(p)}return Promise.all([Promise.all(i),Promise.all(s),Promise.all(r),Promise.all(a),Promise.all(l)]).then(function(c){let h=c[0],u=c[1],f=c[2],p=c[3],g=c[4],A=[];for(let _=0,E=h.length;_<E;_++){let x=h[_],y=u[_],w=f[_],I=p[_],S=g[_];if(x===void 0)continue;x.updateMatrix();let v;switch(Zi[S.path]){case Zi.weights:v=qi;break;case Zi.rotation:v=ai;break;case Zi.position:case Zi.scale:default:v=$i;break}let b=x.name?x.name:x.uuid,R=I.interpolation!==void 0?Tb[I.interpolation]:wi,N=[];Zi[S.path]===Zi.weights?x.traverse(function(O){O.morphTargetInfluences&&N.push(O.name?O.name:O.uuid)}):N.push(b);let z=w.array;if(w.normalized){let O=Ed(z.constructor),D=new Float32Array(z.length);for(let Q=0,q=z.length;Q<q;Q++)D[Q]=z[Q]*O;z=D}for(let O=0,D=N.length;O<D;O++){let Q=new v(N[O]+"."+Zi[S.path],y.array,z,R);I.interpolation==="CUBICSPLINE"&&(Q.createInterpolant=d(function(H){let k=this instanceof ai?xd:rc;return new k(this.times,this.values,this.getValueSize()/3,H)},"InterpolantFactoryMethodGLTFCubicSpline"),Q.createInterpolant.isInterpolantFactoryMethodGLTFCubicSpline=!0),A.push(Q)}}let m=n.name?n.name:"animation_"+e;return new fr(m,void 0,A)})}createNodeMesh(e){let t=this.json,n=this,i=t.nodes[e];return i.mesh===void 0?null:n.getDependency("mesh",i.mesh).then(function(s){let r=n._getNodeRef(n.meshCache,i.mesh,s);return i.weights!==void 0&&r.traverse(function(a){if(a.isMesh)for(let l=0,c=i.weights.length;l<c;l++)a.morphTargetInfluences[l]=i.weights[l]}),r})}loadNode(e){let t=this.json,n=this.extensions,i=this,s=t.nodes[e],r=s.name?i.createUniqueName(s.name):"";return function(){let a=[],l=i._invokeOne(function(f){return f.createNodeMesh&&f.createNodeMesh(e)});l&&a.push(l),s.camera!==void 0&&a.push(i.getDependency("camera",s.camera).then(function(f){return i._getNodeRef(i.cameraCache,s.camera,f)})),i._invokeAll(function(f){return f.createNodeAttachment&&f.createNodeAttachment(e)}).forEach(function(f){a.push(f)});let c=[],h=s.children||[];for(let f=0,p=h.length;f<p;f++)c.push(i.getDependency("node",h[f]));let u=s.skin===void 0?Promise.resolve(null):i.getDependency("skin",s.skin);return Promise.all([Promise.all(a),Promise.all(c),u])}().then(function(a){let l=a[0],c=a[1],h=a[2],u;if(s.isBone===!0?u=new Uo:l.length>1?u=new En:l.length===1?u=l[0]:u=new Ze,u!==l[0])for(let f=0,p=l.length;f<p;f++)u.add(l[f]);if(s.name&&(u.userData.name=s.name,u.name=r),es(u,s),s.extensions&&sa(n,u,s),s.matrix!==void 0){let f=new Ie;f.fromArray(s.matrix),u.applyMatrix4(f)}else s.translation!==void 0&&u.position.fromArray(s.translation),s.rotation!==void 0&&u.quaternion.fromArray(s.rotation),s.scale!==void 0&&u.scale.fromArray(s.scale);i.associations.has(u)||i.associations.set(u,{}),i.associations.get(u).nodes=e,h!==null&&u.traverse(function(f){f.isSkinnedMesh&&f.bind(h,Fb)});for(let f=0,p=c.length;f<p;f++)u.add(c[f]);return u})}loadScene(e){let t=this.extensions,n=this.json.scenes[e],i=this,s=new En;n.name&&(s.name=i.createUniqueName(n.name)),es(s,n),n.extensions&&sa(t,s,n);let r=n.nodes||[],a=[];for(let l=0,c=r.length;l<c;l++)a.push(i.getDependency("node",r[l]));return Promise.all(a).then(function(l){for(let h=0,u=l.length;h<u;h++)s.add(l[h]);let c=d(h=>{let u=new Map;for(let[f,p]of i.associations)(f instanceof sn||f instanceof st)&&u.set(f,p);return h.traverse(f=>{let p=i.associations.get(f);p!=null&&u.set(f,p)}),u},"reduceAssociations");return i.associations=c(s),s})}};function Ob(o,e,t){let n=e.attributes,i=new Qt;if(n.POSITION!==void 0){let a=t.json.accessors[n.POSITION],l=a.min,c=a.max;if(l!==void 0&&c!==void 0){if(i.set(new B(l[0],l[1],l[2]),new B(c[0],c[1],c[2])),a.normalized){let h=Ed(Dr[a.componentType]);i.min.multiplyScalar(h),i.max.multiplyScalar(h)}}else{console.warn("THREE.GLTFLoader: Missing min/max properties for accessor POSITION.");return}}else return;let s=e.targets;if(s!==void 0){let a=new B,l=new B;for(let c=0,h=s.length;c<h;c++){let u=s[c];if(u.POSITION!==void 0){let f=t.json.accessors[u.POSITION],p=f.min,g=f.max;if(p!==void 0&&g!==void 0){if(l.setX(Math.max(Math.abs(p[0]),Math.abs(g[0]))),l.setY(Math.max(Math.abs(p[1]),Math.abs(g[1]))),l.setZ(Math.max(Math.abs(p[2]),Math.abs(g[2]))),f.normalized){let A=Ed(Dr[f.componentType]);l.multiplyScalar(A)}a.max(l)}else console.warn("THREE.GLTFLoader: Missing min/max properties for accessor POSITION.")}}i.expandByVector(a)}o.boundingBox=i;let r=new Mn;i.getCenter(r.center),r.radius=i.min.distanceTo(i.max)/2,o.boundingSphere=r}d(Ob,"computeBounds");function Pm(o,e,t){let n=e.attributes,i=[];function s(r,a){return t.getDependency("accessor",r).then(function(l){o.setAttribute(a,l)})}d(s,"assignAttributeAccessor");for(let r in n){let a=vd[r]||r.toLowerCase();a in o.attributes||i.push(s(n[r],a))}if(e.indices!==void 0&&!o.index){let r=t.getDependency("accessor",e.indices).then(function(a){o.setIndex(a)});i.push(r)}return es(o,e),Ob(o,e,t),Promise.all(i).then(function(){return e.targets!==void 0?Rb(o,e.targets,t):o})}d(Pm,"addPrimitiveAttributes");L();P();L();P();var oc=class{static{d(this,"WorkerPool")}constructor(e=4){this.pool=e,this.queue=[],this.workers=[],this.workersResolve=[],this.workerStatus=0}_initWorker(e){if(!this.workers[e]){let t=this.workerCreator();t.addEventListener("message",this._onMessage.bind(this,e)),this.workers[e]=t}}_getIdleWorker(){for(let e=0;e<this.pool;e++)if(!(this.workerStatus&1<<e))return e;return-1}_onMessage(e,t){let n=this.workersResolve[e];if(n&&n(t),this.queue.length){let{resolve:i,msg:s,transfer:r}=this.queue.shift();this.workersResolve[e]=i,this.workers[e].postMessage(s,r)}else this.workerStatus^=1<<e}setWorkerCreator(e){this.workerCreator=e}setWorkerLimit(e){this.pool=e}postMessage(e,t){return new Promise(n=>{let i=this._getIdleWorker();i!==-1?(this._initWorker(i),this.workerStatus|=1<<i,this.workersResolve[i]=n,this.workers[i].postMessage(e,t)):this.queue.push({resolve:n,msg:e,transfer:t})})}dispose(){this.workers.forEach(e=>e.terminate()),this.workersResolve.length=0,this.workers.length=0,this.queue.length=0,this.workerStatus=0}};L();P();var Md=class{static{d(this,"Si")}constructor(){this.vkFormat=0,this.typeSize=1,this.pixelWidth=0,this.pixelHeight=0,this.pixelDepth=0,this.layerCount=0,this.faceCount=1,this.supercompressionScheme=0,this.levels=[],this.dataFormatDescriptor=[{vendorId:0,descriptorType:0,descriptorBlockSize:0,versionNumber:2,colorModel:0,colorPrimaries:1,transferFunction:2,flags:0,texelBlockDimension:[0,0,0,0],bytesPlane:[0,0,0,0,0,0,0,0],samples:[]}],this.keyValue={},this.globalData=null}},bs=class{static{d(this,"Ii")}constructor(e,t,n,i){this._dataView=new DataView(e.buffer,e.byteOffset+t,n),this._littleEndian=i,this._offset=0}_nextUint8(){let e=this._dataView.getUint8(this._offset);return this._offset+=1,e}_nextUint16(){let e=this._dataView.getUint16(this._offset,this._littleEndian);return this._offset+=2,e}_nextUint32(){let e=this._dataView.getUint32(this._offset,this._littleEndian);return this._offset+=4,e}_nextUint64(){let e=this._dataView.getUint32(this._offset,this._littleEndian)+4294967296*this._dataView.getUint32(this._offset+4,this._littleEndian);return this._offset+=8,e}_nextInt32(){let e=this._dataView.getInt32(this._offset,this._littleEndian);return this._offset+=4,e}_skip(e){return this._offset+=e,this}_scan(e,t=0){let n=this._offset,i=0;for(;this._dataView.getUint8(this._offset)!==t&&i<e;)i++,this._offset++;return i<e&&this._offset++,new Uint8Array(this._dataView.buffer,this._dataView.byteOffset+n,i)}},$T=new Uint8Array([0]),rn=[171,75,84,88,32,50,48,187,13,10,26,10];function Om(o){return typeof TextDecoder<"u"?new TextDecoder().decode(o):Buffer.from(o).toString("utf8")}d(Om,"Ei");function Nm(o){let e=new Uint8Array(o.buffer,o.byteOffset,rn.length);if(e[0]!==rn[0]||e[1]!==rn[1]||e[2]!==rn[2]||e[3]!==rn[3]||e[4]!==rn[4]||e[5]!==rn[5]||e[6]!==rn[6]||e[7]!==rn[7]||e[8]!==rn[8]||e[9]!==rn[9]||e[10]!==rn[10]||e[11]!==rn[11])throw new Error("Missing KTX 2.0 identifier.");let t=new Md,n=17*Uint32Array.BYTES_PER_ELEMENT,i=new bs(o,rn.length,n,!0);t.vkFormat=i._nextUint32(),t.typeSize=i._nextUint32(),t.pixelWidth=i._nextUint32(),t.pixelHeight=i._nextUint32(),t.pixelDepth=i._nextUint32(),t.layerCount=i._nextUint32(),t.faceCount=i._nextUint32();let s=i._nextUint32();t.supercompressionScheme=i._nextUint32();let r=i._nextUint32(),a=i._nextUint32(),l=i._nextUint32(),c=i._nextUint32(),h=i._nextUint64(),u=i._nextUint64(),f=new bs(o,rn.length+n,3*s*8,!0);for(let H=0;H<s;H++)t.levels.push({levelData:new Uint8Array(o.buffer,o.byteOffset+f._nextUint64(),f._nextUint64()),uncompressedByteLength:f._nextUint64()});let p=new bs(o,r,a,!0),g={vendorId:p._skip(4)._nextUint16(),descriptorType:p._nextUint16(),versionNumber:p._nextUint16(),descriptorBlockSize:p._nextUint16(),colorModel:p._nextUint8(),colorPrimaries:p._nextUint8(),transferFunction:p._nextUint8(),flags:p._nextUint8(),texelBlockDimension:[p._nextUint8(),p._nextUint8(),p._nextUint8(),p._nextUint8()],bytesPlane:[p._nextUint8(),p._nextUint8(),p._nextUint8(),p._nextUint8(),p._nextUint8(),p._nextUint8(),p._nextUint8(),p._nextUint8()],samples:[]},A=(g.descriptorBlockSize/4-6)/4;for(let H=0;H<A;H++){let k={bitOffset:p._nextUint16(),bitLength:p._nextUint8(),channelType:p._nextUint8(),samplePosition:[p._nextUint8(),p._nextUint8(),p._nextUint8(),p._nextUint8()],sampleLower:-1/0,sampleUpper:1/0};64&k.channelType?(k.sampleLower=p._nextInt32(),k.sampleUpper=p._nextInt32()):(k.sampleLower=p._nextUint32(),k.sampleUpper=p._nextUint32()),g.samples[H]=k}t.dataFormatDescriptor.length=0,t.dataFormatDescriptor.push(g);let m=new bs(o,l,c,!0);for(;m._offset<c;){let H=m._nextUint32(),k=m._scan(H),j=Om(k),Z=m._scan(H-k.byteLength);t.keyValue[j]=j.match(/^ktx/i)?Om(Z):Z,m._offset%4&&m._skip(4-m._offset%4)}if(u<=0)return t;let _=new bs(o,h,u,!0),E=_._nextUint16(),x=_._nextUint16(),y=_._nextUint32(),w=_._nextUint32(),I=_._nextUint32(),S=_._nextUint32(),v=[];for(let H=0;H<s;H++)v.push({imageFlags:_._nextUint32(),rgbSliceByteOffset:_._nextUint32(),rgbSliceByteLength:_._nextUint32(),alphaSliceByteOffset:_._nextUint32(),alphaSliceByteLength:_._nextUint32()});let b=h+_._offset,R=b+y,N=R+w,z=N+I,O=new Uint8Array(o.buffer,o.byteOffset+b,y),D=new Uint8Array(o.buffer,o.byteOffset+R,w),Q=new Uint8Array(o.buffer,o.byteOffset+N,I),q=new Uint8Array(o.buffer,o.byteOffset+z,S);return t.globalData={endpointCount:E,selectorCount:x,imageDescs:v,endpointsData:O,selectorsData:D,tablesData:Q,extendedData:q},t}d(Nm,"Pi");L();P();var bd,bi,Cd,Id={env:{emscripten_notify_memory_growth:d(function(o){Cd=new Uint8Array(bi.exports.memory.buffer)},"emscripten_notify_memory_growth")}},ac=class{static{d(this,"Q")}init(){return bd||(bd=typeof fetch<"u"?fetch("data:application/wasm;base64,"+Um).then(e=>e.arrayBuffer()).then(e=>WebAssembly.instantiate(e,Id)).then(this._init):WebAssembly.instantiate(Buffer.from(Um,"base64"),Id).then(this._init),bd)}_init(e){bi=e.instance,Id.env.emscripten_notify_memory_growth(0)}decode(e,t=0){if(!bi)throw new Error("ZSTDDecoder: Await .init() before decoding.");let n=e.byteLength,i=bi.exports.malloc(n);Cd.set(e,i),t=t||Number(bi.exports.ZSTD_findDecompressedSize(i,n));let s=bi.exports.malloc(t),r=bi.exports.ZSTD_decompress(s,t,i,n),a=Cd.slice(s,s+r);return bi.exports.free(i),bi.exports.free(s),a}},Um="AGFzbQEAAAABpQEVYAF/AX9gAn9/AGADf39/AX9gBX9/f39/AX9gAX8AYAJ/fwF/YAR/f39/AX9gA39/fwBgBn9/f39/fwF/YAd/f39/f39/AX9gAn9/AX5gAn5+AX5gAABgBX9/f39/AGAGf39/f39/AGAIf39/f39/f38AYAl/f39/f39/f38AYAABf2AIf39/f39/f38Bf2ANf39/f39/f39/f39/fwF/YAF/AX4CJwEDZW52H2Vtc2NyaXB0ZW5fbm90aWZ5X21lbW9yeV9ncm93dGgABANpaAEFAAAFAgEFCwACAQABAgIFBQcAAwABDgsBAQcAEhMHAAUBDAQEAAANBwQCAgYCBAgDAwMDBgEACQkHBgICAAYGAgQUBwYGAwIGAAMCAQgBBwUGCgoEEQAEBAEIAwgDBQgDEA8IAAcABAUBcAECAgUEAQCAAgYJAX8BQaCgwAILB2AHBm1lbW9yeQIABm1hbGxvYwAoBGZyZWUAJgxaU1REX2lzRXJyb3IAaBlaU1REX2ZpbmREZWNvbXByZXNzZWRTaXplAFQPWlNURF9kZWNvbXByZXNzAEoGX3N0YXJ0ACQJBwEAQQELASQKussBaA8AIAAgACgCBCABajYCBAsZACAAKAIAIAAoAgRBH3F0QQAgAWtBH3F2CwgAIABBiH9LC34BBH9BAyEBIAAoAgQiA0EgTQRAIAAoAggiASAAKAIQTwRAIAAQDQ8LIAAoAgwiAiABRgRAQQFBAiADQSBJGw8LIAAgASABIAJrIANBA3YiBCABIARrIAJJIgEbIgJrIgQ2AgggACADIAJBA3RrNgIEIAAgBCgAADYCAAsgAQsUAQF/IAAgARACIQIgACABEAEgAgv3AQECfyACRQRAIABCADcCACAAQQA2AhAgAEIANwIIQbh/DwsgACABNgIMIAAgAUEEajYCECACQQRPBEAgACABIAJqIgFBfGoiAzYCCCAAIAMoAAA2AgAgAUF/ai0AACIBBEAgAEEIIAEQFGs2AgQgAg8LIABBADYCBEF/DwsgACABNgIIIAAgAS0AACIDNgIAIAJBfmoiBEEBTQRAIARBAWtFBEAgACABLQACQRB0IANyIgM2AgALIAAgAS0AAUEIdCADajYCAAsgASACakF/ai0AACIBRQRAIABBADYCBEFsDwsgAEEoIAEQFCACQQN0ams2AgQgAgsWACAAIAEpAAA3AAAgACABKQAINwAICy8BAX8gAUECdEGgHWooAgAgACgCAEEgIAEgACgCBGprQR9xdnEhAiAAIAEQASACCyEAIAFCz9bTvtLHq9lCfiAAfEIfiUKHla+vmLbem55/fgsdAQF/IAAoAgggACgCDEYEfyAAKAIEQSBGBUEACwuCBAEDfyACQYDAAE8EQCAAIAEgAhBnIAAPCyAAIAJqIQMCQCAAIAFzQQNxRQRAAkAgAkEBSARAIAAhAgwBCyAAQQNxRQRAIAAhAgwBCyAAIQIDQCACIAEtAAA6AAAgAUEBaiEBIAJBAWoiAiADTw0BIAJBA3ENAAsLAkAgA0F8cSIEQcAASQ0AIAIgBEFAaiIFSw0AA0AgAiABKAIANgIAIAIgASgCBDYCBCACIAEoAgg2AgggAiABKAIMNgIMIAIgASgCEDYCECACIAEoAhQ2AhQgAiABKAIYNgIYIAIgASgCHDYCHCACIAEoAiA2AiAgAiABKAIkNgIkIAIgASgCKDYCKCACIAEoAiw2AiwgAiABKAIwNgIwIAIgASgCNDYCNCACIAEoAjg2AjggAiABKAI8NgI8IAFBQGshASACQUBrIgIgBU0NAAsLIAIgBE8NAQNAIAIgASgCADYCACABQQRqIQEgAkEEaiICIARJDQALDAELIANBBEkEQCAAIQIMAQsgA0F8aiIEIABJBEAgACECDAELIAAhAgNAIAIgAS0AADoAACACIAEtAAE6AAEgAiABLQACOgACIAIgAS0AAzoAAyABQQRqIQEgAkEEaiICIARNDQALCyACIANJBEADQCACIAEtAAA6AAAgAUEBaiEBIAJBAWoiAiADRw0ACwsgAAsMACAAIAEpAAA3AAALQQECfyAAKAIIIgEgACgCEEkEQEEDDwsgACAAKAIEIgJBB3E2AgQgACABIAJBA3ZrIgE2AgggACABKAAANgIAQQALDAAgACABKAIANgAAC/cCAQJ/AkAgACABRg0AAkAgASACaiAASwRAIAAgAmoiBCABSw0BCyAAIAEgAhALDwsgACABc0EDcSEDAkACQCAAIAFJBEAgAwRAIAAhAwwDCyAAQQNxRQRAIAAhAwwCCyAAIQMDQCACRQ0EIAMgAS0AADoAACABQQFqIQEgAkF/aiECIANBAWoiA0EDcQ0ACwwBCwJAIAMNACAEQQNxBEADQCACRQ0FIAAgAkF/aiICaiIDIAEgAmotAAA6AAAgA0EDcQ0ACwsgAkEDTQ0AA0AgACACQXxqIgJqIAEgAmooAgA2AgAgAkEDSw0ACwsgAkUNAgNAIAAgAkF/aiICaiABIAJqLQAAOgAAIAINAAsMAgsgAkEDTQ0AIAIhBANAIAMgASgCADYCACABQQRqIQEgA0EEaiEDIARBfGoiBEEDSw0ACyACQQNxIQILIAJFDQADQCADIAEtAAA6AAAgA0EBaiEDIAFBAWohASACQX9qIgINAAsLIAAL8wICAn8BfgJAIAJFDQAgACACaiIDQX9qIAE6AAAgACABOgAAIAJBA0kNACADQX5qIAE6AAAgACABOgABIANBfWogAToAACAAIAE6AAIgAkEHSQ0AIANBfGogAToAACAAIAE6AAMgAkEJSQ0AIABBACAAa0EDcSIEaiIDIAFB/wFxQYGChAhsIgE2AgAgAyACIARrQXxxIgRqIgJBfGogATYCACAEQQlJDQAgAyABNgIIIAMgATYCBCACQXhqIAE2AgAgAkF0aiABNgIAIARBGUkNACADIAE2AhggAyABNgIUIAMgATYCECADIAE2AgwgAkFwaiABNgIAIAJBbGogATYCACACQWhqIAE2AgAgAkFkaiABNgIAIAQgA0EEcUEYciIEayICQSBJDQAgAa0iBUIghiAFhCEFIAMgBGohAQNAIAEgBTcDGCABIAU3AxAgASAFNwMIIAEgBTcDACABQSBqIQEgAkFgaiICQR9LDQALCyAACy8BAn8gACgCBCAAKAIAQQJ0aiICLQACIQMgACACLwEAIAEgAi0AAxAIajYCACADCy8BAn8gACgCBCAAKAIAQQJ0aiICLQACIQMgACACLwEAIAEgAi0AAxAFajYCACADCx8AIAAgASACKAIEEAg2AgAgARAEGiAAIAJBCGo2AgQLCAAgAGdBH3MLugUBDX8jAEEQayIKJAACfyAEQQNNBEAgCkEANgIMIApBDGogAyAEEAsaIAAgASACIApBDGpBBBAVIgBBbCAAEAMbIAAgACAESxsMAQsgAEEAIAEoAgBBAXRBAmoQECENQVQgAygAACIGQQ9xIgBBCksNABogAiAAQQVqNgIAIAMgBGoiAkF8aiEMIAJBeWohDiACQXtqIRAgAEEGaiELQQQhBSAGQQR2IQRBICAAdCIAQQFyIQkgASgCACEPQQAhAiADIQYCQANAIAlBAkggAiAPS3JFBEAgAiEHAkAgCARAA0AgBEH//wNxQf//A0YEQCAHQRhqIQcgBiAQSQR/IAZBAmoiBigAACAFdgUgBUEQaiEFIARBEHYLIQQMAQsLA0AgBEEDcSIIQQNGBEAgBUECaiEFIARBAnYhBCAHQQNqIQcMAQsLIAcgCGoiByAPSw0EIAVBAmohBQNAIAIgB0kEQCANIAJBAXRqQQA7AQAgAkEBaiECDAELCyAGIA5LQQAgBiAFQQN1aiIHIAxLG0UEQCAHKAAAIAVBB3EiBXYhBAwCCyAEQQJ2IQQLIAYhBwsCfyALQX9qIAQgAEF/anEiBiAAQQF0QX9qIgggCWsiEUkNABogBCAIcSIEQQAgESAEIABIG2shBiALCyEIIA0gAkEBdGogBkF/aiIEOwEAIAlBASAGayAEIAZBAUgbayEJA0AgCSAASARAIABBAXUhACALQX9qIQsMAQsLAn8gByAOS0EAIAcgBSAIaiIFQQN1aiIGIAxLG0UEQCAFQQdxDAELIAUgDCIGIAdrQQN0awshBSACQQFqIQIgBEUhCCAGKAAAIAVBH3F2IQQMAQsLQWwgCUEBRyAFQSBKcg0BGiABIAJBf2o2AgAgBiAFQQdqQQN1aiADawwBC0FQCyEAIApBEGokACAACwkAQQFBBSAAGwsMACAAIAEoAAA2AAALqgMBCn8jAEHwAGsiCiQAIAJBAWohDiAAQQhqIQtBgIAEIAVBf2p0QRB1IQxBACECQQEhBkEBIAV0IglBf2oiDyEIA0AgAiAORkUEQAJAIAEgAkEBdCINai8BACIHQf//A0YEQCALIAhBA3RqIAI2AgQgCEF/aiEIQQEhBwwBCyAGQQAgDCAHQRB0QRB1ShshBgsgCiANaiAHOwEAIAJBAWohAgwBCwsgACAFNgIEIAAgBjYCACAJQQN2IAlBAXZqQQNqIQxBACEAQQAhBkEAIQIDQCAGIA5GBEADQAJAIAAgCUYNACAKIAsgAEEDdGoiASgCBCIGQQF0aiICIAIvAQAiAkEBajsBACABIAUgAhAUayIIOgADIAEgAiAIQf8BcXQgCWs7AQAgASAEIAZBAnQiAmooAgA6AAIgASACIANqKAIANgIEIABBAWohAAwBCwsFIAEgBkEBdGouAQAhDUEAIQcDQCAHIA1ORQRAIAsgAkEDdGogBjYCBANAIAIgDGogD3EiAiAISw0ACyAHQQFqIQcMAQsLIAZBAWohBgwBCwsgCkHwAGokAAsjAEIAIAEQCSAAhUKHla+vmLbem55/fkLj3MqV/M7y9YV/fAsQACAAQn43AwggACABNgIACyQBAX8gAARAIAEoAgQiAgRAIAEoAgggACACEQEADwsgABAmCwsfACAAIAEgAi8BABAINgIAIAEQBBogACACQQRqNgIEC0oBAX9BoCAoAgAiASAAaiIAQX9MBEBBiCBBMDYCAEF/DwsCQCAAPwBBEHRNDQAgABBmDQBBiCBBMDYCAEF/DwtBoCAgADYCACABC9cBAQh/Qbp/IQoCQCACKAIEIgggAigCACIJaiIOIAEgAGtLDQBBbCEKIAkgBCADKAIAIgtrSw0AIAAgCWoiBCACKAIIIgxrIQ0gACABQWBqIg8gCyAJQQAQKSADIAkgC2o2AgACQAJAIAwgBCAFa00EQCANIQUMAQsgDCAEIAZrSw0CIAcgDSAFayIAaiIBIAhqIAdNBEAgBCABIAgQDxoMAgsgBCABQQAgAGsQDyEBIAIgACAIaiIINgIEIAEgAGshBAsgBCAPIAUgCEEBECkLIA4hCgsgCgubAgEBfyMAQYABayINJAAgDSADNgJ8AkAgAkEDSwRAQX8hCQwBCwJAAkACQAJAIAJBAWsOAwADAgELIAZFBEBBuH8hCQwEC0FsIQkgBS0AACICIANLDQMgACAHIAJBAnQiAmooAgAgAiAIaigCABA7IAEgADYCAEEBIQkMAwsgASAJNgIAQQAhCQwCCyAKRQRAQWwhCQwCC0EAIQkgC0UgDEEZSHINAUEIIAR0QQhqIQBBACECA0AgAiAATw0CIAJBQGshAgwAAAsAC0FsIQkgDSANQfwAaiANQfgAaiAFIAYQFSICEAMNACANKAJ4IgMgBEsNACAAIA0gDSgCfCAHIAggAxAYIAEgADYCACACIQkLIA1BgAFqJAAgCQsLACAAIAEgAhALGgsQACAALwAAIAAtAAJBEHRyCy8AAn9BuH8gAUEISQ0AGkFyIAAoAAQiAEF3Sw0AGkG4fyAAQQhqIgAgACABSxsLCwkAIAAgATsAAAsDAAELigYBBX8gACAAKAIAIgVBfnE2AgBBACAAIAVBAXZqQYQgKAIAIgQgAEYbIQECQAJAIAAoAgQiAkUNACACKAIAIgNBAXENACACQQhqIgUgA0EBdkF4aiIDQQggA0EISxtnQR9zQQJ0QYAfaiIDKAIARgRAIAMgAigCDDYCAAsgAigCCCIDBEAgAyACKAIMNgIECyACKAIMIgMEQCADIAIoAgg2AgALIAIgAigCACAAKAIAQX5xajYCAEGEICEAAkACQCABRQ0AIAEgAjYCBCABKAIAIgNBAXENASADQQF2QXhqIgNBCCADQQhLG2dBH3NBAnRBgB9qIgMoAgAgAUEIakYEQCADIAEoAgw2AgALIAEoAggiAwRAIAMgASgCDDYCBAsgASgCDCIDBEAgAyABKAIINgIAQYQgKAIAIQQLIAIgAigCACABKAIAQX5xajYCACABIARGDQAgASABKAIAQQF2akEEaiEACyAAIAI2AgALIAIoAgBBAXZBeGoiAEEIIABBCEsbZ0Efc0ECdEGAH2oiASgCACEAIAEgBTYCACACIAA2AgwgAkEANgIIIABFDQEgACAFNgIADwsCQCABRQ0AIAEoAgAiAkEBcQ0AIAJBAXZBeGoiAkEIIAJBCEsbZ0Efc0ECdEGAH2oiAigCACABQQhqRgRAIAIgASgCDDYCAAsgASgCCCICBEAgAiABKAIMNgIECyABKAIMIgIEQCACIAEoAgg2AgBBhCAoAgAhBAsgACAAKAIAIAEoAgBBfnFqIgI2AgACQCABIARHBEAgASABKAIAQQF2aiAANgIEIAAoAgAhAgwBC0GEICAANgIACyACQQF2QXhqIgFBCCABQQhLG2dBH3NBAnRBgB9qIgIoAgAhASACIABBCGoiAjYCACAAIAE2AgwgAEEANgIIIAFFDQEgASACNgIADwsgBUEBdkF4aiIBQQggAUEISxtnQR9zQQJ0QYAfaiICKAIAIQEgAiAAQQhqIgI2AgAgACABNgIMIABBADYCCCABRQ0AIAEgAjYCAAsLDgAgAARAIABBeGoQJQsLgAIBA38CQCAAQQ9qQXhxQYQgKAIAKAIAQQF2ayICEB1Bf0YNAAJAQYQgKAIAIgAoAgAiAUEBcQ0AIAFBAXZBeGoiAUEIIAFBCEsbZ0Efc0ECdEGAH2oiASgCACAAQQhqRgRAIAEgACgCDDYCAAsgACgCCCIBBEAgASAAKAIMNgIECyAAKAIMIgFFDQAgASAAKAIINgIAC0EBIQEgACAAKAIAIAJBAXRqIgI2AgAgAkEBcQ0AIAJBAXZBeGoiAkEIIAJBCEsbZ0Efc0ECdEGAH2oiAygCACECIAMgAEEIaiIDNgIAIAAgAjYCDCAAQQA2AgggAkUNACACIAM2AgALIAELtwIBA38CQAJAIABBASAAGyICEDgiAA0AAkACQEGEICgCACIARQ0AIAAoAgAiA0EBcQ0AIAAgA0EBcjYCACADQQF2QXhqIgFBCCABQQhLG2dBH3NBAnRBgB9qIgEoAgAgAEEIakYEQCABIAAoAgw2AgALIAAoAggiAQRAIAEgACgCDDYCBAsgACgCDCIBBEAgASAAKAIINgIACyACECchAkEAIQFBhCAoAgAhACACDQEgACAAKAIAQX5xNgIAQQAPCyACQQ9qQXhxIgMQHSICQX9GDQIgAkEHakF4cSIAIAJHBEAgACACaxAdQX9GDQMLAkBBhCAoAgAiAUUEQEGAICAANgIADAELIAAgATYCBAtBhCAgADYCACAAIANBAXRBAXI2AgAMAQsgAEUNAQsgAEEIaiEBCyABC7kDAQJ/IAAgA2ohBQJAIANBB0wEQANAIAAgBU8NAiAAIAItAAA6AAAgAEEBaiEAIAJBAWohAgwAAAsACyAEQQFGBEACQCAAIAJrIgZBB00EQCAAIAItAAA6AAAgACACLQABOgABIAAgAi0AAjoAAiAAIAItAAM6AAMgAEEEaiACIAZBAnQiBkHAHmooAgBqIgIQFyACIAZB4B5qKAIAayECDAELIAAgAhAMCyACQQhqIQIgAEEIaiEACwJAAkACQAJAIAUgAU0EQCAAIANqIQEgBEEBRyAAIAJrQQ9Kcg0BA0AgACACEAwgAkEIaiECIABBCGoiACABSQ0ACwwFCyAAIAFLBEAgACEBDAQLIARBAUcgACACa0EPSnINASAAIQMgAiEEA0AgAyAEEAwgBEEIaiEEIANBCGoiAyABSQ0ACwwCCwNAIAAgAhAHIAJBEGohAiAAQRBqIgAgAUkNAAsMAwsgACEDIAIhBANAIAMgBBAHIARBEGohBCADQRBqIgMgAUkNAAsLIAIgASAAa2ohAgsDQCABIAVPDQEgASACLQAAOgAAIAFBAWohASACQQFqIQIMAAALAAsLQQECfyAAIAAoArjgASIDNgLE4AEgACgCvOABIQQgACABNgK84AEgACABIAJqNgK44AEgACABIAQgA2tqNgLA4AELpgEBAX8gACAAKALs4QEQFjYCyOABIABCADcD+OABIABCADcDuOABIABBwOABakIANwMAIABBqNAAaiIBQYyAgOAANgIAIABBADYCmOIBIABCADcDiOEBIABCAzcDgOEBIABBrNABakHgEikCADcCACAAQbTQAWpB6BIoAgA2AgAgACABNgIMIAAgAEGYIGo2AgggACAAQaAwajYCBCAAIABBEGo2AgALYQEBf0G4fyEDAkAgAUEDSQ0AIAIgABAhIgFBA3YiADYCCCACIAFBAXE2AgQgAiABQQF2QQNxIgM2AgACQCADQX9qIgFBAksNAAJAIAFBAWsOAgEAAgtBbA8LIAAhAwsgAwsMACAAIAEgAkEAEC4LiAQCA38CfiADEBYhBCAAQQBBKBAQIQAgBCACSwRAIAQPCyABRQRAQX8PCwJAAkAgA0EBRg0AIAEoAAAiBkGo6r5pRg0AQXYhAyAGQXBxQdDUtMIBRw0BQQghAyACQQhJDQEgAEEAQSgQECEAIAEoAAQhASAAQQE2AhQgACABrTcDAEEADwsgASACIAMQLyIDIAJLDQAgACADNgIYQXIhAyABIARqIgVBf2otAAAiAkEIcQ0AIAJBIHEiBkUEQEFwIQMgBS0AACIFQacBSw0BIAVBB3GtQgEgBUEDdkEKaq2GIgdCA4h+IAd8IQggBEEBaiEECyACQQZ2IQMgAkECdiEFAkAgAkEDcUF/aiICQQJLBEBBACECDAELAkACQAJAIAJBAWsOAgECAAsgASAEai0AACECIARBAWohBAwCCyABIARqLwAAIQIgBEECaiEEDAELIAEgBGooAAAhAiAEQQRqIQQLIAVBAXEhBQJ+AkACQAJAIANBf2oiA0ECTQRAIANBAWsOAgIDAQtCfyAGRQ0DGiABIARqMQAADAMLIAEgBGovAACtQoACfAwCCyABIARqKAAArQwBCyABIARqKQAACyEHIAAgBTYCICAAIAI2AhwgACAHNwMAQQAhAyAAQQA2AhQgACAHIAggBhsiBzcDCCAAIAdCgIAIIAdCgIAIVBs+AhALIAMLWwEBf0G4fyEDIAIQFiICIAFNBH8gACACakF/ai0AACIAQQNxQQJ0QaAeaigCACACaiAAQQZ2IgFBAnRBsB5qKAIAaiAAQSBxIgBFaiABRSAAQQV2cWoFQbh/CwsdACAAKAKQ4gEQWiAAQQA2AqDiASAAQgA3A5DiAQu1AwEFfyMAQZACayIKJABBuH8hBgJAIAVFDQAgBCwAACIIQf8BcSEHAkAgCEF/TARAIAdBgn9qQQF2IgggBU8NAkFsIQYgB0GBf2oiBUGAAk8NAiAEQQFqIQdBACEGA0AgBiAFTwRAIAUhBiAIIQcMAwUgACAGaiAHIAZBAXZqIgQtAABBBHY6AAAgACAGQQFyaiAELQAAQQ9xOgAAIAZBAmohBgwBCwAACwALIAcgBU8NASAAIARBAWogByAKEFMiBhADDQELIAYhBEEAIQYgAUEAQTQQECEJQQAhBQNAIAQgBkcEQCAAIAZqIggtAAAiAUELSwRAQWwhBgwDBSAJIAFBAnRqIgEgASgCAEEBajYCACAGQQFqIQZBASAILQAAdEEBdSAFaiEFDAILAAsLQWwhBiAFRQ0AIAUQFEEBaiIBQQxLDQAgAyABNgIAQQFBASABdCAFayIDEBQiAXQgA0cNACAAIARqIAFBAWoiADoAACAJIABBAnRqIgAgACgCAEEBajYCACAJKAIEIgBBAkkgAEEBcXINACACIARBAWo2AgAgB0EBaiEGCyAKQZACaiQAIAYLxhEBDH8jAEHwAGsiBSQAQWwhCwJAIANBCkkNACACLwAAIQogAi8AAiEJIAIvAAQhByAFQQhqIAQQDgJAIAMgByAJIApqakEGaiIMSQ0AIAUtAAohCCAFQdgAaiACQQZqIgIgChAGIgsQAw0BIAVBQGsgAiAKaiICIAkQBiILEAMNASAFQShqIAIgCWoiAiAHEAYiCxADDQEgBUEQaiACIAdqIAMgDGsQBiILEAMNASAAIAFqIg9BfWohECAEQQRqIQZBASELIAAgAUEDakECdiIDaiIMIANqIgIgA2oiDiEDIAIhBCAMIQcDQCALIAMgEElxBEAgACAGIAVB2ABqIAgQAkECdGoiCS8BADsAACAFQdgAaiAJLQACEAEgCS0AAyELIAcgBiAFQUBrIAgQAkECdGoiCS8BADsAACAFQUBrIAktAAIQASAJLQADIQogBCAGIAVBKGogCBACQQJ0aiIJLwEAOwAAIAVBKGogCS0AAhABIAktAAMhCSADIAYgBUEQaiAIEAJBAnRqIg0vAQA7AAAgBUEQaiANLQACEAEgDS0AAyENIAAgC2oiCyAGIAVB2ABqIAgQAkECdGoiAC8BADsAACAFQdgAaiAALQACEAEgAC0AAyEAIAcgCmoiCiAGIAVBQGsgCBACQQJ0aiIHLwEAOwAAIAVBQGsgBy0AAhABIActAAMhByAEIAlqIgkgBiAFQShqIAgQAkECdGoiBC8BADsAACAFQShqIAQtAAIQASAELQADIQQgAyANaiIDIAYgBUEQaiAIEAJBAnRqIg0vAQA7AAAgBUEQaiANLQACEAEgACALaiEAIAcgCmohByAEIAlqIQQgAyANLQADaiEDIAVB2ABqEA0gBUFAaxANciAFQShqEA1yIAVBEGoQDXJFIQsMAQsLIAQgDksgByACS3INAEFsIQsgACAMSw0BIAxBfWohCQNAQQAgACAJSSAFQdgAahAEGwRAIAAgBiAFQdgAaiAIEAJBAnRqIgovAQA7AAAgBUHYAGogCi0AAhABIAAgCi0AA2oiACAGIAVB2ABqIAgQAkECdGoiCi8BADsAACAFQdgAaiAKLQACEAEgACAKLQADaiEADAEFIAxBfmohCgNAIAVB2ABqEAQgACAKS3JFBEAgACAGIAVB2ABqIAgQAkECdGoiCS8BADsAACAFQdgAaiAJLQACEAEgACAJLQADaiEADAELCwNAIAAgCk0EQCAAIAYgBUHYAGogCBACQQJ0aiIJLwEAOwAAIAVB2ABqIAktAAIQASAAIAktAANqIQAMAQsLAkAgACAMTw0AIAAgBiAFQdgAaiAIEAIiAEECdGoiDC0AADoAACAMLQADQQFGBEAgBUHYAGogDC0AAhABDAELIAUoAlxBH0sNACAFQdgAaiAGIABBAnRqLQACEAEgBSgCXEEhSQ0AIAVBIDYCXAsgAkF9aiEMA0BBACAHIAxJIAVBQGsQBBsEQCAHIAYgBUFAayAIEAJBAnRqIgAvAQA7AAAgBUFAayAALQACEAEgByAALQADaiIAIAYgBUFAayAIEAJBAnRqIgcvAQA7AAAgBUFAayAHLQACEAEgACAHLQADaiEHDAEFIAJBfmohDANAIAVBQGsQBCAHIAxLckUEQCAHIAYgBUFAayAIEAJBAnRqIgAvAQA7AAAgBUFAayAALQACEAEgByAALQADaiEHDAELCwNAIAcgDE0EQCAHIAYgBUFAayAIEAJBAnRqIgAvAQA7AAAgBUFAayAALQACEAEgByAALQADaiEHDAELCwJAIAcgAk8NACAHIAYgBUFAayAIEAIiAEECdGoiAi0AADoAACACLQADQQFGBEAgBUFAayACLQACEAEMAQsgBSgCREEfSw0AIAVBQGsgBiAAQQJ0ai0AAhABIAUoAkRBIUkNACAFQSA2AkQLIA5BfWohAgNAQQAgBCACSSAFQShqEAQbBEAgBCAGIAVBKGogCBACQQJ0aiIALwEAOwAAIAVBKGogAC0AAhABIAQgAC0AA2oiACAGIAVBKGogCBACQQJ0aiIELwEAOwAAIAVBKGogBC0AAhABIAAgBC0AA2ohBAwBBSAOQX5qIQIDQCAFQShqEAQgBCACS3JFBEAgBCAGIAVBKGogCBACQQJ0aiIALwEAOwAAIAVBKGogAC0AAhABIAQgAC0AA2ohBAwBCwsDQCAEIAJNBEAgBCAGIAVBKGogCBACQQJ0aiIALwEAOwAAIAVBKGogAC0AAhABIAQgAC0AA2ohBAwBCwsCQCAEIA5PDQAgBCAGIAVBKGogCBACIgBBAnRqIgItAAA6AAAgAi0AA0EBRgRAIAVBKGogAi0AAhABDAELIAUoAixBH0sNACAFQShqIAYgAEECdGotAAIQASAFKAIsQSFJDQAgBUEgNgIsCwNAQQAgAyAQSSAFQRBqEAQbBEAgAyAGIAVBEGogCBACQQJ0aiIALwEAOwAAIAVBEGogAC0AAhABIAMgAC0AA2oiACAGIAVBEGogCBACQQJ0aiICLwEAOwAAIAVBEGogAi0AAhABIAAgAi0AA2ohAwwBBSAPQX5qIQIDQCAFQRBqEAQgAyACS3JFBEAgAyAGIAVBEGogCBACQQJ0aiIALwEAOwAAIAVBEGogAC0AAhABIAMgAC0AA2ohAwwBCwsDQCADIAJNBEAgAyAGIAVBEGogCBACQQJ0aiIALwEAOwAAIAVBEGogAC0AAhABIAMgAC0AA2ohAwwBCwsCQCADIA9PDQAgAyAGIAVBEGogCBACIgBBAnRqIgItAAA6AAAgAi0AA0EBRgRAIAVBEGogAi0AAhABDAELIAUoAhRBH0sNACAFQRBqIAYgAEECdGotAAIQASAFKAIUQSFJDQAgBUEgNgIUCyABQWwgBUHYAGoQCiAFQUBrEApxIAVBKGoQCnEgBUEQahAKcRshCwwJCwAACwALAAALAAsAAAsACwAACwALQWwhCwsgBUHwAGokACALC7UEAQ5/IwBBEGsiBiQAIAZBBGogABAOQVQhBQJAIARB3AtJDQAgBi0ABCEHIANB8ARqQQBB7AAQECEIIAdBDEsNACADQdwJaiIJIAggBkEIaiAGQQxqIAEgAhAxIhAQA0UEQCAGKAIMIgQgB0sNASADQdwFaiEPIANBpAVqIREgAEEEaiESIANBqAVqIQEgBCEFA0AgBSICQX9qIQUgCCACQQJ0aigCAEUNAAsgAkEBaiEOQQEhBQNAIAUgDk9FBEAgCCAFQQJ0IgtqKAIAIQwgASALaiAKNgIAIAVBAWohBSAKIAxqIQoMAQsLIAEgCjYCAEEAIQUgBigCCCELA0AgBSALRkUEQCABIAUgCWotAAAiDEECdGoiDSANKAIAIg1BAWo2AgAgDyANQQF0aiINIAw6AAEgDSAFOgAAIAVBAWohBQwBCwtBACEBIANBADYCqAUgBEF/cyAHaiEJQQEhBQNAIAUgDk9FBEAgCCAFQQJ0IgtqKAIAIQwgAyALaiABNgIAIAwgBSAJanQgAWohASAFQQFqIQUMAQsLIAcgBEEBaiIBIAJrIgRrQQFqIQgDQEEBIQUgBCAIT0UEQANAIAUgDk9FBEAgBUECdCIJIAMgBEE0bGpqIAMgCWooAgAgBHY2AgAgBUEBaiEFDAELCyAEQQFqIQQMAQsLIBIgByAPIAogESADIAIgARBkIAZBAToABSAGIAc6AAYgACAGKAIENgIACyAQIQULIAZBEGokACAFC8ENAQt/IwBB8ABrIgUkAEFsIQkCQCADQQpJDQAgAi8AACEKIAIvAAIhDCACLwAEIQYgBUEIaiAEEA4CQCADIAYgCiAMampBBmoiDUkNACAFLQAKIQcgBUHYAGogAkEGaiICIAoQBiIJEAMNASAFQUBrIAIgCmoiAiAMEAYiCRADDQEgBUEoaiACIAxqIgIgBhAGIgkQAw0BIAVBEGogAiAGaiADIA1rEAYiCRADDQEgACABaiIOQX1qIQ8gBEEEaiEGQQEhCSAAIAFBA2pBAnYiAmoiCiACaiIMIAJqIg0hAyAMIQQgCiECA0AgCSADIA9JcQRAIAYgBUHYAGogBxACQQF0aiIILQAAIQsgBUHYAGogCC0AARABIAAgCzoAACAGIAVBQGsgBxACQQF0aiIILQAAIQsgBUFAayAILQABEAEgAiALOgAAIAYgBUEoaiAHEAJBAXRqIggtAAAhCyAFQShqIAgtAAEQASAEIAs6AAAgBiAFQRBqIAcQAkEBdGoiCC0AACELIAVBEGogCC0AARABIAMgCzoAACAGIAVB2ABqIAcQAkEBdGoiCC0AACELIAVB2ABqIAgtAAEQASAAIAs6AAEgBiAFQUBrIAcQAkEBdGoiCC0AACELIAVBQGsgCC0AARABIAIgCzoAASAGIAVBKGogBxACQQF0aiIILQAAIQsgBUEoaiAILQABEAEgBCALOgABIAYgBUEQaiAHEAJBAXRqIggtAAAhCyAFQRBqIAgtAAEQASADIAs6AAEgA0ECaiEDIARBAmohBCACQQJqIQIgAEECaiEAIAkgBUHYAGoQDUVxIAVBQGsQDUVxIAVBKGoQDUVxIAVBEGoQDUVxIQkMAQsLIAQgDUsgAiAMS3INAEFsIQkgACAKSw0BIApBfWohCQNAIAVB2ABqEAQgACAJT3JFBEAgBiAFQdgAaiAHEAJBAXRqIggtAAAhCyAFQdgAaiAILQABEAEgACALOgAAIAYgBUHYAGogBxACQQF0aiIILQAAIQsgBUHYAGogCC0AARABIAAgCzoAASAAQQJqIQAMAQsLA0AgBUHYAGoQBCAAIApPckUEQCAGIAVB2ABqIAcQAkEBdGoiCS0AACEIIAVB2ABqIAktAAEQASAAIAg6AAAgAEEBaiEADAELCwNAIAAgCkkEQCAGIAVB2ABqIAcQAkEBdGoiCS0AACEIIAVB2ABqIAktAAEQASAAIAg6AAAgAEEBaiEADAELCyAMQX1qIQADQCAFQUBrEAQgAiAAT3JFBEAgBiAFQUBrIAcQAkEBdGoiCi0AACEJIAVBQGsgCi0AARABIAIgCToAACAGIAVBQGsgBxACQQF0aiIKLQAAIQkgBUFAayAKLQABEAEgAiAJOgABIAJBAmohAgwBCwsDQCAFQUBrEAQgAiAMT3JFBEAgBiAFQUBrIAcQAkEBdGoiAC0AACEKIAVBQGsgAC0AARABIAIgCjoAACACQQFqIQIMAQsLA0AgAiAMSQRAIAYgBUFAayAHEAJBAXRqIgAtAAAhCiAFQUBrIAAtAAEQASACIAo6AAAgAkEBaiECDAELCyANQX1qIQADQCAFQShqEAQgBCAAT3JFBEAgBiAFQShqIAcQAkEBdGoiAi0AACEKIAVBKGogAi0AARABIAQgCjoAACAGIAVBKGogBxACQQF0aiICLQAAIQogBUEoaiACLQABEAEgBCAKOgABIARBAmohBAwBCwsDQCAFQShqEAQgBCANT3JFBEAgBiAFQShqIAcQAkEBdGoiAC0AACECIAVBKGogAC0AARABIAQgAjoAACAEQQFqIQQMAQsLA0AgBCANSQRAIAYgBUEoaiAHEAJBAXRqIgAtAAAhAiAFQShqIAAtAAEQASAEIAI6AAAgBEEBaiEEDAELCwNAIAVBEGoQBCADIA9PckUEQCAGIAVBEGogBxACQQF0aiIALQAAIQIgBUEQaiAALQABEAEgAyACOgAAIAYgBUEQaiAHEAJBAXRqIgAtAAAhAiAFQRBqIAAtAAEQASADIAI6AAEgA0ECaiEDDAELCwNAIAVBEGoQBCADIA5PckUEQCAGIAVBEGogBxACQQF0aiIALQAAIQIgBUEQaiAALQABEAEgAyACOgAAIANBAWohAwwBCwsDQCADIA5JBEAgBiAFQRBqIAcQAkEBdGoiAC0AACECIAVBEGogAC0AARABIAMgAjoAACADQQFqIQMMAQsLIAFBbCAFQdgAahAKIAVBQGsQCnEgBUEoahAKcSAFQRBqEApxGyEJDAELQWwhCQsgBUHwAGokACAJC8oCAQR/IwBBIGsiBSQAIAUgBBAOIAUtAAIhByAFQQhqIAIgAxAGIgIQA0UEQCAEQQRqIQIgACABaiIDQX1qIQQDQCAFQQhqEAQgACAET3JFBEAgAiAFQQhqIAcQAkEBdGoiBi0AACEIIAVBCGogBi0AARABIAAgCDoAACACIAVBCGogBxACQQF0aiIGLQAAIQggBUEIaiAGLQABEAEgACAIOgABIABBAmohAAwBCwsDQCAFQQhqEAQgACADT3JFBEAgAiAFQQhqIAcQAkEBdGoiBC0AACEGIAVBCGogBC0AARABIAAgBjoAACAAQQFqIQAMAQsLA0AgACADT0UEQCACIAVBCGogBxACQQF0aiIELQAAIQYgBUEIaiAELQABEAEgACAGOgAAIABBAWohAAwBCwsgAUFsIAVBCGoQChshAgsgBUEgaiQAIAILtgMBCX8jAEEQayIGJAAgBkEANgIMIAZBADYCCEFUIQQCQAJAIANBQGsiDCADIAZBCGogBkEMaiABIAIQMSICEAMNACAGQQRqIAAQDiAGKAIMIgcgBi0ABEEBaksNASAAQQRqIQogBkEAOgAFIAYgBzoABiAAIAYoAgQ2AgAgB0EBaiEJQQEhBANAIAQgCUkEQCADIARBAnRqIgEoAgAhACABIAU2AgAgACAEQX9qdCAFaiEFIARBAWohBAwBCwsgB0EBaiEHQQAhBSAGKAIIIQkDQCAFIAlGDQEgAyAFIAxqLQAAIgRBAnRqIgBBASAEdEEBdSILIAAoAgAiAWoiADYCACAHIARrIQhBACEEAkAgC0EDTQRAA0AgBCALRg0CIAogASAEakEBdGoiACAIOgABIAAgBToAACAEQQFqIQQMAAALAAsDQCABIABPDQEgCiABQQF0aiIEIAg6AAEgBCAFOgAAIAQgCDoAAyAEIAU6AAIgBCAIOgAFIAQgBToABCAEIAg6AAcgBCAFOgAGIAFBBGohAQwAAAsACyAFQQFqIQUMAAALAAsgAiEECyAGQRBqJAAgBAutAQECfwJAQYQgKAIAIABHIAAoAgBBAXYiAyABa0F4aiICQXhxQQhHcgR/IAIFIAMQJ0UNASACQQhqC0EQSQ0AIAAgACgCACICQQFxIAAgAWpBD2pBeHEiASAAa0EBdHI2AgAgASAANgIEIAEgASgCAEEBcSAAIAJBAXZqIAFrIgJBAXRyNgIAQYQgIAEgAkH/////B3FqQQRqQYQgKAIAIABGGyABNgIAIAEQJQsLygIBBX8CQAJAAkAgAEEIIABBCEsbZ0EfcyAAaUEBR2oiAUEESSAAIAF2cg0AIAFBAnRB/B5qKAIAIgJFDQADQCACQXhqIgMoAgBBAXZBeGoiBSAATwRAIAIgBUEIIAVBCEsbZ0Efc0ECdEGAH2oiASgCAEYEQCABIAIoAgQ2AgALDAMLIARBHksNASAEQQFqIQQgAigCBCICDQALC0EAIQMgAUEgTw0BA0AgAUECdEGAH2ooAgAiAkUEQCABQR5LIQIgAUEBaiEBIAJFDQEMAwsLIAIgAkF4aiIDKAIAQQF2QXhqIgFBCCABQQhLG2dBH3NBAnRBgB9qIgEoAgBGBEAgASACKAIENgIACwsgAigCACIBBEAgASACKAIENgIECyACKAIEIgEEQCABIAIoAgA2AgALIAMgAygCAEEBcjYCACADIAAQNwsgAwvhCwINfwV+IwBB8ABrIgckACAHIAAoAvDhASIINgJcIAEgAmohDSAIIAAoAoDiAWohDwJAAkAgBUUEQCABIQQMAQsgACgCxOABIRAgACgCwOABIREgACgCvOABIQ4gAEEBNgKM4QFBACEIA0AgCEEDRwRAIAcgCEECdCICaiAAIAJqQazQAWooAgA2AkQgCEEBaiEIDAELC0FsIQwgB0EYaiADIAQQBhADDQEgB0EsaiAHQRhqIAAoAgAQEyAHQTRqIAdBGGogACgCCBATIAdBPGogB0EYaiAAKAIEEBMgDUFgaiESIAEhBEEAIQwDQCAHKAIwIAcoAixBA3RqKQIAIhRCEIinQf8BcSEIIAcoAkAgBygCPEEDdGopAgAiFUIQiKdB/wFxIQsgBygCOCAHKAI0QQN0aikCACIWQiCIpyEJIBVCIIghFyAUQiCIpyECAkAgFkIQiKdB/wFxIgNBAk8EQAJAIAZFIANBGUlyRQRAIAkgB0EYaiADQSAgBygCHGsiCiAKIANLGyIKEAUgAyAKayIDdGohCSAHQRhqEAQaIANFDQEgB0EYaiADEAUgCWohCQwBCyAHQRhqIAMQBSAJaiEJIAdBGGoQBBoLIAcpAkQhGCAHIAk2AkQgByAYNwNIDAELAkAgA0UEQCACBEAgBygCRCEJDAMLIAcoAkghCQwBCwJAAkAgB0EYakEBEAUgCSACRWpqIgNBA0YEQCAHKAJEQX9qIgMgA0VqIQkMAQsgA0ECdCAHaigCRCIJIAlFaiEJIANBAUYNAQsgByAHKAJINgJMCwsgByAHKAJENgJIIAcgCTYCRAsgF6chAyALBEAgB0EYaiALEAUgA2ohAwsgCCALakEUTwRAIAdBGGoQBBoLIAgEQCAHQRhqIAgQBSACaiECCyAHQRhqEAQaIAcgB0EYaiAUQhiIp0H/AXEQCCAUp0H//wNxajYCLCAHIAdBGGogFUIYiKdB/wFxEAggFadB//8DcWo2AjwgB0EYahAEGiAHIAdBGGogFkIYiKdB/wFxEAggFqdB//8DcWo2AjQgByACNgJgIAcoAlwhCiAHIAk2AmggByADNgJkAkACQAJAIAQgAiADaiILaiASSw0AIAIgCmoiEyAPSw0AIA0gBGsgC0Egak8NAQsgByAHKQNoNwMQIAcgBykDYDcDCCAEIA0gB0EIaiAHQdwAaiAPIA4gESAQEB4hCwwBCyACIARqIQggBCAKEAcgAkERTwRAIARBEGohAgNAIAIgCkEQaiIKEAcgAkEQaiICIAhJDQALCyAIIAlrIQIgByATNgJcIAkgCCAOa0sEQCAJIAggEWtLBEBBbCELDAILIBAgAiAOayICaiIKIANqIBBNBEAgCCAKIAMQDxoMAgsgCCAKQQAgAmsQDyEIIAcgAiADaiIDNgJkIAggAmshCCAOIQILIAlBEE8EQCADIAhqIQMDQCAIIAIQByACQRBqIQIgCEEQaiIIIANJDQALDAELAkAgCUEHTQRAIAggAi0AADoAACAIIAItAAE6AAEgCCACLQACOgACIAggAi0AAzoAAyAIQQRqIAIgCUECdCIDQcAeaigCAGoiAhAXIAIgA0HgHmooAgBrIQIgBygCZCEDDAELIAggAhAMCyADQQlJDQAgAyAIaiEDIAhBCGoiCCACQQhqIgJrQQ9MBEADQCAIIAIQDCACQQhqIQIgCEEIaiIIIANJDQAMAgALAAsDQCAIIAIQByACQRBqIQIgCEEQaiIIIANJDQALCyAHQRhqEAQaIAsgDCALEAMiAhshDCAEIAQgC2ogAhshBCAFQX9qIgUNAAsgDBADDQFBbCEMIAdBGGoQBEECSQ0BQQAhCANAIAhBA0cEQCAAIAhBAnQiAmpBrNABaiACIAdqKAJENgIAIAhBAWohCAwBCwsgBygCXCEIC0G6fyEMIA8gCGsiACANIARrSw0AIAQEfyAEIAggABALIABqBUEACyABayEMCyAHQfAAaiQAIAwLkRcCFn8FfiMAQdABayIHJAAgByAAKALw4QEiCDYCvAEgASACaiESIAggACgCgOIBaiETAkACQCAFRQRAIAEhAwwBCyAAKALE4AEhESAAKALA4AEhFSAAKAK84AEhDyAAQQE2AozhAUEAIQgDQCAIQQNHBEAgByAIQQJ0IgJqIAAgAmpBrNABaigCADYCVCAIQQFqIQgMAQsLIAcgETYCZCAHIA82AmAgByABIA9rNgJoQWwhECAHQShqIAMgBBAGEAMNASAFQQQgBUEESBshFyAHQTxqIAdBKGogACgCABATIAdBxABqIAdBKGogACgCCBATIAdBzABqIAdBKGogACgCBBATQQAhBCAHQeAAaiEMIAdB5ABqIQoDQCAHQShqEARBAksgBCAXTnJFBEAgBygCQCAHKAI8QQN0aikCACIdQhCIp0H/AXEhCyAHKAJQIAcoAkxBA3RqKQIAIh5CEIinQf8BcSEJIAcoAkggBygCREEDdGopAgAiH0IgiKchCCAeQiCIISAgHUIgiKchAgJAIB9CEIinQf8BcSIDQQJPBEACQCAGRSADQRlJckUEQCAIIAdBKGogA0EgIAcoAixrIg0gDSADSxsiDRAFIAMgDWsiA3RqIQggB0EoahAEGiADRQ0BIAdBKGogAxAFIAhqIQgMAQsgB0EoaiADEAUgCGohCCAHQShqEAQaCyAHKQJUISEgByAINgJUIAcgITcDWAwBCwJAIANFBEAgAgRAIAcoAlQhCAwDCyAHKAJYIQgMAQsCQAJAIAdBKGpBARAFIAggAkVqaiIDQQNGBEAgBygCVEF/aiIDIANFaiEIDAELIANBAnQgB2ooAlQiCCAIRWohCCADQQFGDQELIAcgBygCWDYCXAsLIAcgBygCVDYCWCAHIAg2AlQLICCnIQMgCQRAIAdBKGogCRAFIANqIQMLIAkgC2pBFE8EQCAHQShqEAQaCyALBEAgB0EoaiALEAUgAmohAgsgB0EoahAEGiAHIAcoAmggAmoiCSADajYCaCAKIAwgCCAJSxsoAgAhDSAHIAdBKGogHUIYiKdB/wFxEAggHadB//8DcWo2AjwgByAHQShqIB5CGIinQf8BcRAIIB6nQf//A3FqNgJMIAdBKGoQBBogB0EoaiAfQhiIp0H/AXEQCCEOIAdB8ABqIARBBHRqIgsgCSANaiAIazYCDCALIAg2AgggCyADNgIEIAsgAjYCACAHIA4gH6dB//8DcWo2AkQgBEEBaiEEDAELCyAEIBdIDQEgEkFgaiEYIAdB4ABqIRogB0HkAGohGyABIQMDQCAHQShqEARBAksgBCAFTnJFBEAgBygCQCAHKAI8QQN0aikCACIdQhCIp0H/AXEhCyAHKAJQIAcoAkxBA3RqKQIAIh5CEIinQf8BcSEIIAcoAkggBygCREEDdGopAgAiH0IgiKchCSAeQiCIISAgHUIgiKchDAJAIB9CEIinQf8BcSICQQJPBEACQCAGRSACQRlJckUEQCAJIAdBKGogAkEgIAcoAixrIgogCiACSxsiChAFIAIgCmsiAnRqIQkgB0EoahAEGiACRQ0BIAdBKGogAhAFIAlqIQkMAQsgB0EoaiACEAUgCWohCSAHQShqEAQaCyAHKQJUISEgByAJNgJUIAcgITcDWAwBCwJAIAJFBEAgDARAIAcoAlQhCQwDCyAHKAJYIQkMAQsCQAJAIAdBKGpBARAFIAkgDEVqaiICQQNGBEAgBygCVEF/aiICIAJFaiEJDAELIAJBAnQgB2ooAlQiCSAJRWohCSACQQFGDQELIAcgBygCWDYCXAsLIAcgBygCVDYCWCAHIAk2AlQLICCnIRQgCARAIAdBKGogCBAFIBRqIRQLIAggC2pBFE8EQCAHQShqEAQaCyALBEAgB0EoaiALEAUgDGohDAsgB0EoahAEGiAHIAcoAmggDGoiGSAUajYCaCAbIBogCSAZSxsoAgAhHCAHIAdBKGogHUIYiKdB/wFxEAggHadB//8DcWo2AjwgByAHQShqIB5CGIinQf8BcRAIIB6nQf//A3FqNgJMIAdBKGoQBBogByAHQShqIB9CGIinQf8BcRAIIB+nQf//A3FqNgJEIAcgB0HwAGogBEEDcUEEdGoiDSkDCCIdNwPIASAHIA0pAwAiHjcDwAECQAJAAkAgBygCvAEiDiAepyICaiIWIBNLDQAgAyAHKALEASIKIAJqIgtqIBhLDQAgEiADayALQSBqTw0BCyAHIAcpA8gBNwMQIAcgBykDwAE3AwggAyASIAdBCGogB0G8AWogEyAPIBUgERAeIQsMAQsgAiADaiEIIAMgDhAHIAJBEU8EQCADQRBqIQIDQCACIA5BEGoiDhAHIAJBEGoiAiAISQ0ACwsgCCAdpyIOayECIAcgFjYCvAEgDiAIIA9rSwRAIA4gCCAVa0sEQEFsIQsMAgsgESACIA9rIgJqIhYgCmogEU0EQCAIIBYgChAPGgwCCyAIIBZBACACaxAPIQggByACIApqIgo2AsQBIAggAmshCCAPIQILIA5BEE8EQCAIIApqIQoDQCAIIAIQByACQRBqIQIgCEEQaiIIIApJDQALDAELAkAgDkEHTQRAIAggAi0AADoAACAIIAItAAE6AAEgCCACLQACOgACIAggAi0AAzoAAyAIQQRqIAIgDkECdCIKQcAeaigCAGoiAhAXIAIgCkHgHmooAgBrIQIgBygCxAEhCgwBCyAIIAIQDAsgCkEJSQ0AIAggCmohCiAIQQhqIgggAkEIaiICa0EPTARAA0AgCCACEAwgAkEIaiECIAhBCGoiCCAKSQ0ADAIACwALA0AgCCACEAcgAkEQaiECIAhBEGoiCCAKSQ0ACwsgCxADBEAgCyEQDAQFIA0gDDYCACANIBkgHGogCWs2AgwgDSAJNgIIIA0gFDYCBCAEQQFqIQQgAyALaiEDDAILAAsLIAQgBUgNASAEIBdrIQtBACEEA0AgCyAFSARAIAcgB0HwAGogC0EDcUEEdGoiAikDCCIdNwPIASAHIAIpAwAiHjcDwAECQAJAAkAgBygCvAEiDCAepyICaiIKIBNLDQAgAyAHKALEASIJIAJqIhBqIBhLDQAgEiADayAQQSBqTw0BCyAHIAcpA8gBNwMgIAcgBykDwAE3AxggAyASIAdBGGogB0G8AWogEyAPIBUgERAeIRAMAQsgAiADaiEIIAMgDBAHIAJBEU8EQCADQRBqIQIDQCACIAxBEGoiDBAHIAJBEGoiAiAISQ0ACwsgCCAdpyIGayECIAcgCjYCvAEgBiAIIA9rSwRAIAYgCCAVa0sEQEFsIRAMAgsgESACIA9rIgJqIgwgCWogEU0EQCAIIAwgCRAPGgwCCyAIIAxBACACaxAPIQggByACIAlqIgk2AsQBIAggAmshCCAPIQILIAZBEE8EQCAIIAlqIQYDQCAIIAIQByACQRBqIQIgCEEQaiIIIAZJDQALDAELAkAgBkEHTQRAIAggAi0AADoAACAIIAItAAE6AAEgCCACLQACOgACIAggAi0AAzoAAyAIQQRqIAIgBkECdCIGQcAeaigCAGoiAhAXIAIgBkHgHmooAgBrIQIgBygCxAEhCQwBCyAIIAIQDAsgCUEJSQ0AIAggCWohBiAIQQhqIgggAkEIaiICa0EPTARAA0AgCCACEAwgAkEIaiECIAhBCGoiCCAGSQ0ADAIACwALA0AgCCACEAcgAkEQaiECIAhBEGoiCCAGSQ0ACwsgEBADDQMgC0EBaiELIAMgEGohAwwBCwsDQCAEQQNHBEAgACAEQQJ0IgJqQazQAWogAiAHaigCVDYCACAEQQFqIQQMAQsLIAcoArwBIQgLQbp/IRAgEyAIayIAIBIgA2tLDQAgAwR/IAMgCCAAEAsgAGoFQQALIAFrIRALIAdB0AFqJAAgEAslACAAQgA3AgAgAEEAOwEIIABBADoACyAAIAE2AgwgACACOgAKC7QFAQN/IwBBMGsiBCQAIABB/wFqIgVBfWohBgJAIAMvAQIEQCAEQRhqIAEgAhAGIgIQAw0BIARBEGogBEEYaiADEBwgBEEIaiAEQRhqIAMQHCAAIQMDQAJAIARBGGoQBCADIAZPckUEQCADIARBEGogBEEYahASOgAAIAMgBEEIaiAEQRhqEBI6AAEgBEEYahAERQ0BIANBAmohAwsgBUF+aiEFAn8DQEG6fyECIAMiASAFSw0FIAEgBEEQaiAEQRhqEBI6AAAgAUEBaiEDIARBGGoQBEEDRgRAQQIhAiAEQQhqDAILIAMgBUsNBSABIARBCGogBEEYahASOgABIAFBAmohA0EDIQIgBEEYahAEQQNHDQALIARBEGoLIQUgAyAFIARBGGoQEjoAACABIAJqIABrIQIMAwsgAyAEQRBqIARBGGoQEjoAAiADIARBCGogBEEYahASOgADIANBBGohAwwAAAsACyAEQRhqIAEgAhAGIgIQAw0AIARBEGogBEEYaiADEBwgBEEIaiAEQRhqIAMQHCAAIQMDQAJAIARBGGoQBCADIAZPckUEQCADIARBEGogBEEYahAROgAAIAMgBEEIaiAEQRhqEBE6AAEgBEEYahAERQ0BIANBAmohAwsgBUF+aiEFAn8DQEG6fyECIAMiASAFSw0EIAEgBEEQaiAEQRhqEBE6AAAgAUEBaiEDIARBGGoQBEEDRgRAQQIhAiAEQQhqDAILIAMgBUsNBCABIARBCGogBEEYahAROgABIAFBAmohA0EDIQIgBEEYahAEQQNHDQALIARBEGoLIQUgAyAFIARBGGoQEToAACABIAJqIABrIQIMAgsgAyAEQRBqIARBGGoQEToAAiADIARBCGogBEEYahAROgADIANBBGohAwwAAAsACyAEQTBqJAAgAgtpAQF/An8CQAJAIAJBB00NACABKAAAQbfIwuF+Rw0AIAAgASgABDYCmOIBQWIgAEEQaiABIAIQPiIDEAMNAhogAEKBgICAEDcDiOEBIAAgASADaiACIANrECoMAQsgACABIAIQKgtBAAsLrQMBBn8jAEGAAWsiAyQAQWIhCAJAIAJBCUkNACAAQZjQAGogAUEIaiIEIAJBeGogAEGY0AAQMyIFEAMiBg0AIANBHzYCfCADIANB/ABqIANB+ABqIAQgBCAFaiAGGyIEIAEgAmoiAiAEaxAVIgUQAw0AIAMoAnwiBkEfSw0AIAMoAngiB0EJTw0AIABBiCBqIAMgBkGAC0GADCAHEBggA0E0NgJ8IAMgA0H8AGogA0H4AGogBCAFaiIEIAIgBGsQFSIFEAMNACADKAJ8IgZBNEsNACADKAJ4IgdBCk8NACAAQZAwaiADIAZBgA1B4A4gBxAYIANBIzYCfCADIANB/ABqIANB+ABqIAQgBWoiBCACIARrEBUiBRADDQAgAygCfCIGQSNLDQAgAygCeCIHQQpPDQAgACADIAZBwBBB0BEgBxAYIAQgBWoiBEEMaiIFIAJLDQAgAiAFayEFQQAhAgNAIAJBA0cEQCAEKAAAIgZBf2ogBU8NAiAAIAJBAnRqQZzQAWogBjYCACACQQFqIQIgBEEEaiEEDAELCyAEIAFrIQgLIANBgAFqJAAgCAtGAQN/IABBCGohAyAAKAIEIQJBACEAA0AgACACdkUEQCABIAMgAEEDdGotAAJBFktqIQEgAEEBaiEADAELCyABQQggAmt0C4YDAQV/Qbh/IQcCQCADRQ0AIAItAAAiBEUEQCABQQA2AgBBAUG4fyADQQFGGw8LAn8gAkEBaiIFIARBGHRBGHUiBkF/Sg0AGiAGQX9GBEAgA0EDSA0CIAUvAABBgP4BaiEEIAJBA2oMAQsgA0ECSA0BIAItAAEgBEEIdHJBgIB+aiEEIAJBAmoLIQUgASAENgIAIAVBAWoiASACIANqIgNLDQBBbCEHIABBEGogACAFLQAAIgVBBnZBI0EJIAEgAyABa0HAEEHQEUHwEiAAKAKM4QEgACgCnOIBIAQQHyIGEAMiCA0AIABBmCBqIABBCGogBUEEdkEDcUEfQQggASABIAZqIAgbIgEgAyABa0GAC0GADEGAFyAAKAKM4QEgACgCnOIBIAQQHyIGEAMiCA0AIABBoDBqIABBBGogBUECdkEDcUE0QQkgASABIAZqIAgbIgEgAyABa0GADUHgDkGQGSAAKAKM4QEgACgCnOIBIAQQHyIAEAMNACAAIAFqIAJrIQcLIAcLrQMBCn8jAEGABGsiCCQAAn9BUiACQf8BSw0AGkFUIANBDEsNABogAkEBaiELIABBBGohCUGAgAQgA0F/anRBEHUhCkEAIQJBASEEQQEgA3QiB0F/aiIMIQUDQCACIAtGRQRAAkAgASACQQF0Ig1qLwEAIgZB//8DRgRAIAkgBUECdGogAjoAAiAFQX9qIQVBASEGDAELIARBACAKIAZBEHRBEHVKGyEECyAIIA1qIAY7AQAgAkEBaiECDAELCyAAIAQ7AQIgACADOwEAIAdBA3YgB0EBdmpBA2ohBkEAIQRBACECA0AgBCALRkUEQCABIARBAXRqLgEAIQpBACEAA0AgACAKTkUEQCAJIAJBAnRqIAQ6AAIDQCACIAZqIAxxIgIgBUsNAAsgAEEBaiEADAELCyAEQQFqIQQMAQsLQX8gAg0AGkEAIQIDfyACIAdGBH9BAAUgCCAJIAJBAnRqIgAtAAJBAXRqIgEgAS8BACIBQQFqOwEAIAAgAyABEBRrIgU6AAMgACABIAVB/wFxdCAHazsBACACQQFqIQIMAQsLCyEFIAhBgARqJAAgBQvjBgEIf0FsIQcCQCACQQNJDQACQAJAAkACQCABLQAAIgNBA3EiCUEBaw4DAwEAAgsgACgCiOEBDQBBYg8LIAJBBUkNAkEDIQYgASgAACEFAn8CQAJAIANBAnZBA3EiCEF+aiIEQQFNBEAgBEEBaw0BDAILIAVBDnZB/wdxIQQgBUEEdkH/B3EhAyAIRQwCCyAFQRJ2IQRBBCEGIAVBBHZB//8AcSEDQQAMAQsgBUEEdkH//w9xIgNBgIAISw0DIAEtAARBCnQgBUEWdnIhBEEFIQZBAAshBSAEIAZqIgogAksNAgJAIANBgQZJDQAgACgCnOIBRQ0AQQAhAgNAIAJBg4ABSw0BIAJBQGshAgwAAAsACwJ/IAlBA0YEQCABIAZqIQEgAEHw4gFqIQIgACgCDCEGIAUEQCACIAMgASAEIAYQXwwCCyACIAMgASAEIAYQXQwBCyAAQbjQAWohAiABIAZqIQEgAEHw4gFqIQYgAEGo0ABqIQggBQRAIAggBiADIAEgBCACEF4MAQsgCCAGIAMgASAEIAIQXAsQAw0CIAAgAzYCgOIBIABBATYCiOEBIAAgAEHw4gFqNgLw4QEgCUECRgRAIAAgAEGo0ABqNgIMCyAAIANqIgBBiOMBakIANwAAIABBgOMBakIANwAAIABB+OIBakIANwAAIABB8OIBakIANwAAIAoPCwJ/AkACQAJAIANBAnZBA3FBf2oiBEECSw0AIARBAWsOAgACAQtBASEEIANBA3YMAgtBAiEEIAEvAABBBHYMAQtBAyEEIAEQIUEEdgsiAyAEaiIFQSBqIAJLBEAgBSACSw0CIABB8OIBaiABIARqIAMQCyEBIAAgAzYCgOIBIAAgATYC8OEBIAEgA2oiAEIANwAYIABCADcAECAAQgA3AAggAEIANwAAIAUPCyAAIAM2AoDiASAAIAEgBGo2AvDhASAFDwsCfwJAAkACQCADQQJ2QQNxQX9qIgRBAksNACAEQQFrDgIAAgELQQEhByADQQN2DAILQQIhByABLwAAQQR2DAELIAJBBEkgARAhIgJBj4CAAUtyDQFBAyEHIAJBBHYLIQIgAEHw4gFqIAEgB2otAAAgAkEgahAQIQEgACACNgKA4gEgACABNgLw4QEgB0EBaiEHCyAHC0sAIABC+erQ0OfJoeThADcDICAAQgA3AxggAELP1tO+0ser2UI3AxAgAELW64Lu6v2J9eAANwMIIABCADcDACAAQShqQQBBKBAQGgviAgICfwV+IABBKGoiASAAKAJIaiECAn4gACkDACIDQiBaBEAgACkDECIEQgeJIAApAwgiBUIBiXwgACkDGCIGQgyJfCAAKQMgIgdCEol8IAUQGSAEEBkgBhAZIAcQGQwBCyAAKQMYQsXP2bLx5brqJ3wLIAN8IQMDQCABQQhqIgAgAk0EQEIAIAEpAAAQCSADhUIbiUKHla+vmLbem55/fkLj3MqV/M7y9YV/fCEDIAAhAQwBCwsCQCABQQRqIgAgAksEQCABIQAMAQsgASgAAK1Ch5Wvr5i23puef34gA4VCF4lCz9bTvtLHq9lCfkL5893xmfaZqxZ8IQMLA0AgACACSQRAIAAxAABCxc/ZsvHluuonfiADhUILiUKHla+vmLbem55/fiEDIABBAWohAAwBCwsgA0IhiCADhULP1tO+0ser2UJ+IgNCHYggA4VC+fPd8Zn2masWfiIDQiCIIAOFC+8CAgJ/BH4gACAAKQMAIAKtfDcDAAJAAkAgACgCSCIDIAJqIgRBH00EQCABRQ0BIAAgA2pBKGogASACECAgACgCSCACaiEEDAELIAEgAmohAgJ/IAMEQCAAQShqIgQgA2ogAUEgIANrECAgACAAKQMIIAQpAAAQCTcDCCAAIAApAxAgACkAMBAJNwMQIAAgACkDGCAAKQA4EAk3AxggACAAKQMgIABBQGspAAAQCTcDICAAKAJIIQMgAEEANgJIIAEgA2tBIGohAQsgAUEgaiACTQsEQCACQWBqIQMgACkDICEFIAApAxghBiAAKQMQIQcgACkDCCEIA0AgCCABKQAAEAkhCCAHIAEpAAgQCSEHIAYgASkAEBAJIQYgBSABKQAYEAkhBSABQSBqIgEgA00NAAsgACAFNwMgIAAgBjcDGCAAIAc3AxAgACAINwMICyABIAJPDQEgAEEoaiABIAIgAWsiBBAgCyAAIAQ2AkgLCy8BAX8gAEUEQEG2f0EAIAMbDwtBun8hBCADIAFNBH8gACACIAMQEBogAwVBun8LCy8BAX8gAEUEQEG2f0EAIAMbDwtBun8hBCADIAFNBH8gACACIAMQCxogAwVBun8LC6gCAQZ/IwBBEGsiByQAIABB2OABaikDAEKAgIAQViEIQbh/IQUCQCAEQf//B0sNACAAIAMgBBBCIgUQAyIGDQAgACgCnOIBIQkgACAHQQxqIAMgAyAFaiAGGyIKIARBACAFIAYbayIGEEAiAxADBEAgAyEFDAELIAcoAgwhBCABRQRAQbp/IQUgBEEASg0BCyAGIANrIQUgAyAKaiEDAkAgCQRAIABBADYCnOIBDAELAkACQAJAIARBBUgNACAAQdjgAWopAwBCgICACFgNAAwBCyAAQQA2ApziAQwBCyAAKAIIED8hBiAAQQA2ApziASAGQRRPDQELIAAgASACIAMgBSAEIAgQOSEFDAELIAAgASACIAMgBSAEIAgQOiEFCyAHQRBqJAAgBQtnACAAQdDgAWogASACIAAoAuzhARAuIgEQAwRAIAEPC0G4fyECAkAgAQ0AIABB7OABaigCACIBBEBBYCECIAAoApjiASABRw0BC0EAIQIgAEHw4AFqKAIARQ0AIABBkOEBahBDCyACCycBAX8QVyIERQRAQUAPCyAEIAAgASACIAMgBBBLEE8hACAEEFYgAAs/AQF/AkACQAJAIAAoAqDiAUEBaiIBQQJLDQAgAUEBaw4CAAECCyAAEDBBAA8LIABBADYCoOIBCyAAKAKU4gELvAMCB38BfiMAQRBrIgkkAEG4fyEGAkAgBCgCACIIQQVBCSAAKALs4QEiBRtJDQAgAygCACIHQQFBBSAFGyAFEC8iBRADBEAgBSEGDAELIAggBUEDakkNACAAIAcgBRBJIgYQAw0AIAEgAmohCiAAQZDhAWohCyAIIAVrIQIgBSAHaiEHIAEhBQNAIAcgAiAJECwiBhADDQEgAkF9aiICIAZJBEBBuH8hBgwCCyAJKAIAIghBAksEQEFsIQYMAgsgB0EDaiEHAn8CQAJAAkAgCEEBaw4CAgABCyAAIAUgCiAFayAHIAYQSAwCCyAFIAogBWsgByAGEEcMAQsgBSAKIAVrIActAAAgCSgCCBBGCyIIEAMEQCAIIQYMAgsgACgC8OABBEAgCyAFIAgQRQsgAiAGayECIAYgB2ohByAFIAhqIQUgCSgCBEUNAAsgACkD0OABIgxCf1IEQEFsIQYgDCAFIAFrrFINAQsgACgC8OABBEBBaiEGIAJBBEkNASALEEQhDCAHKAAAIAynRw0BIAdBBGohByACQXxqIQILIAMgBzYCACAEIAI2AgAgBSABayEGCyAJQRBqJAAgBgsuACAAECsCf0EAQQAQAw0AGiABRSACRXJFBEBBYiAAIAEgAhA9EAMNARoLQQALCzcAIAEEQCAAIAAoAsTgASABKAIEIAEoAghqRzYCnOIBCyAAECtBABADIAFFckUEQCAAIAEQWwsL0QIBB38jAEEQayIGJAAgBiAENgIIIAYgAzYCDCAFBEAgBSgCBCEKIAUoAgghCQsgASEIAkACQANAIAAoAuzhARAWIQsCQANAIAQgC0kNASADKAAAQXBxQdDUtMIBRgRAIAMgBBAiIgcQAw0EIAQgB2shBCADIAdqIQMMAQsLIAYgAzYCDCAGIAQ2AggCQCAFBEAgACAFEE5BACEHQQAQA0UNAQwFCyAAIAogCRBNIgcQAw0ECyAAIAgQUCAMQQFHQQAgACAIIAIgBkEMaiAGQQhqEEwiByIDa0EAIAMQAxtBCkdyRQRAQbh/IQcMBAsgBxADDQMgAiAHayECIAcgCGohCEEBIQwgBigCDCEDIAYoAgghBAwBCwsgBiADNgIMIAYgBDYCCEG4fyEHIAQNASAIIAFrIQcMAQsgBiADNgIMIAYgBDYCCAsgBkEQaiQAIAcLRgECfyABIAAoArjgASICRwRAIAAgAjYCxOABIAAgATYCuOABIAAoArzgASEDIAAgATYCvOABIAAgASADIAJrajYCwOABCwutAgIEfwF+IwBBQGoiBCQAAkACQCACQQhJDQAgASgAAEFwcUHQ1LTCAUcNACABIAIQIiEBIABCADcDCCAAQQA2AgQgACABNgIADAELIARBGGogASACEC0iAxADBEAgACADEBoMAQsgAwRAIABBuH8QGgwBCyACIAQoAjAiA2shAiABIANqIQMDQAJAIAAgAyACIARBCGoQLCIFEAMEfyAFBSACIAVBA2oiBU8NAUG4fwsQGgwCCyAGQQFqIQYgAiAFayECIAMgBWohAyAEKAIMRQ0ACyAEKAI4BEAgAkEDTQRAIABBuH8QGgwCCyADQQRqIQMLIAQoAighAiAEKQMYIQcgAEEANgIEIAAgAyABazYCACAAIAIgBmytIAcgB0J/URs3AwgLIARBQGskAAslAQF/IwBBEGsiAiQAIAIgACABEFEgAigCACEAIAJBEGokACAAC30BBH8jAEGQBGsiBCQAIARB/wE2AggCQCAEQRBqIARBCGogBEEMaiABIAIQFSIGEAMEQCAGIQUMAQtBVCEFIAQoAgwiB0EGSw0AIAMgBEEQaiAEKAIIIAcQQSIFEAMNACAAIAEgBmogAiAGayADEDwhBQsgBEGQBGokACAFC4cBAgJ/An5BABAWIQMCQANAIAEgA08EQAJAIAAoAABBcHFB0NS0wgFGBEAgACABECIiAhADRQ0BQn4PCyAAIAEQVSIEQn1WDQMgBCAFfCIFIARUIQJCfiEEIAINAyAAIAEQUiICEAMNAwsgASACayEBIAAgAmohAAwBCwtCfiAFIAEbIQQLIAQLPwIBfwF+IwBBMGsiAiQAAn5CfiACQQhqIAAgARAtDQAaQgAgAigCHEEBRg0AGiACKQMICyEDIAJBMGokACADC40BAQJ/IwBBMGsiASQAAkAgAEUNACAAKAKI4gENACABIABB/OEBaigCADYCKCABIAApAvThATcDICAAEDAgACgCqOIBIQIgASABKAIoNgIYIAEgASkDIDcDECACIAFBEGoQGyAAQQA2AqjiASABIAEoAig2AgggASABKQMgNwMAIAAgARAbCyABQTBqJAALKgECfyMAQRBrIgAkACAAQQA2AgggAEIANwMAIAAQWCEBIABBEGokACABC4cBAQN/IwBBEGsiAiQAAkAgACgCAEUgACgCBEVzDQAgAiAAKAIINgIIIAIgACkCADcDAAJ/IAIoAgAiAQRAIAIoAghBqOMJIAERBQAMAQtBqOMJECgLIgFFDQAgASAAKQIANwL04QEgAUH84QFqIAAoAgg2AgAgARBZIAEhAwsgAkEQaiQAIAMLywEBAn8jAEEgayIBJAAgAEGBgIDAADYCtOIBIABBADYCiOIBIABBADYC7OEBIABCADcDkOIBIABBADYCpOMJIABBADYC3OIBIABCADcCzOIBIABBADYCvOIBIABBADYCxOABIABCADcCnOIBIABBpOIBakIANwIAIABBrOIBakEANgIAIAFCADcCECABQgA3AhggASABKQMYNwMIIAEgASkDEDcDACABKAIIQQh2QQFxIQIgAEEANgLg4gEgACACNgKM4gEgAUEgaiQAC3YBA38jAEEwayIBJAAgAARAIAEgAEHE0AFqIgIoAgA2AiggASAAKQK80AE3AyAgACgCACEDIAEgAigCADYCGCABIAApArzQATcDECADIAFBEGoQGyABIAEoAig2AgggASABKQMgNwMAIAAgARAbCyABQTBqJAALzAEBAX8gACABKAK00AE2ApjiASAAIAEoAgQiAjYCwOABIAAgAjYCvOABIAAgAiABKAIIaiICNgK44AEgACACNgLE4AEgASgCuNABBEAgAEKBgICAEDcDiOEBIAAgAUGk0ABqNgIMIAAgAUGUIGo2AgggACABQZwwajYCBCAAIAFBDGo2AgAgAEGs0AFqIAFBqNABaigCADYCACAAQbDQAWogAUGs0AFqKAIANgIAIABBtNABaiABQbDQAWooAgA2AgAPCyAAQgA3A4jhAQs7ACACRQRAQbp/DwsgBEUEQEFsDwsgAiAEEGAEQCAAIAEgAiADIAQgBRBhDwsgACABIAIgAyAEIAUQZQtGAQF/IwBBEGsiBSQAIAVBCGogBBAOAn8gBS0ACQRAIAAgASACIAMgBBAyDAELIAAgASACIAMgBBA0CyEAIAVBEGokACAACzQAIAAgAyAEIAUQNiIFEAMEQCAFDwsgBSAESQR/IAEgAiADIAVqIAQgBWsgABA1BUG4fwsLRgEBfyMAQRBrIgUkACAFQQhqIAQQDgJ/IAUtAAkEQCAAIAEgAiADIAQQYgwBCyAAIAEgAiADIAQQNQshACAFQRBqJAAgAAtZAQF/QQ8hAiABIABJBEAgAUEEdCAAbiECCyAAQQh2IgEgAkEYbCIAQYwIaigCAGwgAEGICGooAgBqIgJBA3YgAmogAEGACGooAgAgAEGECGooAgAgAWxqSQs3ACAAIAMgBCAFQYAQEDMiBRADBEAgBQ8LIAUgBEkEfyABIAIgAyAFaiAEIAVrIAAQMgVBuH8LC78DAQN/IwBBIGsiBSQAIAVBCGogAiADEAYiAhADRQRAIAAgAWoiB0F9aiEGIAUgBBAOIARBBGohAiAFLQACIQMDQEEAIAAgBkkgBUEIahAEGwRAIAAgAiAFQQhqIAMQAkECdGoiBC8BADsAACAFQQhqIAQtAAIQASAAIAQtAANqIgQgAiAFQQhqIAMQAkECdGoiAC8BADsAACAFQQhqIAAtAAIQASAEIAAtAANqIQAMAQUgB0F+aiEEA0AgBUEIahAEIAAgBEtyRQRAIAAgAiAFQQhqIAMQAkECdGoiBi8BADsAACAFQQhqIAYtAAIQASAAIAYtAANqIQAMAQsLA0AgACAES0UEQCAAIAIgBUEIaiADEAJBAnRqIgYvAQA7AAAgBUEIaiAGLQACEAEgACAGLQADaiEADAELCwJAIAAgB08NACAAIAIgBUEIaiADEAIiA0ECdGoiAC0AADoAACAALQADQQFGBEAgBUEIaiAALQACEAEMAQsgBSgCDEEfSw0AIAVBCGogAiADQQJ0ai0AAhABIAUoAgxBIUkNACAFQSA2AgwLIAFBbCAFQQhqEAobIQILCwsgBUEgaiQAIAILkgIBBH8jAEFAaiIJJAAgCSADQTQQCyEDAkAgBEECSA0AIAMgBEECdGooAgAhCSADQTxqIAgQIyADQQE6AD8gAyACOgA+QQAhBCADKAI8IQoDQCAEIAlGDQEgACAEQQJ0aiAKNgEAIARBAWohBAwAAAsAC0EAIQkDQCAGIAlGRQRAIAMgBSAJQQF0aiIKLQABIgtBAnRqIgwoAgAhBCADQTxqIAotAABBCHQgCGpB//8DcRAjIANBAjoAPyADIAcgC2siCiACajoAPiAEQQEgASAKa3RqIQogAygCPCELA0AgACAEQQJ0aiALNgEAIARBAWoiBCAKSQ0ACyAMIAo2AgAgCUEBaiEJDAELCyADQUBrJAALowIBCX8jAEHQAGsiCSQAIAlBEGogBUE0EAsaIAcgBmshDyAHIAFrIRADQAJAIAMgCkcEQEEBIAEgByACIApBAXRqIgYtAAEiDGsiCGsiC3QhDSAGLQAAIQ4gCUEQaiAMQQJ0aiIMKAIAIQYgCyAPTwRAIAAgBkECdGogCyAIIAUgCEE0bGogCCAQaiIIQQEgCEEBShsiCCACIAQgCEECdGooAgAiCEEBdGogAyAIayAHIA4QYyAGIA1qIQgMAgsgCUEMaiAOECMgCUEBOgAPIAkgCDoADiAGIA1qIQggCSgCDCELA0AgBiAITw0CIAAgBkECdGogCzYBACAGQQFqIQYMAAALAAsgCUHQAGokAA8LIAwgCDYCACAKQQFqIQoMAAALAAs0ACAAIAMgBCAFEDYiBRADBEAgBQ8LIAUgBEkEfyABIAIgAyAFaiAEIAVrIAAQNAVBuH8LCyMAIAA/AEEQdGtB//8DakEQdkAAQX9GBEBBAA8LQQAQAEEBCzsBAX8gAgRAA0AgACABIAJBgCAgAkGAIEkbIgMQCyEAIAFBgCBqIQEgAEGAIGohACACIANrIgINAAsLCwYAIAAQAwsLqBUJAEGICAsNAQAAAAEAAAACAAAAAgBBoAgLswYBAAAAAQAAAAIAAAACAAAAJgAAAIIAAAAhBQAASgAAAGcIAAAmAAAAwAEAAIAAAABJBQAASgAAAL4IAAApAAAALAIAAIAAAABJBQAASgAAAL4IAAAvAAAAygIAAIAAAACKBQAASgAAAIQJAAA1AAAAcwMAAIAAAACdBQAASgAAAKAJAAA9AAAAgQMAAIAAAADrBQAASwAAAD4KAABEAAAAngMAAIAAAABNBgAASwAAAKoKAABLAAAAswMAAIAAAADBBgAATQAAAB8NAABNAAAAUwQAAIAAAAAjCAAAUQAAAKYPAABUAAAAmQQAAIAAAABLCQAAVwAAALESAABYAAAA2gQAAIAAAABvCQAAXQAAACMUAABUAAAARQUAAIAAAABUCgAAagAAAIwUAABqAAAArwUAAIAAAAB2CQAAfAAAAE4QAAB8AAAA0gIAAIAAAABjBwAAkQAAAJAHAACSAAAAAAAAAAEAAAABAAAABQAAAA0AAAAdAAAAPQAAAH0AAAD9AAAA/QEAAP0DAAD9BwAA/Q8AAP0fAAD9PwAA/X8AAP3/AAD9/wEA/f8DAP3/BwD9/w8A/f8fAP3/PwD9/38A/f//AP3//wH9//8D/f//B/3//w/9//8f/f//P/3//38AAAAAAQAAAAIAAAADAAAABAAAAAUAAAAGAAAABwAAAAgAAAAJAAAACgAAAAsAAAAMAAAADQAAAA4AAAAPAAAAEAAAABEAAAASAAAAEwAAABQAAAAVAAAAFgAAABcAAAAYAAAAGQAAABoAAAAbAAAAHAAAAB0AAAAeAAAAHwAAAAMAAAAEAAAABQAAAAYAAAAHAAAACAAAAAkAAAAKAAAACwAAAAwAAAANAAAADgAAAA8AAAAQAAAAEQAAABIAAAATAAAAFAAAABUAAAAWAAAAFwAAABgAAAAZAAAAGgAAABsAAAAcAAAAHQAAAB4AAAAfAAAAIAAAACEAAAAiAAAAIwAAACUAAAAnAAAAKQAAACsAAAAvAAAAMwAAADsAAABDAAAAUwAAAGMAAACDAAAAAwEAAAMCAAADBAAAAwgAAAMQAAADIAAAA0AAAAOAAAADAAEAQeAPC1EBAAAAAQAAAAEAAAABAAAAAgAAAAIAAAADAAAAAwAAAAQAAAAEAAAABQAAAAcAAAAIAAAACQAAAAoAAAALAAAADAAAAA0AAAAOAAAADwAAABAAQcQQC4sBAQAAAAIAAAADAAAABAAAAAUAAAAGAAAABwAAAAgAAAAJAAAACgAAAAsAAAAMAAAADQAAAA4AAAAPAAAAEAAAABIAAAAUAAAAFgAAABgAAAAcAAAAIAAAACgAAAAwAAAAQAAAAIAAAAAAAQAAAAIAAAAEAAAACAAAABAAAAAgAAAAQAAAAIAAAAAAAQBBkBIL5gQBAAAAAQAAAAEAAAABAAAAAgAAAAIAAAADAAAAAwAAAAQAAAAGAAAABwAAAAgAAAAJAAAACgAAAAsAAAAMAAAADQAAAA4AAAAPAAAAEAAAAAEAAAAEAAAACAAAAAAAAAABAAEBBgAAAAAAAAQAAAAAEAAABAAAAAAgAAAFAQAAAAAAAAUDAAAAAAAABQQAAAAAAAAFBgAAAAAAAAUHAAAAAAAABQkAAAAAAAAFCgAAAAAAAAUMAAAAAAAABg4AAAAAAAEFEAAAAAAAAQUUAAAAAAABBRYAAAAAAAIFHAAAAAAAAwUgAAAAAAAEBTAAAAAgAAYFQAAAAAAABwWAAAAAAAAIBgABAAAAAAoGAAQAAAAADAYAEAAAIAAABAAAAAAAAAAEAQAAAAAAAAUCAAAAIAAABQQAAAAAAAAFBQAAACAAAAUHAAAAAAAABQgAAAAgAAAFCgAAAAAAAAULAAAAAAAABg0AAAAgAAEFEAAAAAAAAQUSAAAAIAABBRYAAAAAAAIFGAAAACAAAwUgAAAAAAADBSgAAAAAAAYEQAAAABAABgRAAAAAIAAHBYAAAAAAAAkGAAIAAAAACwYACAAAMAAABAAAAAAQAAAEAQAAACAAAAUCAAAAIAAABQMAAAAgAAAFBQAAACAAAAUGAAAAIAAABQgAAAAgAAAFCQAAACAAAAULAAAAIAAABQwAAAAAAAAGDwAAACAAAQUSAAAAIAABBRQAAAAgAAIFGAAAACAAAgUcAAAAIAADBSgAAAAgAAQFMAAAAAAAEAYAAAEAAAAPBgCAAAAAAA4GAEAAAAAADQYAIABBgBcLhwIBAAEBBQAAAAAAAAUAAAAAAAAGBD0AAAAAAAkF/QEAAAAADwX9fwAAAAAVBf3/HwAAAAMFBQAAAAAABwR9AAAAAAAMBf0PAAAAABIF/f8DAAAAFwX9/38AAAAFBR0AAAAAAAgE/QAAAAAADgX9PwAAAAAUBf3/DwAAAAIFAQAAABAABwR9AAAAAAALBf0HAAAAABEF/f8BAAAAFgX9/z8AAAAEBQ0AAAAQAAgE/QAAAAAADQX9HwAAAAATBf3/BwAAAAEFAQAAABAABgQ9AAAAAAAKBf0DAAAAABAF/f8AAAAAHAX9//8PAAAbBf3//wcAABoF/f//AwAAGQX9//8BAAAYBf3//wBBkBkLhgQBAAEBBgAAAAAAAAYDAAAAAAAABAQAAAAgAAAFBQAAAAAAAAUGAAAAAAAABQgAAAAAAAAFCQAAAAAAAAULAAAAAAAABg0AAAAAAAAGEAAAAAAAAAYTAAAAAAAABhYAAAAAAAAGGQAAAAAAAAYcAAAAAAAABh8AAAAAAAAGIgAAAAAAAQYlAAAAAAABBikAAAAAAAIGLwAAAAAAAwY7AAAAAAAEBlMAAAAAAAcGgwAAAAAACQYDAgAAEAAABAQAAAAAAAAEBQAAACAAAAUGAAAAAAAABQcAAAAgAAAFCQAAAAAAAAUKAAAAAAAABgwAAAAAAAAGDwAAAAAAAAYSAAAAAAAABhUAAAAAAAAGGAAAAAAAAAYbAAAAAAAABh4AAAAAAAAGIQAAAAAAAQYjAAAAAAABBicAAAAAAAIGKwAAAAAAAwYzAAAAAAAEBkMAAAAAAAUGYwAAAAAACAYDAQAAIAAABAQAAAAwAAAEBAAAABAAAAQFAAAAIAAABQcAAAAgAAAFCAAAACAAAAUKAAAAIAAABQsAAAAAAAAGDgAAAAAAAAYRAAAAAAAABhQAAAAAAAAGFwAAAAAAAAYaAAAAAAAABh0AAAAAAAAGIAAAAAAAEAYDAAEAAAAPBgOAAAAAAA4GA0AAAAAADQYDIAAAAAAMBgMQAAAAAAsGAwgAAAAACgYDBABBpB0L2QEBAAAAAwAAAAcAAAAPAAAAHwAAAD8AAAB/AAAA/wAAAP8BAAD/AwAA/wcAAP8PAAD/HwAA/z8AAP9/AAD//wAA//8BAP//AwD//wcA//8PAP//HwD//z8A//9/AP///wD///8B////A////wf///8P////H////z////9/AAAAAAEAAAACAAAABAAAAAAAAAACAAAABAAAAAgAAAAAAAAAAQAAAAIAAAABAAAABAAAAAQAAAAEAAAABAAAAAgAAAAIAAAACAAAAAcAAAAIAAAACQAAAAoAAAALAEGgIAsDwBBQ";var Sd=new WeakMap,Td=0,Bd,ts=class o extends pn{static{d(this,"KTX2Loader")}constructor(e){super(e),this.transcoderPath="",this.transcoderBinary=null,this.transcoderPending=null,this.workerPool=new oc,this.workerSourceURL="",this.workerConfig=null,typeof MSC_TRANSCODER<"u"&&console.warn('THREE.KTX2Loader: Please update to latest "basis_transcoder". "msc_basis_transcoder" is no longer supported in three.js r125+.')}setTranscoderPath(e){return this.transcoderPath=e,this}setWorkerLimit(e){return this.workerPool.setWorkerLimit(e),this}detectSupport(e){return this.workerConfig={astcSupported:e.extensions.has("WEBGL_compressed_texture_astc"),etc1Supported:e.extensions.has("WEBGL_compressed_texture_etc1"),etc2Supported:e.extensions.has("WEBGL_compressed_texture_etc"),dxtSupported:e.extensions.has("WEBGL_compressed_texture_s3tc"),bptcSupported:e.extensions.has("EXT_texture_compression_bptc"),pvrtcSupported:e.extensions.has("WEBGL_compressed_texture_pvrtc")||e.extensions.has("WEBKIT_WEBGL_compressed_texture_pvrtc")},e.capabilities.isWebGL2&&(this.workerConfig.etc1Supported=!1),this}init(){if(!this.transcoderPending){let e=new An(this.manager);e.setPath(this.transcoderPath),e.setWithCredentials(this.withCredentials);let t=e.loadAsync("basis_transcoder.js"),n=new An(this.manager);n.setPath(this.transcoderPath),n.setResponseType("arraybuffer"),n.setWithCredentials(this.withCredentials);let i=n.loadAsync("basis_transcoder.wasm");this.transcoderPending=Promise.all([t,i]).then(([s,r])=>{let a=o.BasisWorker.toString(),l=["/* constants */","let _EngineFormat = "+JSON.stringify(o.EngineFormat),"let _TranscoderFormat = "+JSON.stringify(o.TranscoderFormat),"let _BasisFormat = "+JSON.stringify(o.BasisFormat),"/* basis_transcoder.js */",s,"/* worker */",a.substring(a.indexOf("{")+1,a.lastIndexOf("}"))].join(`
`);this.workerSourceURL=URL.createObjectURL(new Blob([l])),this.transcoderBinary=r,this.workerPool.setWorkerCreator(()=>{let c=new Worker(this.workerSourceURL),h=this.transcoderBinary.slice(0);return c.postMessage({type:"init",config:this.workerConfig,transcoderBinary:h},[h]),c})}),Td>0&&console.warn("THREE.KTX2Loader: Multiple active KTX2 loaders may cause performance issues. Use a single KTX2Loader instance, or call .dispose() on old instances."),Td++}return this.transcoderPending}load(e,t,n,i){if(this.workerConfig===null)throw new Error("THREE.KTX2Loader: Missing initialization with `.detectSupport( renderer )`.");let s=new An(this.manager);s.setResponseType("arraybuffer"),s.setWithCredentials(this.withCredentials),s.load(e,r=>{if(Sd.has(r))return Sd.get(r).promise.then(t).catch(i);this._createTexture(r).then(a=>t?t(a):null).catch(i)},n,i)}_createTextureFrom(e,t){let{mipmaps:n,width:i,height:s,format:r,type:a,error:l,dfdTransferFn:c,dfdFlags:h}=e;if(a==="error")return Promise.reject(l);let u=t.layerCount>1?new Ll(n,i,s,t.layerCount,r,$t):new zo(n,i,s,r,$t);return u.minFilter=n.length===1?Je:wn,u.magFilter=Je,u.generateMipmaps=!1,u.needsUpdate=!0,u.encoding=c===2?Se:ft,u.premultiplyAlpha=!!(h&1),u}async _createTexture(e,t={}){let n=Nm(new Uint8Array(e));if(n.vkFormat!==0)return Vb(n);let i=t,s=this.init().then(()=>this.workerPool.postMessage({type:"transcode",buffer:e,taskConfig:i},[e])).then(r=>this._createTextureFrom(r.data,n));return Sd.set(e,{promise:s}),s}dispose(){return this.workerPool.dispose(),this.workerSourceURL&&URL.revokeObjectURL(this.workerSourceURL),Td--,this}};ts.BasisFormat={ETC1S:0,UASTC_4x4:1};ts.TranscoderFormat={ETC1:0,ETC2:1,BC1:2,BC3:3,BC4:4,BC5:5,BC7_M6_OPAQUE_ONLY:6,BC7_M5:7,PVRTC1_4_RGB:8,PVRTC1_4_RGBA:9,ASTC_4x4:10,ATC_RGB:11,ATC_RGBA_INTERPOLATED_ALPHA:12,RGBA32:13,RGB565:14,BGR565:15,RGBA4444:16};ts.EngineFormat={RGBAFormat:lt,RGBA_ASTC_4x4_Format:ml,RGBA_BPTC_Format:Mo,RGBA_ETC2_EAC_Format:Al,RGBA_PVRTC_4BPPV1_Format:fl,RGBA_S3TC_DXT5_Format:wo,RGB_ETC1_Format:Iu,RGB_ETC2_Format:pl,RGB_PVRTC_4BPPV1_Format:dl,RGB_S3TC_DXT1_Format:Eo};ts.BasisWorker=function(){let o,e,t,n=_EngineFormat,i=_TranscoderFormat,s=_BasisFormat;self.addEventListener("message",function(g){let A=g.data;switch(A.type){case"init":o=A.config,r(A.transcoderBinary);break;case"transcode":e.then(()=>{try{let{width:m,height:_,hasAlpha:E,mipmaps:x,format:y,dfdTransferFn:w,dfdFlags:I}=a(A.buffer),S=[];for(let v=0;v<x.length;++v)S.push(x[v].data.buffer);self.postMessage({type:"transcode",id:A.id,width:m,height:_,hasAlpha:E,mipmaps:x,format:y,dfdTransferFn:w,dfdFlags:I},S)}catch(m){console.error(m),self.postMessage({type:"error",id:A.id,error:m.message})}});break}});function r(g){e=new Promise(A=>{t={wasmBinary:g,onRuntimeInitialized:A},BASIS(t)}).then(()=>{t.initializeBasis(),t.KTX2File===void 0&&console.warn("THREE.KTX2Loader: Please update Basis Universal transcoder.")})}d(r,"init");function a(g){let A=new t.KTX2File(new Uint8Array(g));function m(){A.close(),A.delete()}if(d(m,"cleanup"),!A.isValid())throw m(),new Error("THREE.KTX2Loader:	Invalid or unsupported .ktx2 file");let _=A.isUASTC()?s.UASTC_4x4:s.ETC1S,E=A.getWidth(),x=A.getHeight(),y=A.getLayers()||1,w=A.getLevels(),I=A.getHasAlpha(),S=A.getDFDTransferFunc(),v=A.getDFDFlags(),{transcoderFormat:b,engineFormat:R}=u(_,E,x,I);if(!E||!x||!w)throw m(),new Error("THREE.KTX2Loader:	Invalid texture");if(!A.startTranscoding())throw m(),new Error("THREE.KTX2Loader: .startTranscoding failed");let N=[];for(let z=0;z<w;z++){let O=[],D,Q;for(let q=0;q<y;q++){let H=A.getImageLevelInfo(z,q,0);D=H.origWidth,Q=H.origHeight;let k=new Uint8Array(A.getImageTranscodedSizeInBytes(z,q,0,b));if(!A.transcodeImage(k,z,q,0,b,0,-1,-1))throw m(),new Error("THREE.KTX2Loader: .transcodeImage failed.");O.push(k)}N.push({data:p(O),width:D,height:Q})}return m(),{width:E,height:x,hasAlpha:I,mipmaps:N,format:R,dfdTransferFn:S,dfdFlags:v}}d(a,"transcode");let l=[{if:"astcSupported",basisFormat:[s.UASTC_4x4],transcoderFormat:[i.ASTC_4x4,i.ASTC_4x4],engineFormat:[n.RGBA_ASTC_4x4_Format,n.RGBA_ASTC_4x4_Format],priorityETC1S:1/0,priorityUASTC:1,needsPowerOfTwo:!1},{if:"bptcSupported",basisFormat:[s.ETC1S,s.UASTC_4x4],transcoderFormat:[i.BC7_M5,i.BC7_M5],engineFormat:[n.RGBA_BPTC_Format,n.RGBA_BPTC_Format],priorityETC1S:3,priorityUASTC:2,needsPowerOfTwo:!1},{if:"dxtSupported",basisFormat:[s.ETC1S,s.UASTC_4x4],transcoderFormat:[i.BC1,i.BC3],engineFormat:[n.RGB_S3TC_DXT1_Format,n.RGBA_S3TC_DXT5_Format],priorityETC1S:4,priorityUASTC:5,needsPowerOfTwo:!1},{if:"etc2Supported",basisFormat:[s.ETC1S,s.UASTC_4x4],transcoderFormat:[i.ETC1,i.ETC2],engineFormat:[n.RGB_ETC2_Format,n.RGBA_ETC2_EAC_Format],priorityETC1S:1,priorityUASTC:3,needsPowerOfTwo:!1},{if:"etc1Supported",basisFormat:[s.ETC1S,s.UASTC_4x4],transcoderFormat:[i.ETC1],engineFormat:[n.RGB_ETC1_Format],priorityETC1S:2,priorityUASTC:4,needsPowerOfTwo:!1},{if:"pvrtcSupported",basisFormat:[s.ETC1S,s.UASTC_4x4],transcoderFormat:[i.PVRTC1_4_RGB,i.PVRTC1_4_RGBA],engineFormat:[n.RGB_PVRTC_4BPPV1_Format,n.RGBA_PVRTC_4BPPV1_Format],priorityETC1S:5,priorityUASTC:6,needsPowerOfTwo:!0}],c=l.sort(function(g,A){return g.priorityETC1S-A.priorityETC1S}),h=l.sort(function(g,A){return g.priorityUASTC-A.priorityUASTC});function u(g,A,m,_){let E,x,y=g===s.ETC1S?c:h;for(let w=0;w<y.length;w++){let I=y[w];if(o[I.if]&&I.basisFormat.includes(g)&&!(_&&I.transcoderFormat.length<2)&&!(I.needsPowerOfTwo&&!(f(A)&&f(m))))return E=I.transcoderFormat[_?1:0],x=I.engineFormat[_?1:0],{transcoderFormat:E,engineFormat:x}}return console.warn("THREE.KTX2Loader: No suitable compressed texture format found. Decoding to RGBA32."),E=i.RGBA32,x=n.RGBAFormat,{transcoderFormat:E,engineFormat:x}}d(u,"getTranscoderFormat");function f(g){return g<=2?!0:(g&g-1)===0&&g!==0}d(f,"isPowerOfTwo");function p(g){let A=0;for(let E of g)A+=E.byteLength;let m=new Uint8Array(A),_=0;for(let E of g)m.set(E,_),_+=E.byteLength;return m}d(p,"concat")};var Qm={[109]:lt,[97]:lt,[37]:lt,[43]:lt,[103]:xr,[83]:xr,[16]:xr,[22]:xr,[100]:yr,[76]:yr,[15]:yr,[9]:yr},Rd={[109]:Ut,[97]:Pt,[37]:$t,[43]:$t,[103]:Ut,[83]:Pt,[16]:$t,[22]:$t,[100]:Ut,[76]:Pt,[15]:$t,[9]:$t},zb={[43]:Se,[22]:Se,[15]:Se};async function Vb(o){let{vkFormat:e,pixelWidth:t,pixelHeight:n,pixelDepth:i}=o;if(Qm[e]===void 0)throw new Error("THREE.KTX2Loader: Unsupported vkFormat.");let s=o.levels[0],r,a;if(o.supercompressionScheme===0)r=s.levelData;else if(o.supercompressionScheme===2)Bd||(Bd=new Promise(async c=>{let h=new ac;await h.init(),c(h)})),r=(await Bd).decode(s.levelData,s.uncompressedByteLength);else throw new Error("THREE.KTX2Loader: Unsupported supercompressionScheme.");Rd[e]===Ut?a=new Float32Array(r.buffer,r.byteOffset,r.byteLength/Float32Array.BYTES_PER_ELEMENT):Rd[e]===Pt?a=new Uint16Array(r.buffer,r.byteOffset,r.byteLength/Uint16Array.BYTES_PER_ELEMENT):a=r;let l=i===0?new ur(a,t,n):new Do(a,t,n,i);return l.type=Rd[e],l.format=Qm[e],l.encoding=zb[e]||ft,l.needsUpdate=!0,Promise.resolve(l)}d(Vb,"createDataTexture");L();P();var Xm,Ym,jn=Symbol("retainerCount"),Ii=Symbol("recentlyUsed"),lc=Symbol("evict"),ra=Symbol("evictionThreshold"),Fd=Symbol("cache"),cc=class{static{d(this,"CacheEvictionPolicy")}constructor(e,t=5){this[Xm]=new Map,this[Ym]=[],this[Fd]=e,this[ra]=t}set evictionThreshold(e){this[ra]=e,this[lc]()}get evictionThreshold(){return this[ra]}get cache(){return this[Fd]}retainerCount(e){return this[jn].get(e)||0}reset(){this[jn].clear(),this[Ii]=[]}retain(e){this[jn].has(e)||this[jn].set(e,0),this[jn].set(e,this[jn].get(e)+1);let t=this[Ii].indexOf(e);t!==-1&&this[Ii].splice(t,1),this[Ii].unshift(e),this[lc]()}release(e){this[jn].has(e)&&this[jn].set(e,Math.max(this[jn].get(e)-1,0)),this[lc]()}[(Xm=jn,Ym=Ii,lc)](){if(!(this[Ii].length<this[ra]))for(let e=this[Ii].length-1;e>=this[ra];--e){let t=this[Ii][e];this[jn].get(t)===0&&(this[Fd].delete(t),this[Ii].splice(e,1))}}};L();P();var Hb=d(o=>{let e=[],t=new Set;for(let n of o){let i=n,s=0;for(;t.has(i);)i=n+"."+ ++s;t.add(i),e.push(i)}return e},"ensureUniqueNames"),Wb=d(o=>{let e=new Map;for(let t of o.mappings)for(let n of t.variants)e.set(n,{material:null,gltfMaterialIndex:t.material});return e},"mappingsArrayToTable"),oa=class{static{d(this,"GLTFMaterialsVariantsExtension")}constructor(e){this.parser=e,this.name="KHR_materials_variants"}afterRoot(e){let t=this.parser,n=t.json;if(n.extensions===void 0||n.extensions[this.name]===void 0)return null;let s=n.extensions[this.name].variants||[],r=Hb(s.map(a=>a.name));for(let a of e.scenes)a.traverse(l=>{let c=l;if(!c.isMesh)return;let h=t.associations.get(c);if(h==null||h.meshes==null||h.primitives==null)return;let g=n.meshes[h.meshes].primitives[h.primitives].extensions;!g||!g[this.name]||(c.userData.variantMaterials=Wb(g[this.name]))});return e.userData.variants=r,Promise.resolve()}};var ng,Jm;st.DEFAULT_ANISOTROPY=4;var qb=d((o,e,t=()=>{})=>{let n=d(i=>{let s=i.loaded/i.total;t(Math.max(0,Math.min(1,isFinite(s)?s:1)))},"onProgress");return new Promise((i,s)=>{e.load(o,i,n,s)})},"loadWithLoader"),Kb=d(o=>new Promise((e,t)=>{let n=document.createElement("script");document.body.appendChild(n),n.onload=e,n.onerror=t,n.async=!0,n.src=o}),"fetchScript"),Ci=new Map,Od=new Map,jm,Zm=new ic,eg,Nd=new ts,Ud,Qd,ns=Symbol("loader"),Si=Symbol("evictionPolicy"),tg=Symbol("GLTFInstance"),pt=class o extends Mt{static{d(this,"CachingGLTFLoader")}constructor(e){super(),this[Jm]=new sc().register(t=>new oa(t)),this[tg]=e,this[ns].setDRACOLoader(Zm),this[ns].setKTX2Loader(Nd)}static setDRACODecoderLocation(e){jm=e,Zm.setDecoderPath(e)}static getDRACODecoderLocation(){return jm}static setKTX2TranscoderLocation(e){eg=e,Nd.setTranscoderPath(e)}static getKTX2TranscoderLocation(){return eg}static setMeshoptDecoderLocation(e){Ud!==e&&(Ud=e,Qd=Kb(e).then(()=>MeshoptDecoder.ready).then(()=>MeshoptDecoder))}static getMeshoptDecoderLocation(){return Ud}static initializeKTX2Loader(e){Nd.detectSupport(e)}static get cache(){return Ci}static clearCache(){Ci.forEach((e,t)=>{this.delete(t)}),this[Si].reset()}static has(e){return Ci.has(e)}static async delete(e){if(!this.has(e))return;let t=Ci.get(e);Od.delete(e),Ci.delete(e),(await t).dispose()}static hasFinishedLoading(e){return!!Od.get(e)}get[(ng=Si,Jm=ns,Si)](){return this.constructor[Si]}async preload(e,t,n=()=>{}){if(this[ns].setWithCredentials(o.withCredentials),this.dispatchEvent({type:"preload",element:t,src:e}),!Ci.has(e)){Qd!=null&&this[ns].setMeshoptDecoder(await Qd);let i=qb(e,this[ns],a=>{n(a*.8)}),s=this[tg],r=i.then(a=>s.prepare(a)).then(a=>(n(.9),new s(a))).catch(a=>(console.error(a),new s));Ci.set(e,r)}await Ci.get(e),Od.set(e,!0),n&&n(1)}async load(e,t,n=()=>{}){await this.preload(e,t,n);let s=await(await Ci.get(e)).clone();return this[Si].retain(e),s.dispose=()=>{this[Si].release(e)},s}};pt[ng]=new cc(pt);L();P();L();P();var hc=class extends Ze{static{d(this,"CSS2DObject")}constructor(e=document.createElement("div")){super(),this.isCSS2DObject=!0,this.element=e,this.element.style.position="absolute",this.element.style.userSelect="none",this.element.setAttribute("draggable",!1),this.addEventListener("removed",function(){this.traverse(function(t){t.element instanceof Element&&t.element.parentNode!==null&&t.element.parentNode.removeChild(t.element)})})}copy(e,t){return super.copy(e,t),this.element=e.element.cloneNode(!0),this}},Lr=new B,ig=new Ie,sg=new Ie,rg=new B,og=new B,uc=class{static{d(this,"CSS2DRenderer")}constructor(e={}){let t=this,n,i,s,r,a={objects:new WeakMap},l=e.element!==void 0?e.element:document.createElement("div");l.style.overflow="hidden",this.domElement=l,this.getSize=function(){return{width:n,height:i}},this.render=function(p,g){p.matrixWorldAutoUpdate===!0&&p.updateMatrixWorld(),g.parent===null&&g.matrixWorldAutoUpdate===!0&&g.updateMatrixWorld(),ig.copy(g.matrixWorldInverse),sg.multiplyMatrices(g.projectionMatrix,ig),c(p,p,g),f(p)},this.setSize=function(p,g){n=p,i=g,s=n/2,r=i/2,l.style.width=p+"px",l.style.height=g+"px"};function c(p,g,A){if(p.isCSS2DObject){Lr.setFromMatrixPosition(p.matrixWorld),Lr.applyMatrix4(sg);let m=p.visible===!0&&Lr.z>=-1&&Lr.z<=1&&p.layers.test(A.layers)===!0;if(p.element.style.display=m===!0?"":"none",m===!0){p.onBeforeRender(t,g,A);let E=p.element;E.style.transform="translate(-50%,-50%) translate("+(Lr.x*s+s)+"px,"+(-Lr.y*r+r)+"px)",E.parentNode!==l&&l.appendChild(E),p.onAfterRender(t,g,A)}let _={distanceToCameraSquared:h(A,p)};a.objects.set(p,_)}for(let m=0,_=p.children.length;m<_;m++)c(p.children[m],g,A)}d(c,"renderObject");function h(p,g){return rg.setFromMatrixPosition(p.matrixWorld),og.setFromMatrixPosition(g.matrixWorld),rg.distanceToSquared(og)}d(h,"getDistanceToSquared");function u(p){let g=[];return p.traverse(function(A){A.isCSS2DObject&&g.push(A)}),g}d(u,"filterAndFlatten");function f(p){let g=u(p).sort(function(m,_){if(m.renderOrder!==_.renderOrder)return _.renderOrder-m.renderOrder;let E=a.objects.get(m).distanceToCameraSquared,x=a.objects.get(_).distanceToCameraSquared;return E-x}),A=g.length;for(let m=0,_=g.length;m<_;m++)g[m].element.style.zIndex=A-m}d(f,"zOrder")}};L();P();function aa(o,e,t){let n=t,i=new B;return o.updateWorldMatrix(!0,!0),o.traverseVisible(s=>{let{geometry:r}=s;if(r!==void 0){let{position:a}=r.attributes;if(a!==void 0)for(let l=0,c=a.count;l<c;l++)s.isMesh?s.getVertexPosition(l,i):i.fromBufferAttribute(a,l),s.isSkinnedMesh||i.applyMatrix4(s.matrixWorld),n=e(n,i)}}),n}d(aa,"reduceVertices");L();P();L();P();var Pr=class{static{d(this,"GLTFExporter")}constructor(){this.pluginCallbacks=[],this.register(function(e){return new zd(e)}),this.register(function(e){return new Vd(e)}),this.register(function(e){return new qd(e)}),this.register(function(e){return new Kd(e)}),this.register(function(e){return new $d(e)}),this.register(function(e){return new Xd(e)}),this.register(function(e){return new Hd(e)}),this.register(function(e){return new Wd(e)})}register(e){return this.pluginCallbacks.indexOf(e)===-1&&this.pluginCallbacks.push(e),this}unregister(e){return this.pluginCallbacks.indexOf(e)!==-1&&this.pluginCallbacks.splice(this.pluginCallbacks.indexOf(e),1),this}parse(e,t,n,i){let s=new Gd,r=[];for(let a=0,l=this.pluginCallbacks.length;a<l;a++)r.push(this.pluginCallbacks[a](s));s.setPlugins(r),s.write(e,t,i).catch(n)}parseAsync(e,t){let n=this;return new Promise(function(i,s){n.parse(e,i,s,t)})}},et={POINTS:0,LINES:1,LINE_LOOP:2,LINE_STRIP:3,TRIANGLES:4,TRIANGLE_STRIP:5,TRIANGLE_FAN:6,UNSIGNED_BYTE:5121,UNSIGNED_SHORT:5123,FLOAT:5126,UNSIGNED_INT:5125,ARRAY_BUFFER:34962,ELEMENT_ARRAY_BUFFER:34963,NEAREST:9728,LINEAR:9729,NEAREST_MIPMAP_NEAREST:9984,LINEAR_MIPMAP_NEAREST:9985,NEAREST_MIPMAP_LINEAR:9986,LINEAR_MIPMAP_LINEAR:9987,CLAMP_TO_EDGE:33071,MIRRORED_REPEAT:33648,REPEAT:10497},bn={};bn[ct]=et.NEAREST;bn[rr]=et.NEAREST_MIPMAP_NEAREST;bn[_s]=et.NEAREST_MIPMAP_LINEAR;bn[Je]=et.LINEAR;bn[Wo]=et.LINEAR_MIPMAP_NEAREST;bn[wn]=et.LINEAR_MIPMAP_LINEAR;bn[Lt]=et.CLAMP_TO_EDGE;bn[Pn]=et.REPEAT;bn[vs]=et.MIRRORED_REPEAT;var ag={scale:"scale",position:"translation",quaternion:"rotation",morphTargetInfluences:"weights"},$b=new Me,lg=12,Xb=1179937895,Yb=2,cg=8,Jb=1313821514,jb=5130562;function la(o,e){return o.length===e.length&&o.every(function(t,n){return t===e[n]})}d(la,"equalArray");function Zb(o){return new TextEncoder().encode(o).buffer}d(Zb,"stringToArrayBuffer");function eI(o){return la(o.elements,[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1])}d(eI,"isIdentityMatrix");function tI(o,e,t){let n={min:new Array(o.itemSize).fill(Number.POSITIVE_INFINITY),max:new Array(o.itemSize).fill(Number.NEGATIVE_INFINITY)};for(let i=e;i<e+t;i++)for(let s=0;s<o.itemSize;s++){let r;o.itemSize>4?r=o.array[i*o.itemSize+s]:(s===0?r=o.getX(i):s===1?r=o.getY(i):s===2?r=o.getZ(i):s===3&&(r=o.getW(i)),o.normalized===!0&&(r=vr.normalize(r,o.array))),n.min[s]=Math.min(n.min[s],r),n.max[s]=Math.max(n.max[s],r)}return n}d(tI,"getMinMax");function dg(o){return Math.ceil(o/4)*4}d(dg,"getPaddedBufferSize");function kd(o,e=0){let t=dg(o.byteLength);if(t!==o.byteLength){let n=new Uint8Array(t);if(n.set(new Uint8Array(o)),e!==0)for(let i=o.byteLength;i<t;i++)n[i]=e;return n.buffer}return o}d(kd,"getPaddedArrayBuffer");function hg(){return typeof document>"u"&&typeof OffscreenCanvas<"u"?new OffscreenCanvas(1,1):document.createElement("canvas")}d(hg,"getCanvas");function ug(o,e){if(o.toBlob!==void 0)return new Promise(n=>o.toBlob(n,e));let t;return e==="image/jpeg"?t=.92:e==="image/webp"&&(t=.8),o.convertToBlob({type:e,quality:t})}d(ug,"getToBlobPromise");var Gd=class{static{d(this,"GLTFWriter")}constructor(){this.plugins=[],this.options={},this.pending=[],this.buffers=[],this.byteOffset=0,this.buffers=[],this.nodeMap=new Map,this.skins=[],this.extensionsUsed={},this.uids=new Map,this.uid=0,this.json={asset:{version:"2.0",generator:"THREE.GLTFExporter"}},this.cache={meshes:new Map,attributes:new Map,attributesNormalized:new Map,materials:new Map,textures:new Map,images:new Map}}setPlugins(e){this.plugins=e}async write(e,t,n={}){this.options=Object.assign({binary:!1,trs:!1,onlyVisible:!0,maxTextureSize:1/0,animations:[],includeCustomExtensions:!1},n),this.options.animations.length>0&&(this.options.trs=!0),this.processInput(e),await Promise.all(this.pending);let i=this,s=i.buffers,r=i.json;n=i.options;let a=i.extensionsUsed,l=new Blob(s,{type:"application/octet-stream"}),c=Object.keys(a);if(c.length>0&&(r.extensionsUsed=c),r.buffers&&r.buffers.length>0&&(r.buffers[0].byteLength=l.size),n.binary===!0){let h=new FileReader;h.readAsArrayBuffer(l),h.onloadend=function(){let u=kd(h.result),f=new DataView(new ArrayBuffer(cg));f.setUint32(0,u.byteLength,!0),f.setUint32(4,jb,!0);let p=kd(Zb(JSON.stringify(r)),32),g=new DataView(new ArrayBuffer(cg));g.setUint32(0,p.byteLength,!0),g.setUint32(4,Jb,!0);let A=new ArrayBuffer(lg),m=new DataView(A);m.setUint32(0,Xb,!0),m.setUint32(4,Yb,!0);let _=lg+g.byteLength+p.byteLength+f.byteLength+u.byteLength;m.setUint32(8,_,!0);let E=new Blob([A,g,p,f,u],{type:"application/octet-stream"}),x=new FileReader;x.readAsArrayBuffer(E),x.onloadend=function(){t(x.result)}}}else if(r.buffers&&r.buffers.length>0){let h=new FileReader;h.readAsDataURL(l),h.onloadend=function(){let u=h.result;r.buffers[0].uri=u,t(r)}}else t(r)}serializeUserData(e,t){if(Object.keys(e.userData).length===0)return;let n=this.options,i=this.extensionsUsed;try{let s=JSON.parse(JSON.stringify(e.userData));if(n.includeCustomExtensions&&s.gltfExtensions){t.extensions===void 0&&(t.extensions={});for(let r in s.gltfExtensions)t.extensions[r]=s.gltfExtensions[r],i[r]=!0;delete s.gltfExtensions}Object.keys(s).length>0&&(t.extras=s)}catch(s){console.warn("THREE.GLTFExporter: userData of '"+e.name+"' won't be serialized because of JSON.stringify error - "+s.message)}}getUID(e,t=!1){if(this.uids.has(e)===!1){let i=new Map;i.set(!0,this.uid++),i.set(!1,this.uid++),this.uids.set(e,i)}return this.uids.get(e).get(t)}isNormalizedNormalAttribute(e){if(this.cache.attributesNormalized.has(e))return!1;let n=new B;for(let i=0,s=e.count;i<s;i++)if(Math.abs(n.fromBufferAttribute(e,i).length()-1)>5e-4)return!1;return!0}createNormalizedNormalAttribute(e){let t=this.cache;if(t.attributesNormalized.has(e))return t.attributesNormalized.get(e);let n=e.clone(),i=new B;for(let s=0,r=n.count;s<r;s++)i.fromBufferAttribute(n,s),i.x===0&&i.y===0&&i.z===0?i.setX(1):i.normalize(),n.setXYZ(s,i.x,i.y,i.z);return t.attributesNormalized.set(e,n),n}applyTextureTransform(e,t){let n=!1,i={};(t.offset.x!==0||t.offset.y!==0)&&(i.offset=t.offset.toArray(),n=!0),t.rotation!==0&&(i.rotation=t.rotation,n=!0),(t.repeat.x!==1||t.repeat.y!==1)&&(i.scale=t.repeat.toArray(),n=!0),n&&(e.extensions=e.extensions||{},e.extensions.KHR_texture_transform=i,this.extensionsUsed.KHR_texture_transform=!0)}buildMetalRoughTexture(e,t){if(e===t)return e;function n(p){return p.encoding===Se?d(function(A){return A<.04045?A*.0773993808:Math.pow(A*.9478672986+.0521327014,2.4)},"SRGBToLinear"):d(function(A){return A},"LinearToLinear")}d(n,"getEncodingConversion"),console.warn("THREE.GLTFExporter: Merged metalnessMap and roughnessMap textures.");let i=e?e.image:null,s=t?t.image:null,r=Math.max(i?i.width:0,s?s.width:0),a=Math.max(i?i.height:0,s?s.height:0),l=hg();l.width=r,l.height=a;let c=l.getContext("2d");c.fillStyle="#00ffff",c.fillRect(0,0,r,a);let h=c.getImageData(0,0,r,a);if(i){c.drawImage(i,0,0,r,a);let p=n(e),g=c.getImageData(0,0,r,a).data;for(let A=2;A<g.length;A+=4)h.data[A]=p(g[A]/256)*256}if(s){c.drawImage(s,0,0,r,a);let p=n(t),g=c.getImageData(0,0,r,a).data;for(let A=1;A<g.length;A+=4)h.data[A]=p(g[A]/256)*256}c.putImageData(h,0,0);let f=(e||t).clone();return f.source=new ar(l),f.encoding=ft,f}processBuffer(e){let t=this.json,n=this.buffers;return t.buffers||(t.buffers=[{byteLength:0}]),n.push(e),0}processBufferView(e,t,n,i,s){let r=this.json;r.bufferViews||(r.bufferViews=[]);let a;t===et.UNSIGNED_BYTE?a=1:t===et.UNSIGNED_SHORT?a=2:a=4;let l=dg(i*e.itemSize*a),c=new DataView(new ArrayBuffer(l)),h=0;for(let p=n;p<n+i;p++)for(let g=0;g<e.itemSize;g++){let A;e.itemSize>4?A=e.array[p*e.itemSize+g]:(g===0?A=e.getX(p):g===1?A=e.getY(p):g===2?A=e.getZ(p):g===3&&(A=e.getW(p)),e.normalized===!0&&(A=vr.normalize(A,e.array))),t===et.FLOAT?c.setFloat32(h,A,!0):t===et.UNSIGNED_INT?c.setUint32(h,A,!0):t===et.UNSIGNED_SHORT?c.setUint16(h,A,!0):t===et.UNSIGNED_BYTE&&c.setUint8(h,A),h+=a}let u={buffer:this.processBuffer(c.buffer),byteOffset:this.byteOffset,byteLength:l};return s!==void 0&&(u.target=s),s===et.ARRAY_BUFFER&&(u.byteStride=e.itemSize*a),this.byteOffset+=l,r.bufferViews.push(u),{id:r.bufferViews.length-1,byteLength:0}}processBufferViewImage(e){let t=this,n=t.json;return n.bufferViews||(n.bufferViews=[]),new Promise(function(i){let s=new FileReader;s.readAsArrayBuffer(e),s.onloadend=function(){let r=kd(s.result),a={buffer:t.processBuffer(r),byteOffset:t.byteOffset,byteLength:r.byteLength};t.byteOffset+=r.byteLength,i(n.bufferViews.push(a)-1)}})}processAccessor(e,t,n,i){let s=this.json,r={1:"SCALAR",2:"VEC2",3:"VEC3",4:"VEC4",16:"MAT4"},a;if(e.array.constructor===Float32Array)a=et.FLOAT;else if(e.array.constructor===Uint32Array)a=et.UNSIGNED_INT;else if(e.array.constructor===Uint16Array)a=et.UNSIGNED_SHORT;else if(e.array.constructor===Uint8Array)a=et.UNSIGNED_BYTE;else throw new Error("THREE.GLTFExporter: Unsupported bufferAttribute component type.");if(n===void 0&&(n=0),i===void 0&&(i=e.count),i===0)return null;let l=tI(e,n,i),c;t!==void 0&&(c=e===t.index?et.ELEMENT_ARRAY_BUFFER:et.ARRAY_BUFFER);let h=this.processBufferView(e,a,n,i,c),u={bufferView:h.id,byteOffset:h.byteOffset,componentType:a,count:i,max:l.max,min:l.min,type:r[e.itemSize]};return e.normalized===!0&&(u.normalized=!0),s.accessors||(s.accessors=[]),s.accessors.push(u)-1}processImage(e,t,n,i="image/png"){if(e!==null){let s=this,r=s.cache,a=s.json,l=s.options,c=s.pending;r.images.has(e)||r.images.set(e,{});let h=r.images.get(e),u=i+":flipY/"+n.toString();if(h[u]!==void 0)return h[u];a.images||(a.images=[]);let f={mimeType:i},p=hg();p.width=Math.min(e.width,l.maxTextureSize),p.height=Math.min(e.height,l.maxTextureSize);let g=p.getContext("2d");if(n===!0&&(g.translate(0,p.height),g.scale(1,-1)),e.data!==void 0){t!==lt&&console.error("GLTFExporter: Only RGBAFormat is supported."),(e.width>l.maxTextureSize||e.height>l.maxTextureSize)&&console.warn("GLTFExporter: Image size is bigger than maxTextureSize",e);let m=new Uint8ClampedArray(e.height*e.width*4);for(let _=0;_<m.length;_+=4)m[_+0]=e.data[_+0],m[_+1]=e.data[_+1],m[_+2]=e.data[_+2],m[_+3]=e.data[_+3];g.putImageData(new ImageData(m,e.width,e.height),0,0)}else g.drawImage(e,0,0,p.width,p.height);l.binary===!0?c.push(ug(p,i).then(m=>s.processBufferViewImage(m)).then(m=>{f.bufferView=m})):p.toDataURL!==void 0?f.uri=p.toDataURL(i):c.push(ug(p,i).then(m=>new FileReader().readAsDataURL(m)).then(m=>{f.uri=m}));let A=a.images.push(f)-1;return h[u]=A,A}else throw new Error("THREE.GLTFExporter: No valid image data found. Unable to process texture.")}processSampler(e){let t=this.json;t.samplers||(t.samplers=[]);let n={magFilter:bn[e.magFilter],minFilter:bn[e.minFilter],wrapS:bn[e.wrapS],wrapT:bn[e.wrapT]};return t.samplers.push(n)-1}processTexture(e){let t=this.cache,n=this.json;if(t.textures.has(e))return t.textures.get(e);n.textures||(n.textures=[]);let i=e.userData.mimeType;i==="image/webp"&&(i="image/png");let s={sampler:this.processSampler(e),source:this.processImage(e.image,e.format,e.flipY,i)};e.name&&(s.name=e.name),this._invokeAll(function(a){a.writeTexture&&a.writeTexture(e,s)});let r=n.textures.push(s)-1;return t.textures.set(e,r),r}processMaterial(e){let t=this.cache,n=this.json;if(t.materials.has(e))return t.materials.get(e);if(e.isShaderMaterial)return console.warn("GLTFExporter: THREE.ShaderMaterial not supported."),null;n.materials||(n.materials=[]);let i={pbrMetallicRoughness:{}};e.isMeshStandardMaterial!==!0&&e.isMeshBasicMaterial!==!0&&console.warn("GLTFExporter: Use MeshStandardMaterial or MeshBasicMaterial for best results.");let s=e.color.toArray().concat([e.opacity]);if(la(s,[1,1,1,1])||(i.pbrMetallicRoughness.baseColorFactor=s),e.isMeshStandardMaterial?(i.pbrMetallicRoughness.metallicFactor=e.metalness,i.pbrMetallicRoughness.roughnessFactor=e.roughness):(i.pbrMetallicRoughness.metallicFactor=.5,i.pbrMetallicRoughness.roughnessFactor=.5),e.metalnessMap||e.roughnessMap){let a=this.buildMetalRoughTexture(e.metalnessMap,e.roughnessMap),l={index:this.processTexture(a)};this.applyTextureTransform(l,a),i.pbrMetallicRoughness.metallicRoughnessTexture=l}if(e.map){let a={index:this.processTexture(e.map)};this.applyTextureTransform(a,e.map),i.pbrMetallicRoughness.baseColorTexture=a}if(e.emissive){let a=e.emissive.clone().multiplyScalar(e.emissiveIntensity),l=Math.max(a.r,a.g,a.b);if(l>1&&(a.multiplyScalar(1/l),console.warn("THREE.GLTFExporter: Some emissive components exceed 1; emissive has been limited")),l>0&&(i.emissiveFactor=a.toArray()),e.emissiveMap){let c={index:this.processTexture(e.emissiveMap)};this.applyTextureTransform(c,e.emissiveMap),i.emissiveTexture=c}}if(e.normalMap){let a={index:this.processTexture(e.normalMap)};e.normalScale&&e.normalScale.x!==1&&(a.scale=e.normalScale.x),this.applyTextureTransform(a,e.normalMap),i.normalTexture=a}if(e.aoMap){let a={index:this.processTexture(e.aoMap),texCoord:1};e.aoMapIntensity!==1&&(a.strength=e.aoMapIntensity),this.applyTextureTransform(a,e.aoMap),i.occlusionTexture=a}e.transparent?i.alphaMode="BLEND":e.alphaTest>0&&(i.alphaMode="MASK",i.alphaCutoff=e.alphaTest),e.side===Et&&(i.doubleSided=!0),e.name!==""&&(i.name=e.name),this.serializeUserData(e,i),this._invokeAll(function(a){a.writeMaterial&&a.writeMaterial(e,i)});let r=n.materials.push(i)-1;return t.materials.set(e,r),r}processMesh(e){let t=this.cache,n=this.json,i=[e.geometry.uuid];if(Array.isArray(e.material))for(let x=0,y=e.material.length;x<y;x++)i.push(e.material[x].uuid);else i.push(e.material.uuid);let s=i.join(":");if(t.meshes.has(s))return t.meshes.get(s);let r=e.geometry,a;e.isLineSegments?a=et.LINES:e.isLineLoop?a=et.LINE_LOOP:e.isLine?a=et.LINE_STRIP:e.isPoints?a=et.POINTS:a=e.material.wireframe?et.LINES:et.TRIANGLES;let l={},c={},h=[],u=[],f={uv:"TEXCOORD_0",uv2:"TEXCOORD_1",color:"COLOR_0",skinWeight:"WEIGHTS_0",skinIndex:"JOINTS_0"},p=r.getAttribute("normal");p!==void 0&&!this.isNormalizedNormalAttribute(p)&&(console.warn("THREE.GLTFExporter: Creating normalized normal attribute from the non-normalized one."),r.setAttribute("normal",this.createNormalizedNormalAttribute(p)));let g=null;for(let x in r.attributes){if(x.slice(0,5)==="morph")continue;let y=r.attributes[x];if(x=f[x]||x.toUpperCase(),/^(POSITION|NORMAL|TANGENT|TEXCOORD_\d+|COLOR_\d+|JOINTS_\d+|WEIGHTS_\d+)$/.test(x)||(x="_"+x),t.attributes.has(this.getUID(y))){c[x]=t.attributes.get(this.getUID(y));continue}g=null;let I=y.array;x==="JOINTS_0"&&!(I instanceof Uint16Array)&&!(I instanceof Uint8Array)&&(console.warn('GLTFExporter: Attribute "skinIndex" converted to type UNSIGNED_SHORT.'),g=new je(new Uint16Array(I),y.itemSize,y.normalized));let S=this.processAccessor(g||y,r);S!==null&&(c[x]=S,t.attributes.set(this.getUID(y),S))}if(p!==void 0&&r.setAttribute("normal",p),Object.keys(c).length===0)return null;if(e.morphTargetInfluences!==void 0&&e.morphTargetInfluences.length>0){let x=[],y=[],w={};if(e.morphTargetDictionary!==void 0)for(let I in e.morphTargetDictionary)w[e.morphTargetDictionary[I]]=I;for(let I=0;I<e.morphTargetInfluences.length;++I){let S={},v=!1;for(let b in r.morphAttributes){if(b!=="position"&&b!=="normal"){v||(console.warn("GLTFExporter: Only POSITION and NORMAL morph are supported."),v=!0);continue}let R=r.morphAttributes[b][I],N=b.toUpperCase(),z=r.attributes[b];if(t.attributes.has(this.getUID(R,!0))){S[N]=t.attributes.get(this.getUID(R,!0));continue}let O=R.clone();if(!r.morphTargetsRelative)for(let D=0,Q=R.count;D<Q;D++)for(let q=0;q<R.itemSize;q++)q===0&&O.setX(D,R.getX(D)-z.getX(D)),q===1&&O.setY(D,R.getY(D)-z.getY(D)),q===2&&O.setZ(D,R.getZ(D)-z.getZ(D)),q===3&&O.setW(D,R.getW(D)-z.getW(D));S[N]=this.processAccessor(O,r),t.attributes.set(this.getUID(z,!0),S[N])}u.push(S),x.push(e.morphTargetInfluences[I]),e.morphTargetDictionary!==void 0&&y.push(w[I])}l.weights=x,y.length>0&&(l.extras={},l.extras.targetNames=y)}let A=Array.isArray(e.material);if(A&&r.groups.length===0)return null;let m=A?e.material:[e.material],_=A?r.groups:[{materialIndex:0,start:void 0,count:void 0}];for(let x=0,y=_.length;x<y;x++){let w={mode:a,attributes:c};if(this.serializeUserData(r,w),u.length>0&&(w.targets=u),r.index!==null){let S=this.getUID(r.index);(_[x].start!==void 0||_[x].count!==void 0)&&(S+=":"+_[x].start+":"+_[x].count),t.attributes.has(S)?w.indices=t.attributes.get(S):(w.indices=this.processAccessor(r.index,r,_[x].start,_[x].count),t.attributes.set(S,w.indices)),w.indices===null&&delete w.indices}let I=this.processMaterial(m[_[x].materialIndex]);I!==null&&(w.material=I),h.push(w)}l.primitives=h,n.meshes||(n.meshes=[]),this._invokeAll(function(x){x.writeMesh&&x.writeMesh(e,l)});let E=n.meshes.push(l)-1;return t.meshes.set(s,E),E}processCamera(e){let t=this.json;t.cameras||(t.cameras=[]);let n=e.isOrthographicCamera,i={type:n?"orthographic":"perspective"};return n?i.orthographic={xmag:e.right*2,ymag:e.top*2,zfar:e.far<=0?.001:e.far,znear:e.near<0?0:e.near}:i.perspective={aspectRatio:e.aspect,yfov:vr.degToRad(e.fov),zfar:e.far<=0?.001:e.far,znear:e.near<0?0:e.near},e.name!==""&&(i.name=e.type),t.cameras.push(i)-1}processAnimation(e,t){let n=this.json,i=this.nodeMap;n.animations||(n.animations=[]),e=Pr.Utils.mergeMorphTargetTracks(e.clone(),t);let s=e.tracks,r=[],a=[];for(let l=0;l<s.length;++l){let c=s[l],h=We.parseTrackName(c.name),u=We.findNode(t,h.nodeName),f=ag[h.propertyName];if(h.objectName==="bones"&&(u.isSkinnedMesh===!0?u=u.skeleton.getBoneByName(h.objectIndex):u=void 0),!u||!f)return console.warn('THREE.GLTFExporter: Could not export animation track "%s".',c.name),null;let p=1,g=c.values.length/c.times.length;f===ag.morphTargetInfluences&&(g/=u.morphTargetInfluences.length);let A;c.createInterpolant.isInterpolantFactoryMethodGLTFCubicSpline===!0?(A="CUBICSPLINE",g/=3):c.getInterpolation()===zi?A="STEP":A="LINEAR",a.push({input:this.processAccessor(new je(c.times,p)),output:this.processAccessor(new je(c.values,g)),interpolation:A}),r.push({sampler:a.length-1,target:{node:i.get(u),path:f}})}return n.animations.push({name:e.name||"clip_"+n.animations.length,samplers:a,channels:r}),n.animations.length-1}processSkin(e){let t=this.json,n=this.nodeMap,i=t.nodes[n.get(e)],s=e.skeleton;if(s===void 0)return null;let r=e.skeleton.bones[0];if(r===void 0)return null;let a=[],l=new Float32Array(s.bones.length*16),c=new Ie;for(let u=0;u<s.bones.length;++u)a.push(n.get(s.bones[u])),c.copy(s.boneInverses[u]),c.multiply(e.bindMatrix).toArray(l,u*16);return t.skins===void 0&&(t.skins=[]),t.skins.push({inverseBindMatrices:this.processAccessor(new je(l,16)),joints:a,skeleton:n.get(r)}),i.skin=t.skins.length-1}processNode(e){let t=this.json,n=this.options,i=this.nodeMap;t.nodes||(t.nodes=[]);let s={};if(n.trs){let a=e.quaternion.toArray(),l=e.position.toArray(),c=e.scale.toArray();la(a,[0,0,0,1])||(s.rotation=a),la(l,[0,0,0])||(s.translation=l),la(c,[1,1,1])||(s.scale=c)}else e.matrixAutoUpdate&&e.updateMatrix(),eI(e.matrix)===!1&&(s.matrix=e.matrix.elements);if(e.name!==""&&(s.name=String(e.name)),this.serializeUserData(e,s),e.isMesh||e.isLine||e.isPoints){let a=this.processMesh(e);a!==null&&(s.mesh=a)}else e.isCamera&&(s.camera=this.processCamera(e));if(e.isSkinnedMesh&&this.skins.push(e),e.children.length>0){let a=[];for(let l=0,c=e.children.length;l<c;l++){let h=e.children[l];if(h.visible||n.onlyVisible===!1){let u=this.processNode(h);u!==null&&a.push(u)}}a.length>0&&(s.children=a)}this._invokeAll(function(a){a.writeNode&&a.writeNode(e,s)});let r=t.nodes.push(s)-1;return i.set(e,r),r}processScene(e){let t=this.json,n=this.options;t.scenes||(t.scenes=[],t.scene=0);let i={};e.name!==""&&(i.name=e.name),t.scenes.push(i);let s=[];for(let r=0,a=e.children.length;r<a;r++){let l=e.children[r];if(l.visible||n.onlyVisible===!1){let c=this.processNode(l);c!==null&&s.push(c)}}s.length>0&&(i.nodes=s),this.serializeUserData(e,i)}processObjects(e){let t=new Gt;t.name="AuxScene";for(let n=0;n<e.length;n++)t.children.push(e[n]);this.processScene(t)}processInput(e){let t=this.options;e=e instanceof Array?e:[e],this._invokeAll(function(i){i.beforeParse&&i.beforeParse(e)});let n=[];for(let i=0;i<e.length;i++)e[i]instanceof Gt?this.processScene(e[i]):n.push(e[i]);n.length>0&&this.processObjects(n);for(let i=0;i<this.skins.length;++i)this.processSkin(this.skins[i]);for(let i=0;i<t.animations.length;++i)this.processAnimation(t.animations[i],e[0]);this._invokeAll(function(i){i.afterParse&&i.afterParse(e)})}_invokeAll(e){for(let t=0,n=this.plugins.length;t<n;t++)e(this.plugins[t])}},zd=class{static{d(this,"GLTFLightExtension")}constructor(e){this.writer=e,this.name="KHR_lights_punctual"}writeNode(e,t){if(!e.isLight)return;if(!e.isDirectionalLight&&!e.isPointLight&&!e.isSpotLight){console.warn("THREE.GLTFExporter: Only directional, point, and spot lights are supported.",e);return}let n=this.writer,i=n.json,s=n.extensionsUsed,r={};e.name&&(r.name=e.name),r.color=e.color.toArray(),r.intensity=e.intensity,e.isDirectionalLight?r.type="directional":e.isPointLight?(r.type="point",e.distance>0&&(r.range=e.distance)):e.isSpotLight&&(r.type="spot",e.distance>0&&(r.range=e.distance),r.spot={},r.spot.innerConeAngle=(e.penumbra-1)*e.angle*-1,r.spot.outerConeAngle=e.angle),e.decay!==void 0&&e.decay!==2&&console.warn("THREE.GLTFExporter: Light decay may be lost. glTF is physically-based, and expects light.decay=2."),e.target&&(e.target.parent!==e||e.target.position.x!==0||e.target.position.y!==0||e.target.position.z!==-1)&&console.warn("THREE.GLTFExporter: Light direction may be lost. For best results, make light.target a child of the light with position 0,0,-1."),s[this.name]||(i.extensions=i.extensions||{},i.extensions[this.name]={lights:[]},s[this.name]=!0);let a=i.extensions[this.name].lights;a.push(r),t.extensions=t.extensions||{},t.extensions[this.name]={light:a.length-1}}},Vd=class{static{d(this,"GLTFMaterialsUnlitExtension")}constructor(e){this.writer=e,this.name="KHR_materials_unlit"}writeMaterial(e,t){if(!e.isMeshBasicMaterial)return;let i=this.writer.extensionsUsed;t.extensions=t.extensions||{},t.extensions[this.name]={},i[this.name]=!0,t.pbrMetallicRoughness.metallicFactor=0,t.pbrMetallicRoughness.roughnessFactor=.9}},Hd=class{static{d(this,"GLTFMaterialsClearcoatExtension")}constructor(e){this.writer=e,this.name="KHR_materials_clearcoat"}writeMaterial(e,t){if(!e.isMeshPhysicalMaterial||e.clearcoat===0)return;let n=this.writer,i=n.extensionsUsed,s={};if(s.clearcoatFactor=e.clearcoat,e.clearcoatMap){let r={index:n.processTexture(e.clearcoatMap)};n.applyTextureTransform(r,e.clearcoatMap),s.clearcoatTexture=r}if(s.clearcoatRoughnessFactor=e.clearcoatRoughness,e.clearcoatRoughnessMap){let r={index:n.processTexture(e.clearcoatRoughnessMap)};n.applyTextureTransform(r,e.clearcoatRoughnessMap),s.clearcoatRoughnessTexture=r}if(e.clearcoatNormalMap){let r={index:n.processTexture(e.clearcoatNormalMap)};n.applyTextureTransform(r,e.clearcoatNormalMap),s.clearcoatNormalTexture=r}t.extensions=t.extensions||{},t.extensions[this.name]=s,i[this.name]=!0}},Wd=class{static{d(this,"GLTFMaterialsIridescenceExtension")}constructor(e){this.writer=e,this.name="KHR_materials_iridescence"}writeMaterial(e,t){if(!e.isMeshPhysicalMaterial||e.iridescence===0)return;let n=this.writer,i=n.extensionsUsed,s={};if(s.iridescenceFactor=e.iridescence,e.iridescenceMap){let r={index:n.processTexture(e.iridescenceMap)};n.applyTextureTransform(r,e.iridescenceMap),s.iridescenceTexture=r}if(s.iridescenceIor=e.iridescenceIOR,s.iridescenceThicknessMinimum=e.iridescenceThicknessRange[0],s.iridescenceThicknessMaximum=e.iridescenceThicknessRange[1],e.iridescenceThicknessMap){let r={index:n.processTexture(e.iridescenceThicknessMap)};n.applyTextureTransform(r,e.iridescenceThicknessMap),s.iridescenceThicknessTexture=r}t.extensions=t.extensions||{},t.extensions[this.name]=s,i[this.name]=!0}},qd=class{static{d(this,"GLTFMaterialsTransmissionExtension")}constructor(e){this.writer=e,this.name="KHR_materials_transmission"}writeMaterial(e,t){if(!e.isMeshPhysicalMaterial||e.transmission===0)return;let n=this.writer,i=n.extensionsUsed,s={};if(s.transmissionFactor=e.transmission,e.transmissionMap){let r={index:n.processTexture(e.transmissionMap)};n.applyTextureTransform(r,e.transmissionMap),s.transmissionTexture=r}t.extensions=t.extensions||{},t.extensions[this.name]=s,i[this.name]=!0}},Kd=class{static{d(this,"GLTFMaterialsVolumeExtension")}constructor(e){this.writer=e,this.name="KHR_materials_volume"}writeMaterial(e,t){if(!e.isMeshPhysicalMaterial||e.transmission===0)return;let n=this.writer,i=n.extensionsUsed,s={};if(s.thicknessFactor=e.thickness,e.thicknessMap){let r={index:n.processTexture(e.thicknessMap)};n.applyTextureTransform(r,e.thicknessMap),s.thicknessTexture=r}s.attenuationDistance=e.attenuationDistance,s.attenuationColor=e.attenuationColor.toArray(),t.extensions=t.extensions||{},t.extensions[this.name]=s,i[this.name]=!0}},$d=class{static{d(this,"GLTFMaterialsIorExtension")}constructor(e){this.writer=e,this.name="KHR_materials_ior"}writeMaterial(e,t){if(!e.isMeshPhysicalMaterial||e.ior===1.5)return;let i=this.writer.extensionsUsed,s={};s.ior=e.ior,t.extensions=t.extensions||{},t.extensions[this.name]=s,i[this.name]=!0}},Xd=class{static{d(this,"GLTFMaterialsSpecularExtension")}constructor(e){this.writer=e,this.name="KHR_materials_specular"}writeMaterial(e,t){if(!e.isMeshPhysicalMaterial||e.specularIntensity===1&&e.specularColor.equals($b)&&!e.specularIntensityMap&&!e.specularColorTexture)return;let n=this.writer,i=n.extensionsUsed,s={};if(e.specularIntensityMap){let r={index:n.processTexture(e.specularIntensityMap)};n.applyTextureTransform(r,e.specularIntensityMap),s.specularTexture=r}if(e.specularColorMap){let r={index:n.processTexture(e.specularColorMap)};n.applyTextureTransform(r,e.specularColorMap),s.specularColorTexture=r}s.specularFactor=e.specularIntensity,s.specularColorFactor=e.specularColor.toArray(),t.extensions=t.extensions||{},t.extensions[this.name]=s,i[this.name]=!0}};Pr.Utils={insertKeyframe:d(function(o,e){let n=o.getValueSize(),i=new o.TimeBufferType(o.times.length+1),s=new o.ValueBufferType(o.values.length+n),r=o.createInterpolant(new o.ValueBufferType(n)),a;if(o.times.length===0){i[0]=e;for(let l=0;l<n;l++)s[l]=0;a=0}else if(e<o.times[0]){if(Math.abs(o.times[0]-e)<.001)return 0;i[0]=e,i.set(o.times,1),s.set(r.evaluate(e),0),s.set(o.values,n),a=0}else if(e>o.times[o.times.length-1]){if(Math.abs(o.times[o.times.length-1]-e)<.001)return o.times.length-1;i[i.length-1]=e,i.set(o.times,0),s.set(o.values,0),s.set(r.evaluate(e),o.values.length),a=i.length-1}else for(let l=0;l<o.times.length;l++){if(Math.abs(o.times[l]-e)<.001)return l;if(o.times[l]<e&&o.times[l+1]>e){i.set(o.times.slice(0,l+1),0),i[l+1]=e,i.set(o.times.slice(l+1),l+2),s.set(o.values.slice(0,(l+1)*n),0),s.set(r.evaluate(e),(l+1)*n),s.set(o.values.slice((l+1)*n),(l+2)*n),a=l+1;break}}return o.times=i,o.values=s,a},"insertKeyframe"),mergeMorphTargetTracks:d(function(o,e){let t=[],n={},i=o.tracks;for(let s=0;s<i.length;++s){let r=i[s],a=We.parseTrackName(r.name),l=We.findNode(e,a.nodeName);if(a.propertyName!=="morphTargetInfluences"||a.propertyIndex===void 0){t.push(r);continue}if(r.createInterpolant!==r.InterpolantFactoryMethodDiscrete&&r.createInterpolant!==r.InterpolantFactoryMethodLinear){if(r.createInterpolant.isInterpolantFactoryMethodGLTFCubicSpline)throw new Error("THREE.GLTFExporter: Cannot merge tracks with glTF CUBICSPLINE interpolation.");console.warn("THREE.GLTFExporter: Morph target interpolation mode not yet supported. Using LINEAR instead."),r=r.clone(),r.setInterpolation(wi)}let c=l.morphTargetInfluences.length,h=l.morphTargetDictionary[a.propertyIndex];if(h===void 0)throw new Error("THREE.GLTFExporter: Morph target name not found: "+a.propertyIndex);let u;if(n[l.uuid]===void 0){u=r.clone();let p=new u.ValueBufferType(c*u.times.length);for(let g=0;g<u.times.length;g++)p[g*c+h]=u.values[g];u.name=(a.nodeName||"")+".morphTargetInfluences",u.values=p,n[l.uuid]=u,t.push(u);continue}let f=r.createInterpolant(new r.ValueBufferType(1));u=n[l.uuid];for(let p=0;p<u.times.length;p++)u.values[p*c+h]=f.evaluate(u.times[p]);for(let p=0;p<r.times.length;p++){let g=this.insertKeyframe(u,r.times[p]);u.values[g*c+h]=r.values[p]}}return o.tracks=t,o},"mergeMorphTargetTracks")};L();P();var fg=d(o=>o.material!==void 0&&o.userData&&o.userData.variantMaterials&&!!Array.from(o.userData.variantMaterials.values()).filter(e=>dc(e.material)),"compatibleObject"),dc=d(o=>o&&o.isMaterial&&!Array.isArray(o),"compatibleMaterial"),ca=class{static{d(this,"GLTFExporterMaterialsVariantsExtension")}constructor(e){this.writer=e,this.name="KHR_materials_variants",this.variantNames=[]}beforeParse(e){let t=new Set;for(let n of e)n.traverse(i=>{if(!fg(i))return;let s=i.userData.variantMaterials,r=i.userData.variantData;for(let[a,l]of r){let c=s.get(l.index);c&&dc(c.material)&&t.add(a)}});t.forEach(n=>this.variantNames.push(n))}writeMesh(e,t){if(!fg(e))return;let n=e.userData,i=n.variantMaterials,s=n.variantData,r=new Map,a=new Map,l=Array.from(s.values()).sort((u,f)=>u.index-f.index);for(let[u,f]of l.entries())a.set(f.index,u);for(let u of s.values()){let f=i.get(u.index);if(!f||!dc(f.material))continue;let p=this.writer.processMaterial(f.material);r.has(p)||r.set(p,{material:p,variants:[]}),r.get(p).variants.push(a.get(u.index))}let c=Array.from(r.values()).map(u=>u.variants.sort((f,p)=>f-p)&&u).sort((u,f)=>u.material-f.material);if(c.length===0)return;let h=dc(n.originalMaterial)?this.writer.processMaterial(n.originalMaterial):-1;for(let u of t.primitives)h>=0&&(u.material=h),u.extensions=u.extensions||{},u.extensions[this.name]={mappings:c}}afterParse(){if(this.variantNames.length===0)return;let e=this.writer.json;e.extensions=e.extensions||{};let t=this.variantNames.map(n=>({name:n}));e.extensions[this.name]={variants:t},this.writer.extensionsUsed[this.name]=!0}};L();P();L();P();L();P();L();P();L();P();L();P();L();P();L();P();var Yd=class{static{d(this,"SessionLightProbe")}constructor(e,t,n,i,s){this.xrLight=e,this.renderer=t,this.lightProbe=n,this.xrWebGLBinding=null,this.estimationStartCallback=s,this.frameCallback=this.onXRFrame.bind(this);let r=t.xr.getSession();if(i&&"XRWebGLBinding"in self){let a=new Es(16);e.environment=a.texture;let l=t.getContext();switch(r.preferredReflectionFormat){case"srgba8":l.getExtension("EXT_sRGB");break;case"rgba16f":l.getExtension("OES_texture_half_float");break}this.xrWebGLBinding=new XRWebGLBinding(r,l),this.lightProbe.addEventListener("reflectionchange",()=>{this.updateReflection()})}r.requestAnimationFrame(this.frameCallback)}updateReflection(){let e=this.renderer.properties.get(this.xrLight.environment);if(e){let t=this.xrWebGLBinding.getReflectionCubeMap(this.lightProbe);t&&(e.__webglTexture=t,this.xrLight.environment.needsPMREMUpdate=!0)}}onXRFrame(e,t){if(!this.xrLight)return;t.session.requestAnimationFrame(this.frameCallback);let i=t.getLightEstimate(this.lightProbe);if(i){this.xrLight.lightProbe.sh.fromArray(i.sphericalHarmonicsCoefficients),this.xrLight.lightProbe.intensity=1;let s=Math.max(1,Math.max(i.primaryLightIntensity.x,Math.max(i.primaryLightIntensity.y,i.primaryLightIntensity.z)));this.xrLight.directionalLight.color.setRGB(i.primaryLightIntensity.x/s,i.primaryLightIntensity.y/s,i.primaryLightIntensity.z/s),this.xrLight.directionalLight.intensity=s,this.xrLight.directionalLight.position.copy(i.primaryLightDirection),this.estimationStartCallback&&(this.estimationStartCallback(),this.estimationStartCallback=null)}}dispose(){this.xrLight=null,this.renderer=null,this.lightProbe=null,this.xrWebGLBinding=null}},fc=class extends En{static{d(this,"XREstimatedLight")}constructor(e,t=!0){super(),this.lightProbe=new Ul,this.lightProbe.intensity=0,this.add(this.lightProbe),this.directionalLight=new gr,this.directionalLight.intensity=0,this.add(this.directionalLight),this.environment=null;let n=null,i=!1;e.xr.addEventListener("sessionstart",()=>{let s=e.xr.getSession();"requestLightProbe"in s&&s.requestLightProbe({reflectionFormat:s.preferredReflectionFormat}).then(r=>{n=new Yd(this,e,r,t,()=>{i=!0,this.dispatchEvent({type:"estimationstart"})})})}),e.xr.addEventListener("sessionend",()=>{n&&(n.dispose(),n=null),i&&this.dispatchEvent({type:"estimationend"})}),this.dispose=()=>{n&&(n.dispose(),n=null),this.remove(this.lightProbe),this.lightProbe=null,this.remove(this.directionalLight),this.directionalLight=null,this.environment=null}}};L();P();var Ct=class{static{d(this,"Damper")}constructor(e=50){this.velocity=0,this.naturalFrequency=0,this.setDecayTime(e)}setDecayTime(e){this.naturalFrequency=1/Math.max(.001,e)}update(e,t,n,i){let s=2e-4*this.naturalFrequency;if(e==null||i===0||e===t&&this.velocity===0)return t;if(n<0)return e;let r=e-t,a=this.velocity+this.naturalFrequency*r,l=r+n*a,c=Math.exp(-this.naturalFrequency*n),h=(a-this.naturalFrequency*l)*c,u=-this.naturalFrequency*(h+a*c);return Math.abs(h)<s*Math.abs(i)&&u*r>=0?(this.velocity=0,t):(this.velocity=h,t+l*c)}};L();P();var Fr=.2,pg=.03,nI=.75,mg=12,iI=Math.PI/(2*mg),Ag=new Be,pc=d((o,e,t)=>{let n=e>0?t>0?0:-Math.PI/2:t>0?Math.PI/2:Math.PI;for(let i=0;i<=mg;++i)o.push(e+(Fr-pg)*Math.cos(n),t+(Fr-pg)*Math.sin(n),0,e+Fr*Math.cos(n),t+Fr*Math.sin(n),0),n+=iI},"addCorner"),ha=class extends pe{static{d(this,"PlacementBox")}constructor(e,t){let n=new kt,i=[],s=[],{size:r,boundingBox:a}=e,l=r.x/2,c=(t==="back"?r.y:r.z)/2;pc(s,l,c),pc(s,-l,c),pc(s,-l,-c),pc(s,l,-c);let h=s.length/3;for(let p=0;p<h-2;p+=2)i.push(p,p+1,p+3,p,p+3,p+2);let u=h-2;i.push(u,u+1,1,u,1,0),n.setAttribute("position",new dn(s,3)),n.setIndex(i),super(n),this.side=t;let f=this.material;switch(f.side=Et,f.transparent=!0,f.opacity=0,this.goalOpacity=0,this.opacityDamper=new Ct,this.hitPlane=new pe(new Xn(2*(l+Fr),2*(c+Fr))),this.hitPlane.visible=!1,this.hitPlane.material.side=Et,this.add(this.hitPlane),a.getCenter(this.position),t){case"bottom":this.rotateX(-Math.PI/2),this.shadowHeight=a.min.y,this.position.y=this.shadowHeight;break;case"back":this.shadowHeight=a.min.z,this.position.z=this.shadowHeight}e.target.add(this),this.offsetHeight=0}getHit(e,t,n){Ag.set(t,-n),this.hitPlane.visible=!0;let i=e.positionAndNormalFromPoint(Ag,this.hitPlane);return this.hitPlane.visible=!1,i==null?null:i.position}getExpandedHit(e,t,n){this.hitPlane.scale.set(1e3,1e3,1e3),this.hitPlane.updateMatrixWorld();let i=this.getHit(e,t,n);return this.hitPlane.scale.set(1,1,1),i}set offsetHeight(e){e-=.001,this.side==="back"?this.position.z=this.shadowHeight+e:this.position.y=this.shadowHeight+e}get offsetHeight(){return this.side==="back"?this.position.z-this.shadowHeight:this.position.y-this.shadowHeight}set show(e){this.goalOpacity=e?nI:0}updateOpacity(e){let t=this.material;t.opacity=this.opacityDamper.update(t.opacity,this.goalOpacity,e,1),this.visible=t.opacity>0}dispose(){var e;let{geometry:t,material:n}=this.hitPlane;t.dispose(),n.dispose(),this.geometry.dispose(),this.material.dispose(),(e=this.parent)===null||e===void 0||e.remove(this)}};L();P();L();P();L();P();L();P();L();P();L();P();var St=d((o,e)=>({type:"number",number:o,unit:e}),"numberNode"),In=(()=>{let o={};return t=>{let n=t;if(n in o)return o[n];let i=[],s=0;for(;t;){if(++s>1e3){t="";break}let r=yg(t),a=r.nodes[0];if(a==null||a.terms.length===0)break;i.push(a),t=r.remainingInput}return o[n]=i}})(),yg=(()=>{let o=/^(\-\-|[a-z\u0240-\uffff])/i,e=/^([\*\+\/]|[\-]\s)/i,t=/^[\),]/,n="(",i="#";return s=>{let r=[];for(;s.length&&(s=s.trim(),!t.test(s));)if(s[0]===n){let{nodes:a,remainingInput:l}=gg(s);s=l,r.push({type:"function",name:{type:"ident",value:"calc"},arguments:a})}else if(o.test(s)){let a=sI(s),l=a.nodes[0];if(s=a.remainingInput,s[0]===n){let{nodes:c,remainingInput:h}=gg(s);r.push({type:"function",name:l,arguments:c}),s=h}else r.push(l)}else if(e.test(s))r.push({type:"operator",value:s[0]}),s=s.slice(1);else{let{nodes:a,remainingInput:l}=s[0]===i?oI(s):rI(s);if(a.length===0)break;r.push(a[0]),s=l}return{nodes:[{type:"expression",terms:r}],remainingInput:s}}})(),sI=(()=>{let o=/[^a-z0-9_\-\u0240-\uffff]/i;return e=>{let t=e.match(o),n=t==null?e:e.substr(0,t.index),i=t==null?"":e.substr(t.index);return{nodes:[{type:"ident",value:n}],remainingInput:i}}})(),rI=(()=>{let o=/[\+\-]?(\d+[\.]\d+|\d+|[\.]\d+)([eE][\+\-]?\d+)?/,e=/^[a-z%]+/i,t=/^(m|mm|cm|rad|deg|[%])$/;return n=>{let i=n.match(o),s=i==null?"0":i[0];n=s==null?n:n.slice(s.length);let r=n.match(e),a=r!=null&&r[0]!==""?r[0]:null,l=r==null?n:n.slice(a.length);return a!=null&&!t.test(a)&&(a=null),{nodes:[{type:"number",number:parseFloat(s)||0,unit:a}],remainingInput:l}}})(),oI=(()=>{let o=/^[a-f0-9]*/i;return e=>{e=e.slice(1).trim();let t=e.match(o);return{nodes:t==null?[]:[{type:"hex",value:t[0]}],remainingInput:t==null?e:e.slice(t[0].length)}}})(),gg=d(o=>{let e=[];for(o=o.slice(1).trim();o.length;){let t=yg(o);if(e.push(t.nodes[0]),o=t.remainingInput.trim(),o[0]===",")o=o.slice(1).trim();else if(o[0]===")"){o=o.slice(1);break}}return{nodes:e,remainingInput:o}},"parseFunctionArguments"),_g=Symbol("visitedTypes"),Ac=class{static{d(this,"ASTWalker")}constructor(e){this[_g]=e}walk(e,t){let n=e.slice();for(;n.length;){let i=n.shift();switch(this[_g].indexOf(i.type)>-1&&t(i),i.type){case"expression":n.unshift(...i.terms);break;case"function":n.unshift(i.name,...i.arguments);break}}}},li=Object.freeze({type:"number",number:0,unit:null});var Or=d((o,e=0)=>{let{number:t,unit:n}=o;if(!isFinite(t))t=e,n="rad";else if(o.unit==="rad"||o.unit==null)return o;return{type:"number",number:(n==="deg"&&t!=null?t:0)*Math.PI/180,unit:"rad"}},"degreesToRadians");var xg=d((o,e=0)=>{let{number:t,unit:n}=o;if(!isFinite(t))t=e,n="m";else if(o.unit==="m")return o;let i;switch(n){default:i=1;break;case"cm":i=1/100;break;case"mm":i=1/1e3;break}return{type:"number",number:i*t,unit:"m"}},"lengthToBaseMeters"),Cn=(()=>{let o=d(t=>t,"identity"),e={rad:o,deg:Or,m:o,mm:xg,cm:xg};return(t,n=li)=>{isFinite(t.number)||(t.number=n.number,t.unit=n.unit);let{unit:i}=t;if(i==null)return t;let s=e[i];return s==null?n:s(t)}})();var Ig,vg,Eg,Qr=Symbol("evaluate"),gc=Symbol("lastValue"),ut=class o{static{d(this,"Evaluator")}constructor(){this[Ig]=null}static evaluatableFor(e,t=li){if(e instanceof o)return e;if(e.type==="number")return e.unit==="%"?new tf(e,t):e;switch(e.name.value){case"calc":return new sf(e,t);case"env":return new nf(e)}return li}static evaluate(e){return e instanceof o?e.evaluate():e}static isConstant(e){return e instanceof o?e.isConstant:!0}static applyIntrinsics(e,t){let{basis:n,keywords:i}=t,{auto:s}=i;return n.map((r,a)=>{let l=s[a]==null?r:s[a],c=e[a]?e[a]:l;if(c.type==="ident"){let h=c.value;h in i&&(c=i[h][a])}return(c==null||c.type==="ident")&&(c=l),c.unit==="%"?St(c.number/100*r.number,r.unit):(c=Cn(c,r),c.unit!==r.unit?r:c)})}get isConstant(){return!1}evaluate(){return(!this.isConstant||this[gc]==null)&&(this[gc]=this[Qr]()),this[gc]}};Ig=gc;var wg=Symbol("percentage"),Jd=Symbol("basis"),tf=class extends ut{static{d(this,"PercentageEvaluator")}constructor(e,t){super(),this[wg]=e,this[Jd]=t}get isConstant(){return!0}[Qr](){return St(this[wg].number/100*this[Jd].number,this[Jd].unit)}},mc=Symbol("identNode"),nf=class extends ut{static{d(this,"EnvEvaluator")}constructor(e){super(),this[vg]=null;let t=e.arguments.length?e.arguments[0].terms[0]:null;t!=null&&t.type==="ident"&&(this[mc]=t)}get isConstant(){return!1}[(vg=mc,Qr)](){if(this[mc]!=null)switch(this[mc].value){case"window-scroll-y":let e=self.pageYOffset,t=Math.max(document.body.scrollHeight,document.body.offsetHeight,document.documentElement.clientHeight,document.documentElement.scrollHeight,document.documentElement.offsetHeight);return{type:"number",number:e/(t-self.innerHeight)||0,unit:null}}return li}},aI=/[\*\/]/,Nr=Symbol("evaluator"),sf=class extends ut{static{d(this,"CalcEvaluator")}constructor(e,t=li){if(super(),this[Eg]=null,e.arguments.length!==1)return;let n=e.arguments[0].terms.slice(),i=[];for(;n.length;){let s=n.shift();if(i.length>0){let r=i[i.length-1];if(r.type==="operator"&&aI.test(r.value)){let a=i.pop(),l=i.pop();if(l==null)return;i.push(new _c(a,ut.evaluatableFor(l,t),ut.evaluatableFor(s,t)));continue}}i.push(s.type==="operator"?s:ut.evaluatableFor(s,t))}for(;i.length>2;){let[s,r,a]=i.splice(0,3);if(r.type!=="operator")return;i.unshift(new _c(r,ut.evaluatableFor(s,t),ut.evaluatableFor(a,t)))}i.length===1&&(this[Nr]=i[0])}get isConstant(){return this[Nr]==null||ut.isConstant(this[Nr])}[(Eg=Nr,Qr)](){return this[Nr]!=null?ut.evaluate(this[Nr]):li}},Mg=Symbol("operator"),jd=Symbol("left"),Zd=Symbol("right"),_c=class extends ut{static{d(this,"OperatorEvaluator")}constructor(e,t,n){super(),this[Mg]=e,this[jd]=t,this[Zd]=n}get isConstant(){return ut.isConstant(this[jd])&&ut.isConstant(this[Zd])}[Qr](){let e=Cn(ut.evaluate(this[jd])),t=Cn(ut.evaluate(this[Zd])),{number:n,unit:i}=e,{number:s,unit:r}=t;if(r!=null&&i!=null&&r!=i)return li;let a=i||r,l;switch(this[Mg].value){case"+":l=n+s;break;case"-":l=n-s;break;case"/":l=n/s;break;case"*":l=n*s;break;default:return li}return{type:"number",number:l,unit:a}}},ef=Symbol("evaluatables"),bg=Symbol("intrinsics"),Ur=class extends ut{static{d(this,"StyleEvaluator")}constructor(e,t){super(),this[bg]=t;let n=e[0],i=n!=null?n.terms:[];this[ef]=t.basis.map((s,r)=>{let a=i[r];return a==null?{type:"ident",value:"auto"}:a.type==="ident"?a:ut.evaluatableFor(a,s)})}get isConstant(){for(let e of this[ef])if(!ut.isConstant(e))return!1;return!0}[Qr](){let e=this[ef].map(t=>ut.evaluate(t));return ut.applyIntrinsics(e,this[bg]).map(t=>t.number)}};L();P();var Dg,Lg,Pg,Fg,kr=Symbol("instances"),Cg=Symbol("activateListener"),Sg=Symbol("deactivateListener"),rf=Symbol("notifyInstances"),Tg=Symbol("notify"),Bg=Symbol("callback"),yc=class o{static{d(this,"ScrollObserver")}constructor(e){this[Bg]=e}static[rf](){for(let e of o[kr])e[Tg]()}static[(Dg=kr,Cg)](){self.addEventListener("scroll",this[rf],{passive:!0})}static[Sg](){self.removeEventListener("scroll",this[rf])}observe(){o[kr].size===0&&o[Cg](),o[kr].add(this)}disconnect(){o[kr].delete(this),o[kr].size===0&&o[Sg]()}[Tg](){this[Bg]()}};yc[Dg]=new Set;var Rg=Symbol("computeStyleCallback"),Og=Symbol("astWalker"),ua=Symbol("dependencies"),Ng=Symbol("onScroll"),xc=class{static{d(this,"StyleEffector")}constructor(e){this[Lg]={},this[Pg]=new Ac(["function"]),this[Fg]=()=>{this[Rg]({relatedState:"window-scroll"})},this[Rg]=e}observeEffectsFor(e){let t={},n=this[ua];this[Og].walk(e,i=>{let{name:s}=i,a=i.arguments[0].terms[0];if(!(s.value!=="env"||a==null||a.type!=="ident"))switch(a.value){case"window-scroll-y":if(t["window-scroll"]==null){let l="window-scroll"in n?n["window-scroll"]:new yc(this[Ng]);l.observe(),delete n["window-scroll"],t["window-scroll"]=l}break}});for(let i in n)n[i].disconnect();this[ua]=t}dispose(){for(let e in this[ua])this[ua][e].disconnect()}};Lg=ua,Pg=Og,Fg=Ng;var ci=d(o=>{let e=o.observeEffects||!1,t=o.intrinsics instanceof Function?o.intrinsics:()=>o.intrinsics;return(n,i)=>{let s=n.updated,r=n.connectedCallback,a=n.disconnectedCallback,l=Symbol(`${i}StyleEffector`),c=Symbol(`${i}StyleEvaluator`),h=Symbol(`${i}UpdateEvaluator`),u=Symbol(`${i}EvaluateAndSync`);Object.defineProperties(n,{[l]:{value:null,writable:!0},[c]:{value:null,writable:!0},[h]:{value:d(function(){let f=In(this[i]);this[c]=new Ur(f,t(this)),this[l]==null&&e&&(this[l]=new xc(()=>this[u]())),this[l]!=null&&this[l].observeEffectsFor(f)},"value")},[u]:{value:d(function(){if(this[c]==null)return;let f=this[c].evaluate();this[o.updateHandler](f)},"value")},updated:{value:d(function(f){f.has(i)&&(this[h](),this[u]()),s.call(this,f)},"value")},connectedCallback:{value:d(function(){r.call(this),this.requestUpdate(i,this[i])},"value")},disconnectedCallback:{value:d(function(){a.call(this),this[l]!=null&&(this[l].dispose(),this[l]=null)},"value")}})}},"style");L();P();var Ug=d(o=>o<.5?2*o*o:-1+(4-2*o)*o,"easeInOutQuad"),lI=d((o,e,t=Ug)=>n=>o+(e-o)*t(n),"interpolate"),cI=d((o,e)=>{let t=d(i=>s=>i+=s,"cumulativeSum"),n=e.map(t(0));return i=>{i=Jt(i,0,1),i*=n[n.length-1];let s=n.findIndex(l=>l>=i),r=s<1?0:n[s-1],a=n[s];return o[s]((i-r)/(a-r))}},"sequence"),Is=d(o=>{let e=[],t=[],n=o.initialValue;for(let i=0;i<o.keyframes.length;++i){let s=o.keyframes[i],{value:r,frames:a}=s,l=s.ease||Ug,c=lI(n,r,l);e.push(c),t.push(a),n=r}return cI(e,t)},"timeline");var zt=function(o,e,t,n){var i=arguments.length,s=i<3?e:n===null?n=Object.getOwnPropertyDescriptor(e,t):n,r;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")s=Reflect.decorate(o,e,t,n);else for(var a=o.length-1;a>=0;a--)(r=o[a])&&(s=(i<3?r(s):i>3?r(e,t,s):r(e,t))||s);return i>3&&s&&Object.defineProperty(e,t,s),s},uI=5e3,dI=Is({initialValue:0,keyframes:[{frames:5,value:-1},{frames:1,value:-1},{frames:8,value:1},{frames:1,value:1},{frames:5,value:0},{frames:18,value:0}]}),fI=Is({initialValue:0,keyframes:[{frames:1,value:1},{frames:5,value:1},{frames:1,value:0},{frames:6,value:0}]}),pI=30,AI=12,Xg="0deg 75deg 105%",mI="auto auto auto",gI="auto",_I=2.2,yI=["front","right","back","left"],xI=["upper-","","lower-"],vI=3e3,EI=". Use mouse, touch or arrow keys to move.",vc={AUTO:"auto",NONE:"none"},of={BASIC:"basic",WIGGLE:"wiggle"},wI={PAN_Y:"pan-y",PAN_X:"pan-x",NONE:"none"},Qg=d(()=>({basis:[Or(St(pI,"deg"))],keywords:{auto:[null]}}),"fieldOfViewIntrinsics"),MI=d(()=>({basis:[Or(St(AI,"deg"))],keywords:{auto:[null]}}),"minFieldOfViewIntrinsics"),Yg=(()=>{let o=In(Xg)[0].terms,e=Cn(o[0]),t=Cn(o[1]);return n=>{let i=n[oe].idealCameraDistance();return{basis:[e,t,St(i,"m")],keywords:{auto:[null,null,St(105,"%")]}}}})(),bI=d(o=>{let e=_I*o[oe].boundingSphere.radius;return{basis:[St(-1/0,"rad"),St(Math.PI/8,"rad"),St(e,"m")],keywords:{auto:[null,null,null]}}},"minCameraOrbitIntrinsics"),II=d(o=>{let e=Yg(o),n=new Ur([],e).evaluate()[2];return{basis:[St(1/0,"rad"),St(Math.PI-Math.PI/8,"rad"),St(n,"m")],keywords:{auto:[null,null,null]}}},"maxCameraOrbitIntrinsics"),CI=d(o=>{let e=o[oe].boundingBox.getCenter(new B);return{basis:[St(e.x,"m"),St(e.y,"m"),St(e.z,"m")],keywords:{auto:[null,null,null]}}},"cameraTargetIntrinsics"),Jg=Math.PI/2,SI=Math.PI/3,TI=Jg/2,BI=2*Math.PI,Ye=Symbol("controls"),ma=Symbol("panElement"),af=Symbol("promptElement"),Ec=Symbol("promptAnimatedContainer"),lf=Symbol("fingerAnimatedContainers"),wc=Symbol("deferInteractionPrompt"),kg=Symbol("updateAria"),Gg=Symbol("updateCameraForRadius"),Gr=Symbol("cancelPrompts"),cf=Symbol("onChange"),da=Symbol("onPointerChange"),Cs=Symbol("waitingToPromptUser"),Mc=Symbol("userHasInteracted"),zr=Symbol("promptElementVisibleTime"),fa=Symbol("lastPromptOffset"),bc=Symbol("cancellationSource"),hf=Symbol("lastSpherical"),pa=Symbol("jumpCamera"),uf=Symbol("initialized"),Aa=Symbol("maintainThetaPhi"),zg=Symbol("syncCameraOrbit"),Vg=Symbol("syncFieldOfView"),Hg=Symbol("syncCameraTarget"),Wg=Symbol("syncMinCameraOrbit"),qg=Symbol("syncMaxCameraOrbit"),Kg=Symbol("syncMinFieldOfView"),$g=Symbol("syncMaxFieldOfView"),jg=d(o=>{var e,t,n,i,s,r,a,l,c,h,u,f,p,g,A,m,_;class E extends o{static{d(this,"ControlsModelViewerElement")}constructor(){super(...arguments),this.cameraControls=!1,this.cameraOrbit=Xg,this.cameraTarget=mI,this.fieldOfView=gI,this.minCameraOrbit="auto",this.maxCameraOrbit="auto",this.minFieldOfView="auto",this.maxFieldOfView="auto",this.interactionPromptThreshold=vI,this.interactionPrompt=vc.AUTO,this.interactionPromptStyle=of.WIGGLE,this.orbitSensitivity=1,this.touchAction=wI.NONE,this.disableZoom=!1,this.disablePan=!1,this.disableTap=!1,this.interpolationDecay=50,this[e]=this.shadowRoot.querySelector(".interaction-prompt"),this[t]=this.shadowRoot.querySelector("#prompt"),this[n]=[this.shadowRoot.querySelector("#finger0"),this.shadowRoot.querySelector("#finger1")],this[i]=this.shadowRoot.querySelector(".pan-target"),this[s]=0,this[r]=1/0,this[a]=!1,this[l]=!1,this[c]=rt.AUTOMATIC,this[h]=new Ic(this[oe].camera,this[Qn],this[oe]),this[u]=new Yi,this[f]=!1,this[p]=!1,this[g]=!1,this[A]=()=>{let y=this[Ye].changeSource;this[bc]=y,y===rt.USER_INTERACTION&&(this[Mc]=!0,this[wc]())},this[m]=()=>{this[kg](),this[_t]();let y=this[Ye].changeSource;this.dispatchEvent(new CustomEvent("camera-change",{detail:{source:y}}))},this[_]=y=>{y.type==="pointer-change-start"?this[Hr].classList.add("pointer-tumbling"):this[Hr].classList.remove("pointer-tumbling")}}get inputSensitivity(){return this[Ye].inputSensitivity}set inputSensitivity(y){this[Ye].inputSensitivity=y}getCameraOrbit(){let{theta:y,phi:w,radius:I}=this[hf];return{theta:y,phi:w,radius:I,toString(){return`${this.theta}rad ${this.phi}rad ${this.radius}m`}}}getCameraTarget(){return ti(this[Ne].isPresenting?this[Ne].arRenderer.target:this[oe].getTarget())}getFieldOfView(){return this[Ye].getFieldOfView()}getMinimumFieldOfView(){return this[Ye].options.minimumFieldOfView}getMaximumFieldOfView(){return this[Ye].options.maximumFieldOfView}getIdealAspect(){return this[oe].idealAspect}jumpCameraToGoal(){this[pa]=!0,this.requestUpdate(pa,!1)}resetInteractionPrompt(){this[fa]=0,this[zr]=1/0,this[Mc]=!1,this[Cs]=this.interactionPrompt===vc.AUTO&&this.cameraControls}zoom(y){let w=new WheelEvent("wheel",{deltaY:-30*y});this[Qn].dispatchEvent(w)}connectedCallback(){super.connectedCallback(),this[Ye].addEventListener("user-interaction",this[Gr]),this[Ye].addEventListener("pointer-change-start",this[da]),this[Ye].addEventListener("pointer-change-end",this[da])}disconnectedCallback(){super.disconnectedCallback(),this[Ye].removeEventListener("user-interaction",this[Gr]),this[Ye].removeEventListener("pointer-change-start",this[da]),this[Ye].removeEventListener("pointer-change-end",this[da])}updated(y){super.updated(y);let w=this[Ye],I=this[oe];if(y.has("cameraControls")&&(this.cameraControls?(w.enableInteraction(),this.interactionPrompt===vc.AUTO&&(this[Cs]=!0)):(w.disableInteraction(),this[wc]()),this[Qn].setAttribute("aria-label",this[Vr])),y.has("disableZoom")&&(w.disableZoom=this.disableZoom),y.has("disablePan")&&(w.enablePan=!this.disablePan),y.has("disableTap")&&(w.enableTap=!this.disableTap),(y.has("interactionPrompt")||y.has("cameraControls")||y.has("src"))&&(this.interactionPrompt===vc.AUTO&&this.cameraControls&&!this[Mc]?this[Cs]=!0:this[wc]()),y.has("interactionPromptStyle")&&(this[Ec].style.opacity=this.interactionPromptStyle==of.BASIC?"1":"0"),y.has("touchAction")){let S=this.touchAction;w.applyOptions({touchAction:S}),w.updateTouchActionStyle()}y.has("orbitSensitivity")&&(w.orbitSensitivity=this.orbitSensitivity),y.has("interpolationDecay")&&(w.setDamperDecayTime(this.interpolationDecay),I.setTargetDamperDecayTime(this.interpolationDecay)),this[pa]===!0&&Promise.resolve().then(()=>{w.jumpToGoal(),I.jumpToGoal(),this[cf](),this[pa]=!1})}async updateFraming(){let y=this[oe],w=y.adjustedFoV(y.framedFoVDeg);await y.updateFraming();let I=y.adjustedFoV(y.framedFoVDeg),S=this[Ye].getFieldOfView()/w;this[Ye].setFieldOfView(I*S),this[Aa]=!0,this.requestUpdate("maxFieldOfView"),this.requestUpdate("fieldOfView"),this.requestUpdate("minCameraOrbit"),this.requestUpdate("maxCameraOrbit"),this.requestUpdate("cameraOrbit"),await this.updateComplete}interact(y,w,I){let S=this[Qn],v=this[lf];if(v[0].style.opacity==="1"){console.warn("interact() failed because an existing interaction is running.");return}let b=new Array;b.push({x:Is(w.x),y:Is(w.y)});let R=[{x:b[0].x(0),y:b[0].y(0)}];I!=null&&(b.push({x:Is(I.x),y:Is(I.y)}),R.push({x:b[1].x(0),y:b[1].y(0)}));let N=performance.now(),{width:z,height:O}=this[oe],D=d(H=>{for(let[k,j]of R.entries()){let{style:Z}=v[k];Z.transform=`translateX(${z*j.x}px) translateY(${O*j.y}px)`,H==="pointerdown"?Z.opacity="1":H==="pointerup"&&(Z.opacity="0");let fe={pointerId:k-5678,pointerType:"touch",target:S,clientX:z*j.x,clientY:O*j.y,altKey:!0};S.dispatchEvent(new PointerEvent(H,fe))}},"dispatchTouches"),Q=d(()=>{let H=this[bc];if(H!==rt.AUTOMATIC||!S.isConnected){for(let j of this[lf])j.style.opacity="0";D("pointercancel"),this.dispatchEvent(new CustomEvent("interact-stopped",{detail:{source:H}})),document.removeEventListener("visibilitychange",q);return}let k=Math.min(1,(performance.now()-N)/y);for(let[j,Z]of R.entries())Z.x=b[j].x(k),Z.y=b[j].y(k);D("pointermove"),k<1?requestAnimationFrame(Q):(D("pointerup"),this.dispatchEvent(new CustomEvent("interact-stopped",{detail:{source:rt.AUTOMATIC}})),document.removeEventListener("visibilitychange",q))},"moveTouches"),q=d(()=>{let H=0;document.visibilityState==="hidden"?H=performance.now()-N:N=performance.now()-H},"onVisibilityChange");document.addEventListener("visibilitychange",q),D("pointerdown"),this[bc]=rt.AUTOMATIC,requestAnimationFrame(Q)}[(e=af,t=Ec,n=lf,i=ma,s=fa,r=zr,a=Mc,l=Cs,c=bc,h=Ye,u=hf,f=pa,p=uf,g=Aa,Vg)](y){let w=this[Ye],I=this[oe];I.framedFoVDeg=y[0]*180/Math.PI,w.changeSource=rt.NONE,w.setFieldOfView(I.adjustedFoV(I.framedFoVDeg)),this[Gr]()}[zg](y){let w=this[Ye];if(this[Aa]){let{theta:I,phi:S}=this.getCameraOrbit();y[0]=I,y[1]=S,this[Aa]=!1}w.changeSource=rt.NONE,w.setOrbit(y[0],y[1],y[2]),this[Gr]()}[Wg](y){this[Ye].applyOptions({minimumAzimuthalAngle:y[0],minimumPolarAngle:y[1],minimumRadius:y[2]}),this.jumpCameraToGoal()}[qg](y){this[Ye].applyOptions({maximumAzimuthalAngle:y[0],maximumPolarAngle:y[1],maximumRadius:y[2]}),this[Gg](y[2]),this.jumpCameraToGoal()}[Kg](y){this[Ye].applyOptions({minimumFieldOfView:y[0]*180/Math.PI}),this.jumpCameraToGoal()}[$g](y){let w=this[oe].adjustedFoV(y[0]*180/Math.PI);this[Ye].applyOptions({maximumFieldOfView:w}),this.jumpCameraToGoal()}[Hg](y){let[w,I,S]=y;this[Ne].arRenderer.isPresenting||this[oe].setTarget(w,I,S),this[Ye].changeSource=rt.NONE,this[Ne].arRenderer.updateTarget(),this[Gr]()}[on](y,w){if(super[on](y,w),this[Ne].isPresenting||!this[ei]())return;let I=this[Ye],S=this[oe],v=performance.now();if(this[Cs]&&this.loaded&&v>this[Wr]+this.interactionPromptThreshold&&(this[Cs]=!1,this[zr]=v,this[af].classList.add("visible")),isFinite(this[zr])&&this.interactionPromptStyle===of.WIGGLE){let N=(v-this[zr])/uI%1,z=dI(N),O=fI(N);if(this[Ec].style.opacity=`${O}`,z!==this[fa]){let D=z*S.width*.05,Q=(z-this[fa])*Math.PI/16;this[Ec].style.transform=`translateX(${D}px)`,I.changeSource=rt.AUTOMATIC,I.adjustOrbit(Q,0,0),this[fa]=z}}let b=I.update(y,w),R=S.updateTarget(w);(b||R)&&this[cf]()}[wc](){this[Cs]=!1,this[af].classList.remove("visible"),this[zr]=1/0}[Gg](y){let w=Math.max(this[oe].boundingSphere.radius,y),I=0,S=2*w;this[Ye].updateNearFar(I,S)}[kg](){let{theta:y,phi:w}=this[Ye].getCameraSpherical(this[hf]),I=(4+Math.floor((y%BI+TI)/Jg))%4,S=Math.floor(w/SI),v=yI[I],b=xI[S];this[Cc](`View from stage ${b}${v}`)}get[Vr](){return super[Vr]+(this.cameraControls?EI:"")}async[Ss](y){let w=this[Ye],I=this[oe],S=I.adjustedFoV(I.framedFoVDeg);super[Ss](y);let v=I.adjustedFoV(I.framedFoVDeg)/S,b=w.getFieldOfView()*(isFinite(v)?v:1);w.updateAspect(this[oe].aspect),this.requestUpdate("maxFieldOfView",this.maxFieldOfView),await this.updateComplete,this[Ye].setFieldOfView(b),this.jumpCameraToGoal()}[Zn](){super[Zn](),this[uf]?this[Aa]=!0:this[uf]=!0,this.requestUpdate("maxFieldOfView",this.maxFieldOfView),this.requestUpdate("fieldOfView",this.fieldOfView),this.requestUpdate("minCameraOrbit",this.minCameraOrbit),this.requestUpdate("maxCameraOrbit",this.maxCameraOrbit),this.requestUpdate("cameraOrbit",this.cameraOrbit),this.requestUpdate("cameraTarget",this.cameraTarget),this.jumpCameraToGoal()}}return A=Gr,m=cf,_=da,zt([ye({type:Boolean,attribute:"camera-controls"})],E.prototype,"cameraControls",void 0),zt([ci({intrinsics:Yg,observeEffects:!0,updateHandler:zg}),ye({type:String,attribute:"camera-orbit",hasChanged:d(()=>!0,"hasChanged")})],E.prototype,"cameraOrbit",void 0),zt([ci({intrinsics:CI,observeEffects:!0,updateHandler:Hg}),ye({type:String,attribute:"camera-target",hasChanged:d(()=>!0,"hasChanged")})],E.prototype,"cameraTarget",void 0),zt([ci({intrinsics:Qg,observeEffects:!0,updateHandler:Vg}),ye({type:String,attribute:"field-of-view",hasChanged:d(()=>!0,"hasChanged")})],E.prototype,"fieldOfView",void 0),zt([ci({intrinsics:bI,updateHandler:Wg}),ye({type:String,attribute:"min-camera-orbit",hasChanged:d(()=>!0,"hasChanged")})],E.prototype,"minCameraOrbit",void 0),zt([ci({intrinsics:II,updateHandler:qg}),ye({type:String,attribute:"max-camera-orbit",hasChanged:d(()=>!0,"hasChanged")})],E.prototype,"maxCameraOrbit",void 0),zt([ci({intrinsics:MI,updateHandler:Kg}),ye({type:String,attribute:"min-field-of-view",hasChanged:d(()=>!0,"hasChanged")})],E.prototype,"minFieldOfView",void 0),zt([ci({intrinsics:Qg,updateHandler:$g}),ye({type:String,attribute:"max-field-of-view",hasChanged:d(()=>!0,"hasChanged")})],E.prototype,"maxFieldOfView",void 0),zt([ye({type:Number,attribute:"interaction-prompt-threshold"})],E.prototype,"interactionPromptThreshold",void 0),zt([ye({type:String,attribute:"interaction-prompt"})],E.prototype,"interactionPrompt",void 0),zt([ye({type:String,attribute:"interaction-prompt-style"})],E.prototype,"interactionPromptStyle",void 0),zt([ye({type:Number,attribute:"orbit-sensitivity"})],E.prototype,"orbitSensitivity",void 0),zt([ye({type:String,attribute:"touch-action"})],E.prototype,"touchAction",void 0),zt([ye({type:Boolean,attribute:"disable-zoom"})],E.prototype,"disableZoom",void 0),zt([ye({type:Boolean,attribute:"disable-pan"})],E.prototype,"disablePan",void 0),zt([ye({type:Boolean,attribute:"disable-tap"})],E.prototype,"disableTap",void 0),zt([ye({type:Number,attribute:"interpolation-decay"})],E.prototype,"interpolationDecay",void 0),E},"ControlsMixin");var RI=.018,Zg=2,DI=300,LI=new Be,e0=new B,t0=Object.freeze({minimumRadius:0,maximumRadius:1/0,minimumPolarAngle:Math.PI/8,maximumPolarAngle:Math.PI-Math.PI/8,minimumAzimuthalAngle:-1/0,maximumAzimuthalAngle:1/0,minimumFieldOfView:10,maximumFieldOfView:45,touchAction:"none"}),Sc=Math.PI/8,Tc=.04,Bc=10;var rt={USER_INTERACTION:"user-interaction",NONE:"none",AUTOMATIC:"automatic"},Ic=class extends Mt{static{d(this,"SmoothControls")}constructor(e,t,n){super(),this.camera=e,this.element=t,this.scene=n,this.orbitSensitivity=1,this.inputSensitivity=1,this.changeSource=rt.NONE,this._interactionEnabled=!1,this._disableZoom=!1,this.isUserPointing=!1,this.enablePan=!0,this.enableTap=!0,this.panProjection=new wt,this.panPerPixel=0,this.spherical=new Yi,this.goalSpherical=new Yi,this.thetaDamper=new Ct,this.phiDamper=new Ct,this.radiusDamper=new Ct,this.logFov=Math.log(t0.maximumFieldOfView),this.goalLogFov=this.logFov,this.fovDamper=new Ct,this.touchMode=null,this.pointers=[],this.startTime=0,this.startPointerPosition={clientX:0,clientY:0},this.lastSeparation=0,this.touchDecided=!1,this.onContext=i=>{if(this.enablePan)i.preventDefault();else for(let s of this.pointers)this.onPointerUp(new PointerEvent("pointercancel",Object.assign(Object.assign({},this.startPointerPosition),{pointerId:s.id})))},this.touchModeZoom=(i,s)=>{if(!this._disableZoom){let r=this.twoTouchDistance(this.pointers[0],this.pointers[1]),a=Tc*(this.lastSeparation-r)*50/this.scene.height;this.lastSeparation=r,this.userAdjustOrbit(0,0,a)}this.panPerPixel>0&&this.movePan(i,s)},this.disableScroll=i=>{i.preventDefault()},this.touchModeRotate=(i,s)=>{let{touchAction:r}=this._options;if(!this.touchDecided&&r!=="none"){this.touchDecided=!0;let a=Math.abs(i),l=Math.abs(s);if(this.changeSource===rt.USER_INTERACTION&&(r==="pan-y"&&l>a||r==="pan-x"&&a>l)){this.touchMode=null;return}else this.element.addEventListener("touchmove",this.disableScroll,{passive:!1})}this.handleSinglePointerMove(i,s)},this.onPointerDown=i=>{if(this.pointers.length>2)return;let{element:s}=this;this.pointers.length===0&&(s.addEventListener("pointermove",this.onPointerMove),s.addEventListener("pointerup",this.onPointerUp),this.touchMode=null,this.touchDecided=!1,this.startPointerPosition.clientX=i.clientX,this.startPointerPosition.clientY=i.clientY,this.startTime=performance.now());try{s.setPointerCapture(i.pointerId)}catch{}this.pointers.push({clientX:i.clientX,clientY:i.clientY,id:i.pointerId}),this.isUserPointing=!1,i.pointerType==="touch"?(this.changeSource=i.altKey?rt.AUTOMATIC:rt.USER_INTERACTION,this.onTouchChange(i)):(this.changeSource=rt.USER_INTERACTION,this.onMouseDown(i)),this.changeSource===rt.USER_INTERACTION&&this.dispatchEvent({type:"user-interaction"})},this.onPointerMove=i=>{let s=this.pointers.find(c=>c.id===i.pointerId);if(s==null)return;let r=this.pointers.length,a=(i.clientX-s.clientX)/r,l=(i.clientY-s.clientY)/r;a===0&&l===0||(s.clientX=i.clientX,s.clientY=i.clientY,i.pointerType==="touch"?(this.changeSource=i.altKey?rt.AUTOMATIC:rt.USER_INTERACTION,this.touchMode!==null&&this.touchMode(a,l)):(this.changeSource=rt.USER_INTERACTION,this.panPerPixel>0?this.movePan(a,l):this.handleSinglePointerMove(a,l)))},this.onPointerUp=i=>{let{element:s}=this,r=this.pointers.findIndex(a=>a.id===i.pointerId);r!==-1&&this.pointers.splice(r,1),this.panPerPixel>0&&!i.altKey&&this.resetRadius(),this.pointers.length===0?(s.removeEventListener("pointermove",this.onPointerMove),s.removeEventListener("pointerup",this.onPointerUp),s.removeEventListener("touchmove",this.disableScroll),this.enablePan&&this.enableTap&&this.recenter(i)):this.touchMode!==null&&this.onTouchChange(i),this.scene.element[ma].style.opacity=0,s.style.cursor="grab",this.panPerPixel=0,this.isUserPointing&&this.dispatchEvent({type:"pointer-change-end"})},this.onWheel=i=>{this.changeSource=rt.USER_INTERACTION;let s=i.deltaY*(i.deltaMode==1?18:1)*Tc/30;this.userAdjustOrbit(0,0,s),i.preventDefault(),this.dispatchEvent({type:"user-interaction"})},this.onKeyDown=i=>{let{changeSource:s}=this;this.changeSource=rt.USER_INTERACTION,(i.shiftKey&&this.enablePan?this.panKeyCodeHandler(i):this.orbitZoomKeyCodeHandler(i))?(i.preventDefault(),this.dispatchEvent({type:"user-interaction"})):this.changeSource=s},this._options=Object.assign({},t0),this.setOrbit(0,Math.PI/2,1),this.setFieldOfView(100),this.jumpToGoal()}get interactionEnabled(){return this._interactionEnabled}enableInteraction(){if(this._interactionEnabled===!1){let{element:e}=this;e.addEventListener("pointerdown",this.onPointerDown),e.addEventListener("pointercancel",this.onPointerUp),this._disableZoom||e.addEventListener("wheel",this.onWheel),e.addEventListener("keydown",this.onKeyDown),e.addEventListener("touchmove",()=>{},{passive:!1}),e.addEventListener("contextmenu",this.onContext),this.element.style.cursor="grab",this._interactionEnabled=!0,this.updateTouchActionStyle()}}disableInteraction(){if(this._interactionEnabled===!0){let{element:e}=this;e.removeEventListener("pointerdown",this.onPointerDown),e.removeEventListener("pointermove",this.onPointerMove),e.removeEventListener("pointerup",this.onPointerUp),e.removeEventListener("pointercancel",this.onPointerUp),e.removeEventListener("wheel",this.onWheel),e.removeEventListener("keydown",this.onKeyDown),e.removeEventListener("contextmenu",this.onContext),e.style.cursor="",this.touchMode=null,this._interactionEnabled=!1,this.updateTouchActionStyle()}}get options(){return this._options}set disableZoom(e){this._disableZoom!=e&&(this._disableZoom=e,e===!0?this.element.removeEventListener("wheel",this.onWheel):this.element.addEventListener("wheel",this.onWheel),this.updateTouchActionStyle())}getCameraSpherical(e=new Yi){return e.copy(this.spherical)}getFieldOfView(){return this.camera.fov}applyOptions(e){Object.assign(this._options,e),this.setOrbit(),this.setFieldOfView(Math.exp(this.goalLogFov))}updateNearFar(e,t){this.camera.far=t===0?2:t,this.camera.near=Math.max(e,this.camera.far/1e3),this.camera.updateProjectionMatrix()}updateAspect(e){this.camera.aspect=e,this.camera.updateProjectionMatrix()}setOrbit(e=this.goalSpherical.theta,t=this.goalSpherical.phi,n=this.goalSpherical.radius){let{minimumAzimuthalAngle:i,maximumAzimuthalAngle:s,minimumPolarAngle:r,maximumPolarAngle:a,minimumRadius:l,maximumRadius:c}=this._options,{theta:h,phi:u,radius:f}=this.goalSpherical,p=Jt(e,i,s);!isFinite(i)&&!isFinite(s)&&(this.spherical.theta=this.wrapAngle(this.spherical.theta-p)+p);let g=Jt(t,r,a),A=Jt(n,l,c);return p===h&&g===u&&A===f||!isFinite(p)||!isFinite(g)||!isFinite(A)?!1:(this.goalSpherical.theta=p,this.goalSpherical.phi=g,this.goalSpherical.radius=A,this.goalSpherical.makeSafe(),!0)}setRadius(e){this.goalSpherical.radius=e,this.setOrbit()}setFieldOfView(e){let{minimumFieldOfView:t,maximumFieldOfView:n}=this._options;e=Jt(e,t,n),this.goalLogFov=Math.log(e)}setDamperDecayTime(e){this.thetaDamper.setDecayTime(e),this.phiDamper.setDecayTime(e),this.radiusDamper.setDecayTime(e),this.fovDamper.setDecayTime(e)}adjustOrbit(e,t,n){let{theta:i,phi:s,radius:r}=this.goalSpherical,{minimumRadius:a,maximumRadius:l,minimumFieldOfView:c,maximumFieldOfView:h}=this._options,u=this.spherical.theta-i,f=Math.PI-.001,p=i-Jt(e,-f-u,f-u),g=s-t,A=n===0?0:((n>0?l:a)-r)/(Math.log(n>0?h:c)-this.goalLogFov),m=r+n*(isFinite(A)?A:(l-a)*2);if(this.setOrbit(p,g,m),n!==0){let _=this.goalLogFov+n;this.setFieldOfView(Math.exp(_))}}jumpToGoal(){this.update(0,1e4)}update(e,t){if(this.isStationary())return!1;let{maximumPolarAngle:n,maximumRadius:i}=this._options,s=this.spherical.theta-this.goalSpherical.theta;return Math.abs(s)>Math.PI&&!isFinite(this._options.minimumAzimuthalAngle)&&!isFinite(this._options.maximumAzimuthalAngle)&&(this.spherical.theta-=Math.sign(s)*2*Math.PI),this.spherical.theta=this.thetaDamper.update(this.spherical.theta,this.goalSpherical.theta,t,Math.PI),this.spherical.phi=this.phiDamper.update(this.spherical.phi,this.goalSpherical.phi,t,n),this.spherical.radius=this.radiusDamper.update(this.spherical.radius,this.goalSpherical.radius,t,i),this.logFov=this.fovDamper.update(this.logFov,this.goalLogFov,t,1),this.moveCamera(),!0}updateTouchActionStyle(){let{style:e}=this.element;if(this._interactionEnabled){let{touchAction:t}=this._options;this._disableZoom&&t!=="none"?e.touchAction="manipulation":e.touchAction=t}else e.touchAction=""}isStationary(){return this.goalSpherical.theta===this.spherical.theta&&this.goalSpherical.phi===this.spherical.phi&&this.goalSpherical.radius===this.spherical.radius&&this.goalLogFov===this.logFov}moveCamera(){this.spherical.makeSafe(),this.camera.position.setFromSpherical(this.spherical),this.camera.setRotationFromEuler(new Vi(this.spherical.phi-Math.PI/2,this.spherical.theta,0,"YXZ")),this.camera.fov!==Math.exp(this.logFov)&&(this.camera.fov=Math.exp(this.logFov),this.camera.updateProjectionMatrix())}userAdjustOrbit(e,t,n){this.adjustOrbit(e*this.orbitSensitivity*this.inputSensitivity,t*this.orbitSensitivity*this.inputSensitivity,n*this.inputSensitivity)}wrapAngle(e){let t=(e+Math.PI)/(2*Math.PI);return(t-Math.floor(t))*2*Math.PI-Math.PI}pixelLengthToSphericalAngle(e){return 2*Math.PI*e/this.scene.height}twoTouchDistance(e,t){let{clientX:n,clientY:i}=e,{clientX:s,clientY:r}=t,a=s-n,l=r-i;return Math.sqrt(a*a+l*l)}handleSinglePointerMove(e,t){let n=this.pixelLengthToSphericalAngle(e),i=this.pixelLengthToSphericalAngle(t);this.isUserPointing===!1&&(this.isUserPointing=!0,this.dispatchEvent({type:"pointer-change-start"})),this.userAdjustOrbit(n,i,0)}initializePan(){let{theta:e,phi:t}=this.spherical,n=e-this.scene.yaw;this.panPerPixel=RI/this.scene.height,this.panProjection.set(-Math.cos(n),-Math.cos(t)*Math.sin(n),0,0,Math.sin(t),0,Math.sin(n),-Math.cos(t)*Math.cos(n),0)}movePan(e,t){let{scene:n}=this,i=e0.set(e,t,0).multiplyScalar(this.inputSensitivity),s=this.spherical.radius*Math.exp(this.logFov)*this.panPerPixel;i.multiplyScalar(s);let r=n.getTarget();r.add(i.applyMatrix3(this.panProjection)),n.boundingSphere.clampPoint(r,r),n.setTarget(r.x,r.y,r.z)}recenter(e){if(performance.now()>this.startTime+DI||Math.abs(e.clientX-this.startPointerPosition.clientX)>Zg||Math.abs(e.clientY-this.startPointerPosition.clientY)>Zg)return;let{scene:t}=this,n=t.positionAndNormalFromPoint(t.getNDC(e.clientX,e.clientY));if(n==null){let{cameraTarget:i}=t.element;t.element.cameraTarget="",t.element.cameraTarget=i,this.userAdjustOrbit(0,0,1)}else t.target.worldToLocal(n.position),t.setTarget(n.position.x,n.position.y,n.position.z)}resetRadius(){let{scene:e}=this,t=e.positionAndNormalFromPoint(LI.set(0,0));if(t==null)return;e.target.worldToLocal(t.position);let n=e.getTarget(),{theta:i,phi:s}=this.spherical,r=i-e.yaw,a=e0.set(Math.sin(s)*Math.sin(r),Math.cos(s),Math.sin(s)*Math.cos(r)),l=a.dot(t.position.sub(n));n.add(a.multiplyScalar(l)),e.setTarget(n.x,n.y,n.z),this.setOrbit(void 0,void 0,this.goalSpherical.radius-l)}onTouchChange(e){if(this.pointers.length===1)this.touchMode=this.touchModeRotate;else{if(this._disableZoom){this.touchMode=null,this.element.removeEventListener("touchmove",this.disableScroll);return}this.touchMode=this.touchDecided&&this.touchMode===null?null:this.touchModeZoom,this.touchDecided=!0,this.element.addEventListener("touchmove",this.disableScroll,{passive:!1}),this.lastSeparation=this.twoTouchDistance(this.pointers[0],this.pointers[1]),this.enablePan&&this.touchMode!=null&&(this.initializePan(),e.altKey||(this.scene.element[ma].style.opacity=1))}}onMouseDown(e){this.panPerPixel=0,this.enablePan&&(e.button===2||e.ctrlKey||e.metaKey||e.shiftKey)&&(this.initializePan(),this.scene.element[ma].style.opacity=1),this.element.style.cursor="grabbing"}orbitZoomKeyCodeHandler(e){let t=!0;switch(e.key){case"PageUp":this.userAdjustOrbit(0,0,Tc);break;case"PageDown":this.userAdjustOrbit(0,0,-1*Tc);break;case"ArrowUp":this.userAdjustOrbit(0,-Sc,0);break;case"ArrowDown":this.userAdjustOrbit(0,Sc,0);break;case"ArrowLeft":this.userAdjustOrbit(-Sc,0,0);break;case"ArrowRight":this.userAdjustOrbit(Sc,0,0);break;default:t=!1;break}return t}panKeyCodeHandler(e){this.initializePan();let t=!0;switch(e.key){case"ArrowUp":this.movePan(0,-1*Bc);break;case"ArrowDown":this.movePan(0,Bc);break;case"ArrowLeft":this.movePan(-1*Bc,0);break;case"ArrowRight":this.movePan(Bc,0);break;default:t=!1;break}return t}};var PI=30,FI=.8,n0=1.5,OI=20,i0=1.3,NI=1/i0,UI=.25,QI=10,Ti={NOT_PRESENTING:"not-presenting",SESSION_STARTED:"session-started",OBJECT_PLACED:"object-placed",FAILED:"failed"},Dc={TRACKING:"tracking",NOT_TRACKING:"not-tracking"},Rc=new B,kI=new Ie,GI=new B,zI=new ht(45,1,.1,100),Lc=class extends Mt{static{d(this,"ARRenderer")}constructor(e){super(),this.renderer=e,this.currentSession=null,this.placeOnWall=!1,this.placementBox=null,this.lastTick=null,this.turntableRotation=null,this.oldShadowIntensity=null,this.frame=null,this.initialHitSource=null,this.transientHitTestSource=null,this.inputSource=null,this._presentedScene=null,this.resolveCleanup=null,this.exitWebXRButtonContainer=null,this.overlay=null,this.xrLight=null,this.tracking=!0,this.frames=0,this.initialized=!1,this.oldTarget=new B,this.placementComplete=!1,this.isTranslating=!1,this.isRotating=!1,this.isTwoFingering=!1,this.lastDragPosition=new B,this.firstRatio=0,this.lastAngle=0,this.goalPosition=new B,this.goalYaw=0,this.goalScale=1,this.xDamper=new Ct,this.yDamper=new Ct,this.zDamper=new Ct,this.yawDamper=new Ct,this.scaleDamper=new Ct,this.onExitWebXRButtonContainerClick=()=>this.stopPresenting(),this.onUpdateScene=()=>{this.placementBox!=null&&this.isPresenting&&(this.placementBox.dispose(),this.placementBox=new ha(this.presentedScene,this.placeOnWall?"back":"bottom"))},this.onSelectStart=t=>{let n=this.transientHitTestSource;if(n==null)return;let i=this.frame.getHitTestResultsForTransientInput(n),s=this.presentedScene,r=this.placementBox;if(i.length===1){this.inputSource=t.inputSource;let{axes:a}=this.inputSource.gamepad,l=r.getHit(this.presentedScene,a[0],a[1]);r.show=!0,l!=null?(this.isTranslating=!0,this.lastDragPosition.copy(l)):this.placeOnWall===!1&&(this.isRotating=!0,this.lastAngle=a[0]*n0)}else if(i.length===2){r.show=!0,this.isTwoFingering=!0;let{separation:a}=this.fingerPolar(i);this.firstRatio=a/s.scale.x}},this.onSelectEnd=()=>{this.isTranslating=!1,this.isRotating=!1,this.isTwoFingering=!1,this.inputSource=null,this.goalPosition.y+=this.placementBox.offsetHeight*this.presentedScene.scale.x,this.placementBox.show=!1},this.threeRenderer=e.threeRenderer,this.threeRenderer.xr.enabled=!0}async resolveARSession(){Xu();let e=await navigator.xr.requestSession("immersive-ar",{requiredFeatures:["hit-test"],optionalFeatures:["dom-overlay","light-estimation"],domOverlay:this.overlay?{root:this.overlay}:void 0});return this.threeRenderer.xr.setReferenceSpaceType("local"),await this.threeRenderer.xr.setSession(e),this.threeRenderer.xr.cameraAutoUpdate=!1,e}get presentedScene(){return this._presentedScene}async supportsPresentation(){try{return Xu(),await navigator.xr.isSessionSupported("immersive-ar")}catch(e){return console.warn("Request to present in WebXR denied:"),console.warn(e),console.warn("Falling back to next ar-mode"),!1}}async present(e,t=!1){this.isPresenting&&console.warn("Cannot present while a model is already presenting");let n=new Promise((c,h)=>{requestAnimationFrame(()=>c())});e.setHotspotsVisibility(!1),e.queueRender(),await n,this._presentedScene=e,this.overlay=e.element.shadowRoot.querySelector("div.default"),t===!0&&(this.xrLight=new fc(this.threeRenderer),this.xrLight.addEventListener("estimationstart",()=>{if(!this.isPresenting||this.xrLight==null)return;let c=this.presentedScene;c.add(this.xrLight),c.environment=this.xrLight.environment}));let i=await this.resolveARSession();i.addEventListener("end",()=>{this.postSessionCleanup()},{once:!0});let s=e.element.shadowRoot.querySelector(".slot.exit-webxr-ar-button");s.classList.add("enabled"),s.addEventListener("click",this.onExitWebXRButtonContainerClick),this.exitWebXRButtonContainer=s;let r=await i.requestReferenceSpace("viewer");this.tracking=!0,this.frames=0,this.initialized=!1,this.turntableRotation=e.yaw,this.goalYaw=e.yaw,this.goalScale=1,e.background=null,this.oldShadowIntensity=e.shadowIntensity,e.setShadowIntensity(.01),this.oldTarget.copy(e.getTarget()),e.element.addEventListener("load",this.onUpdateScene);let a=OI*Math.PI/180,l=this.placeOnWall===!0?void 0:new XRRay(new DOMPoint(0,0,0),{x:0,y:-Math.sin(a),z:-Math.cos(a)});i.requestHitTestSource({space:r,offsetRay:l}).then(c=>{this.initialHitSource=c}),this.currentSession=i,this.placementBox=new ha(e,this.placeOnWall?"back":"bottom"),this.placementComplete=!1,this.lastTick=performance.now(),this.dispatchEvent({type:"status",status:Ti.SESSION_STARTED})}async stopPresenting(){if(!this.isPresenting)return;let e=new Promise(t=>{this.resolveCleanup=t});try{await this.currentSession.end(),await e}catch(t){console.warn("Error while trying to end WebXR AR session"),console.warn(t),this.postSessionCleanup()}}get isPresenting(){return this.presentedScene!=null}get target(){return this.oldTarget}updateTarget(){let e=this.presentedScene;if(e!=null){let t=e.getTarget();this.oldTarget.copy(t),this.placeOnWall?t.z=e.boundingBox.min.z:t.y=e.boundingBox.min.y,e.setTarget(t.x,t.y,t.z)}}postSessionCleanup(){let e=this.currentSession;e!=null&&(e.removeEventListener("selectstart",this.onSelectStart),e.removeEventListener("selectend",this.onSelectEnd),this.currentSession=null);let t=this.presentedScene;if(this._presentedScene=null,t!=null){let{element:r}=t;this.xrLight!=null&&(t.remove(this.xrLight),this.xrLight.dispose(),this.xrLight=null),t.position.set(0,0,0),t.scale.set(1,1,1),t.setShadowOffset(0);let a=this.turntableRotation;a!=null&&(t.yaw=a);let l=this.oldShadowIntensity;l!=null&&t.setShadowIntensity(l),t.setEnvironmentAndSkybox(r[Tr],r[Br]);let c=this.oldTarget;t.setTarget(c.x,c.y,c.z),t.xrCamera=null,t.element.removeEventListener("load",this.onUpdateScene),t.orientHotspots(0),r.requestUpdate("cameraTarget"),r.requestUpdate("maxCameraOrbit"),r[Ss](r.getBoundingClientRect()),requestAnimationFrame(()=>{t.element.dispatchEvent(new CustomEvent("camera-change",{detail:{source:rt.NONE}}))})}this.renderer.height=0;let n=this.exitWebXRButtonContainer;n!=null&&(n.classList.remove("enabled"),n.removeEventListener("click",this.onExitWebXRButtonContainerClick),this.exitWebXRButtonContainer=null);let i=this.transientHitTestSource;i!=null&&(i.cancel(),this.transientHitTestSource=null);let s=this.initialHitSource;s!=null&&(s.cancel(),this.initialHitSource=null),this.placementBox!=null&&(this.placementBox.dispose(),this.placementBox=null),this.lastTick=null,this.turntableRotation=null,this.oldShadowIntensity=null,this.frame=null,this.inputSource=null,this.overlay=null,this.resolveCleanup!=null&&this.resolveCleanup(),this.dispatchEvent({type:"status",status:Ti.NOT_PRESENTING})}updateView(e){let t=this.presentedScene,n=this.threeRenderer.xr;n.updateCamera(zI),t.xrCamera=n.getCamera();let{elements:i}=t.getCamera().matrixWorld;if(t.orientHotspots(Math.atan2(i[1],i[5])),this.initialized||(this.placeInitially(),this.initialized=!0),e.requestViewportScale&&e.recommendedViewportScale){let r=e.recommendedViewportScale;e.requestViewportScale(Math.max(r,UI))}let s=n.getBaseLayer();if(s!=null){let r=s instanceof XRWebGLLayer?s.getViewport(e):n.getBinding().getViewSubImage(s,e).viewport;this.threeRenderer.setViewport(r.x,r.y,r.width,r.height)}}placeInitially(){let e=this.presentedScene,{position:t,element:n}=e,i=e.getCamera(),{width:s,height:r}=this.overlay.getBoundingClientRect();e.setSize(s,r),i.projectionMatrixInverse.copy(i.projectionMatrix).invert();let{theta:a,radius:l}=n.getCameraOrbit(),c=i.getWorldDirection(Rc);e.yaw=Math.atan2(-c.x,-c.z)-a,this.goalYaw=e.yaw,t.copy(i.position).add(c.multiplyScalar(l)),this.updateTarget();let h=e.getTarget();t.add(h).sub(this.oldTarget),this.goalPosition.copy(t),e.setHotspotsVisibility(!0);let{session:u}=this.frame;u.addEventListener("selectstart",this.onSelectStart),u.addEventListener("selectend",this.onSelectEnd),u.requestHitTestSourceForTransientInput({profile:"generic-touchscreen"}).then(f=>{this.transientHitTestSource=f})}getTouchLocation(){let{axes:e}=this.inputSource.gamepad,t=this.placementBox.getExpandedHit(this.presentedScene,e[0],e[1]);return t!=null&&(Rc.copy(t).sub(this.presentedScene.getCamera().position),Rc.length()>QI)?null:t}getHitPoint(e){let t=this.threeRenderer.xr.getReferenceSpace(),n=e.getPose(t);if(n==null)return null;let i=kI.fromArray(n.transform.matrix);return this.placeOnWall===!0&&(this.goalYaw=Math.atan2(i.elements[4],i.elements[6])),i.elements[5]>.75!==this.placeOnWall?GI.setFromMatrixPosition(i):null}moveToFloor(e){let t=this.initialHitSource;if(t==null)return;let n=e.getHitTestResults(t);if(n.length==0)return;let i=n[0],s=this.getHitPoint(i);s!=null&&(this.placementBox.show=!0,this.isTranslating||(this.placeOnWall?this.goalPosition.copy(s):this.goalPosition.y=s.y),t.cancel(),this.initialHitSource=null,this.dispatchEvent({type:"status",status:Ti.OBJECT_PLACED}))}fingerPolar(e){let t=e[0].inputSource.gamepad.axes,n=e[1].inputSource.gamepad.axes,i=n[0]-t[0],s=n[1]-t[1],r=Math.atan2(s,i),a=this.lastAngle-r;return a>Math.PI?a-=2*Math.PI:a<-Math.PI&&(a+=2*Math.PI),this.lastAngle=r,{separation:Math.sqrt(i*i+s*s),deltaYaw:a}}processInput(e){let t=this.transientHitTestSource;if(t==null||!this.isTranslating&&!this.isTwoFingering&&!this.isRotating)return;let n=e.getHitTestResultsForTransientInput(t),i=this.presentedScene,s=i.scale.x;if(this.isTwoFingering){if(n.length<2)this.isTwoFingering=!1;else{let{separation:r,deltaYaw:a}=this.fingerPolar(n);if(this.placeOnWall===!1&&(this.goalYaw+=a),i.canScale){let l=r/this.firstRatio;this.goalScale=l<i0&&l>NI?1:l}}return}else if(n.length===2){this.isTranslating=!1,this.isRotating=!1,this.isTwoFingering=!0;let{separation:r}=this.fingerPolar(n);this.firstRatio=r/s;return}if(this.isRotating){let r=this.inputSource.gamepad.axes[0]*n0;this.goalYaw+=r-this.lastAngle,this.lastAngle=r}else this.isTranslating&&n.forEach(r=>{if(r.inputSource!==this.inputSource)return;let a=null;if(r.results.length>0&&(a=this.getHitPoint(r.results[0])),a==null&&(a=this.getTouchLocation()),a!=null){if(this.goalPosition.sub(this.lastDragPosition),this.placeOnWall===!1){let l=a.y-this.lastDragPosition.y;if(l<0){this.placementBox.offsetHeight=l/s,this.presentedScene.setShadowOffset(l);let c=Rc.copy(i.getCamera().position),h=-l/(c.y-a.y);c.multiplyScalar(h),a.multiplyScalar(1-h).add(c)}}this.goalPosition.add(a),this.lastDragPosition.copy(a)}})}moveScene(e){let t=this.presentedScene,{position:n,yaw:i}=t,s=t.boundingSphere.radius,r=this.goalPosition,a=t.scale.x,l=this.placementBox,c=rt.NONE;if(!r.equals(n)||this.goalScale!==a){c=rt.USER_INTERACTION;let{x:h,y:u,z:f}=n;h=this.xDamper.update(h,r.x,e,s),u=this.yDamper.update(u,r.y,e,s),f=this.zDamper.update(f,r.z,e,s),n.set(h,u,f);let p=this.scaleDamper.update(a,this.goalScale,e,1);if(t.scale.set(p,p,p),!this.isTranslating){let g=r.y-u;this.placementComplete&&this.placeOnWall===!1?(l.offsetHeight=g/p,t.setShadowOffset(g)):g===0&&(this.placementComplete=!0,l.show=!1,t.setShadowIntensity(FI))}}l.updateOpacity(e),t.updateTarget(e),t.yaw=this.yawDamper.update(i,this.goalYaw,e,Math.PI),t.element.dispatchEvent(new CustomEvent("camera-change",{detail:{source:c}}))}onWebXRFrame(e,t){this.frame=t,++this.frames;let n=this.threeRenderer.xr.getReferenceSpace(),i=t.getViewerPose(n);i==null&&this.tracking===!0&&this.frames>PI&&(this.tracking=!1,this.dispatchEvent({type:"tracking",status:Dc.NOT_TRACKING}));let s=this.presentedScene;if(i==null||s==null||!s.element.loaded){this.threeRenderer.clear();return}this.tracking===!1&&(this.tracking=!0,this.dispatchEvent({type:"tracking",status:Dc.TRACKING}));let r=!0;for(let a of i.views){if(this.updateView(a),r){this.moveToFloor(t),this.processInput(t);let l=e-this.lastTick;this.moveScene(l),this.renderer.preRender(s,e,l),this.lastTick=e,s.renderShadow(this.threeRenderer)}this.threeRenderer.render(s,s.getCamera()),r=!1}}};L();P();var Pc=class{static{d(this,"Debugger")}constructor(e){e.threeRenderer.debug={checkShaderErrors:!0},Promise.resolve().then(()=>{self.dispatchEvent(new CustomEvent("model-viewer-renderer-debug",{detail:{renderer:e,THREE:{ShaderMaterial:Yt,Texture:st,Mesh:pe,Scene:Gt,PlaneGeometry:Xn,OrthographicCamera:Fn,WebGLRenderTarget:Xt}}}))})}addScene(e){self.dispatchEvent(new CustomEvent("model-viewer-scene-added-debug",{detail:{scene:e}}))}removeScene(e){self.dispatchEvent(new CustomEvent("model-viewer-scene-removed-debug",{detail:{scene:e}}))}};L();P();L();P();L();P();function s0(o){let e=new Map,t=new Map,n=o.clone();return r0(o,n,function(i,s){e.set(s,i),t.set(i,s)}),n.traverse(function(i){if(!i.isSkinnedMesh)return;let s=i,r=e.get(i),a=r.skeleton.bones;s.skeleton=r.skeleton.clone(),s.bindMatrix.copy(r.bindMatrix),s.skeleton.bones=a.map(function(l){return t.get(l)}),s.bind(s.skeleton,s.bindMatrix)}),n}d(s0,"clone");function r0(o,e,t){t(o,e);for(let n=0;n<o.children.length;n++)r0(o.children[n],e.children[n],t)}d(r0,"parallelTraverse");var o0=Symbol("prepared"),ga=Symbol("prepare"),ni=Symbol("preparedGLTF"),_a=Symbol("clone"),Fc=class{static{d(this,"GLTFInstance")}constructor(e){this[ni]=e}static prepare(e){if(e.scene==null)throw new Error("Model does not have a scene");if(e[o0])return e;let t=this[ga](e);return t[o0]=!0,t}static[ga](e){let{scene:t}=e,n=[t];return Object.assign(Object.assign({},e),{scene:t,scenes:n})}get parser(){return this[ni].parser}get animations(){return this[ni].animations}get scene(){return this[ni].scene}get scenes(){return this[ni].scenes}get cameras(){return this[ni].cameras}get asset(){return this[ni].asset}get userData(){return this[ni].userData}clone(){let e=this.constructor,t=this[_a]();return new e(t)}dispose(){this.scenes.forEach(e=>{e.traverse(t=>{if(!t.isMesh)return;let n=t;(Array.isArray(n.material)?n.material:[n.material]).forEach(s=>{for(let r in s){let a=s[r];if(a instanceof st){let l=a.source.data;l.close!=null&&l.close(),a.dispose()}}s.dispose()}),n.geometry.dispose()})})}[_a](){let e=this[ni],t=s0(this.scene);HI(t,this.scene);let n=[t],i=e.userData?Object.assign({},e.userData):{};return Object.assign(Object.assign({},e),{scene:t,scenes:n,userData:i})}},HI=d((o,e)=>{a0(o,e,(t,n)=>{n.userData.variantMaterials!==void 0&&(t.userData.variantMaterials=new Map(n.userData.variantMaterials)),n.userData.variantData!==void 0&&(t.userData.variantData=n.userData.variantData),n.userData.originalMaterial!==void 0&&(t.userData.originalMaterial=n.userData.originalMaterial)})},"cloneVariantMaterials"),a0=d((o,e,t)=>{t(o,e);for(let n=0;n<o.children.length;n++)a0(o.children[n],e.children[n],t)},"traversePair");L();P();var l0=Symbol("threeGLTF"),c0=Symbol("gltf"),h0=Symbol("gltfElementMap"),u0=Symbol("threeObjectMap"),d0=Symbol("parallelTraverseThreeScene"),f0=Symbol("correlateOriginalThreeGLTF"),p0=Symbol("correlateCloneThreeGLTF"),ya=class o{static{d(this,"CorrelatedSceneGraph")}constructor(e,t,n,i){this[l0]=e,this[c0]=t,this[h0]=i,this[u0]=n}static from(e,t){return t!=null?this[p0](e,t):this[f0](e)}static[f0](e){let t=e.parser.json,n=e.parser.associations,i=new Map,s={name:"Default"},r={type:"materials",index:-1};for(let a of n.keys())a instanceof sn&&n.get(a)==null&&(r.index<0&&(t.materials==null&&(t.materials=[]),r.index=t.materials.length,t.materials.push(s)),a.name=s.name,n.set(a,{materials:r.index}));for(let[a,l]of n){if(l){let c=a;c.userData=c.userData||{},c.userData.associations=l}for(let c in l)if(c!=null&&c!=="primitives"){let h=c,f=(t[h]||[])[l[h]];if(f==null)continue;let p=i.get(f);p==null&&(p=new Set,i.set(f,p)),p.add(a)}}return new o(e,t,n,i)}static[p0](e,t){let n=t.threeGLTF,i=t.gltf,s=JSON.parse(JSON.stringify(i)),r=new Map,a=new Map;for(let l=0;l<n.scenes.length;l++)this[d0](n.scenes[l],e.scenes[l],(c,h)=>{let u=t.threeObjectMap.get(c);if(u!=null){for(let f in u)if(f!=null&&f!=="primitives"){let p=f,g=u[p],A=s[p][g],m=r.get(h)||{};m[p]=g,r.set(h,m);let _=a.get(A)||new Set;_.add(h),a.set(A,_)}}});return new o(e,s,r,a)}static[d0](e,t,n){let i=d(r=>r.isMesh,"isMesh"),s=d((r,a)=>{if(n(r,a),r.isObject3D){if(i(r))if(Array.isArray(r.material))for(let l=0;l<r.material.length;++l)s(r.material[l],a.material[l]);else s(r.material,a.material);for(let l=0;l<r.children.length;++l)s(r.children[l],a.children[l])}},"traverse");s(e,t)}get threeGLTF(){return this[l0]}get gltf(){return this[c0]}get gltfElementMap(){return this[h0]}get threeObjectMap(){return this[u0]}};var xa=Symbol("correlatedSceneGraph"),Oc=class extends Fc{static{d(this,"ModelViewerGLTFInstance")}static[ga](e){let t=super[ga](e);t[xa]==null&&(t[xa]=ya.from(t));let{scene:n}=t,i=new Mn(void 0,1/0);return n.traverse(s=>{s.renderOrder=1e3,s.frustumCulled=!1,s.name||(s.name=s.uuid);let r=s;if(r.isMesh){let{geometry:a}=r;r.castShadow=!0,r.isSkinnedMesh&&(a.boundingSphere=i,a.boundingBox=null);let l=r.material;if(l.isMeshBasicMaterial===!0&&(l.toneMapped=!1),l.shadowSide=fn,l.aoMap){let{gltf:c,threeObjectMap:h}=t[xa],u=h.get(l);if(c.materials!=null&&u!=null&&u.materials!=null){let f=c.materials[u.materials];f.occlusionTexture&&f.occlusionTexture.texCoord===0&&a.attributes.uv!=null&&a.setAttribute("uv2",a.attributes.uv)}}}}),t}get correlatedSceneGraph(){return this[ni][xa]}[_a](){let e=super[_a](),t=new Map;return e.scene.traverse(n=>{if(n.isMesh){let i=n,s=i.material;if(s!=null){if(t.has(s.uuid)){i.material=t.get(s.uuid);return}i.material=s.clone(),t.set(s.uuid,i.material)}}}),e[xa]=ya.from(e,this.correlatedSceneGraph),e}};L();P();L();P();var Nc=class extends Ol{static{d(this,"RGBELoader")}constructor(e){super(e),this.type=Pt}parse(e){let a=d(function(x,y){switch(x){case 1:console.error("THREE.RGBELoader Read Error: "+(y||""));break;case 2:console.error("THREE.RGBELoader Write Error: "+(y||""));break;case 3:console.error("THREE.RGBELoader Bad File Format: "+(y||""));break;default:case 4:console.error("THREE.RGBELoader: Error: "+(y||""))}return-1},"rgbe_error"),l=1,c=2,h=4,u=`
`,f=d(function(x,y,w){y=y||1024;let S=x.pos,v=-1,b=0,R="",N=String.fromCharCode.apply(null,new Uint16Array(x.subarray(S,S+128)));for(;0>(v=N.indexOf(u))&&b<y&&S<x.byteLength;)R+=N,b+=N.length,S+=128,N+=String.fromCharCode.apply(null,new Uint16Array(x.subarray(S,S+128)));return-1<v?(w!==!1&&(x.pos+=b+v+1),R+N.slice(0,v)):!1},"fgets"),p=d(function(x){let y=/^#\?(\S+)/,w=/^\s*GAMMA\s*=\s*(\d+(\.\d+)?)\s*$/,I=/^\s*EXPOSURE\s*=\s*(\d+(\.\d+)?)\s*$/,S=/^\s*FORMAT=(\S+)\s*$/,v=/^\s*\-Y\s+(\d+)\s+\+X\s+(\d+)\s*$/,b={valid:0,string:"",comments:"",programtype:"RGBE",format:"",gamma:1,exposure:1,width:0,height:0},R,N;if(x.pos>=x.byteLength||!(R=f(x)))return a(1,"no header found");if(!(N=R.match(y)))return a(3,"bad initial token");for(b.valid|=l,b.programtype=N[1],b.string+=R+`
`;R=f(x),R!==!1;){if(b.string+=R+`
`,R.charAt(0)==="#"){b.comments+=R+`
`;continue}if((N=R.match(w))&&(b.gamma=parseFloat(N[1])),(N=R.match(I))&&(b.exposure=parseFloat(N[1])),(N=R.match(S))&&(b.valid|=c,b.format=N[1]),(N=R.match(v))&&(b.valid|=h,b.height=parseInt(N[1],10),b.width=parseInt(N[2],10)),b.valid&c&&b.valid&h)break}return b.valid&c?b.valid&h?b:a(3,"missing image size specifier"):a(3,"missing format specifier")},"RGBE_ReadHeader"),g=d(function(x,y,w){let I=y;if(I<8||I>32767||x[0]!==2||x[1]!==2||x[2]&128)return new Uint8Array(x);if(I!==(x[2]<<8|x[3]))return a(3,"wrong scanline width");let S=new Uint8Array(4*y*w);if(!S.length)return a(4,"unable to allocate buffer space");let v=0,b=0,R=4*I,N=new Uint8Array(4),z=new Uint8Array(R),O=w;for(;O>0&&b<x.byteLength;){if(b+4>x.byteLength)return a(1);if(N[0]=x[b++],N[1]=x[b++],N[2]=x[b++],N[3]=x[b++],N[0]!=2||N[1]!=2||(N[2]<<8|N[3])!=I)return a(3,"bad rgbe scanline format");let D=0,Q;for(;D<R&&b<x.byteLength;){Q=x[b++];let H=Q>128;if(H&&(Q-=128),Q===0||D+Q>R)return a(3,"bad scanline data");if(H){let k=x[b++];for(let j=0;j<Q;j++)z[D++]=k}else z.set(x.subarray(b,b+Q),D),D+=Q,b+=Q}let q=I;for(let H=0;H<q;H++){let k=0;S[v]=z[H+k],k+=I,S[v+1]=z[H+k],k+=I,S[v+2]=z[H+k],k+=I,S[v+3]=z[H+k],v+=4}O--}return S},"RGBE_ReadPixels_RLE"),A=d(function(x,y,w,I){let S=x[y+3],v=Math.pow(2,S-128)/255;w[I+0]=x[y+0]*v,w[I+1]=x[y+1]*v,w[I+2]=x[y+2]*v,w[I+3]=1},"RGBEByteToRGBFloat"),m=d(function(x,y,w,I){let S=x[y+3],v=Math.pow(2,S-128)/255;w[I+0]=Xo.toHalfFloat(Math.min(x[y+0]*v,65504)),w[I+1]=Xo.toHalfFloat(Math.min(x[y+1]*v,65504)),w[I+2]=Xo.toHalfFloat(Math.min(x[y+2]*v,65504)),w[I+3]=Xo.toHalfFloat(1)},"RGBEByteToRGBHalf"),_=new Uint8Array(e);_.pos=0;let E=p(_);if(E!==-1){let x=E.width,y=E.height,w=g(_.subarray(_.pos),x,y);if(w!==-1){let I,S,v;switch(this.type){case Ut:v=w.length/4;let b=new Float32Array(v*4);for(let N=0;N<v;N++)A(w,N*4,b,N*4);I=b,S=Ut;break;case Pt:v=w.length/4;let R=new Uint16Array(v*4);for(let N=0;N<v;N++)m(w,N*4,R,N*4);I=R,S=Pt;break;default:console.error("THREE.RGBELoader: unsupported type: ",this.type);break}return{width:x,height:y,data:I,header:E.string,gamma:E.gamma,exposure:E.exposure,type:S}}}return null}setDataType(e){return this.type=e,this}load(e,t,n,i){function s(r,a){switch(r.type){case Ut:case Pt:r.encoding=ft,r.minFilter=Je,r.magFilter=Je,r.generateMipmaps=!1,r.flipY=!0;break}t&&t(r,a)}return d(s,"onLoadCallback"),super.load(e,s,n,i)}};L();P();var va=class extends Gt{static{d(this,"EnvironmentScene")}constructor(){super(),this.position.y=-3.5;let e=new $n;e.deleteAttribute("uv");let t=new On({metalness:0,side:dt}),n=new On({metalness:0}),i=new Xi(16777215,500,28,2);i.position.set(.418,16.199,.3),this.add(i);let s=new pe(e,t);s.position.set(-.757,13.219,.717),s.scale.set(31.713,28.305,28.591),this.add(s);let r=new pe(e,n);r.position.set(-10.906,2.009,1.846),r.rotation.set(0,-.195,0),r.scale.set(2.328,7.905,4.651),this.add(r);let a=new pe(e,n);a.position.set(-5.607,-.754,-.758),a.rotation.set(0,.994,0),a.scale.set(1.97,1.534,3.955),this.add(a);let l=new pe(e,n);l.position.set(6.167,.857,7.803),l.rotation.set(0,.561,0),l.scale.set(3.927,6.285,3.687),this.add(l);let c=new pe(e,n);c.position.set(-2.017,.018,6.124),c.rotation.set(0,.333,0),c.scale.set(2.002,4.566,2.064),this.add(c);let h=new pe(e,n);h.position.set(2.291,-.756,-2.621),h.rotation.set(0,-.286,0),h.scale.set(1.546,1.552,1.496),this.add(h);let u=new pe(e,n);u.position.set(-2.193,-.369,-5.547),u.rotation.set(0,.516,0),u.scale.set(3.875,3.487,2.986),this.add(u);let f=new pe(e,this.createAreaLightMaterial(50));f.position.set(-16.116,14.37,8.208),f.scale.set(.1,2.428,2.739),this.add(f);let p=new pe(e,this.createAreaLightMaterial(50));p.position.set(-16.109,18.021,-8.207),p.scale.set(.1,2.425,2.751),this.add(p);let g=new pe(e,this.createAreaLightMaterial(17));g.position.set(14.904,12.198,-1.832),g.scale.set(.15,4.265,6.331),this.add(g);let A=new pe(e,this.createAreaLightMaterial(43));A.position.set(-.462,8.89,14.52),A.scale.set(4.38,5.441,.088),this.add(A);let m=new pe(e,this.createAreaLightMaterial(20));m.position.set(3.235,11.486,-12.541),m.scale.set(2.5,2,.1),this.add(m);let _=new pe(e,this.createAreaLightMaterial(100));_.position.set(0,20,0),_.scale.set(1,.1,1),this.add(_)}createAreaLightMaterial(e){let t=new Ft;return t.color.setScalar(e),t}};L();P();var Ea=class extends Gt{static{d(this,"EnvironmentSceneAlt")}constructor(){super(),this.position.y=-3.5;let e=new $n;e.deleteAttribute("uv");let t=new On({metalness:0,side:dt}),n=new On({metalness:0}),i=new Xi(16777215,400,28,2);i.position.set(.5,14,.5),this.add(i);let s=new pe(e,t);s.position.set(0,13.2,0),s.scale.set(31.5,28.5,31.5),this.add(s);let r=new pe(e,n);r.position.set(-10.906,-1,1.846),r.rotation.set(0,-.195,0),r.scale.set(2.328,7.905,4.651),this.add(r);let a=new pe(e,n);a.position.set(-5.607,-.754,-.758),a.rotation.set(0,.994,0),a.scale.set(1.97,1.534,3.955),this.add(a);let l=new pe(e,n);l.position.set(6.167,-.16,7.803),l.rotation.set(0,.561,0),l.scale.set(3.927,6.285,3.687),this.add(l);let c=new pe(e,n);c.position.set(-2.017,.018,6.124),c.rotation.set(0,.333,0),c.scale.set(2.002,4.566,2.064),this.add(c);let h=new pe(e,n);h.position.set(2.291,-.756,-2.621),h.rotation.set(0,-.286,0),h.scale.set(1.546,1.552,1.496),this.add(h);let u=new pe(e,n);u.position.set(-2.193,-.369,-5.547),u.rotation.set(0,.516,0),u.scale.set(3.875,3.487,2.986),this.add(u);let f=new pe(e,this.createAreaLightMaterial(80));f.position.set(-14,10,8),f.scale.set(.1,2.5,2.5),this.add(f);let p=new pe(e,this.createAreaLightMaterial(80));p.position.set(-14,14,-4),p.scale.set(.1,2.5,2.5),this.add(p);let g=new pe(e,this.createAreaLightMaterial(23));g.position.set(14,12,0),g.scale.set(.1,5,5),this.add(g);let A=new pe(e,this.createAreaLightMaterial(16));A.position.set(0,9,14),A.scale.set(5,5,.1),this.add(A);let m=new pe(e,this.createAreaLightMaterial(80));m.position.set(7,8,-14),m.scale.set(2.5,2.5,.1),this.add(m);let _=new pe(e,this.createAreaLightMaterial(80));_.position.set(-7,16,-14),_.scale.set(2.5,2.5,.1),this.add(_);let E=new pe(e,this.createAreaLightMaterial(1));E.position.set(0,20,0),E.scale.set(.1,.1,.1),this.add(E)}createAreaLightMaterial(e){let t=new Ft;return t.color.setScalar(e),t}};var WI=.04,qr=20,qI=/\.hdr(\.js)?$/,Kr=class extends Mt{static{d(this,"TextureUtils")}constructor(e){super(),this.threeRenderer=e,this.lottieLoaderUrl="",this.withCredentials=!1,this._ldrLoader=null,this._hdrLoader=null,this._lottieLoader=null,this.generatedEnvironmentMap=null,this.generatedEnvironmentMapAlt=null,this.skyboxCache=new Map,this.blurMaterial=null,this.blurScene=null}get ldrLoader(){return this._ldrLoader==null&&(this._ldrLoader=new Ar),this._ldrLoader.withCredentials=this.withCredentials,this._ldrLoader}get hdrLoader(){return this._hdrLoader==null&&(this._hdrLoader=new Nc,this._hdrLoader.setDataType(Pt)),this._hdrLoader.withCredentials=this.withCredentials,this._hdrLoader}async getLottieLoader(){if(this._lottieLoader==null){let{LottieLoader:e}=await import(this.lottieLoaderUrl);this._lottieLoader=new e}return this._lottieLoader.withCredentials=this.withCredentials,this._lottieLoader}async loadImage(e){let t=await new Promise((n,i)=>this.ldrLoader.load(e,n,()=>{},i));return t.name=e,t.flipY=!1,t}async loadLottie(e,t){let n=await this.getLottieLoader();n.setQuality(t);let i=await new Promise((s,r)=>n.load(e,s,()=>{},r));return i.name=e,i}async loadEquirect(e,t=()=>{}){try{let n=qI.test(e),i=n?this.hdrLoader:this.ldrLoader,s=await new Promise((r,a)=>i.load(e,r,l=>{t(l.loaded/l.total*.9)},a));return t(1),s.name=e,s.mapping=So,n||(s.encoding=Se),s}finally{t&&t(1)}}async generateEnvironmentMapAndSkybox(e=null,t=null,n=()=>{}){let i=t!=="legacy";(t==="legacy"||t==="neutral")&&(t=null),t=tc(t);let s=Promise.resolve(null),r;e&&(s=this.loadEquirectFromUrl(e,n)),t?r=this.loadEquirectFromUrl(t,n):e?r=this.loadEquirectFromUrl(e,n):r=i?this.loadGeneratedEnvironmentMapAlt():this.loadGeneratedEnvironmentMap();let[a,l]=await Promise.all([r,s]);if(a==null)throw new Error("Failed to load environment map.");return{environmentMap:a,skybox:l}}async loadEquirectFromUrl(e,t){if(!this.skyboxCache.has(e)){let n=this.loadEquirect(e,t);this.skyboxCache.set(e,n)}return this.skyboxCache.get(e)}async GenerateEnvironmentMap(e,t){await wm();let n=this.threeRenderer,i=new Es(256,{generateMipmaps:!1,type:Pt,format:lt,encoding:ft,depthBuffer:!0}),s=new hr(.1,100,i),r=s.renderTarget.texture;r.name=t;let a=n.outputEncoding,l=n.toneMapping;return n.toneMapping=qn,n.outputEncoding=ft,s.update(n,e),this.blurCubemap(i,WI),n.toneMapping=l,n.outputEncoding=a,r}async loadGeneratedEnvironmentMap(){return this.generatedEnvironmentMap==null&&(this.generatedEnvironmentMap=this.GenerateEnvironmentMap(new va,"legacy")),this.generatedEnvironmentMap}async loadGeneratedEnvironmentMapAlt(){return this.generatedEnvironmentMapAlt==null&&(this.generatedEnvironmentMapAlt=this.GenerateEnvironmentMap(new Ea,"neutral")),this.generatedEnvironmentMapAlt}blurCubemap(e,t){if(this.blurMaterial==null){this.blurMaterial=this.getBlurShader(qr);let i=new $n,s=new pe(i,this.blurMaterial);this.blurScene=new Gt,this.blurScene.add(s)}let n=e.clone();this.halfblur(e,n,t,"latitudinal"),this.halfblur(n,e,t,"longitudinal")}halfblur(e,t,n,i){let r=e.width,a=isFinite(n)?Math.PI/(2*r):2*Math.PI/(2*qr-1),l=n/a,c=isFinite(n)?1+Math.floor(3*l):qr;c>qr&&console.warn(`sigmaRadians, ${n}, is too large and will clip, as it requested ${c} samples when the maximum is set to ${qr}`);let h=[],u=0;for(let g=0;g<qr;++g){let A=g/l,m=Math.exp(-A*A/2);h.push(m),g==0?u+=m:g<c&&(u+=2*m)}for(let g=0;g<h.length;g++)h[g]=h[g]/u;let f=this.blurMaterial.uniforms;f.envMap.value=e.texture,f.samples.value=c,f.weights.value=h,f.latitudinal.value=i==="latitudinal",f.dTheta.value=a,new hr(.1,100,t).update(this.threeRenderer,this.blurScene)}getBlurShader(e){let t=new Float32Array(e),n=new B(0,1,0);return new Yt({name:"SphericalGaussianBlur",defines:{n:e},uniforms:{envMap:{value:null},samples:{value:1},weights:{value:t},latitudinal:{value:!1},dTheta:{value:0},poleAxis:{value:n}},vertexShader:`
      
      varying vec3 vOutputDirection;
  
      void main() {
  
        vOutputDirection = vec3( position );
        gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
  
      }
    `,fragmentShader:`
        varying vec3 vOutputDirection;
  
        uniform samplerCube envMap;
        uniform int samples;
        uniform float weights[ n ];
        uniform bool latitudinal;
        uniform float dTheta;
        uniform vec3 poleAxis;
  
        vec3 getSample( float theta, vec3 axis ) {
  
          float cosTheta = cos( theta );
          // Rodrigues' axis-angle rotation
          vec3 sampleDirection = vOutputDirection * cosTheta
            + cross( axis, vOutputDirection ) * sin( theta )
            + axis * dot( axis, vOutputDirection ) * ( 1.0 - cosTheta );
  
          return vec3( textureCube( envMap, sampleDirection ) );
  
        }
  
        void main() {
  
          vec3 axis = latitudinal ? poleAxis : cross( poleAxis, vOutputDirection );
  
          if ( all( equal( axis, vec3( 0.0 ) ) ) ) {
  
            axis = vec3( vOutputDirection.z, 0.0, - vOutputDirection.x );
  
          }
  
          axis = normalize( axis );
  
          gl_FragColor = vec4( 0.0, 0.0, 0.0, 1.0 );
          gl_FragColor.rgb += weights[ 0 ] * getSample( 0.0, axis );
  
          for ( int i = 1; i < n; i++ ) {
  
            if ( i >= samples ) {
  
              break;
  
            }
  
            float theta = dTheta * float( i );
            gl_FragColor.rgb += weights[ i ] * getSample( -1.0 * theta, axis );
            gl_FragColor.rgb += weights[ i ] * getSample( theta, axis );
  
          }
        }
      `,blending:ri,depthTest:!1,depthWrite:!1,side:dt})}async dispose(){for(let[,e]of this.skyboxCache)(await e).dispose();this.generatedEnvironmentMap!=null&&((await this.generatedEnvironmentMap).dispose(),this.generatedEnvironmentMap=null),this.generatedEnvironmentMapAlt!=null&&((await this.generatedEnvironmentMapAlt).dispose(),this.generatedEnvironmentMapAlt=null),this.blurMaterial!=null&&this.blurMaterial.dispose()}};var KI=.2,ff=40,pf=60,A0=5,$r=[1,.79,.62,.5,.4,.31,.25],$I=3,m0="high-performance",an=class o extends Mt{static{d(this,"Renderer")}constructor(e){super(),this.loader=new pt(Oc),this.width=0,this.height=0,this.dpr=1,this.debugger=null,this.scenes=new Set,this.multipleScenesVisible=!1,this.lastTick=performance.now(),this.renderedLastFrame=!1,this.scaleStep=0,this.lastStep=$I,this.avgFrameDuration=(pf+ff)/2,this.onWebGLContextLost=t=>{this.dispatchEvent({type:"contextlost",sourceEvent:t})},this.onWebGLContextRestored=()=>{var t;(t=this.textureUtils)===null||t===void 0||t.dispose(),this.textureUtils=new Kr(this.threeRenderer);for(let n of this.scenes)n.element[Rr]()},this.dpr=ta(),this.canvas3D=document.createElement("canvas"),this.canvas3D.id="webgl-canvas",this.canvas3D.classList.add("show");try{this.threeRenderer=new Ru({canvas:this.canvas3D,alpha:!0,antialias:!0,powerPreference:e.powerPreference,preserveDrawingBuffer:!0}),this.threeRenderer.autoClear=!0,this.threeRenderer.outputEncoding=Se,this.threeRenderer.physicallyCorrectLights=!0,this.threeRenderer.setPixelRatio(1),this.debugger=e.debug?new Pc(this):null,this.threeRenderer.debug={checkShaderErrors:!!this.debugger},this.threeRenderer.toneMapping=bu}catch(t){console.warn(t)}this.arRenderer=new Lc(this),this.textureUtils=this.canRender?new Kr(this.threeRenderer):null,pt.initializeKTX2Loader(this.threeRenderer),this.canvas3D.addEventListener("webglcontextlost",this.onWebGLContextLost),this.canvas3D.addEventListener("webglcontextrestored",this.onWebGLContextRestored),this.updateRendererSize()}static get singleton(){return this._singleton}static resetSingleton(){let e=this._singleton.dispose();for(let t of e)t.disconnectedCallback();this._singleton=new o({powerPreference:(self.ModelViewerElement||{}).powerPreference||m0,debug:Ju()});for(let t of e)t.connectedCallback()}get canRender(){return this.threeRenderer!=null}get scaleFactor(){return $r[this.scaleStep]}set minScale(e){let t=1;for(;t<$r.length&&!($r[t]<e);)++t;this.lastStep=t-1}registerScene(e){this.scenes.add(e),e.forceRescale();let t=new Be;this.threeRenderer.getSize(t),e.canvas.width=t.x,e.canvas.height=t.y,this.canRender&&this.scenes.size>0&&this.threeRenderer.setAnimationLoop((n,i)=>this.render(n,i)),this.debugger!=null&&this.debugger.addScene(e)}unregisterScene(e){this.scenes.delete(e),this.canvas3D.parentElement===e.canvas.parentElement&&e.canvas.parentElement.removeChild(this.canvas3D),this.canRender&&this.scenes.size===0&&this.threeRenderer.setAnimationLoop(null),this.debugger!=null&&this.debugger.removeScene(e)}displayCanvas(e){return this.multipleScenesVisible?e.element[Uc]:this.canvas3D}countVisibleScenes(){let{canvas3D:e}=this,t=0,n=null;for(let s of this.scenes){let{element:r}=s;r.modelIsVisible&&s.externalRenderer==null&&++t,e.parentElement===s.canvas.parentElement&&(n=s)}let i=t>1;if(n!=null){let s=i&&!this.multipleScenesVisible,r=!n.element.modelIsVisible;if(s||r){let{width:a,height:l}=this.sceneSize(n);this.copyPixels(n,a,l),e.parentElement.removeChild(e)}}this.multipleScenesVisible=i}updateRendererSize(){let e=ta();if(e!==this.dpr)for(let i of this.scenes){let{element:s}=i;s[Ts](s.getBoundingClientRect())}let t=0,n=0;for(let i of this.scenes)t=Math.max(t,i.width),n=Math.max(n,i.height);if(!(t===this.width&&n===this.height&&e===this.dpr)){this.width=t,this.height=n,this.dpr=e,t=Math.ceil(t*e),n=Math.ceil(n*e),this.canRender&&this.threeRenderer.setSize(t,n,!1);for(let i of this.scenes){let{canvas:s}=i;s.width=t,s.height=n,i.forceRescale()}}}updateRendererScale(e){let t=this.scaleStep;this.avgFrameDuration+=Jt(KI*(e-this.avgFrameDuration),-A0,A0),this.avgFrameDuration>pf?++this.scaleStep:this.avgFrameDuration<ff&&this.scaleStep>0&&--this.scaleStep,this.scaleStep=Math.min(this.scaleStep,this.lastStep),t!==this.scaleStep&&(this.avgFrameDuration=(pf+ff)/2)}shouldRender(e){if(e.shouldRender())e.scaleStep!=this.scaleStep&&(e.scaleStep=this.scaleStep,this.rescaleCanvas(e));else if(e.scaleStep!=0)e.scaleStep=0,this.rescaleCanvas(e);else return!1;return!0}rescaleCanvas(e){let t=$r[e.scaleStep],n=Math.ceil(this.width/t),i=Math.ceil(this.height/t),{style:s}=e.canvas;s.width=`${n}px`,s.height=`${i}px`,this.canvas3D.style.width=`${n}px`,this.canvas3D.style.height=`${i}px`;let r=this.dpr*t,a=t<1?"GPU throttling":this.dpr!==self.devicePixelRatio?"No meta viewport tag":"";e.element.dispatchEvent(new CustomEvent("render-scale",{detail:{reportedDpr:self.devicePixelRatio,renderedDpr:r,minimumDpr:this.dpr*$r[this.lastStep],pixelWidth:Math.ceil(e.width*r),pixelHeight:Math.ceil(e.height*r),reason:a}}))}sceneSize(e){let{dpr:t}=this,n=$r[e.scaleStep],i=Math.min(Math.ceil(e.width*n*t),this.canvas3D.width),s=Math.min(Math.ceil(e.height*n*t),this.canvas3D.height);return{width:i,height:s}}copyPixels(e,t,n){let i=e.context;if(i==null){console.log("could not acquire 2d context");return}i.clearRect(0,0,t,n),i.drawImage(this.canvas3D,0,0,t,n,0,0,t,n),e.canvas.classList.add("show")}orderedScenes(){let e=[];for(let t of[!1,!0])for(let n of this.scenes)n.element.modelIsVisible===t&&e.push(n);return e}get isPresenting(){return this.arRenderer.isPresenting}preRender(e,t,n){let{element:i,exposure:s}=e;i[on](t,n);let r=typeof s=="number"&&!Number.isNaN(s);this.threeRenderer.toneMappingExposure=r?s:1}render(e,t){if(t!=null){this.arRenderer.onWebXRFrame(e,t);return}let n=e-this.lastTick;if(this.lastTick=e,!this.canRender||this.isPresenting)return;this.countVisibleScenes(),this.updateRendererSize(),this.renderedLastFrame&&(this.updateRendererScale(n),this.renderedLastFrame=!1);let{canvas3D:i}=this;for(let s of this.orderedScenes()){let{element:r}=s;if(!r.loaded||!r.modelIsVisible&&s.renderCount>0||(this.preRender(s,e,n),!this.shouldRender(s)))continue;if(s.externalRenderer!=null){let c=s.getCamera();c.updateMatrix();let{matrix:h,projectionMatrix:u}=c,f=h.elements.slice(),p=s.getTarget();f[12]+=p.x,f[13]+=p.y,f[14]+=p.z,s.externalRenderer.render({viewMatrix:f,projectionMatrix:u.elements});continue}if(!r.modelIsVisible&&!this.multipleScenesVisible)for(let c of this.scenes)c.element.modelIsVisible&&c.queueRender();let{width:a,height:l}=this.sceneSize(s);s.renderShadow(this.threeRenderer),this.threeRenderer.setRenderTarget(null),this.threeRenderer.setViewport(0,Math.ceil(this.height*this.dpr)-l,a,l),this.threeRenderer.render(s,s.camera),this.multipleScenesVisible||!s.element.modelIsVisible&&s.renderCount===0?this.copyPixels(s,a,l):i.parentElement!==s.canvas.parentElement&&(s.canvas.parentElement.appendChild(i),s.canvas.classList.remove("show")),s.hasRendered(),++s.renderCount,this.renderedLastFrame=!0}}dispose(){this.textureUtils!=null&&this.textureUtils.dispose(),this.threeRenderer!=null&&this.threeRenderer.dispose(),this.textureUtils=null,this.threeRenderer=null;let e=[];for(let t of this.scenes)e.push(t.element);return this.canvas3D.removeEventListener("webglcontextlost",this.onWebGLContextLost),this.canvas3D.removeEventListener("webglcontextrestored",this.onWebGLContextRestored),e}};an._singleton=new an({powerPreference:(self.ModelViewerElement||{}).powerPreference||m0,debug:Ju()});L();P();var it=Symbol("correlatedObjects"),Ue=Symbol("sourceObject"),ln=Symbol("onUpdate"),kn=class{static{d(this,"ThreeDOMElement")}constructor(e,t,n=null){this[ln]=e,this[Ue]=t,this[it]=n}};var g0=new Ft,XI=new Xn(2,2),YI=0,is=Symbol("threeTexture"),ND=Symbol("applyTexture"),Qc=class extends kn{static{d(this,"Image")}get[is](){var e;return console.assert(this[it]!=null&&this[it].size>0,"Image correlated object is undefined"),(e=this[it])===null||e===void 0?void 0:e.values().next().value}constructor(e,t,n){n=n??{name:t&&t.image&&t.image.src?t.image.src.split("/").pop():"adhoc_image",uri:t&&t.image&&t.image.src?t.image.src:"adhoc_image"+YI++},super(e,n,new Set(t?[t]:[]))}get name(){return this[Ue].name||""}get uri(){return this[Ue].uri}get bufferView(){return this[Ue].bufferView}get element(){let e=this[is];if(e&&(e.isCanvasTexture||e.isVideoTexture))return e.image}get animation(){let e=this[is];if(e&&e.isCanvasTexture&&e.animation)return e.animation}get type(){return this.uri!=null?"external":"embedded"}set name(e){this[Ue].name=e}update(){let e=this[is];e&&e.isCanvasTexture&&!e.animation&&(this[is].needsUpdate=!0,this[ln]())}async createThumbnail(e,t){let n=new Gt;g0.map=this[is];let i=new pe(XI,g0);n.add(i);let s=new Fn(-1,1,1,-1,0,1),{threeRenderer:r}=an.singleton,a=new Xt(e,t);r.setRenderTarget(a),r.render(n,s),r.setRenderTarget(null);let l=new Uint8Array(e*t*4);r.readRenderTargetPixels(a,0,0,e,t,l),Sn.width=e,Sn.height=t;let c=Sn.getContext("2d"),h=c.createImageData(e,t);return h.data.set(l),c.putImageData(h,0,0),new Promise(async(u,f)=>{Sn.toBlob(p=>{if(!p)return f("Failed to capture thumbnail.");u(URL.createObjectURL(p))},"image/png")})}};L();P();L();P();L();P();var Tn;(function(o){o[o.Nearest=9728]="Nearest",o[o.Linear=9729]="Linear",o[o.NearestMipmapNearest=9984]="NearestMipmapNearest",o[o.LinearMipmapNearest=9985]="LinearMipmapNearest",o[o.NearestMipmapLinear=9986]="NearestMipmapLinear",o[o.LinearMipmapLinear=9987]="LinearMipmapLinear"})(Tn||(Tn={}));var ss;(function(o){o[o.ClampToEdge=33071]="ClampToEdge",o[o.MirroredRepeat=33648]="MirroredRepeat",o[o.Repeat=10497]="Repeat"})(ss||(ss={}));var JI=(()=>{let o=[Tn.Nearest,Tn.Linear,Tn.NearestMipmapNearest,Tn.LinearMipmapLinear,Tn.NearestMipmapLinear,Tn.LinearMipmapLinear];return e=>o.indexOf(e)>-1})(),jI=(()=>{let o=[Tn.Nearest,Tn.Linear];return e=>o.indexOf(e)>-1})(),ZI=(()=>{let o=[ss.ClampToEdge,ss.MirroredRepeat,ss.Repeat];return e=>o.indexOf(e)>-1})(),eC=d((o,e)=>{switch(o){case"minFilter":return JI(e);case"magFilter":return jI(e);case"wrapS":case"wrapT":return ZI(e);default:throw new Error(`Cannot configure property "${o}" on Sampler`)}},"isValidSamplerValue"),_0=Symbol("threeTextures"),wa=Symbol("setProperty"),Xr=Symbol("sourceSampler"),kc=class extends kn{static{d(this,"Sampler")}get[_0](){return console.assert(this[it]!=null&&this[it].size>0,"Sampler correlated object is undefined"),this[it]}get[Xr](){return console.assert(this[Ue]!=null,"Sampler source is undefined"),this[Ue]}constructor(e,t,n){n=n??{},n.minFilter==null&&(n.minFilter=t?t.minFilter:Tn.LinearMipmapLinear),n.magFilter==null&&(n.magFilter=t?t.magFilter:Tn.Linear),n.wrapS==null&&(n.wrapS=t?t.wrapS:ss.Repeat),n.wrapT==null&&(n.wrapT=t?t.wrapT:ss.Repeat),super(e,n,new Set(t?[t]:[]))}get name(){return this[Ue].name||""}get minFilter(){return this[Xr].minFilter}get magFilter(){return this[Xr].magFilter}get wrapS(){return this[Xr].wrapS}get wrapT(){return this[Xr].wrapT}setMinFilter(e){this[wa]("minFilter",e)}setMagFilter(e){this[wa]("magFilter",e)}setWrapS(e){this[wa]("wrapS",e)}setWrapT(e){this[wa]("wrapT",e)}[wa](e,t){let n=this[Xr];if(n!=null){if(eC(e,t)){n[e]=t;for(let i of this[_0])i[e]=t,i.needsUpdate=!0}this[ln]()}}};var y0=Symbol("image"),x0=Symbol("sampler"),Yr=class extends kn{static{d(this,"Texture")}constructor(e,t,n=null,i=null,s=null){super(e,n||{},new Set(t?[t]:[])),this[x0]=new kc(e,t,i),this[y0]=new Qc(e,t,s)}get name(){return this[Ue].name||""}set name(e){this[Ue].name=e}get sampler(){return this[x0]}get source(){return this[y0]}};var E0,w0,M0,ba=Symbol("texture"),Bs=Symbol("transform"),Af=Symbol("materials"),v0=Symbol("usage"),Ma=Symbol("onUpdate"),Gc=Symbol("activeVideo"),mn;(function(o){o[o.Base=0]="Base",o[o.MetallicRoughness=1]="MetallicRoughness",o[o.Normal=2]="Normal",o[o.Occlusion=3]="Occlusion",o[o.Emissive=4]="Emissive"})(mn||(mn={}));var Bi=class{static{d(this,"TextureInfo")}constructor(e,t,n,i,s,r){if(this[E0]=null,this[w0]={rotation:0,scale:new Be(1,1),offset:new Be(0,0)},this[M0]=!1,r&&n){let a=s.textures?s.textures[r.index]:null,l=a&&s.samplers?s.samplers[a.sampler]:null,c=a&&s.images?s.images[a.source]:null;this[Bs].rotation=n.rotation,this[Bs].scale.copy(n.repeat),this[Bs].offset.copy(n.offset),this[ba]=new Yr(e,n,a,l,c)}this[Ma]=e,this[Af]=i,this[v0]=t}get texture(){return this[ba]}setTexture(e){let t=e!=null?e.source[is]:null,n=this[ba];if(n!=null&&n.isVideoTexture){let s=n.image;this[Gc]=!1,s.requestVideoFrameCallback==null&&s.removeEventListener("timeupdate",this[Ma])}if(this[ba]=e,t!=null&&t.isVideoTexture){let s=t.image;if(this[Gc]=!0,s.requestVideoFrameCallback!=null){let r=d(()=>{this[Gc]&&(this[Ma](),s.requestVideoFrameCallback(r))},"update");s.requestVideoFrameCallback(r)}else s.addEventListener("timeupdate",this[Ma])}let i=Se;if(this[Af])for(let s of this[Af]){switch(this[v0]){case mn.Base:s.map=t;break;case mn.MetallicRoughness:i=ft,s.metalnessMap=t,s.roughnessMap=t;break;case mn.Normal:i=ft,s.normalMap=t;break;case mn.Occlusion:i=ft,s.aoMap=t;break;case mn.Emissive:s.emissiveMap=t;break;default:}s.needsUpdate=!0}t&&(t.encoding=i,t.rotation=this[Bs].rotation,t.repeat=this[Bs].scale,t.offset=this[Bs].offset),this[Ma]()}};E0=ba,w0=Bs,M0=Gc;var zc=Symbol("threeMaterials"),b0=Symbol("baseColorTexture"),I0=Symbol("metallicRoughnessTexture"),Vc=class extends kn{static{d(this,"PBRMetallicRoughness")}constructor(e,t,n,i){super(e,n,i),n.baseColorFactor==null&&(n.baseColorFactor=[1,1,1,1]),n.roughnessFactor==null&&(n.roughnessFactor=1),n.metallicFactor==null&&(n.metallicFactor=1);let{baseColorTexture:s,metallicRoughnessTexture:r}=n,{map:a,metalnessMap:l}=i.values().next().value;this[b0]=new Bi(e,mn.Base,a,i,t,s||null),this[I0]=new Bi(e,mn.MetallicRoughness,l,i,t,r||null)}get[zc](){return this[it]}get baseColorFactor(){return this[Ue].baseColorFactor}get metallicFactor(){return this[Ue].metallicFactor}get roughnessFactor(){return this[Ue].roughnessFactor}get baseColorTexture(){return this[b0]}get metallicRoughnessTexture(){return this[I0]}setBaseColorFactor(e){let t=new Me;e instanceof Array?t.fromArray(e):t.set(e).convertSRGBToLinear();for(let i of this[zc])i.color.set(t),e instanceof Array?i.opacity=e[3]:(e=[0,0,0,i.opacity],t.toArray(e));let n=this[Ue];n.baseColorFactor=e,this[ln]()}setMetallicFactor(e){for(let n of this[zc])n.metalness=e;let t=this[Ue];t.metallicFactor=e,this[ln]()}setRoughnessFactor(e){for(let n of this[zc])n.roughness=e;let t=this[Ue];t.roughnessFactor=e,this[ln]()}};var C0,S0=Symbol("pbrMetallicRoughness"),T0=Symbol("normalTexture"),B0=Symbol("occlusionTexture"),R0=Symbol("emissiveTexture"),tC=Symbol("backingThreeMaterial"),mf=Symbol("applyAlphaCutoff"),Rs=Symbol("lazyLoadGLTFInfo"),gf=Symbol("initialize"),Hc=Symbol("getLoadedMaterial"),gn=Symbol("ensureMaterialIsLoaded"),D0=Symbol("gltfIndex"),jr=Symbol("setActive"),Ca=Symbol("variantIndices"),_f=Symbol("isActive"),Ia=Symbol("variantSet"),L0=Symbol("modelVariants"),Jr=class extends kn{static{d(this,"Material")}constructor(e,t,n,i,s,r,a,l=void 0){super(e,n,a),this[C0]=new Set,this[D0]=i,this[_f]=s,this[L0]=r,l==null?this[gf](t):this[Rs]=l}get[(C0=Ia,tC)](){return this[it].values().next().value}[gf](e){let t=this[ln],n=this[Ue],i=this[it];n.extensions&&n.extensions.KHR_materials_pbrSpecularGlossiness&&console.warn(`Material ${n.name} uses a deprecated extension
          "KHR_materials_pbrSpecularGlossiness", please use
          "pbrMetallicRoughness" instead. Specular Glossiness materials are
          no longer supported; to convert to metal-rough, see 
          https://www.donmccurdy.com/2022/11/28/converting-gltf-pbr-materials-from-specgloss-to-metalrough/.`),n.pbrMetallicRoughness==null&&(n.pbrMetallicRoughness={}),this[S0]=new Vc(t,e,n.pbrMetallicRoughness,i),n.emissiveFactor==null&&(n.emissiveFactor=[0,0,0]),n.doubleSided==null&&(n.doubleSided=!1),n.alphaMode==null&&(n.alphaMode="OPAQUE"),n.alphaCutoff==null&&(n.alphaCutoff=.5);let{normalTexture:s,occlusionTexture:r,emissiveTexture:a}=n,{normalMap:l,aoMap:c,emissiveMap:h}=i.values().next().value;this[T0]=new Bi(t,mn.Normal,l,i,e,s||null),this[B0]=new Bi(t,mn.Occlusion,c,i,e,r||null),this[R0]=new Bi(t,mn.Emissive,h,i,e,a||null)}async[Hc](){if(this[Rs]!=null){let{set:e,material:t}=await this[Rs].doLazyLoad();return this[it]=e,this[gf](this[Rs].gltf),this[Rs]=void 0,this.ensureLoaded=async()=>{},t}return this[it].values().next().value}[gn](){if(this[Rs]!=null)throw new Error(`Material "${this.name}" has not been loaded, call 'await
    myMaterial.ensureLoaded()' before using an unloaded material.`)}async ensureLoaded(){await this[Hc]()}get isLoaded(){return this[Rs]==null}get isActive(){return this[_f]}[jr](e){this[_f]=e}get name(){return this[Ue].name}set name(e){let t=this[Ue];if(t!=null&&(t.name=e),this[it]!=null)for(let n of this[it])n.name=e}get pbrMetallicRoughness(){return this[gn](),this[S0]}get normalTexture(){return this[gn](),this[T0]}get occlusionTexture(){return this[gn](),this[B0]}get emissiveTexture(){return this[gn](),this[R0]}get emissiveFactor(){return this[gn](),this[Ue].emissiveFactor}get index(){return this[D0]}[Ca](){return this[Ia]}hasVariant(e){let t=this[L0].get(e);return t!=null&&this[Ia].has(t.index)}setEmissiveFactor(e){this[gn]();let t=new Me;e instanceof Array?t.fromArray(e):t.set(e).convertSRGBToLinear();for(let n of this[it])n.emissive.set(t);this[Ue].emissiveFactor=t.toArray(),this[ln]()}[mf](){this[gn]();let e=this[Ue];for(let t of this[it])this[Ue].alphaMode==="MASK"?t.alphaTest=e.alphaCutoff:t.alphaTest=void 0,t.needsUpdate=!0}setAlphaCutoff(e){this[gn](),this[Ue].alphaCutoff=e,this[mf](),this[ln]()}getAlphaCutoff(){return this[gn](),this[Ue].alphaCutoff}setDoubleSided(e){this[gn]();for(let t of this[it])t.side=e?Et:fn,t.needsUpdate=!0;this[Ue].doubleSided=e,this[ln]()}getDoubleSided(){return this[gn](),this[Ue].doubleSided}setAlphaMode(e){this[gn]();let t=d((n,i)=>{n.transparent=i,n.depthWrite=!i},"enableTransparency");this[Ue].alphaMode=e;for(let n of this[it])t(n,e==="BLEND"),this[mf](),n.needsUpdate=!0;this[ln]()}getAlphaMode(){return this[gn](),this[Ue].alphaMode}};L();P();var Sa=class{static{d(this,"Node")}constructor(e){this.name="",this.children=new Array,this.name=e}},Zr=class extends Sa{static{d(this,"PrimitiveNode")}constructor(e,t,n,i){super(e.name),this.materials=new Map,this.variantToMaterialMap=new Map,this.initialMaterialIdx=0,this.activeMaterialIdx=0,this.mesh=e;let{gltf:s,threeGLTF:r,threeObjectMap:a}=i;this.modelVariants=n,this.mesh.userData.variantData=n;let l=a.get(e.material);l.materials!=null?this.initialMaterialIdx=this.activeMaterialIdx=l.materials:console.error(`Primitive (${e.name}) missing initial material reference.`);let c=e.userData.associations||{};if(c.meshes==null){console.error("Mesh is missing primitive index association");return}let f=((s.meshes||[])[c.meshes].primitives||[])[c.primitives];if(f==null){console.error("Mesh primitive definition is missing.");return}if(f.material!=null)this.materials.set(f.material,t[f.material]);else{let p=t.findIndex(g=>g.name==="Default");p>=0?this.materials.set(p,t[p]):console.warn("gltfPrimitive has no material!")}if(f.extensions&&f.extensions.KHR_materials_variants){let p=f.extensions.KHR_materials_variants,A=r.parser.json.extensions.KHR_materials_variants.variants;for(let m of p.mappings){let _=t[m.material];this.materials.set(m.material,_);for(let E of m.variants){let{name:x}=A[E];this.variantToMaterialMap.set(E,_),_[Ca]().add(E),n.has(x)||n.set(x,{name:x,index:E})}}}}async setActiveMaterial(e){let t=this.materials.get(e);return t!=null&&(this.mesh.material=await t[Hc](),this.activeMaterialIdx=e),this.mesh.material}getActiveMaterial(){return this.materials.get(this.activeMaterialIdx)}getMaterial(e){return this.materials.get(e)}async enableVariant(e){if(e==null)return this.setActiveMaterial(this.initialMaterialIdx);if(this.variantToMaterialMap!=null&&this.modelVariants.has(e)){let t=this.modelVariants.get(e);return this.enableVariantHelper(t.index)}return null}async enableVariantHelper(e){if(this.variantToMaterialMap!=null&&e!=null){let t=this.variantToMaterialMap.get(e);if(t!=null)return this.setActiveMaterial(t.index)}return null}async instantiateVariants(){if(this.variantToMaterialMap!=null)for(let e of this.variantToMaterialMap.keys()){let t=this.mesh.userData.variantMaterials.get(e);if(t.material!=null)continue;let n=await this.enableVariantHelper(e);n!=null&&(t.material=n)}}get variantInfo(){return this.variantToMaterialMap}addVariant(e,t){if(!this.ensureVariantIsUnused(t))return!1;this.modelVariants.has(t)||this.modelVariants.set(t,{name:t,index:this.modelVariants.size});let i=this.modelVariants.get(t).index;return e[Ca]().add(i),this.variantToMaterialMap.set(i,e),this.materials.set(e.index,e),this.updateVariantUserData(i,e),!0}deleteVariant(e){if(this.variantInfo.has(e)){this.variantInfo.delete(e);let t=this.mesh.userData.variantMaterials;t?.delete(e)}}updateVariantUserData(e,t){t[Ca]().add(e),this.mesh.userData.variantData=this.modelVariants,this.mesh.userData.variantMaterials=this.mesh.userData.variantMaterials||new Map,this.mesh.userData.variantMaterials.set(e,{material:t[it].values().next().value,gltfMaterialIndex:t.index})}ensureVariantIsUnused(e){let t=this.modelVariants.get(e);return t!=null&&this.variantInfo.has(t.index)?(console.warn(`Primitive cannot add variant '${e}' for this material, it already exists.`),!1):!0}};var P0,F0,O0,N0,U0,Q0,Ds=Symbol("materials"),Wc=Symbol("hierarchy"),k0=Symbol("roots"),Ri=Symbol("primitives"),O3=Symbol("loadVariant"),yf=Symbol("correlatedSceneGraph"),Ef=Symbol("prepareVariantsForExport"),wf=Symbol("switchVariant"),Mf=Symbol("materialFromPoint"),qc=Symbol("nodeFromPoint"),bf=Symbol("nodeFromIndex"),jt=Symbol("variantData"),Kc=Symbol("availableVariants"),xf=Symbol("modelOnUpdate"),G0=Symbol("cloneMaterial"),vf=class{static{d(this,"LazyLoader")}constructor(e,t,n,i){this.gltf=e,this.gltfElementMap=t,this.mapKey=n,this.doLazyLoad=i}},$c=class{static{d(this,"Model")}constructor(e,t=()=>{}){this[P0]=new Array,this[F0]=new Array,this[O0]=new Array,this[N0]=new Array,this[U0]=()=>{},this[Q0]=new Map,this[xf]=t,this[yf]=e;let{gltf:n,threeGLTF:i,gltfElementMap:s}=e;for(let[l,c]of n.materials.entries()){let h=s.get(c);if(h!=null)this[Ds].push(new Jr(t,n,c,l,!0,this[jt],h));else{let f=(n.materials||[])[l],p=l,g=d(async()=>{let A=await i.parser.getDependency("material",p),m=new Set;return s.set(f,m),m.add(A),{set:m,material:A}},"materialLoadCallback");this[Ds].push(new Jr(t,n,f,l,!1,this[jt],h,new vf(n,s,f,g)))}}let r=new Map,a=new Array;for(let l of i.scene.children)a.push(l);for(;a.length>0;){let l=a.pop(),c=null;l instanceof pe?(c=new Zr(l,this.materials,this[jt],e),this[Ri].push(c)):c=new Sa(l.name);let h=r.get(l);h!=null?h.children.push(c):this[k0].push(c),this[Wc].push(c);for(let u of l.children)a.push(u),r.set(l,c)}}get materials(){return this[Ds]}[(P0=Ds,F0=Wc,O0=k0,N0=Ri,U0=xf,Q0=jt,Kc)](){let e=Array.from(this[jt].values());return e.sort((t,n)=>t.index-n.index),e.map(t=>t.name)}getMaterialByName(e){let t=this[Ds].filter(n=>n.name===e);return t.length>0?t[0]:null}[bf](e,t){let n=this[Wc].find(i=>{if(i instanceof Zr){let{meshes:s,primitives:r}=i.mesh.userData.associations;if(s==e&&r==t)return!0}return!1});return n??null}[qc](e){return this[Wc].find(t=>t instanceof Zr&&t.mesh===e.object)}[Mf](e){return this[qc](e).getActiveMaterial()}async[wf](e){for(let t of this[Ri])await t.enableVariant(e);for(let t of this.materials)t[jr](!1);for(let t of this[Ri])this.materials[t.getActiveMaterial().index][jr](!0)}async[Ef](){let e=new Array;for(let t of this[Ri])e.push(t.instantiateVariants());await Promise.all(e)}[G0](e,t){let n=this.materials[e];n.isLoaded||console.error(`Cloning an unloaded material,
           call 'material.ensureLoaded() before cloning the material.`);let i=n[it],s=JSON.parse(JSON.stringify(n[Ue]));s.name=t,this[yf].gltf.materials.push(s);let a=new Set;for(let[c,h]of i.entries()){let u=h.clone();u.name=t+(i.size>1?"_inst"+c:""),a.add(u)}let l=new Jr(this[xf],this[yf].gltf,s,this[Ds].length,!1,this[jt],a);return this[Ds].push(l),l}createMaterialInstanceForVariant(e,t,n,i=!0){let s=null;for(let r of this[Ri]){let a=this[jt].get(n);a!=null&&r.variantInfo.has(a.index)||r.getMaterial(e)!=null&&(this.hasVariant(n)||this.createVariant(n),s==null&&(s=this[G0](e,t)),r.addVariant(s,n))}if(i&&s!=null){s[jr](!0),this.materials[e][jr](!1);for(let r of this[Ri])r.enableVariant(n)}return s}createVariant(e){this[jt].has(e)?console.warn(`Variant '${e}'' already exists`):this[jt].set(e,{name:e,index:this[jt].size})}hasVariant(e){return this[jt].has(e)}setMaterialToVariant(e,t){if(this[Kc]().find(n=>n===t)==null){console.warn(`Can't add material to '${t}', the variant does not exist.'`);return}if(e<0||e>=this.materials.length){console.error("setMaterialToVariant(): materialIndex is out of bounds.");return}for(let n of this[Ri]){let i=n.getMaterial(e);i!=null&&n.addVariant(i,t)}}updateVariantName(e,t){let n=this[jt].get(e);n!=null&&(n.name=t,this[jt].set(t,n),this[jt].delete(e))}deleteVariant(e){let t=this[jt].get(e);if(t!=null){for(let n of this.materials)n.hasVariant(e)&&n[Ia].delete(t.index);for(let n of this[Ri])n.deleteVariant(t.index);this[jt].delete(e)}}};var If=function(o,e,t,n){var i=arguments.length,s=i<3?e:n===null?n=Object.getOwnPropertyDescriptor(e,t):n,r;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")s=Reflect.decorate(o,e,t,n);else for(var a=o.length-1;a>=0;a--)(r=o[a])&&(s=(i<3?r(s):i>3?r(e,t,s):r(e,t))||s);return i>3&&s&&Object.defineProperty(e,t,s),s},Ba=Symbol("currentGLTF"),Ra=Symbol("originalGltfJson"),rs=Symbol("model"),Cf=Symbol("getOnUpdateMethod"),Ta=Symbol("buildTexture"),z0=d(o=>{var e,t,n;class i extends o{static{d(this,"SceneGraphModelViewerElement")}constructor(){super(...arguments),this[e]=void 0,this[t]=null,this[n]=null,this.variantName=null,this.orientation="0 0 0",this.scale="1 1 1"}get model(){return this[rs]}get availableVariants(){return this.model?this.model[Kc]():[]}get originalGltfJson(){return this[Ra]}[(e=rs,t=Ba,n=Ra,Cf)](){return()=>{this[_t]()}}[Ta](r){return r.encoding=Se,r.wrapS=Pn,r.wrapT=Pn,new Yr(this[Cf](),r)}async createTexture(r,a="image/png"){let{textureUtils:l}=this[Ne],c=await l.loadImage(r);return c.userData.mimeType=a,this[Ta](c)}async createLottieTexture(r,a=1){let{textureUtils:l}=this[Ne],c=await l.loadLottie(r,a);return this[Ta](c)}createVideoTexture(r){let a=document.createElement("video");a.src=r,a.muted=!0,a.play(),a.loop=!0;let l=new Dl(a);return this[Ta](l)}createCanvasTexture(){let r=document.createElement("canvas"),a=new Vo(r);return this[Ta](a)}async updated(r){if(super.updated(r),r.has("variantName")){let a=this[Jn].beginActivity();a(.1);let l=this[rs],{variantName:c}=this;l!=null&&(await l[wf](c),this[_t](),this.dispatchEvent(new CustomEvent("variant-applied"))),a(1)}if(r.has("orientation")||r.has("scale")){if(!this.loaded)return;let a=this[oe];a.applyTransform(),a.updateBoundingBox(),a.updateShadow(),this[Ne].arRenderer.onUpdateScene(),this[_t]()}}[Zn](){super[Zn]();let{currentGLTF:r}=this[oe];if(r!=null){let{correlatedSceneGraph:a}=r;a!=null&&r!==this[Ba]&&(this[rs]=new $c(a,this[Cf]()),this[Ra]=JSON.parse(JSON.stringify(a.gltf))),"variants"in r.userData&&this.requestUpdate("variantName")}this[Ba]=r}async exportScene(r){let a=this[oe];return new Promise(async(l,c)=>{let h={binary:!0,onlyVisible:!0,maxTextureSize:1/0,includeCustomExtensions:!1,forceIndices:!1};Object.assign(h,r),h.animations=a.animations,h.truncateDrawRange=!0;let u=a.shadow,f=!1;u!=null&&(f=u.visible,u.visible=!1),await this[rs][Ef](),new Pr().register(g=>new ca(g)).parse(a.model,g=>l(new Blob([h.binary?g:JSON.stringify(g)],{type:h.binary?"application/octet-stream":"application/json"})),()=>c("glTF export failed"),h),u!=null&&(u.visible=f)})}materialFromPoint(r,a){let l=this[rs];if(l==null)return null;let c=this[oe],h=c.getNDC(r,a),u=c.hitFromPoint(h);return u==null||u.face==null?null:l[Mf](u)}}return If([ye({type:String,attribute:"variant-name"})],i.prototype,"variantName",void 0),If([ye({type:String,attribute:"orientation"})],i.prototype,"orientation",void 0),If([ye({type:String,attribute:"scale"})],i.prototype,"scale",void 0),i},"SceneGraphMixin");L();P();var Xc=new B,Sf=new B,Tf=new B,Yc=new wt,V0=new Ei,H0=new Kt,eo=class extends hc{static{d(this,"Hotspot")}constructor(e){super(document.createElement("div")),this.normal=new B(0,1,0),this.initialized=!1,this.referenceCount=1,this.pivot=document.createElement("div"),this.slot=document.createElement("slot"),this.element.classList.add("annotation-wrapper"),this.slot.name=e.name,this.element.appendChild(this.pivot),this.pivot.appendChild(this.slot),this.updatePosition(e.position),this.updateNormal(e.normal),this.surface=e.surface}get facingCamera(){return!this.element.classList.contains("hide")}show(){(!this.facingCamera||!this.initialized)&&this.updateVisibility(!0)}hide(){(this.facingCamera||!this.initialized)&&this.updateVisibility(!1)}increment(){this.referenceCount++}decrement(){return this.referenceCount>0&&--this.referenceCount,this.referenceCount===0}updatePosition(e){if(e==null)return;let t=In(e)[0].terms;for(let n=0;n<3;++n)this.position.setComponent(n,Cn(t[n]).number);this.updateMatrixWorld()}updateNormal(e){if(e==null)return;let t=In(e)[0].terms;for(let n=0;n<3;++n)this.normal.setComponent(n,t[n].number)}updateSurface(e){if(!e&&this.initialized)return;let{mesh:t,tri:n,bary:i}=this;if(t==null||n==null||i==null)return;t.getVertexPosition(n.x,Xc),t.getVertexPosition(n.y,Sf),t.getVertexPosition(n.z,Tf),Xc.toArray(Yc.elements,0),Sf.toArray(Yc.elements,3),Tf.toArray(Yc.elements,6),this.position.copy(i).applyMatrix3(Yc);let s=this.parent;s.worldToLocal(t.localToWorld(this.position)),V0.set(Xc,Sf,Tf),V0.getNormal(this.normal).transformDirection(t.matrixWorld);let r=s.parent;H0.setFromAxisAngle(Xc.set(0,1,0),-r.yaw),this.normal.applyQuaternion(H0)}orient(e){this.pivot.style.transform=`rotate(${e}rad)`}updateVisibility(e){e?this.element.classList.remove("hide"):this.element.classList.add("hide"),this.slot.assignedNodes().forEach(t=>{if(t.nodeType!==Node.ELEMENT_NODE)return;let n=t,i=n.dataset.visibilityAttribute;if(i!=null){let s=`data-${i}`;e?n.setAttribute(s,""):n.removeAttribute(s)}n.dispatchEvent(new CustomEvent("hotspot-visibility",{detail:{visible:e}}))}),this.initialized=!0}};L();P();L();P();var W0={uniforms:{tDiffuse:{value:null},h:{value:.001953125}},vertexShader:`

		varying vec2 vUv;

		void main() {

			vUv = uv;
			gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );

		}`,fragmentShader:`

		uniform sampler2D tDiffuse;
		uniform float h;

		varying vec2 vUv;

		void main() {

			vec4 sum = vec4( 0.0 );

			sum += texture2D( tDiffuse, vec2( vUv.x - 4.0 * h, vUv.y ) ) * 0.051;
			sum += texture2D( tDiffuse, vec2( vUv.x - 3.0 * h, vUv.y ) ) * 0.0918;
			sum += texture2D( tDiffuse, vec2( vUv.x - 2.0 * h, vUv.y ) ) * 0.12245;
			sum += texture2D( tDiffuse, vec2( vUv.x - 1.0 * h, vUv.y ) ) * 0.1531;
			sum += texture2D( tDiffuse, vec2( vUv.x, vUv.y ) ) * 0.1633;
			sum += texture2D( tDiffuse, vec2( vUv.x + 1.0 * h, vUv.y ) ) * 0.1531;
			sum += texture2D( tDiffuse, vec2( vUv.x + 2.0 * h, vUv.y ) ) * 0.12245;
			sum += texture2D( tDiffuse, vec2( vUv.x + 3.0 * h, vUv.y ) ) * 0.0918;
			sum += texture2D( tDiffuse, vec2( vUv.x + 4.0 * h, vUv.y ) ) * 0.051;

			gl_FragColor = sum;

		}`};L();P();var q0={uniforms:{tDiffuse:{value:null},v:{value:.001953125}},vertexShader:`

		varying vec2 vUv;

		void main() {

			vUv = uv;
			gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );

		}`,fragmentShader:`

		uniform sampler2D tDiffuse;
		uniform float v;

		varying vec2 vUv;

		void main() {

			vec4 sum = vec4( 0.0 );

			sum += texture2D( tDiffuse, vec2( vUv.x, vUv.y - 4.0 * v ) ) * 0.051;
			sum += texture2D( tDiffuse, vec2( vUv.x, vUv.y - 3.0 * v ) ) * 0.0918;
			sum += texture2D( tDiffuse, vec2( vUv.x, vUv.y - 2.0 * v ) ) * 0.12245;
			sum += texture2D( tDiffuse, vec2( vUv.x, vUv.y - 1.0 * v ) ) * 0.1531;
			sum += texture2D( tDiffuse, vec2( vUv.x, vUv.y ) ) * 0.1633;
			sum += texture2D( tDiffuse, vec2( vUv.x, vUv.y + 1.0 * v ) ) * 0.1531;
			sum += texture2D( tDiffuse, vec2( vUv.x, vUv.y + 2.0 * v ) ) * 0.12245;
			sum += texture2D( tDiffuse, vec2( vUv.x, vUv.y + 3.0 * v ) ) * 0.0918;
			sum += texture2D( tDiffuse, vec2( vUv.x, vUv.y + 4.0 * v ) ) * 0.051;

			gl_FragColor = sum;

		}`};L();P();var dL=Math.PI/180,fL=180/Math.PI;function Bf(o,e,t){return(1-t)*o+t*e}d(Bf,"lerp");var K0=9,nC=6,Rf=2,iC=.3,Jc=class extends Ze{static{d(this,"Shadow")}constructor(e,t,n){super(),this.camera=new Fn,this.renderTarget=null,this.renderTargetBlur=null,this.depthMaterial=new Fo,this.horizontalBlurMaterial=new Yt(W0),this.verticalBlurMaterial=new Yt(q0),this.intensity=0,this.softness=1,this.boundingBox=new Qt,this.size=new B,this.maxDimension=0,this.isAnimated=!1,this.needsUpdate=!1;let{camera:i}=this;i.rotation.x=Math.PI/2,i.left=-.5,i.right=.5,i.bottom=-.5,i.top=.5,this.add(i);let s=new Xn,r=new Ft({opacity:1,transparent:!0,side:dt});this.floor=new pe(s,r),this.floor.userData.shadow=!0,i.add(this.floor),this.blurPlane=new pe(s),this.blurPlane.visible=!1,i.add(this.blurPlane),e.target.add(this),this.depthMaterial.onBeforeCompile=function(a){a.fragmentShader=a.fragmentShader.replace("gl_FragColor = vec4( vec3( 1.0 - fragCoordZ ), opacity );","gl_FragColor = vec4( vec3( 0.0 ), ( 1.0 - fragCoordZ ) * opacity );")},this.horizontalBlurMaterial.depthTest=!1,this.verticalBlurMaterial.depthTest=!1,this.setScene(e,t,n)}setScene(e,t,n){let{boundingBox:i,size:s,rotation:r,position:a}=this;if(this.isAnimated=e.animationNames.length>0,this.boundingBox.copy(e.boundingBox),this.size.copy(e.size),this.maxDimension=Math.max(s.x,s.y,s.z)*(this.isAnimated?Rf:1),this.boundingBox.getCenter(a),n==="back"){let{min:l,max:c}=i;[l.y,l.z]=[l.z,l.y],[c.y,c.z]=[c.z,c.y],[s.y,s.z]=[s.z,s.y],r.x=Math.PI/2,r.y=Math.PI}else r.x=0,r.y=0;if(this.isAnimated){let l=i.min.y,c=i.max.y;s.y=this.maxDimension,i.expandByVector(s.subScalar(this.maxDimension).multiplyScalar(-.5)),i.min.y=l,i.max.y=c,s.set(this.maxDimension,c-l,this.maxDimension)}n==="bottom"?a.y=i.min.y:a.z=i.min.y,this.setSoftness(t)}setSoftness(e){this.softness=e;let{size:t,camera:n}=this,i=this.isAnimated?Rf:1,s=i*Math.pow(2,K0-e*(K0-nC));this.setMapSize(s);let r=t.y/2,a=t.y*i;n.near=0,n.far=Bf(a,r,e),this.depthMaterial.opacity=1/e,n.updateProjectionMatrix(),this.setIntensity(this.intensity),this.setOffset(0)}setMapSize(e){let{size:t}=this;this.isAnimated&&(e*=Rf);let n=Math.floor(t.x>t.z?e:e*t.x/t.z),i=Math.floor(t.x>t.z?e*t.z/t.x:e),s=10,r=s+n,a=s+i;if(this.renderTarget!=null&&(this.renderTarget.width!==r||this.renderTarget.height!==a)&&(this.renderTarget.dispose(),this.renderTarget=null,this.renderTargetBlur.dispose(),this.renderTargetBlur=null),this.renderTarget==null){let l={format:lt};this.renderTarget=new Xt(r,a,l),this.renderTargetBlur=new Xt(r,a,l),this.floor.material.map=this.renderTarget.texture}this.camera.scale.set(t.x*(1+s/n),t.z*(1+s/i),1),this.needsUpdate=!0}setIntensity(e){this.intensity=e,e>0?(this.visible=!0,this.floor.visible=!0,this.floor.material.opacity=e*Bf(iC,1,this.softness*this.softness)):(this.visible=!1,this.floor.visible=!1)}getIntensity(){return this.intensity}setOffset(e){this.floor.position.z=-e+.001*this.maxDimension}render(e,t){t.overrideMaterial=this.depthMaterial;let n=e.getClearAlpha();e.setClearAlpha(0),this.floor.visible=!1;let i=e.xr.enabled;e.xr.enabled=!1;let s=e.getRenderTarget();e.setRenderTarget(this.renderTarget),e.render(t,this.camera),t.overrideMaterial=null,this.floor.visible=!0,this.blurShadow(e),e.xr.enabled=i,e.setRenderTarget(s),e.setClearAlpha(n)}blurShadow(e){let{camera:t,horizontalBlurMaterial:n,verticalBlurMaterial:i,renderTarget:s,renderTargetBlur:r,blurPlane:a}=this;a.visible=!0,a.material=n,n.uniforms.h.value=1/this.renderTarget.width,n.uniforms.tDiffuse.value=this.renderTarget.texture,e.setRenderTarget(r),e.render(a,t),a.material=i,i.uniforms.v.value=1/this.renderTarget.height,i.uniforms.tDiffuse.value=this.renderTargetBlur.texture,e.setRenderTarget(s),e.render(a,t),a.visible=!1}dispose(){this.renderTarget!=null&&this.renderTarget.dispose(),this.renderTargetBlur!=null&&this.renderTargetBlur.dispose(),this.depthMaterial.dispose(),this.horizontalBlurMaterial.dispose(),this.verticalBlurMaterial.dispose(),this.floor.material.dispose(),this.floor.geometry.dispose(),this.blurPlane.geometry.dispose(),this.removeFromParent()}};var Df=100;var Lf=new B,$0=new B,X0=new B,sC=new Gl,rC=new B,Da=new Be,jc=class extends Gt{static{d(this,"ModelScene")}constructor({canvas:e,element:t,width:n,height:i}){super(),this.annotationRenderer=new uc,this.schemaElement=document.createElement("script"),this.width=1,this.height=1,this.aspect=1,this.scaleStep=0,this.renderCount=0,this.externalRenderer=null,this.camera=new ht(45,1,.1,100),this.xrCamera=null,this.url=null,this.target=new Ze,this.animationNames=[],this.boundingBox=new Qt,this.boundingSphere=new Mn,this.size=new B,this.idealAspect=0,this.framedFoVDeg=0,this.shadow=null,this.shadowIntensity=0,this.shadowSoftness=1,this.bakedShadows=new Set,this.exposure=1,this.canScale=!0,this.isDirty=!1,this.goalTarget=new B,this.targetDamperX=new Ct,this.targetDamperY=new Ct,this.targetDamperZ=new Ct,this._currentGLTF=null,this._model=null,this.cancelPendingSourceChange=null,this.animationsByName=new Map,this.currentAnimationAction=null,this.name="ModelScene",this.element=t,this.canvas=e,this.camera=new ht(45,1,.1,100),this.camera.name="MainCamera",this.add(this.target),this.setSize(n,i),this.target.name="Target",this.mixer=new kl(this.target);let{domElement:s}=this.annotationRenderer,{style:r}=s;r.display="none",r.pointerEvents="none",r.position="absolute",r.top="0",this.element.shadowRoot.querySelector(".default").appendChild(s),this.schemaElement.setAttribute("type","application/ld+json")}get context(){return this.canvas.getContext("2d")}getCamera(){return this.xrCamera!=null?this.xrCamera:this.camera}queueRender(){this.isDirty=!0}shouldRender(){return this.isDirty}hasRendered(){this.isDirty=!1}forceRescale(){this.scaleStep=-1,this.queueRender()}async setObject(e){this.reset(),this._model=e,this.target.add(e),await this.setupScene()}async setSource(e,t=()=>{}){if(!e||e===this.url){t(1);return}if(this.reset(),this.url=e,this.externalRenderer!=null){let a=await this.externalRenderer.load(t);this.boundingSphere.radius=a.framedRadius,this.idealAspect=a.fieldOfViewAspect;return}this.cancelPendingSourceChange!=null&&(this.cancelPendingSourceChange(),this.cancelPendingSourceChange=null);let n;try{n=await new Promise(async(a,l)=>{this.cancelPendingSourceChange=()=>l();try{let c=await this.element[Ne].loader.load(e,this.element,t);a(c)}catch(c){l(c)}})}catch(a){if(a==null)return;throw a}this.cancelPendingSourceChange=null,this.reset(),this.url=e,this._currentGLTF=n,n!=null&&(this._model=n.scene,this.target.add(n.scene));let{animations:i}=n,s=new Map,r=[];for(let a of i)s.set(a.name,a),r.push(a.name);this.animations=i,this.animationsByName=s,this.animationNames=r,await this.setupScene()}async setupScene(){this.applyTransform(),this.updateBoundingBox(),await this.updateFraming(),this.updateShadow(),this.setShadowIntensity(this.shadowIntensity)}reset(){this.url=null,this.renderCount=0,this.queueRender(),this.shadow!=null&&this.shadow.setIntensity(0),this.bakedShadows.clear();let{_model:e}=this;e!=null&&(e.removeFromParent(),this._model=null);let t=this._currentGLTF;t!=null&&(t.dispose(),this._currentGLTF=null),this.currentAnimationAction!=null&&(this.currentAnimationAction.stop(),this.currentAnimationAction=null),this.mixer.stopAllAction(),this.mixer.uncacheRoot(this)}dispose(){this.reset(),this.shadow!=null&&(this.shadow.dispose(),this.shadow=null),this.element[Ba]=null,this.element[Ra]=null,this.element[rs]=null}get currentGLTF(){return this._currentGLTF}setSize(e,t){if(!(this.width===e&&this.height===t)){if(this.width=Math.max(e,1),this.height=Math.max(t,1),this.annotationRenderer.setSize(e,t),this.aspect=this.width/this.height,this.externalRenderer!=null){let n=ta();this.externalRenderer.resize(e*n,t*n)}this.queueRender()}}markBakedShadow(e){e.userData.shadow=!0,this.bakedShadows.add(e)}unmarkBakedShadow(e){e.userData.shadow=!1,e.visible=!0,this.bakedShadows.delete(e),this.boundingBox.expandByObject(e)}findBakedShadows(e){let t=new Qt;e.traverse(n=>{let i=n;if(!i.isMesh||!i.material.transparent)return;t.setFromObject(i);let r=t.getSize(rC),a=Math.min(r.x,r.y,r.z);Math.max(r.x,r.y,r.z)<Df*a||this.markBakedShadow(i)})}checkBakedShadows(){let{min:e,max:t}=this.boundingBox,n=new Qt;this.boundingBox.getSize(this.size);for(let i of this.bakedShadows)n.setFromObject(i),!(n.min.y<e.y+this.size.y/Df&&n.min.x<=e.x&&n.max.x>=t.x&&n.min.z<=e.z&&n.max.z>=t.z)&&(n.min.z<e.z+this.size.z/Df&&n.min.x<=e.x&&n.max.x>=t.x&&n.min.y<=e.y&&n.max.y>=t.y||this.unmarkBakedShadow(i))}applyTransform(){let{model:e}=this;if(e==null)return;let t=In(this.element.orientation)[0].terms,n=Cn(t[0]).number,i=Cn(t[1]).number,s=Cn(t[2]).number;e.quaternion.setFromEuler(new Vi(i,s,n,"YXZ"));let r=In(this.element.scale)[0].terms;e.scale.set(r[0].number,r[1].number,r[2].number)}updateBoundingBox(){let{model:e}=this;if(e==null)return;this.target.remove(e),this.findBakedShadows(e);let t=d((n,i)=>n.expandByPoint(i),"bound");this.setBakedShadowVisibility(!1),this.boundingBox=aa(e,t,new Qt),this.boundingBox.isEmpty()&&(this.setBakedShadowVisibility(!0),this.bakedShadows.forEach(n=>this.unmarkBakedShadow(n)),this.boundingBox=aa(e,t,new Qt)),this.checkBakedShadows(),this.setBakedShadowVisibility(),this.boundingBox.getSize(this.size),this.target.add(e)}async updateFraming(){let{model:e}=this;if(e==null)return;this.target.remove(e),this.setBakedShadowVisibility(!1);let{center:t}=this.boundingSphere;this.element.requestUpdate("cameraTarget"),await this.element.updateComplete,t.copy(this.getTarget());let n=d((s,r)=>Math.max(s,t.distanceToSquared(r)),"radiusSquared");this.boundingSphere.radius=Math.sqrt(aa(e,n,0));let i=d((s,r)=>{r.sub(t);let a=Math.sqrt(r.x*r.x+r.z*r.z);return Math.max(s,a/(this.idealCameraDistance()-Math.abs(r.y)))},"horizontalTanFov");this.idealAspect=aa(e,i,0)/Math.tan(this.framedFoVDeg/2*Math.PI/180),this.setBakedShadowVisibility(),this.target.add(e)}setBakedShadowVisibility(e=this.shadowIntensity<=0){for(let t of this.bakedShadows)t.visible=e}idealCameraDistance(){let e=this.framedFoVDeg/2*Math.PI/180;return this.boundingSphere.radius/Math.sin(e)}adjustedFoV(e){let t=Math.tan(e/2*Math.PI/180)*Math.max(1,this.idealAspect/this.aspect);return 2*Math.atan(t)*180/Math.PI}getNDC(e,t){if(this.xrCamera!=null)Da.set(e/self.screen.width,t/self.screen.height);else{let n=this.element.getBoundingClientRect();Da.set((e-n.x)/this.width,(t-n.y)/this.height)}return Da.multiplyScalar(2).subScalar(1),Da.y*=-1,Da}getSize(){return{width:this.width,height:this.height}}setEnvironmentAndSkybox(e,t){this.element[Ne].arRenderer.presentedScene!==this&&(this.environment=e,this.background=t,this.queueRender())}setTarget(e,t,n){this.goalTarget.set(-e,-t,-n)}setTargetDamperDecayTime(e){this.targetDamperX.setDecayTime(e),this.targetDamperY.setDecayTime(e),this.targetDamperZ.setDecayTime(e)}getTarget(){return this.goalTarget.clone().multiplyScalar(-1)}jumpToGoal(){this.updateTarget(1e4)}updateTarget(e){let t=this.goalTarget,n=this.target.position;if(t.equals(n))return!1;{let i=this.boundingSphere.radius/10,{x:s,y:r,z:a}=n;return s=this.targetDamperX.update(s,t.x,e,i),r=this.targetDamperY.update(r,t.y,e,i),a=this.targetDamperZ.update(a,t.z,e,i),this.target.position.set(s,r,a),this.target.updateMatrixWorld(),this.queueRender(),!0}}pointTowards(e,t){let{x:n,z:i}=this.position;this.yaw=Math.atan2(e-n,t-i)}get model(){return this._model}set yaw(e){this.rotation.y=e,this.queueRender()}get yaw(){return this.rotation.y}set animationTime(e){this.mixer.setTime(e),this.queueShadowRender()}get animationTime(){if(this.currentAnimationAction!=null){let e=Math.max(this.currentAnimationAction._loopCount,0);return this.currentAnimationAction.loop===Ko&&(e&1)===1?this.duration-this.currentAnimationAction.time:this.currentAnimationAction.time}return 0}set animationTimeScale(e){this.mixer.timeScale=e}get animationTimeScale(){return this.mixer.timeScale}get duration(){return this.currentAnimationAction!=null&&this.currentAnimationAction.getClip()?this.currentAnimationAction.getClip().duration:0}get hasActiveAnimation(){return this.currentAnimationAction!=null}playAnimation(e=null,t=0,n=qo,i=1/0){if(this._currentGLTF==null)return;let{animations:s}=this;if(s==null||s.length===0){console.warn("Cannot play animation (model does not have any animations)");return}let r=null;if(e!=null&&(r=this.animationsByName.get(e),r==null)){let a=parseInt(e);!isNaN(a)&&a>=0&&a<s.length&&(r=s[a])}r==null&&(r=s[0]);try{let{currentAnimationAction:a}=this,l=this.mixer.clipAction(r,this);this.currentAnimationAction=l,this.element.paused?this.mixer.stopAllAction():(l.paused=!1,a!=null&&l!==a?l.crossFadeFrom(a,t,!1):this.animationTimeScale>0&&this.animationTime==this.duration&&(this.animationTime=0)),l.setLoop(n,i),l.enabled=!0,l.clampWhenFinished=!0,l.play()}catch(a){console.error(a)}}stopAnimation(){this.currentAnimationAction=null,this.mixer.stopAllAction()}updateAnimation(e){this.mixer.update(e),this.queueShadowRender()}subscribeMixerEvent(e,t){this.mixer.addEventListener(e,t)}updateShadow(){let e=this.shadow;if(e!=null){let t=this.element.arPlacement==="wall"?"back":"bottom";e.setScene(this,this.shadowSoftness,t),e.needsUpdate=!0}}renderShadow(e){let t=this.shadow;t!=null&&t.needsUpdate==!0&&(t.render(e,this),t.needsUpdate=!1)}queueShadowRender(){this.shadow!=null&&(this.shadow.needsUpdate=!0)}setShadowIntensity(e){if(this.shadowIntensity=e,this._currentGLTF!=null&&(this.setBakedShadowVisibility(),!(e<=0&&this.shadow==null))){if(this.shadow==null){let t=this.element.arPlacement==="wall"?"back":"bottom";this.shadow=new Jc(this,this.shadowSoftness,t)}this.shadow.setIntensity(e)}}setShadowSoftness(e){this.shadowSoftness=e;let t=this.shadow;t?.setSoftness(e)}setShadowOffset(e){let t=this.shadow;t?.setOffset(e)}get raycaster(){return sC}hitFromPoint(e,t=this){return this.raycaster.setFromCamera(e,this.getCamera()),this.raycaster.intersectObject(t,!0).find(i=>i.object.visible&&!i.object.userData.shadow)}positionAndNormalFromPoint(e,t=this){let n=this.hitFromPoint(e,t);return n==null||n.face==null?null:n.uv==null?{position:n.point,normal:n.face.normal,uv:null}:(n.face.normal.applyNormalMatrix(new wt().getNormalMatrix(n.object.matrixWorld)),{position:n.point,normal:n.face.normal,uv:n.uv})}surfaceFromPoint(e,t=this){let n=this.element.model;if(n==null)return null;let i=this.hitFromPoint(e,t);if(i==null||i.face==null)return null;let s=n[qc](i),{meshes:r,primitives:a}=s.mesh.userData.associations,l=new B,c=new B,h=new B,{a:u,b:f,c:p}=i.face,g=i.object;g.getVertexPosition(u,l),g.getVertexPosition(f,c),g.getVertexPosition(p,h);let A=new Ei(l,c,h),m=new B;return A.getBarycoord(g.worldToLocal(i.point),m),`${r} ${a} ${u} ${f} ${p} ${m.x.toFixed(3)} ${m.y.toFixed(3)} ${m.z.toFixed(3)}`}addHotspot(e){this.target.add(e),this.annotationRenderer.domElement.appendChild(e.element)}removeHotspot(e){this.target.remove(e)}forHotspots(e){let{children:t}=this.target;for(let n=0,i=t.length;n<i;n++){let s=t[n];s instanceof eo&&e(s)}}initializeSurface(e){if(e.surface!=null&&e.mesh==null){let t=In(e.surface)[0].terms;if(t.length!=8){console.warn(e.surface+" does not have exactly 8 numbers.");return}let n=this.element.model[bf](t[0].number,t[1].number),i=new B(t[2].number,t[3].number,t[4].number);if(n==null){console.warn(e.surface+" does not match a node/primitive in this glTF! Skipping this hotspot.");return}let s=n.mesh.geometry.attributes.position.count;if(i.x>=s||i.y>=s||i.z>=s){console.warn(e.surface+" vertex indices out of range in this glTF! Skipping this hotspot.");return}let r=new B(t[5].number,t[6].number,t[7].number);e.mesh=n.mesh,e.tri=i,e.bary=r}}updateSurfaceHotspots(){let e=!this.element.paused;this.forHotspots(t=>{this.initializeSurface(t),t.updateSurface(e)})}updateHotspotsVisibility(e){this.forHotspots(t=>{Lf.copy(e),$0.setFromMatrixPosition(t.matrixWorld),Lf.sub($0),X0.copy(t.normal).transformDirection(this.target.matrixWorld),Lf.dot(X0)<0?t.hide():t.show()})}orientHotspots(e){this.forHotspots(t=>{t.orient(e)})}setHotspotsVisibility(e){this.forHotspots(t=>{t.visible=e})}updateSchema(e){var t;let{schemaElement:n,element:i}=this,{alt:s,poster:r,iosSrc:a}=i;if(e!=null){let l=[{"@type":"MediaObject",contentUrl:e,encodingFormat:((t=e.split(".").pop())===null||t===void 0?void 0:t.toLowerCase())==="gltf"?"model/gltf+json":"model/gltf-binary"}];a&&l.push({"@type":"MediaObject",contentUrl:a,encodingFormat:"model/vnd.usdz+zip"});let c={"@context":"http://schema.org/","@type":"3DModel",image:r??void 0,name:s??void 0,encoding:l};n.textContent=JSON.stringify(c),document.head.appendChild(n)}else n.parentElement!=null&&n.parentElement.removeChild(n)}};L();P();var Y0=d(async o=>new Promise((e,t)=>{let i=o.match(/data:(.*);/);if(!i)return t(new Error(`${o} is not a valid data Url`));let s=i[1],r=o.replace(/data:image\/\w+;base64,/,""),a=atob(r),l=[];for(let c=0;c<a.length;c+=512){let h=a.slice(c,c+512),u=new Array(h.length);for(let p=0;p<h.length;p++)u[p]=h.charCodeAt(p);let f=new Uint8Array(u);l.push(f)}e(new Blob(l,{type:s}))}),"dataUrlToBlob");L();P();var Zc=class extends EventTarget{static{d(this,"ProgressTracker")}constructor(){super(...arguments),this.ongoingActivities=new Set,this.totalProgress=0}get ongoingActivityCount(){return this.ongoingActivities.size}beginActivity(){let e={progress:0,completed:!1};return this.ongoingActivities.add(e),this.ongoingActivityCount===1&&this.announceTotalProgress(e,0),t=>{let n;return n=Math.max(Jt(t,0,1),e.progress),n!==e.progress&&this.announceTotalProgress(e,n),e.progress}}announceTotalProgress(e,t){let n=0,i=0;t==1&&(e.completed=!0);for(let a of this.ongoingActivities){let{progress:l}=a;n+=1-l,a.completed===!0&&i++}let s=e.progress;e.progress=t,this.totalProgress+=(t-s)*(1-this.totalProgress)/n;let r=i===this.ongoingActivityCount?1:this.totalProgress;this.dispatchEvent(new CustomEvent("progress",{detail:{totalProgress:r}})),i===this.ongoingActivityCount&&(this.totalProgress=0,this.ongoingActivities.clear())}};var ih=function(o,e,t,n){var i=arguments.length,s=i<3?e:n===null?n=Object.getOwnPropertyDescriptor(e,t):n,r;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")s=Reflect.decorate(o,e,t,n);else for(var a=o.length-1;a>=0;a--)(r=o[a])&&(s=(i<3?r(s):i>3?r(e,t,s):r(e,t))||s);return i>3&&s&&Object.defineProperty(e,t,s),s},J0,j0,Z0,e_,t_,n_,i_,s_,r_,o_,a_,l_,c_,oC=10,aC=50,lC=0,cC=300,hC=150,Sn=document.createElement("canvas"),Pf=Symbol("fallbackResizeHandler"),h_=Symbol("defaultAriaLabel"),eh=Symbol("resizeObserver"),to=Symbol("clearModelTimeout"),Ff=Symbol("onContextLost"),no=Symbol("loaded"),Of=Symbol("status"),Nf=Symbol("onFocus"),Uf=Symbol("onBlur"),Ts=Symbol("updateSize"),th=Symbol("intersectionObserver"),os=Symbol("isElementInViewport"),Pa=Symbol("announceModelVisibility"),Vr=Symbol("ariaLabel"),nh=Symbol("altDefaulted"),La=Symbol("statusElement"),Cc=Symbol("updateStatus"),Wr=Symbol("loadedTime"),as=Symbol("updateSource"),u_=Symbol("markLoaded"),Hr=Symbol("container"),Qn=Symbol("input"),Uc=Symbol("canvas"),oe=Symbol("scene"),_t=Symbol("needsRender"),on=Symbol("tick"),Zn=Symbol("onModelLoad"),Ss=Symbol("onResize"),Ne=Symbol("renderer"),Jn=Symbol("progressTracker"),d_=Symbol("getLoaded"),ei=Symbol("getModelIsVisible"),Mi=Symbol("shouldAttemptPreload"),ti=d(o=>({x:o.x,y:o.y,z:o.z,toString(){return`${this.x}m ${this.y}m ${this.z}m`}}),"toVector3D"),f_=d(o=>({u:o.x,v:o.y,toString(){return`${this.u} ${this.v}`}}),"toVector2D"),Di=class extends Yn{static{d(this,"ModelViewerElementBase")}constructor(){super(),this.alt=null,this.src=null,this.withCredentials=!1,this.generateSchema=!1,this[J0]=!1,this[j0]=!1,this[Z0]=0,this[e_]="",this[t_]=null,this[n_]=Yu(()=>{let i=this.getBoundingClientRect();this[Ts](i)},aC),this[i_]=Yu(i=>{let s=this.modelIsVisible;s!==i&&this.dispatchEvent(new CustomEvent("model-visibility",{detail:{visible:s}}))},lC),this[s_]=null,this[r_]=null,this[o_]=new Zc,this[a_]=()=>{this[La].textContent=this[Of]},this[l_]=()=>{this[La].textContent=""},this[c_]=i=>{this.dispatchEvent(new CustomEvent("error",{detail:{type:"webglcontextlost",sourceError:i.sourceEvent}}))},this.attachShadow({mode:"open"});let e=this.shadowRoot;Tm(e),this[Hr]=e.querySelector(".container"),this[Qn]=e.querySelector(".userInput"),this[Uc]=e.querySelector("canvas"),this[La]=e.querySelector("#status"),this[h_]=this[Qn].getAttribute("aria-label");let t,n;if(this.isConnected){let i=this.getBoundingClientRect();t=i.width,n=i.height}else t=cC,n=hC;this[oe]=new jc({canvas:this[Uc],element:this,width:t,height:n}),Promise.resolve().then(()=>{this[Ts](this.getBoundingClientRect())}),jl&&(this[eh]=new ResizeObserver(i=>{if(!this[Ne].isPresenting)for(let s of i)s.target===this&&this[Ts](s.contentRect)})),Zl?this[th]=new IntersectionObserver(i=>{for(let s of i)if(s.target===this){let r=this.modelIsVisible;this[os]=s.isIntersecting,this[Pa](r),this[os]&&!this.loaded&&this[as]()}},{root:null,rootMargin:"0px",threshold:1e-5}):this[os]=!0}static get is(){return"model-viewer"}static set modelCacheSize(e){pt[Si].evictionThreshold=e}static get modelCacheSize(){return pt[Si].evictionThreshold}static set minimumRenderScale(e){e>1&&console.warn("<model-viewer> minimumRenderScale has been clamped to a maximum value of 1."),e<=0&&console.warn("<model-viewer> minimumRenderScale has been clamped to a minimum value of 0.25."),an.singleton.minScale=e}static get minimumRenderScale(){return an.singleton.minScale}get loaded(){return this[d_]()}get[(J0=os,j0=no,Z0=Wr,e_=Of,t_=to,n_=Pf,i_=Pa,s_=eh,r_=th,o_=Jn,Ne)](){return an.singleton}get modelIsVisible(){return this[ei]()}connectedCallback(){super.connectedCallback&&super.connectedCallback(),jl?this[eh].observe(this):self.addEventListener("resize",this[Pf]),Zl&&this[th].observe(this),this.addEventListener("focus",this[Nf]),this.addEventListener("blur",this[Uf]);let e=this[Ne];e.addEventListener("contextlost",this[Ff]),e.registerScene(this[oe]),this[to]!=null&&(self.clearTimeout(this[to]),this[to]=null,this.requestUpdate("src",null))}disconnectedCallback(){super.disconnectedCallback&&super.disconnectedCallback(),jl?this[eh].unobserve(this):self.removeEventListener("resize",this[Pf]),Zl&&this[th].unobserve(this),this.removeEventListener("focus",this[Nf]),this.removeEventListener("blur",this[Uf]);let e=this[Ne];e.removeEventListener("contextlost",this[Ff]),e.unregisterScene(this[oe]),this[to]=self.setTimeout(()=>{this[oe].dispose(),this[to]=null},oC)}updated(e){super.updated(e),e.has("src")&&(this.src==null?(this[no]=!1,this[Wr]=0,this[oe].reset()):this.src!==this[oe].url&&(this[no]=!1,this[Wr]=0,this[as]())),e.has("alt")&&this[Qn].setAttribute("aria-label",this[Vr]),e.has("withCredentials")&&(pt.withCredentials=this.withCredentials,this[Ne].textureUtils.withCredentials=this.withCredentials),e.has("generateSchema")&&(this.generateSchema?this[oe].updateSchema(this.src):this[oe].updateSchema(null))}toDataURL(e,t){return this[Ne].displayCanvas(this[oe]).toDataURL(e,t)}async toBlob(e){let t=e?e.mimeType:void 0,n=e?e.qualityArgument:void 0,i=e?e.idealAspect:void 0,{width:s,height:r,idealAspect:a,aspect:l}=this[oe],{dpr:c,scaleFactor:h}=this[Ne],u=s*h*c,f=r*h*c,p=0,g=0;if(i===!0)if(a>l){let A=f;f=Math.round(u/a),g=(A-f)/2}else{let A=u;u=Math.round(f*a),p=(A-u)/2}Sn.width=u,Sn.height=f;try{return new Promise(async(A,m)=>{if(Sn.getContext("2d").drawImage(this[Ne].displayCanvas(this[oe]),p,g,u,f,0,0,u,f),Sn.msToBlob&&(!t||t==="image/png"))return A(Sn.msToBlob());if(!Sn.toBlob)return A(await Y0(Sn.toDataURL(t,n)));Sn.toBlob(_=>{if(!_)return m(new Error("Unable to retrieve canvas blob"));A(_)},t,n)})}finally{this[Ts]({width:s,height:r})}}registerRenderer(e){this[oe].externalRenderer=e}unregisterRenderer(){this[oe].externalRenderer=null}get[Vr](){return this[nh]}get[nh](){return this.alt==null||this.alt==="null"?this[h_]:this.alt}[d_](){return this[no]}[ei](){return this.loaded&&this[os]}[Mi](){return!!this.src&&this[os]}[Ts]({width:e,height:t}){e===0||t===0||(this[Hr].style.width=`${e}px`,this[Hr].style.height=`${t}px`,this[Ss]({width:e,height:t}))}[on](e,t){}[u_](){this[no]||(this[no]=!0,this[Wr]=performance.now())}[_t](){this[oe].queueRender()}[Zn](){}[Cc](e){this[Of]=e;let t=this.getRootNode();t!=null&&t.activeElement===this&&this[La].textContent!=e&&(this[La].textContent=e)}[(a_=Nf,l_=Uf,Ss)](e){this[oe].setSize(e.width,e.height)}async[(c_=Ff,as)](){let e=this[oe];if(this.loaded||!this[Mi]()||this.src===e.url)return;this.generateSchema&&e.updateSchema(this.src),this[Cc]("Loading"),e.stopAnimation();let t=this[Jn].beginActivity(),n=this.src;try{let i=e.setSource(n,r=>t(Jt(r,0,1)*.95)),s=this[Rr]();await Promise.all([i,s]),this[u_](),this[Zn](),await new Promise(r=>{requestAnimationFrame(()=>{requestAnimationFrame(()=>{this.dispatchEvent(new CustomEvent("load",{detail:{url:n}})),r()})})})}catch(i){this.dispatchEvent(new CustomEvent("error",{detail:{type:"loadfailure",sourceError:i}}))}finally{t(1)}}};ih([ye({type:String})],Di.prototype,"alt",void 0);ih([ye({type:String})],Di.prototype,"src",void 0);ih([ye({type:Boolean,attribute:"with-credentials"})],Di.prototype,"withCredentials",void 0);ih([ye({type:Boolean,attribute:"generate-schema"})],Di.prototype,"generateSchema",void 0);var Qf=function(o,e,t,n){var i=arguments.length,s=i<3?e:n===null?n=Object.getOwnPropertyDescriptor(e,t):n,r;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")s=Reflect.decorate(o,e,t,n);else for(var a=o.length-1;a>=0;a--)(r=o[a])&&(s=(i<3?r(s):i>3?r(e,t,s):r(e,t))||s);return i>3&&s&&Object.defineProperty(e,t,s),s},p_=1e3,kf=Symbol("changeAnimation"),Li=Symbol("paused"),uC={repetitions:1/0,pingpong:!1},A_=d(o=>{var e;class t extends o{static{d(this,"AnimationModelViewerElement")}constructor(...i){super(i),this.autoplay=!1,this.animationName=void 0,this.animationCrossfadeDuration=300,this[e]=!0,this[oe].subscribeMixerEvent("loop",s=>{let r=s.action._loopCount;this.dispatchEvent(new CustomEvent("loop",{detail:{count:r}}))}),this[oe].subscribeMixerEvent("finished",()=>{this[Li]=!0,this.dispatchEvent(new CustomEvent("finished"))})}get availableAnimations(){return this.loaded?this[oe].animationNames:[]}get duration(){return this[oe].duration}get paused(){return this[Li]}get currentTime(){return this[oe].animationTime}set currentTime(i){this[oe].animationTime=i,this[_t]()}get timeScale(){return this[oe].animationTimeScale}set timeScale(i){this[oe].animationTimeScale=i}pause(){this[Li]||(this[Li]=!0,this.dispatchEvent(new CustomEvent("pause")))}play(i){this.availableAnimations.length>0&&(this[Li]=!1,this[kf](i),this.dispatchEvent(new CustomEvent("play")))}[(e=Li,Zn)](){super[Zn](),this[Li]=!0,this.autoplay&&this.play()}[on](i,s){super[on](i,s),!(this[Li]||!this[ei]()&&!this[Ne].isPresenting)&&(this[oe].updateAnimation(s/p_),this[_t]())}updated(i){super.updated(i),i.has("autoplay")&&this.autoplay&&this.play(),i.has("animationName")&&this[kf]()}[kf](i=uC){var s;let r=(s=i.repetitions)!==null&&s!==void 0?s:1/0,a=i.pingpong?Ko:r===1?Cu:qo;this[oe].playAnimation(this.animationName,this.animationCrossfadeDuration/p_,a,r),this[Li]&&(this[oe].updateAnimation(0),this[_t]())}}return Qf([ye({type:Boolean})],t.prototype,"autoplay",void 0),Qf([ye({type:String,attribute:"animation-name"})],t.prototype,"animationName",void 0),Qf([ye({type:Number,attribute:"animation-crossfade-duration"})],t.prototype,"animationCrossfadeDuration",void 0),t},"AnimationMixin");L();P();var Ls=Symbol("hotspotMap"),Gf=Symbol("mutationCallback"),Fa=Symbol("observer"),zf=Symbol("addHotspot"),m_=Symbol("removeHotspot"),Vf=new Ie,g_=d(o=>{var e,t,n;class i extends o{static{d(this,"AnnotationModelViewerElement")}constructor(){super(...arguments),this[e]=new Map,this[t]=r=>{r.forEach(a=>{(!(a instanceof MutationRecord)||a.type==="childList")&&(a.addedNodes.forEach(l=>{this[zf](l)}),a.removedNodes.forEach(l=>{this[m_](l)}),this[_t]())})},this[n]=new MutationObserver(this[Gf])}connectedCallback(){super.connectedCallback();for(let a=0;a<this.children.length;++a)this[zf](this.children[a]);let{ShadyDOM:r}=self;r==null?this[Fa].observe(this,{childList:!0}):this[Fa]=r.observeChildren(this,this[Gf])}disconnectedCallback(){super.disconnectedCallback();let{ShadyDOM:r}=self;r==null?this[Fa].disconnect():r.unobserveChildren(this[Fa])}[(e=Ls,t=Gf,n=Fa,on)](r,a){super[on](r,a);let l=this[oe],{annotationRenderer:c}=l,h=l.getCamera();l.shouldRender()&&(l.updateSurfaceHotspots(),l.updateHotspotsVisibility(h.position),c.domElement.style.display="",c.render(l,h))}updateHotspot(r){let a=this[Ls].get(r.name);a!=null&&(a.updatePosition(r.position),a.updateNormal(r.normal),this[_t]())}queryHotspot(r){let a=this[Ls].get(r);if(a==null)return null;let l=ti(a.position),c=ti(a.normal),h=a.facingCamera,u=this[oe],f=u.getCamera(),p=new B;p.setFromMatrixPosition(a.matrixWorld),p.project(f);let g=u.width/2,A=u.height/2;p.x=p.x*g+g,p.y=-(p.y*A)+A;let m=ti(new B(p.x,p.y,p.z));return!Number.isFinite(m.x)||!Number.isFinite(m.y)?null:{position:l,normal:c,canvasPosition:m,facingCamera:h}}positionAndNormalFromPoint(r,a){let l=this[oe],c=l.getNDC(r,a),h=l.positionAndNormalFromPoint(c);if(h==null)return null;Vf.copy(l.target.matrixWorld).invert();let u=ti(h.position.applyMatrix4(Vf)),f=ti(h.normal.transformDirection(Vf)),p=null;return h.uv!=null&&(p=f_(h.uv)),{position:u,normal:f,uv:p}}surfaceFromPoint(r,a){let l=this[oe],c=l.getNDC(r,a);return l.surfaceFromPoint(c)}[zf](r){if(!(r instanceof HTMLElement&&r.slot.indexOf("hotspot")===0))return;let a=this[Ls].get(r.slot);a!=null?a.increment():(a=new eo({name:r.slot,position:r.dataset.position,normal:r.dataset.normal,surface:r.dataset.surface}),this[Ls].set(r.slot,a),this[oe].addHotspot(a)),this[oe].queueRender()}[m_](r){if(!(r instanceof HTMLElement))return;let a=this[Ls].get(r.slot);a&&(a.decrement()&&(this[oe].removeHotspot(a),this[Ls].delete(r.slot)),this[oe].queueRender())}}return i},"AnnotationMixin");L();P();L();P();L();P();var __=d(function(o){return URL.createObjectURL(new Blob([o],{type:"text/javascript"}))},"durl"),dC=d(function(o){return new Worker(o)},"cwk");try{URL.revokeObjectURL(__(""))}catch{__=d(function(e){return"data:application/javascript;charset=UTF-8,"+encodeURI(e)},"durl"),dC=d(function(e){return new Worker(e,{type:"module"})},"cwk")}var hn=Uint8Array,cn=Uint16Array,io=Uint32Array,Xf=new hn([0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,0,0,0,0]),Yf=new hn([0,0,0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,13,13,0,0]),y_=new hn([16,17,18,0,8,7,9,6,10,5,11,4,12,3,13,2,14,1,15]),b_=d(function(o,e){for(var t=new cn(31),n=0;n<31;++n)t[n]=e+=1<<o[n-1];for(var i=new io(t[30]),n=1;n<30;++n)for(var s=t[n];s<t[n+1];++s)i[s]=s-t[n]<<5|n;return[t,i]},"freb"),I_=b_(Xf,2),fC=I_[0],Wf=I_[1];fC[28]=258,Wf[258]=28;var C_=b_(Yf,0),IP=C_[0],x_=C_[1],qf=new cn(32768);for(qe=0;qe<32768;++qe)Pi=(qe&43690)>>>1|(qe&21845)<<1,Pi=(Pi&52428)>>>2|(Pi&13107)<<2,Pi=(Pi&61680)>>>4|(Pi&3855)<<4,qf[qe]=((Pi&65280)>>>8|(Pi&255)<<8)>>>1;var Pi,qe,Ua=d(function(o,e,t){for(var n=o.length,i=0,s=new cn(e);i<n;++i)++s[o[i]-1];var r=new cn(e);for(i=0;i<e;++i)r[i]=r[i-1]+s[i-1]<<1;var a;if(t){a=new cn(1<<e);var l=15-e;for(i=0;i<n;++i)if(o[i])for(var c=i<<4|o[i],h=e-o[i],u=r[o[i]-1]++<<h,f=u|(1<<h)-1;u<=f;++u)a[qf[u]>>>l]=c}else for(a=new cn(n),i=0;i<n;++i)o[i]&&(a[i]=qf[r[o[i]-1]++]>>>15-o[i]);return a},"hMap"),Ps=new hn(288);for(qe=0;qe<144;++qe)Ps[qe]=8;var qe;for(qe=144;qe<256;++qe)Ps[qe]=9;var qe;for(qe=256;qe<280;++qe)Ps[qe]=7;var qe;for(qe=280;qe<288;++qe)Ps[qe]=8;var qe,rh=new hn(32);for(qe=0;qe<32;++qe)rh[qe]=5;var qe,pC=Ua(Ps,9,0);var AC=Ua(rh,5,0);var S_=d(function(o){return(o/8|0)+(o&7&&1)},"shft"),T_=d(function(o,e,t){(e==null||e<0)&&(e=0),(t==null||t>o.length)&&(t=o.length);var n=new(o instanceof cn?cn:o instanceof io?io:hn)(t-e);return n.set(o.subarray(e,t)),n},"slc");var Fi=d(function(o,e,t){t<<=e&7;var n=e/8|0;o[n]|=t,o[n+1]|=t>>>8},"wbits"),Oa=d(function(o,e,t){t<<=e&7;var n=e/8|0;o[n]|=t,o[n+1]|=t>>>8,o[n+2]|=t>>>16},"wbits16"),Hf=d(function(o,e){for(var t=[],n=0;n<o.length;++n)o[n]&&t.push({s:n,f:o[n]});var i=t.length,s=t.slice();if(!i)return[Jf,0];if(i==1){var r=new hn(t[0].s+1);return r[t[0].s]=1,[r,1]}t.sort(function(w,I){return w.f-I.f}),t.push({s:-1,f:25001});var a=t[0],l=t[1],c=0,h=1,u=2;for(t[0]={s:-1,f:a.f+l.f,l:a,r:l};h!=i-1;)a=t[t[c].f<t[u].f?c++:u++],l=t[c!=h&&t[c].f<t[u].f?c++:u++],t[h++]={s:-1,f:a.f+l.f,l:a,r:l};for(var f=s[0].s,n=1;n<i;++n)s[n].s>f&&(f=s[n].s);var p=new cn(f+1),g=Kf(t[h-1],p,0);if(g>e){var n=0,A=0,m=g-e,_=1<<m;for(s.sort(function(I,S){return p[S.s]-p[I.s]||I.f-S.f});n<i;++n){var E=s[n].s;if(p[E]>e)A+=_-(1<<g-p[E]),p[E]=e;else break}for(A>>>=m;A>0;){var x=s[n].s;p[x]<e?A-=1<<e-p[x]++-1:++n}for(;n>=0&&A;--n){var y=s[n].s;p[y]==e&&(--p[y],++A)}g=e}return[new hn(p),g]},"hTree"),Kf=d(function(o,e,t){return o.s==-1?Math.max(Kf(o.l,e,t+1),Kf(o.r,e,t+1)):e[o.s]=t},"ln"),v_=d(function(o){for(var e=o.length;e&&!o[--e];);for(var t=new cn(++e),n=0,i=o[0],s=1,r=d(function(l){t[n++]=l},"w"),a=1;a<=e;++a)if(o[a]==i&&a!=e)++s;else{if(!i&&s>2){for(;s>138;s-=138)r(32754);s>2&&(r(s>10?s-11<<5|28690:s-3<<5|12305),s=0)}else if(s>3){for(r(i),--s;s>6;s-=6)r(8304);s>2&&(r(s-3<<5|8208),s=0)}for(;s--;)r(i);s=1,i=o[a]}return[t.subarray(0,n),e]},"lc"),Na=d(function(o,e){for(var t=0,n=0;n<e.length;++n)t+=o[n]*e[n];return t},"clen"),sh=d(function(o,e,t){var n=t.length,i=S_(e+2);o[i]=n&255,o[i+1]=n>>>8,o[i+2]=o[i]^255,o[i+3]=o[i+1]^255;for(var s=0;s<n;++s)o[i+s+4]=t[s];return(i+4+n)*8},"wfblk"),E_=d(function(o,e,t,n,i,s,r,a,l,c,h){Fi(e,h++,t),++i[256];for(var u=Hf(i,15),f=u[0],p=u[1],g=Hf(s,15),A=g[0],m=g[1],_=v_(f),E=_[0],x=_[1],y=v_(A),w=y[0],I=y[1],S=new cn(19),v=0;v<E.length;++v)S[E[v]&31]++;for(var v=0;v<w.length;++v)S[w[v]&31]++;for(var b=Hf(S,7),R=b[0],N=b[1],z=19;z>4&&!R[y_[z-1]];--z);var O=c+5<<3,D=Na(i,Ps)+Na(s,rh)+r,Q=Na(i,f)+Na(s,A)+r+14+3*z+Na(S,R)+(2*S[16]+3*S[17]+7*S[18]);if(O<=D&&O<=Q)return sh(e,h,o.subarray(l,l+c));var q,H,k,j;if(Fi(e,h,1+(Q<D)),h+=2,Q<D){q=Ua(f,p,0),H=f,k=Ua(A,m,0),j=A;var Z=Ua(R,N,0);Fi(e,h,x-257),Fi(e,h+5,I-1),Fi(e,h+10,z-4),h+=14;for(var v=0;v<z;++v)Fi(e,h+3*v,R[y_[v]]);h+=3*z;for(var fe=[E,w],V=0;V<2;++V)for(var ee=fe[V],v=0;v<ee.length;++v){var re=ee[v]&31;Fi(e,h,Z[re]),h+=R[re],re>15&&(Fi(e,h,ee[v]>>>5&127),h+=ee[v]>>>12)}}else q=pC,H=Ps,k=AC,j=rh;for(var v=0;v<a;++v)if(n[v]>255){var re=n[v]>>>18&31;Oa(e,h,q[re+257]),h+=H[re+257],re>7&&(Fi(e,h,n[v]>>>23&31),h+=Xf[re]);var ie=n[v]&31;Oa(e,h,k[ie]),h+=j[ie],ie>3&&(Oa(e,h,n[v]>>>5&8191),h+=Yf[ie])}else Oa(e,h,q[n[v]]),h+=H[n[v]];return Oa(e,h,q[256]),h+H[256]},"wblk"),mC=new io([65540,131080,131088,131104,262176,1048704,1048832,2114560,2117632]),Jf=new hn(0),gC=d(function(o,e,t,n,i,s){var r=o.length,a=new hn(n+r+5*(1+Math.ceil(r/7e3))+i),l=a.subarray(n,a.length-i),c=0;if(!e||r<8)for(var h=0;h<=r;h+=65535){var u=h+65535;u<r?c=sh(l,c,o.subarray(h,u)):(l[h]=s,c=sh(l,c,o.subarray(h,r)))}else{for(var f=mC[e-1],p=f>>>13,g=f&8191,A=(1<<t)-1,m=new cn(32768),_=new cn(A+1),E=Math.ceil(t/3),x=2*E,y=d(function(yt){return(o[yt]^o[yt+1]<<E^o[yt+2]<<x)&A},"hsh"),w=new io(25e3),I=new cn(288),S=new cn(32),v=0,b=0,h=0,R=0,N=0,z=0;h<r;++h){var O=y(h),D=h&32767,Q=_[O];if(m[D]=Q,_[O]=D,N<=h){var q=r-h;if((v>7e3||R>24576)&&q>423){c=E_(o,l,0,w,I,S,b,R,z,h-z,c),R=v=b=0,z=h;for(var H=0;H<286;++H)I[H]=0;for(var H=0;H<30;++H)S[H]=0}var k=2,j=0,Z=g,fe=D-Q&32767;if(q>2&&O==y(h-fe))for(var V=Math.min(p,q)-1,ee=Math.min(32767,h),re=Math.min(258,q);fe<=ee&&--Z&&D!=Q;){if(o[h+k]==o[h+k-fe]){for(var ie=0;ie<re&&o[h+ie]==o[h+ie-fe];++ie);if(ie>k){if(k=ie,j=fe,ie>V)break;for(var W=Math.min(fe,ie-2),Te=0,H=0;H<W;++H){var Ae=h-fe+H+32768&32767,ge=m[Ae],ce=Ae-ge+32768&32767;ce>Te&&(Te=ce,Q=Ae)}}}D=Q,Q=m[D],fe+=D-Q+32768&32767}if(j){w[R++]=268435456|Wf[k]<<18|x_[j];var $e=Wf[k]&31,Le=x_[j]&31;b+=Xf[$e]+Yf[Le],++I[257+$e],++S[Le],N=h+k,++v}else w[R++]=o[h],++I[o[h]]}}c=E_(o,l,s,w,I,S,b,R,z,h-z,c),!s&&c&7&&(c=sh(l,c+1,Jf))}return T_(a,0,n+S_(c)+i)},"dflt"),_C=function(){for(var o=new io(256),e=0;e<256;++e){for(var t=e,n=9;--n;)t=(t&1&&3988292384)^t>>>1;o[e]=t}return o}(),yC=d(function(){var o=-1;return{p:d(function(e){for(var t=o,n=0;n<e.length;++n)t=_C[t&255^e[n]]^t>>>8;o=t},"p"),d:d(function(){return~o},"d")}},"crc");var xC=d(function(o,e,t,n,i){return gC(o,e.level==null?6:e.level,e.mem==null?Math.ceil(Math.max(8,Math.min(13,Math.log(o.length)))*1.5):12+e.mem,t,n,!i)},"dopt"),B_=d(function(o,e){var t={};for(var n in o)t[n]=o[n];for(var n in e)t[n]=e[n];return t},"mrg");var Vt=d(function(o,e,t){for(;t;++e)o[e]=t,t>>>=8},"wbytes");function vC(o,e){return xC(o,e||{},0,0)}d(vC,"deflateSync");var R_=d(function(o,e,t,n){for(var i in o){var s=o[i],r=e+i;s instanceof hn?t[r]=[s,n]:Array.isArray(s)?t[r]=[s[0],B_(n,s[1])]:R_(s,r+"/",t,n)}},"fltn"),w_=typeof TextEncoder<"u"&&new TextEncoder,EC=typeof TextDecoder<"u"&&new TextDecoder,wC=0;try{EC.decode(Jf,{stream:!0}),wC=1}catch{}function Qa(o,e){if(e){for(var t=new hn(o.length),n=0;n<o.length;++n)t[n]=o.charCodeAt(n);return t}if(w_)return w_.encode(o);for(var i=o.length,s=new hn(o.length+(o.length>>1)),r=0,a=d(function(h){s[r++]=h},"w"),n=0;n<i;++n){if(r+5>s.length){var l=new hn(r+8+(i-n<<1));l.set(s),s=l}var c=o.charCodeAt(n);c<128||e?a(c):c<2048?(a(192|c>>6),a(128|c&63)):c>55295&&c<57344?(c=65536+(c&1047552)|o.charCodeAt(++n)&1023,a(240|c>>18),a(128|c>>12&63),a(128|c>>6&63),a(128|c&63)):(a(224|c>>12),a(128|c>>6&63),a(128|c&63))}return T_(s,0,r)}d(Qa,"strToU8");var $f=d(function(o){var e=0;if(o)for(var t in o){var n=o[t].length;if(n>65535)throw"extra field too long";e+=n+4}return e},"exfl"),M_=d(function(o,e,t,n,i,s,r,a){var l=n.length,c=t.extra,h=a&&a.length,u=$f(c);Vt(o,e,r!=null?33639248:67324752),e+=4,r!=null&&(o[e++]=20,o[e++]=t.os),o[e]=20,e+=2,o[e++]=t.flag<<1|(s==null&&8),o[e++]=i&&8,o[e++]=t.compression&255,o[e++]=t.compression>>8;var f=new Date(t.mtime==null?Date.now():t.mtime),p=f.getFullYear()-1980;if(p<0||p>119)throw"date not in range 1980-2099";if(Vt(o,e,p<<25|f.getMonth()+1<<21|f.getDate()<<16|f.getHours()<<11|f.getMinutes()<<5|f.getSeconds()>>>1),e+=4,s!=null&&(Vt(o,e,t.crc),Vt(o,e+4,s),Vt(o,e+8,t.size)),Vt(o,e+12,l),Vt(o,e+14,u),e+=16,r!=null&&(Vt(o,e,h),Vt(o,e+6,t.attrs),Vt(o,e+10,r),e+=14),o.set(n,e),e+=l,u)for(var g in c){var A=c[g],m=A.length;Vt(o,e,+g),Vt(o,e+2,m),o.set(A,e+4),e+=4+m}return h&&(o.set(a,e),e+=h),e},"wzh"),MC=d(function(o,e,t,n,i){Vt(o,e,101010256),Vt(o,e+8,t),Vt(o,e+10,t),Vt(o,e+12,n),Vt(o,e+16,i)},"wzf");function D_(o,e){e||(e={});var t={},n=[];R_(o,"",t,e);var i=0,s=0;for(var r in t){var a=t[r],l=a[0],c=a[1],h=c.level==0?0:8,u=Qa(r),f=u.length,p=c.comment,g=p&&Qa(p),A=g&&g.length,m=$f(c.extra);if(f>65535)throw"filename too long";var _=h?vC(l,c):l,E=_.length,x=yC();x.p(l),n.push(B_(c,{size:l.length,crc:x.d(),c:_,f:u,m:g,u:f!=r.length||g&&p.length!=A,o:i,compression:h})),i+=30+f+m+E,s+=76+2*(f+m)+(A||0)+E}for(var y=new hn(s+22),w=i,I=s-i,S=0;S<n.length;++S){var u=n[S];M_(y,u.o,u,u.f,u.u,u.c.length);var v=30+u.f.length+$f(u.extra);y.set(u.c,u.o+v),M_(y,i,u,u.f,u.u,u.c.length,u.o,u.m),i+=16+v+(u.m?u.m.length:0)}return MC(y,i,n.length,I,w),y}d(D_,"zipSync");var ah=class{static{d(this,"USDZExporter")}async parse(e,t={}){t=Object.assign({ar:{anchoring:{type:"plane"},planeAnchoring:{alignment:"horizontal"}}},t);let n={},i="model.usda";n[i]=null;let s=O_();s+=CC(t);let r={},a={};e.traverseVisible(c=>{if(c.isMesh){let h=c.geometry,u=c.material;if(u.isMeshStandardMaterial){let f="geometries/Geometry_"+h.id+".usd";if(!(f in n)){let p=RC(h);n[f]=TC(p)}u.uuid in r||(r[u.uuid]=u),s+=BC(c,h,u)}else console.warn("THREE.USDZExporter: Unsupported material type (USDZ only supports MeshStandardMaterial)",c)}else c.isCamera&&(s+=UC(c))}),s+=SC(),s+=OC(r,a),n[i]=Qa(s),s=null;for(let c in a){let h=a[c],u=c.split("_")[1],f=h.format===1023,p=IC(h.image,u),g=await new Promise(A=>p.toBlob(A,f?"image/png":"image/jpeg",1));n[`textures/Texture_${c}.${f?"png":"jpg"}`]=new Uint8Array(await g.arrayBuffer())}let l=0;for(let c in n){let h=n[c],u=34+c.length;l+=u;let f=l&63;if(f!==4){let p=64-f,g=new Uint8Array(p);n[c]=[h,{extra:{12345:g}}]}l=h.length}return D_(n,{level:0})}};function IC(o,e){if(typeof HTMLImageElement<"u"&&o instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&o instanceof HTMLCanvasElement||typeof OffscreenCanvas<"u"&&o instanceof OffscreenCanvas||typeof ImageBitmap<"u"&&o instanceof ImageBitmap){let t=1024/Math.max(o.width,o.height),n=document.createElement("canvas");n.width=o.width*Math.min(1,t),n.height=o.height*Math.min(1,t);let i=n.getContext("2d");if(i.drawImage(o,0,0,n.width,n.height),e!==void 0){let s=parseInt(e,16),r=(s>>16&255)/255,a=(s>>8&255)/255,l=(s&255)/255,c=i.getImageData(0,0,n.width,n.height),h=c.data;for(let u=0;u<h.length;u+=4)h[u+0]=h[u+0]*r,h[u+1]=h[u+1]*a,h[u+2]=h[u+2]*l;i.putImageData(c,0,0)}return n}else throw new Error("THREE.USDZExporter: No valid image data found. Unable to process texture.")}d(IC,"imageToCanvas");var un=7;function O_(){return`#usda 1.0
(
    customLayerData = {
        string creator = "Three.js USDZExporter"
    }
    metersPerUnit = 1
    upAxis = "Y"
)

`}d(O_,"buildHeader");function CC(o){return`def Xform "Root"
{
    def Scope "Scenes" (
        kind = "sceneLibrary"
    )
    {
        def Xform "Scene" (
            customData = {
                bool preliminary_collidesWithEnvironment = 0
                string sceneName = "Scene"
            }
            sceneName = "Scene"
        )
        {
        token preliminary:anchoring:type = "${o.ar.anchoring.type}"
        token preliminary:planeAnchoring:alignment = "${o.ar.planeAnchoring.alignment}"

`}d(CC,"buildSceneStart");function SC(){return`
        }
    }
}

`}d(SC,"buildSceneEnd");function TC(o){let e=O_();return e+=o,Qa(e)}d(TC,"buildUSDFileAsString");function BC(o,e,t){let n="Object_"+o.id,i=N_(o.matrixWorld);return o.matrixWorld.determinant()<0&&console.warn("THREE.USDZExporter: USDZ does not support negative scales",o),`def Xform "${n}" (
    prepend references = @./geometries/Geometry_${e.id}.usd@</Geometry>
)
{
    matrix4d xformOp:transform = ${i}
    uniform token[] xformOpOrder = ["xformOp:transform"]

    rel material:binding = </Materials/Material_${t.id}>
}

`}d(BC,"buildXform");function N_(o){let e=o.elements;return`( ${oh(e,0)}, ${oh(e,4)}, ${oh(e,8)}, ${oh(e,12)} )`}d(N_,"buildMatrix");function oh(o,e){return`(${o[e+0]}, ${o[e+1]}, ${o[e+2]}, ${o[e+3]})`}d(oh,"buildMatrixRow");function RC(o){return`
def "Geometry"
{
  ${DC(o)}
}
`}d(RC,"buildMeshObject");function DC(o){let e="Geometry",t=o.attributes,n=t.position.count;return`
    def Mesh "${e}"
    {
        int[] faceVertexCounts = [${LC(o)}]
        int[] faceVertexIndices = [${PC(o)}]
        normal3f[] normals = [${L_(t.normal,n)}] (
            interpolation = "vertex"
        )
        point3f[] points = [${L_(t.position,n)}]
        float2[] primvars:st = [${FC(t.uv,n)}] (
            interpolation = "vertex"
        )
        uniform token subdivisionScheme = "none"
    }
`}d(DC,"buildMesh");function LC(o){let e=o.index!==null?o.index.count:o.attributes.position.count;return Array(e/3).fill(3).join(", ")}d(LC,"buildMeshVertexCount");function PC(o){let e=o.index,t=[];if(e!==null)for(let n=0;n<e.count;n++)t.push(e.getX(n));else{let n=o.attributes.position.count;for(let i=0;i<n;i++)t.push(i)}return t.join(", ")}d(PC,"buildMeshVertexIndices");function L_(o,e){if(o===void 0)return console.warn("USDZExporter: Normals missing."),Array(e).fill("(0, 0, 0)").join(", ");let t=[];for(let n=0;n<o.count;n++){let i=o.getX(n),s=o.getY(n),r=o.getZ(n);t.push(`(${i.toPrecision(un)}, ${s.toPrecision(un)}, ${r.toPrecision(un)})`)}return t.join(", ")}d(L_,"buildVector3Array");function FC(o,e){if(o===void 0)return console.warn("USDZExporter: UVs missing."),Array(e).fill("(0, 0)").join(", ");let t=[];for(let n=0;n<o.count;n++){let i=o.getX(n),s=o.getY(n);t.push(`(${i.toPrecision(un)}, ${1-s.toPrecision(un)})`)}return t.join(", ")}d(FC,"buildVector2Array");function OC(o,e){let t=[];for(let n in o){let i=o[n];t.push(NC(i,e))}return`def "Materials"
{
${t.join("")}
}

`}d(OC,"buildMaterials");function NC(o,e){let t="            ",n=[],i=[];function s(r,a,l){let c=r.id+(l?"_"+l.getHexString():""),h=r.format===1023;return e[c]=r,`
        def Shader "Transform2d_${a}" (
            sdrMetadata = {
                string role = "math"
            }
        )
        {
            uniform token info:id = "UsdTransform2d"
            float2 inputs:in.connect = </Materials/Material_${o.id}/uvReader_st.outputs:result>
            float2 inputs:scale = ${F_(r.repeat)}
            float2 inputs:translation = ${F_(r.offset)}
            float2 outputs:result
        }

        def Shader "Texture_${r.id}_${a}"
        {
            uniform token info:id = "UsdUVTexture"
            asset inputs:file = @textures/Texture_${c}.${h?"png":"jpg"}@
            float2 inputs:st.connect = </Materials/Material_${o.id}/Transform2d_${a}.outputs:result>
            token inputs:wrapS = "repeat"
            token inputs:wrapT = "repeat"
            float outputs:r
            float outputs:g
            float outputs:b
            float3 outputs:rgb
            ${o.transparent||o.alphaTest>0?"float outputs:a":""}
        }`}return d(s,"buildTexture"),o.side===Et&&console.warn("THREE.USDZExporter: USDZ does not support double sided materials",o),o.map!==null?(n.push(`${t}color3f inputs:diffuseColor.connect = </Materials/Material_${o.id}/Texture_${o.map.id}_diffuse.outputs:rgb>`),o.transparent?n.push(`${t}float inputs:opacity.connect = </Materials/Material_${o.id}/Texture_${o.map.id}_diffuse.outputs:a>`):o.alphaTest>0&&(n.push(`${t}float inputs:opacity.connect = </Materials/Material_${o.id}/Texture_${o.map.id}_diffuse.outputs:a>`),n.push(`${t}float inputs:opacityThreshold = ${o.alphaTest}`)),i.push(s(o.map,"diffuse",o.color))):n.push(`${t}color3f inputs:diffuseColor = ${P_(o.color)}`),o.emissiveMap!==null?(n.push(`${t}color3f inputs:emissiveColor.connect = </Materials/Material_${o.id}/Texture_${o.emissiveMap.id}_emissive.outputs:rgb>`),i.push(s(o.emissiveMap,"emissive"))):o.emissive.getHex()>0&&n.push(`${t}color3f inputs:emissiveColor = ${P_(o.emissive)}`),o.normalMap!==null&&(n.push(`${t}normal3f inputs:normal.connect = </Materials/Material_${o.id}/Texture_${o.normalMap.id}_normal.outputs:rgb>`),i.push(s(o.normalMap,"normal"))),o.aoMap!==null&&(n.push(`${t}float inputs:occlusion.connect = </Materials/Material_${o.id}/Texture_${o.aoMap.id}_occlusion.outputs:r>`),i.push(s(o.aoMap,"occlusion"))),o.roughnessMap!==null&&o.roughness===1?(n.push(`${t}float inputs:roughness.connect = </Materials/Material_${o.id}/Texture_${o.roughnessMap.id}_roughness.outputs:g>`),i.push(s(o.roughnessMap,"roughness"))):n.push(`${t}float inputs:roughness = ${o.roughness}`),o.metalnessMap!==null&&o.metalness===1?(n.push(`${t}float inputs:metallic.connect = </Materials/Material_${o.id}/Texture_${o.metalnessMap.id}_metallic.outputs:b>`),i.push(s(o.metalnessMap,"metallic"))):n.push(`${t}float inputs:metallic = ${o.metalness}`),o.alphaMap!==null?(n.push(`${t}float inputs:opacity.connect = </Materials/Material_${o.id}/Texture_${o.alphaMap.id}_opacity.outputs:r>`),n.push(`${t}float inputs:opacityThreshold = 0.0001`),i.push(s(o.alphaMap,"opacity"))):n.push(`${t}float inputs:opacity = ${o.opacity}`),o.isMeshPhysicalMaterial&&(n.push(`${t}float inputs:clearcoat = ${o.clearcoat}`),n.push(`${t}float inputs:clearcoatRoughness = ${o.clearcoatRoughness}`),n.push(`${t}float inputs:ior = ${o.ior}`)),`
    def Material "Material_${o.id}"
    {
        def Shader "PreviewSurface"
        {
            uniform token info:id = "UsdPreviewSurface"
${n.join(`
`)}
            int inputs:useSpecularWorkflow = 0
            token outputs:surface
        }

        token outputs:surface.connect = </Materials/Material_${o.id}/PreviewSurface.outputs:surface>
        token inputs:frame:stPrimvarName = "st"

        def Shader "uvReader_st"
        {
            uniform token info:id = "UsdPrimvarReader_float2"
            token inputs:varname.connect = </Materials/Material_${o.id}.inputs:frame:stPrimvarName>
            float2 inputs:fallback = (0.0, 0.0)
            float2 outputs:result
        }

${i.join(`
`)}

    }
`}d(NC,"buildMaterial");function P_(o){return`(${o.r}, ${o.g}, ${o.b})`}d(P_,"buildColor");function F_(o){return`(${o.x}, ${o.y})`}d(F_,"buildVector2");function UC(o){let e=o.name?o.name:"Camera_"+o.id,t=N_(o.matrixWorld);return o.matrixWorld.determinant()<0&&console.warn("THREE.USDZExporter: USDZ does not support negative scales",o),o.isOrthographicCamera?`def Camera "${e}"
		{
			matrix4d xformOp:transform = ${t}
			uniform token[] xformOpOrder = ["xformOp:transform"]
	
			float2 clippingRange = (${o.near.toPrecision(un)}, ${o.far.toPrecision(un)})
			float horizontalAperture = ${((Math.abs(o.left)+Math.abs(o.right))*10).toPrecision(un)}
			float verticalAperture = ${((Math.abs(o.top)+Math.abs(o.bottom))*10).toPrecision(un)}
			token projection = "orthographic"
		}
	
	`:`def Camera "${e}"
		{
			matrix4d xformOp:transform = ${t}
			uniform token[] xformOpOrder = ["xformOp:transform"]
	
			float2 clippingRange = (${o.near.toPrecision(un)}, ${o.far.toPrecision(un)})
			float focalLength = ${o.getFocalLength().toPrecision(un)}
			float focusDistance = ${o.focus.toPrecision(un)}
			float horizontalAperture = ${o.getFilmWidth().toPrecision(un)}
			token projection = "perspective"
			float verticalAperture = ${o.getFilmHeight().toPrecision(un)}
		}
	
	`}d(UC,"buildCamera");L();P();var U_=d(o=>e=>{try{let t=In(e),n=(t.length?t[0].terms:[]).filter(s=>s&&s.type==="ident").map(s=>s.value).filter(s=>o.indexOf(s)>-1),i=new Set;for(let s of n)i.add(s);return i}catch{}return new Set},"enumerationDeserializer");var so=function(o,e,t,n){var i=arguments.length,s=i<3?e:n===null?n=Object.getOwnPropertyDescriptor(e,t):n,r;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")s=Reflect.decorate(o,e,t,n);else for(var a=o.length-1;a>=0;a--)(r=o[a])&&(s=(i<3?r(s):i>3?r(e,t,s):r(e,t))||s);return i>3&&s&&Object.defineProperty(e,t,s),s},Q_=!1,k_=!1,G_="#model-viewer-no-ar-fallback",QC=U_(["quick-look","scene-viewer","webxr","none"]),kC="webxr scene-viewer quick-look",Gn={QUICK_LOOK:"quick-look",SCENE_VIEWER:"scene-viewer",WEBXR:"webxr",NONE:"none"},Oi=Symbol("arButtonContainer"),z_=Symbol("enterARWithWebXR"),V_=Symbol("openSceneViewer"),H_=Symbol("openIOSARQuickLook"),GC=Symbol("canActivateAR"),lh=Symbol("arMode"),jf=Symbol("arModes"),ro=Symbol("arAnchor"),ch=Symbol("preload"),hh=Symbol("onARButtonContainerClick"),Zf=Symbol("onARStatus"),ep=Symbol("onARTracking"),tp=Symbol("onARTap"),ka=Symbol("selectARMode"),np=Symbol("triggerLoad"),W_=d(o=>{var e,t,n,i,s,r,a,l,c,h;class u extends o{static{d(this,"ARModelViewerElement")}constructor(){super(...arguments),this.ar=!1,this.arScale="auto",this.arPlacement="floor",this.arModes=kC,this.iosSrc=null,this.xrEnvironment=!1,this[e]=!1,this[t]=this.shadowRoot.querySelector(".ar-button"),this[n]=document.createElement("a"),this[i]=new Set,this[s]=Gn.NONE,this[r]=!1,this[a]=p=>{p.preventDefault(),this.activateAR()},this[l]=({status:p})=>{(p===Ti.NOT_PRESENTING||this[Ne].arRenderer.presentedScene===this[oe])&&(this.setAttribute("ar-status",p),this.dispatchEvent(new CustomEvent("ar-status",{detail:{status:p}})),p===Ti.NOT_PRESENTING?this.removeAttribute("ar-tracking"):p===Ti.SESSION_STARTED&&this.setAttribute("ar-tracking",Dc.TRACKING))},this[c]=({status:p})=>{this.setAttribute("ar-tracking",p),this.dispatchEvent(new CustomEvent("ar-tracking",{detail:{status:p}}))},this[h]=p=>{p.data=="_apple_ar_quicklook_button_tapped"&&this.dispatchEvent(new CustomEvent("quick-look-button-tapped"))}}get canActivateAR(){return this[lh]!==Gn.NONE}connectedCallback(){super.connectedCallback(),this[Ne].arRenderer.addEventListener("status",this[Zf]),this.setAttribute("ar-status",Ti.NOT_PRESENTING),this[Ne].arRenderer.addEventListener("tracking",this[ep]),this[ro].addEventListener("message",this[tp])}disconnectedCallback(){super.disconnectedCallback(),this[Ne].arRenderer.removeEventListener("status",this[Zf]),this[Ne].arRenderer.removeEventListener("tracking",this[ep]),this[ro].removeEventListener("message",this[tp])}update(p){super.update(p),p.has("arScale")&&(this[oe].canScale=this.arScale!=="fixed"),p.has("arPlacement")&&(this[oe].updateShadow(),this[_t]()),p.has("arModes")&&(this[jf]=QC(this.arModes)),(p.has("ar")||p.has("arModes")||p.has("src")||p.has("iosSrc"))&&this[ka]()}async activateAR(){switch(this[lh]){case Gn.QUICK_LOOK:this[H_]();break;case Gn.WEBXR:await this[z_]();break;case Gn.SCENE_VIEWER:this[V_]();break;default:console.warn("No AR Mode can be activated. This is probably due to missing configuration or device capabilities");break}}async[(e=GC,t=Oi,n=ro,i=jf,s=lh,r=ch,a=hh,l=Zf,c=ep,h=tp,ka)](){let p=Gn.NONE;if(this.ar){if(this.src!=null)for(let g of this[jf]){if(g==="webxr"&&ec&&!Q_&&await this[Ne].arRenderer.supportsPresentation()){p=Gn.WEBXR;break}if(g==="scene-viewer"&&vm&&!k_){p=Gn.SCENE_VIEWER;break}if(g==="quick-look"&&$u){p=Gn.QUICK_LOOK;break}}p===Gn.NONE&&this.iosSrc!=null&&$u&&(p=Gn.QUICK_LOOK)}if(p!==Gn.NONE)this[Oi].classList.add("enabled"),this[Oi].addEventListener("click",this[hh]);else if(this[Oi].classList.contains("enabled")){this[Oi].removeEventListener("click",this[hh]),this[Oi].classList.remove("enabled");let g=Ti.FAILED;this.setAttribute("ar-status",g),this.dispatchEvent(new CustomEvent("ar-status",{detail:{status:g}}))}this[lh]=p}async[z_](){console.log("Attempting to present in AR with WebXR..."),await this[np]();try{this[Oi].removeEventListener("click",this[hh]);let{arRenderer:p}=this[Ne];p.placeOnWall=this.arPlacement==="wall",await p.present(this[oe],this.xrEnvironment)}catch(p){console.warn("Error while trying to present in AR with WebXR"),console.error(p),await this[Ne].arRenderer.stopPresenting(),Q_=!0,console.warn("Falling back to next ar-mode"),await this[ka](),this.activateAR()}finally{this[ka]()}}async[np](){this.loaded||(this[ch]=!0,this[as](),await Mm(this,"load"),this[ch]=!1)}[Mi](){return super[Mi]()||this[ch]}[V_](){let p=self.location.toString(),g=new URL(p),A=new URL(this.src,p);A.hash&&(A.hash="");let m=new URLSearchParams(A.search);if(g.hash=G_,m.set("mode","ar_preferred"),m.has("disable_occlusion")||m.set("disable_occlusion","true"),this.arScale==="fixed"&&m.set("resizable","false"),this.arPlacement==="wall"&&m.set("enable_vertical_placement","true"),m.has("sound")){let x=new URL(m.get("sound"),p);m.set("sound",x.toString())}if(m.has("link")){let x=new URL(m.get("link"),p);m.set("link",x.toString())}let _=`intent://arvr.google.com/scene-viewer/1.0?${m.toString()+"&file="+encodeURIComponent(A.toString())}#Intent;scheme=https;package=com.google.ar.core;action=android.intent.action.VIEW;S.browser_fallback_url=${encodeURIComponent(g.toString())};end;`,E=d(()=>{self.location.hash===G_&&(k_=!0,self.history.back(),console.warn("Error while trying to present in AR with Scene Viewer"),console.warn("Falling back to next ar-mode"),this[ka]())},"undoHashChange");self.addEventListener("hashchange",E,{once:!0}),this[ro].setAttribute("href",_),console.log("Attempting to present in AR with Scene Viewer..."),this[ro].click()}async[H_](){let p=!this.iosSrc;this[Oi].classList.remove("enabled");let g=p?await this.prepareUSDZ():this.iosSrc,A=new URL(g,self.location.toString());if(p){let E=self.location.toString(),x=new URL(E),y=new URL(this.src,x);y.hash&&(A.hash=y.hash)}this.arScale==="fixed"&&(A.hash&&(A.hash+="&"),A.hash+="allowsContentScaling=0");let m=this[ro];m.setAttribute("rel","ar");let _=document.createElement("img");m.appendChild(_),m.setAttribute("href",A.toString()),p&&m.setAttribute("download","model.usdz"),m.style.display="none",m.isConnected||this.shadowRoot.appendChild(m),console.log("Attempting to present in AR with Quick Look..."),m.click(),m.removeChild(_),p&&URL.revokeObjectURL(g),this[Oi].classList.add("enabled")}async prepareUSDZ(){let p=this[Jn].beginActivity();await this[np]();let{model:g,shadow:A}=this[oe];if(g==null)return"";let m=!1;A!=null&&(m=A.visible,A.visible=!1),p(.2);let E=await new ah().parse(g),x=new Blob([E],{type:"model/vnd.usdz+zip"}),y=URL.createObjectURL(x);return p(1),A!=null&&(A.visible=m),y}}return so([ye({type:Boolean,attribute:"ar"})],u.prototype,"ar",void 0),so([ye({type:String,attribute:"ar-scale"})],u.prototype,"arScale",void 0),so([ye({type:String,attribute:"ar-placement"})],u.prototype,"arPlacement",void 0),so([ye({type:String,attribute:"ar-modes"})],u.prototype,"arModes",void 0),so([ye({type:String,attribute:"ios-src"})],u.prototype,"iosSrc",void 0),so([ye({type:Boolean,attribute:"xr-environment"})],u.prototype,"xrEnvironment",void 0),u},"ARMixin");L();P();var ip=function(o,e,t,n){var i=arguments.length,s=i<3?e:n===null?n=Object.getOwnPropertyDescriptor(e,t):n,r;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")s=Reflect.decorate(o,e,t,n);else for(var a=o.length-1;a>=0;a--)(r=o[a])&&(s=(i<3?r(s):i>3?r(e,t,s):r(e,t))||s);return i>3&&s&&Object.defineProperty(e,t,s),s};var zC=100,VC="https://www.gstatic.com/draco/versioned/decoders/1.4.1/",HC="https://www.gstatic.com/basis-universal/versioned/2021-04-15-ba1c3e4/",WC="https://cdn.jsdelivr.net/npm/three@0.149.0/examples/jsm/loaders/LottieLoader.js",sp={AUTO:"auto",MANUAL:"manual"},q_={AUTO:"auto",LAZY:"lazy",EAGER:"eager"},Fs=Symbol("defaultProgressBarElement"),rp=Symbol("posterContainerElement"),oo=Symbol("defaultPosterElement"),Ga=Symbol("shouldDismissPoster"),op=Symbol("hidePoster"),uh=Symbol("modelIsRevealed"),ap=Symbol("updateProgressBar"),qC=Symbol("ariaLabelCallToAction"),lp=Symbol("onProgress"),K_=d(o=>{var e,t,n,i,s,r,a,l;class c extends o{static{d(this,"LoadingModelViewerElement")}constructor(...u){super(...u),this.poster=null,this.reveal=sp.AUTO,this.loading=q_.AUTO,this[e]=!1,this[t]=!1,this[n]=this.shadowRoot.querySelector(".slot.poster"),this[i]=this.shadowRoot.querySelector("#default-poster"),this[s]=this.shadowRoot.querySelector("#default-progress-bar > .bar"),this[r]=this[oo].getAttribute("aria-label"),this[a]=Em(m=>{let _=this[Fs].parentNode;requestAnimationFrame(()=>{this[Fs].style.transform=`scaleX(${m})`,m===0&&(_.removeChild(this[Fs]),_.appendChild(this[Fs])),m===1?this[Fs].classList.add("hide"):this[Fs].classList.remove("hide")})},zC),this[l]=m=>{let _=m.detail.totalProgress;_===1&&(this[ap].flush(),this.loaded&&(this[Ga]||this.reveal===sp.AUTO)&&this[op]()),this[ap](_),this.dispatchEvent(new CustomEvent("progress",{detail:{totalProgress:_}}))};let f=self.ModelViewerElement||{},p=f.dracoDecoderLocation||VC;pt.setDRACODecoderLocation(p);let g=f.ktx2TranscoderLocation||HC;pt.setKTX2TranscoderLocation(g),f.meshoptDecoderLocation&&pt.setMeshoptDecoderLocation(f.meshoptDecoderLocation);let A=f.lottieLoaderLocation||WC;an.singleton.textureUtils.lottieLoaderUrl=A}static set dracoDecoderLocation(u){pt.setDRACODecoderLocation(u)}static get dracoDecoderLocation(){return pt.getDRACODecoderLocation()}static set ktx2TranscoderLocation(u){pt.setKTX2TranscoderLocation(u)}static get ktx2TranscoderLocation(){return pt.getKTX2TranscoderLocation()}static set meshoptDecoderLocation(u){pt.setMeshoptDecoderLocation(u)}static get meshoptDecoderLocation(){return pt.getMeshoptDecoderLocation()}static set lottieLoaderLocation(u){an.singleton.textureUtils.lottieLoaderUrl=u}static get lottieLoaderLocation(){return an.singleton.textureUtils.lottieLoaderUrl}static mapURLs(u){an.singleton.loader[ns].manager.setURLModifier(u)}dismissPoster(){this.loaded?this[op]():(this[Ga]=!0,this[as]())}showPoster(){let u=this[rp];if(u.classList.contains("show"))return;u.classList.add("show"),this[Qn].classList.remove("show");let f=this[oo];f.removeAttribute("tabindex"),f.removeAttribute("aria-hidden");let p=this.modelIsVisible;this[uh]=!1,this[Pa](p)}getDimensions(){return ti(this[oe].size)}getBoundingBoxCenter(){return ti(this[oe].boundingBox.getCenter(new B))}connectedCallback(){super.connectedCallback(),this.loaded||this.showPoster(),this[Jn].addEventListener("progress",this[lp])}disconnectedCallback(){super.disconnectedCallback(),this[Jn].removeEventListener("progress",this[lp])}async updated(u){super.updated(u),u.has("poster")&&this.poster!=null&&(this[oo].style.backgroundImage=`url(${this.poster})`),u.has("alt")&&this[oo].setAttribute("aria-label",this[nh]),(u.has("reveal")||u.has("loading"))&&this[as]()}[(e=uh,t=Ga,n=rp,i=oo,s=Fs,r=qC,a=ap,l=lp,Mi)](){return!!this.src&&(this[Ga]||this.loading===q_.EAGER||this.reveal===sp.AUTO&&this[os])}[op](){this[Ga]=!1;let u=this[rp];if(!u.classList.contains("show"))return;u.classList.remove("show"),this[Qn].classList.add("show");let f=this.modelIsVisible;this[uh]=!0,this[Pa](f);let p=this.getRootNode();p&&p.activeElement===this&&this[Qn].focus();let g=this[oo];g.setAttribute("aria-hidden","true"),g.tabIndex=-1,this.dispatchEvent(new CustomEvent("poster-dismissed"))}[ei](){return super[ei]()&&this[uh]}}return ip([ye({type:String})],c.prototype,"poster",void 0),ip([ye({type:String})],c.prototype,"reveal",void 0),ip([ye({type:String})],c.prototype,"loading",void 0),c},"LoadingMixin");L();P();var cp=function(o,e,t,n){var i=arguments.length,s=i<3?e:n===null?n=Object.getOwnPropertyDescriptor(e,t):n,r;if(typeof Reflect=="object"&&typeof Reflect.decorate=="function")s=Reflect.decorate(o,e,t,n);else for(var a=o.length-1;a>=0;a--)(r=o[a])&&(s=(i<3?r(s):i>3?r(e,t,s):r(e,t))||s);return i>3&&s&&Object.defineProperty(e,t,s),s},KC=Math.PI/32,$C=3e3,XC={basis:[Or(St(KC,"rad"))],keywords:{auto:[null]}},ao=Symbol("autoRotateStartTime"),hp=Symbol("radiansPerSecond"),$_=Symbol("syncRotationRate"),up=Symbol("onCameraChange"),X_=d(o=>{var e,t,n;class i extends o{static{d(this,"StagingModelViewerElement")}constructor(){super(...arguments),this.autoRotate=!1,this.autoRotateDelay=$C,this.rotationPerSecond="auto",this[e]=performance.now(),this[t]=0,this[n]=r=>{this.autoRotate&&r.detail.source==="user-interaction"&&(this[ao]=performance.now())}}connectedCallback(){super.connectedCallback(),this.addEventListener("camera-change",this[up]),this[ao]=performance.now()}disconnectedCallback(){super.disconnectedCallback(),this.removeEventListener("camera-change",this[up]),this[ao]=performance.now()}updated(r){super.updated(r),r.has("autoRotate")&&(this[ao]=performance.now())}[(e=ao,t=hp,$_)](r){this[hp]=r[0]}[on](r,a){if(super[on](r,a),!this.autoRotate||!this[ei]()||this[Ne].isPresenting)return;let l=Math.min(a,r-this[ao]-this.autoRotateDelay);l>0&&(this[oe].yaw=this.turntableRotation+this[hp]*l*.001)}get turntableRotation(){return this[oe].yaw}resetTurntableRotation(r=0){this[oe].yaw=r}}return n=up,cp([ye({type:Boolean,attribute:"auto-rotate"})],i.prototype,"autoRotate",void 0),cp([ye({type:Number,attribute:"auto-rotate-delay"})],i.prototype,"autoRotateDelay",void 0),cp([ci({intrinsics:XC,updateHandler:$_}),ye({type:String,attribute:"rotation-per-second"})],i.prototype,"rotationPerSecond",void 0),i},"StagingMixin");L();P();var Y_=d(o=>{var e;let t=d(s=>{if(s.shadowRoot==null||s.hasAttribute("data-js-focus-visible"))return()=>{};if(self.applyFocusVisiblePolyfill)self.applyFocusVisiblePolyfill(s.shadowRoot);else{let r=d(()=>{self.applyFocusVisiblePolyfill(s.shadowRoot)},"coordinationHandler");return self.addEventListener("focus-visible-polyfill-ready",r,{once:!0}),()=>{self.removeEventListener("focus-visible-polyfill-ready",r)}}return()=>{}},"coordinateWithPolyfill"),n=Symbol("endPolyfillCoordination");class i extends o{static{d(this,"FocusVisibleCoordinator")}constructor(){super(...arguments),this[e]=null}connectedCallback(){super.connectedCallback&&super.connectedCallback(),this[n]==null&&(this[n]=t(this))}disconnectedCallback(){super.disconnectedCallback&&super.disconnectedCallback(),this[n]!=null&&(this[n](),this[n]=null)}}return e=n,i},"FocusVisiblePolyfillMixin");var YC=g_(z0(X_(bm(jg(W_(K_(A_(Y_(Di)))))))));customElements.define("model-viewer",YC);export{Vo as CanvasTexture,An as FileLoader,pn as Loader,YC as ModelViewerElement,ct as NearestFilter};
/*! Bundled license information:

@lit/reactive-element/decorators/custom-element.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/property.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/state.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/base.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/event-options.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/query.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/query-all.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/query-async.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/query-assigned-elements.js:
  (**
   * @license
   * Copyright 2021 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/decorators/query-assigned-nodes.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

three/build/three.module.js:
  (**
   * @license
   * Copyright 2010-2023 Three.js Authors
   * SPDX-License-Identifier: MIT
   *)

@lit/reactive-element/css-tag.js:
  (**
   * @license
   * Copyright 2019 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/reactive-element.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/lit-html.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-element/lit-element.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/is-server.js:
  (**
   * @license
   * Copyright 2022 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@google/model-viewer/lib/constants.js:
  (* @license
   * Copyright 2019 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/utilities.js:
  (* @license
   * Copyright 2019 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/features/environment.js:
  (* @license
   * Copyright 2019 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/assets/close-material-svg.js:
  (* @license
   * Copyright 2019 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/assets/controls-svg.js:
  (* @license
   * Copyright 2019 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/assets/view-in-ar-material-svg.js:
  (* @license
   * Copyright 2019 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/template.js:
  (* @license
   * Copyright 2019 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/utilities/cache-eviction-policy.js:
  (* @license
   * Copyright 2019 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/three-components/gltf-instance/VariantMaterialLoaderPlugin.js:
  (* @license
   * Copyright 2021 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/three-components/CachingGLTFLoader.js:
  (* @license
   * Copyright 2019 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/three-components/gltf-instance/VariantMaterialExporterPlugin.js:
  (* @license
   * Copyright 2021 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/three-components/Damper.js:
  (* @license
   * Copyright 2020 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/three-components/PlacementBox.js:
  (* @license
   * Copyright 2020 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/styles/parsers.js:
  (* @license
   * Copyright 2019 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/styles/conversions.js:
  (* @license
   * Copyright 2019 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/styles/evaluators.js:
  (* @license
   * Copyright 2019 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/styles/style-effector.js:
  (* @license
   * Copyright 2019 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/decorators.js:
  (* @license
   * Copyright 2019 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/utilities/animation.js:
  (* @license
   * Copyright 2019 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/features/controls.js:
  (* @license
   * Copyright 2019 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/three-components/SmoothControls.js:
  (* @license
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/three-components/ARRenderer.js:
  (* @license
   * Copyright 2019 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/three-components/Debugger.js:
  (* @license
   * Copyright 2019 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/three-components/GLTFInstance.js:
  (* @license
   * Copyright 2020 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/three-components/gltf-instance/ModelViewerGLTFInstance.js:
  (* @license
   * Copyright 2020 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/three-components/EnvironmentScene.js:
  (* @license
   * Copyright 2021 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/three-components/EnvironmentSceneAlt.js:
  (* @license
   * Copyright 2021 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/three-components/TextureUtils.js:
  (* @license
   * Copyright 2019 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/three-components/Renderer.js:
  (* @license
   * Copyright 2019 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/features/scene-graph/three-dom-element.js:
  (* @license
   * Copyright 2020 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/features/scene-graph/image.js:
  (* @license
   * Copyright 2020 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/features/scene-graph/sampler.js:
  (* @license
   * Copyright 2020 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/features/scene-graph/texture.js:
  (* @license
   * Copyright 2020 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/features/scene-graph/texture-info.js:
  (* @license
   * Copyright 2020 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/features/scene-graph/pbr-metallic-roughness.js:
  (* @license
   * Copyright 2020 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/features/scene-graph/material.js:
  (* @license
   * Copyright 2020 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/features/scene-graph/model.js:
  (* @license
   * Copyright 2020 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/features/scene-graph.js:
  (* @license
   * Copyright 2020 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/three-components/Hotspot.js:
  (* @license
   * Copyright 2020 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/three-components/Shadow.js:
  (* @license
   * Copyright 2022 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/three-components/ModelScene.js:
  (* @license
   * Copyright 2019 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/utilities/data-conversion.js:
  (* @license
   * Copyright 2019 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/utilities/progress-tracker.js:
  (* @license
   * Copyright 2019 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/model-viewer-base.js:
  (* @license
   * Copyright 2019 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/features/animation.js:
  (* @license
   * Copyright 2019 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/features/annotation.js:
  (* @license
   * Copyright 2019 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

three/examples/jsm/libs/fflate.module.js:
  (*!
  fflate - fast JavaScript compression/decompression
  <https://101arrowz.github.io/fflate>
  Licensed under MIT. https://github.com/101arrowz/fflate/blob/master/LICENSE
  version 0.6.9
  *)

@google/model-viewer/lib/styles/deserializers.js:
  (* @license
   * Copyright 2019 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/features/ar.js:
  (* @license
   * Copyright 2019 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/features/loading.js:
  (* @license
   * Copyright 2019 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/features/staging.js:
  (* @license
   * Copyright 2019 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)

@google/model-viewer/lib/model-viewer.js:
  (* @license
   * Copyright 2019 Google LLC. All Rights Reserved.
   * Licensed under the Apache License, Version 2.0 (the 'License');
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   *     http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an 'AS IS' BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *)
*/
//# sourceMappingURL=model-viewer-P5RAWAP4.js.map
