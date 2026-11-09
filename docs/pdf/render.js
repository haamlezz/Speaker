const {chromium}=require('playwright');const path=require('path');
(async()=>{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://'+path.resolve(__dirname,'guide.html'));await p.waitForTimeout(500);
await p.pdf({path:path.resolve(__dirname,'../TMW-27_Build_Guide.pdf'),format:'A4',printBackground:true,
 displayHeaderFooter:true,headerTemplate:'<span></span>',
 footerTemplate:'<div style="font:7px monospace;color:#56616A;width:100%;padding:0 14mm;display:flex;justify-content:space-between"><span>TMW-27 FLOORSTANDER · BUILD GUIDE · REV A · ALL DIMENSIONS IN MM</span><span>PAGE <span class="pageNumber"></span> / <span class="totalPages"></span></span></div>',
 margin:{top:'14mm',bottom:'16mm',left:'14mm',right:'14mm'}});await b.close();})();
