import{_ as Q}from"./_plugin-vue_export-helper-BCEt7Ct6.js";/* empty css                   *//* empty css                   *//* empty css                  *//* empty css                   *//* empty css                *//* empty css                      *//* empty css                  *//* empty css                     *//* empty css                 *//* empty css                        */import"./el-tooltip-l0sNRNKZ.js";import{r as u,W as X,F as Z,a9 as G,I as L,m as E,c as B,o as z,d as a,w as o,K as J,H as ee,a1 as te,b as l,n as le,aa as ie,ab as ae,ac as se,l as r,v as s,V as oe,a6 as de,ad as ne,i as re,X as ve,Y as ce,S as ue,Q as me,T as _e,k as pe}from"./index-DURBC1W6.js";const fe={class:"charging-records"},ge={class:"card-header"},be={class:"total-fee"},we={class:"pagination-container"},he={class:"detail-header"},xe={class:"detail-date"},ye={class:"detail-section"},$e={class:"detail-item"},De={class:"detail-value"},Fe={class:"detail-item"},Ce={class:"detail-value"},ke={class:"detail-item"},Ve={class:"detail-value"},Ee={class:"detail-item"},ze={class:"detail-value"},Te={class:"detail-section"},Me={class:"detail-item"},Re={class:"detail-value"},Se={class:"detail-item"},Le={class:"detail-value"},Be={class:"detail-item"},Ie={class:"detail-value"},Pe={class:"detail-item"},Ue={class:"detail-value"},Ne={class:"detail-item total"},Ye={class:"detail-value"},He={class:"detail-footer"},Ke={__name:"ChargingRecords",setup(We){const x=u([]),y=u(!1),g=u(""),m=u(""),_=u(1),p=u(10),$=u(0),b=u(!1),n=u(null),I=G(),P=async()=>{y.value=!0;try{const t=await L.get("/charging/records");x.value=t,$.value=t.length}catch(t){console.error("获取充电记录失败:",t),E.error("获取充电记录失败")}finally{y.value=!1}},U=X(()=>{let t=x.value;if(g.value){const d=g.value.toLowerCase();t=t.filter(v=>v.record_number.toLowerCase().includes(d)||f(v.start_time).includes(d))}if(m.value){const d=new Date;let v=new Date;m.value==="7days"?v.setDate(d.getDate()-7):m.value==="30days"?v.setDate(d.getDate()-30):m.value==="thisMonth"&&(v=new Date(d.getFullYear(),d.getMonth(),1)),t=t.filter(V=>new Date(V.start_time)>=v)}$.value=t.length;const e=(_.value-1)*p.value;return t.slice(e,e+p.value)}),D=t=>{n.value=t,b.value=!0},N=()=>{const t=window.open("","_blank");if(!t){E.warning("请允许弹出窗口以打印详单");return}const e=n.value,d=`
    <html>
      <head>
        <title>充电详单 - ${e.record_number}</title>
        <style>
          body { font-family: Arial, sans-serif; padding: 20px; }
          .header { text-align: center; margin-bottom: 30px; }
          .title { font-size: 24px; font-weight: bold; }
          .subtitle { font-size: 14px; color: #666; }
          .section { margin-bottom: 20px; }
          .section-title { font-size: 18px; border-bottom: 1px solid #eee; padding-bottom: 5px; }
          .item { display: flex; margin: 10px 0; }
          .label { width: 150px; font-weight: bold; }
          .value { flex: 1; }
          .total { font-weight: bold; margin-top: 15px; border-top: 1px solid #eee; padding-top: 10px; }
          .footer { margin-top: 50px; text-align: center; font-size: 12px; color: #999; }
        </style>
      </head>
      <body>
        <div class="header">
          <div class="title">充电详单</div>
          <div class="subtitle">详单编号: ${e.record_number}</div>
          <div class="subtitle">日期: ${f(e.start_time)}</div>
        </div>
        
        <div class="section">
          <div class="section-title">充电信息</div>
          <div class="item">
            <div class="label">开始时间:</div>
            <div class="value">${w(e.start_time)}</div>
          </div>
          <div class="item">
            <div class="label">结束时间:</div>
            <div class="value">${w(e.end_time)}</div>
          </div>
          <div class="item">
            <div class="label">充电时长:</div>
            <div class="value">${C(e.charging_duration)}</div>
          </div>
          <div class="item">
            <div class="label">充电量:</div>
            <div class="value">${e.charging_amount.toFixed(2)} 度</div>
          </div>
        </div>
        
        <div class="section">
          <div class="section-title">费用明细</div>
          <div class="item">
            <div class="label">电价时段:</div>
            <div class="value">${k(e.time_period)}</div>
          </div>
          <div class="item">
            <div class="label">电价单价:</div>
            <div class="value">${e.unit_price.toFixed(2)} 元/度</div>
          </div>
          <div class="item">
            <div class="label">电费:</div>
            <div class="value">${e.electricity_fee.toFixed(2)} 元</div>
          </div>
          <div class="item">
            <div class="label">服务费:</div>
            <div class="value">${e.service_fee.toFixed(2)} 元</div>
          </div>
          <div class="item total">
            <div class="label">总费用:</div>
            <div class="value">${e.total_fee.toFixed(2)} 元</div>
          </div>
        </div>
        
        <div class="footer">
          打印时间: ${new Date().toLocaleString()}<br>
          本详单仅作为充电费用凭证，感谢您使用智能充电桩调度计费系统。
        </div>
      </body>
    </html>
  `;t.document.write(d),t.document.close(),setTimeout(()=>{t.print()},500)},Y=t=>{p.value=t,_.value=1},H=t=>{_.value=t},f=t=>{if(!t)return"";const e=new Date(t);return`${e.getFullYear()}-${h(e.getMonth()+1)}-${h(e.getDate())}`},F=t=>{if(!t)return"";const e=new Date(t);return`${h(e.getHours())}:${h(e.getMinutes())}`},w=t=>t?`${f(t)} ${F(t)}`:"",C=t=>{if(t==null)return"";const e=Math.floor(t),d=Math.round((t-e)*60);return`${e}小时${d?d+"分钟":""}`},h=t=>t.toString().padStart(2,"0"),k=t=>t==="peak"?"峰时":t==="normal"?"平时":t==="valley"?"谷时":t,T=t=>t==="peak"?"danger":t==="normal"?"warning":t==="valley"?"success":"info";return Z(async()=>{await P();const t=I.query.record_id;if(t){const e=x.value.find(d=>d.id==t);if(e)D(e);else try{const d=await L.get(`/charging/records/${t}`);D(d)}catch(d){console.error("获取充电记录详情失败:",d),E.error("获取充电记录详情失败")}}}),(t,e)=>{const d=re,v=ce,V=ve,K=se,c=ae,M=oe,W=ie,j=ne,q=J,R=_e,S=pe,A=ee,O=de;return z(),B("div",fe,[a(q,null,{header:o(()=>[l("div",ge,[e[6]||(e[6]=l("span",null,"充电详单",-1)),l("div",null,[a(d,{modelValue:g.value,"onUpdate:modelValue":e[0]||(e[0]=i=>g.value=i),placeholder:"搜索详单编号/日期","prefix-icon":"Search",style:{width:"220px","margin-right":"10px"}},null,8,["modelValue"]),a(V,{modelValue:m.value,"onUpdate:modelValue":e[1]||(e[1]=i=>m.value=i),placeholder:"时间筛选",style:{width:"120px"}},{default:o(()=>[a(v,{label:"全部时间",value:""}),a(v,{label:"最近7天",value:"7days"}),a(v,{label:"最近30天",value:"30days"}),a(v,{label:"本月",value:"thisMonth"})]),_:1},8,["modelValue"])])])]),default:o(()=>[te((z(),le(W,{data:U.value,style:{width:"100%","min-height":"400px"},"empty-text":"暂无充电记录"},{default:o(()=>[a(c,{label:"详单编号","min-width":"180"},{default:o(i=>[a(K,{type:"primary",onClick:je=>D(i.row)},{default:o(()=>[r(s(i.row.record_number),1)]),_:2},1032,["onClick"])]),_:1}),a(c,{label:"日期","min-width":"100"},{default:o(i=>[r(s(f(i.row.start_time)),1)]),_:1}),a(c,{label:"开始时间","min-width":"100"},{default:o(i=>[r(s(F(i.row.start_time)),1)]),_:1}),a(c,{label:"结束时间","min-width":"100"},{default:o(i=>[r(s(F(i.row.end_time)),1)]),_:1}),a(c,{label:"充电时长","min-width":"100"},{default:o(i=>[r(s(C(i.row.charging_duration)),1)]),_:1}),a(c,{label:"充电量(度)","min-width":"100"},{default:o(i=>[r(s(i.row.charging_amount.toFixed(2)),1)]),_:1}),a(c,{label:"电费(元)","min-width":"100"},{default:o(i=>[r(s(i.row.electricity_fee.toFixed(2)),1)]),_:1}),a(c,{label:"服务费(元)","min-width":"100"},{default:o(i=>[r(s(i.row.service_fee.toFixed(2)),1)]),_:1}),a(c,{label:"总费用(元)","min-width":"100"},{default:o(i=>[l("span",be,s(i.row.total_fee.toFixed(2)),1)]),_:1}),a(c,{label:"单价","min-width":"90"},{default:o(i=>[r(s(i.row.unit_price.toFixed(2))+"元/度 ",1)]),_:1}),a(c,{label:"时段","min-width":"80"},{default:o(i=>[a(M,{type:T(i.row.time_period)},{default:o(()=>[r(s(k(i.row.time_period)),1)]),_:2},1032,["type"])]),_:1})]),_:1},8,["data"])),[[O,y.value]]),l("div",we,[a(j,{"current-page":_.value,"onUpdate:currentPage":e[2]||(e[2]=i=>_.value=i),"page-size":p.value,"onUpdate:pageSize":e[3]||(e[3]=i=>p.value=i),"page-sizes":[10,20,50,100],layout:"total, sizes, prev, pager, next, jumper",total:$.value,onSizeChange:Y,onCurrentChange:H},null,8,["current-page","page-size","total"])])]),_:1}),a(A,{modelValue:b.value,"onUpdate:modelValue":e[5]||(e[5]=i=>b.value=i),title:"充电详单详情",width:"600px"},{default:o(()=>[n.value?(z(),B(me,{key:0},[l("div",he,[l("h3",null,"详单编号: "+s(n.value.record_number),1),l("p",xe,s(f(n.value.start_time)),1)]),a(R),l("div",ye,[e[11]||(e[11]=l("h4",null,"充电信息",-1)),l("div",$e,[e[7]||(e[7]=l("div",{class:"detail-label"},"开始时间:",-1)),l("div",De,s(w(n.value.start_time)),1)]),l("div",Fe,[e[8]||(e[8]=l("div",{class:"detail-label"},"结束时间:",-1)),l("div",Ce,s(w(n.value.end_time)),1)]),l("div",ke,[e[9]||(e[9]=l("div",{class:"detail-label"},"充电时长:",-1)),l("div",Ve,s(C(n.value.charging_duration)),1)]),l("div",Ee,[e[10]||(e[10]=l("div",{class:"detail-label"},"充电量:",-1)),l("div",ze,s(n.value.charging_amount.toFixed(2))+" 度",1)])]),a(R),l("div",Te,[e[17]||(e[17]=l("h4",null,"费用明细",-1)),l("div",Me,[e[12]||(e[12]=l("div",{class:"detail-label"},"电价时段:",-1)),l("div",Re,[a(M,{type:T(n.value.time_period)},{default:o(()=>[r(s(k(n.value.time_period)),1)]),_:1},8,["type"])])]),l("div",Se,[e[13]||(e[13]=l("div",{class:"detail-label"},"电价单价:",-1)),l("div",Le,s(n.value.unit_price.toFixed(2))+" 元/度",1)]),l("div",Be,[e[14]||(e[14]=l("div",{class:"detail-label"},"电费:",-1)),l("div",Ie,s(n.value.electricity_fee.toFixed(2))+" 元",1)]),l("div",Pe,[e[15]||(e[15]=l("div",{class:"detail-label"},"服务费:",-1)),l("div",Ue,s(n.value.service_fee.toFixed(2))+" 元",1)]),l("div",Ne,[e[16]||(e[16]=l("div",{class:"detail-label"},"总费用:",-1)),l("div",Ye,s(n.value.total_fee.toFixed(2))+" 元",1)])]),l("div",He,[a(S,{type:"primary",onClick:N},{default:o(()=>e[18]||(e[18]=[r("打印详单")])),_:1,__:[18]}),a(S,{onClick:e[4]||(e[4]=i=>b.value=!1)},{default:o(()=>e[19]||(e[19]=[r("关闭")])),_:1,__:[19]})])],64)):ue("",!0)]),_:1},8,["modelValue"])])}}},st=Q(Ke,[["__scopeId","data-v-16a0907e"]]);export{st as default};
