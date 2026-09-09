function $(id){return document.getElementById(id)}

const screens={home:$('home'),register:$('register'),movementForm:$('movementForm'),movements:$('movements'),reports:$('reports')};
const screenList=Object.values(screens).filter(Boolean);
let totals=JSON.parse(localStorage.getItem('financial_totals_v1')||'{"income":0,"expense":0}');
let movements=JSON.parse(localStorage.getItem('financial_movements_v1')||'[]');
let digits={income:'',expense:''};

function show(name){screenList.forEach(s=>s.classList.add('hidden'));if(screens[name])screens[name].classList.remove('hidden');window.scrollTo(0,0)}
function money(n){return `€${Number(n).toLocaleString('es-ES',{minimumFractionDigits:2,maximumFractionDigits:2})}`}
function today(){return new Date().toISOString().slice(0,10)}
function renderAmount(type){const input=$(type+'Amount');if(!input)return;const n=Number(digits[type]||0)/100;input.value=n?n.toLocaleString('es-ES',{minimumFractionDigits:2,maximumFractionDigits:2}):''}
function updateReports(){if($('incomeTotal'))$('incomeTotal').textContent=money(totals.income);if($('expenseTotal'))$('expenseTotal').textContent=money(totals.expense);if($('balanceTotal'))$('balanceTotal').textContent=money(totals.income-totals.expense)}
function renderMovements(){const list=$('movementList');if(!list)return;if(!movements.length){list.innerHTML='<p class="empty-list">Todavía no hay movimientos registrados.</p>';return}list.innerHTML=movements.slice().reverse().map(m=>`<article class="movement ${m.type}"><div class="movement-top"><strong>${m.type==='income'?'Ingreso':'Gasto'}</strong><b>${money(m.amount)}</b></div><div><span>Fecha</span><span>${new Date(m.date+'T00:00:00').toLocaleDateString('es-ES')}</span></div><div><span>Categoría</span><span>${m.category||'Sin categoría'}</span></div><div><span>Descripción</span><span>${m.description||'Sin descripción'}</span></div></article>`).join('')}
function resetType(type){digits[type]='';const prefix=type==='income'?'income':'expense';$(prefix+'Amount').value='';$(prefix+'Date').value=today();$(prefix+'Category').value='';$(prefix+'Description').value=''}
function toast(message){const el=$('toast');if(!el)return;el.textContent=message;el.classList.add('show');setTimeout(()=>el.classList.remove('show'),1600)}
function saveMovement(type){const prefix=type==='income'?'income':'expense';const amount=Number(digits[type]||0)/100,category=$(prefix+'Category').value,date=$(prefix+'Date').value,description=$(prefix+'Description').value.trim();if(amount<=0)return toast(`Introduce un importe de ${type==='income'?'ingreso':'gasto'}`);if(!date)return toast('Selecciona una fecha');if(!category)return toast('Selecciona una categoría');totals[type]+=amount;movements.push({type,amount,date,category,description});localStorage.setItem('financial_totals_v1',JSON.stringify(totals));localStorage.setItem('financial_movements_v1',JSON.stringify(movements));resetType(type);toast(type==='income'?'Ingreso guardado':'Gasto guardado');updateReports();renderMovements()}

$('registerButton')?.addEventListener('click',()=>show('register'));
$('reportsButton')?.addEventListener('click',()=>{updateReports();show('reports')});
$('backButton')?.addEventListener('click',()=>show('home'));
$('reportsBack')?.addEventListener('click',()=>show('home'));
$('formBack')?.addEventListener('click',()=>show('register'));
$('movementsButton')?.addEventListener('click',()=>{renderMovements();show('movements')});
$('movementsBack')?.addEventListener('click',()=>show('reports'));
$('saveIncome')?.addEventListener('click',()=>saveMovement('income'));
$('saveExpense')?.addEventListener('click',()=>saveMovement('expense'));

['income','expense'].forEach(type=>{
  const input=$(type+'Amount');
  input?.addEventListener('focus',()=>input.select());
  input?.addEventListener('input',e=>{digits[type]=e.target.value.replace(/[^0-9]/g,'').slice(0,10);renderAmount(type)});
  $(`${type}Date`).value=today();
  $(`[data-pad="${type}"]`)?.querySelectorAll('[data-key]').forEach(b=>b.addEventListener('click',()=>{const k=b.dataset.key;if(k==='clear')digits[type]='';else if(k==='backspace')digits[type]=digits[type].slice(0,-1);else if(digits[type].length<10)digits[type]+=k;renderAmount(type)}));
});

show('home');
if(window.Telegram?.WebApp){Telegram.WebApp.ready();Telegram.WebApp.expand()}
