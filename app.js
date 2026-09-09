function $(id){return document.getElementById(id)}

const screens={home:$('home'),register:$('register'),movementForm:$('movementForm'),movements:$('movements'),reports:$('reports')};
const screenList=Object.values(screens).filter(Boolean);
let movementType='income',digits='';
let totals=JSON.parse(localStorage.getItem('financial_totals_v1')||'{"income":0,"expense":0}');
let movements=JSON.parse(localStorage.getItem('financial_movements_v1')||'[]');

function show(name){screenList.forEach(s=>s.classList.add('hidden'));if(screens[name])screens[name].classList.remove('hidden');window.scrollTo(0,0)}
function money(n){return `€${Number(n).toLocaleString('es-ES',{minimumFractionDigits:2,maximumFractionDigits:2})}`}
function today(){return new Date().toISOString().slice(0,10)}
function renderAmount(){const n=Number(digits||0)/100;if($('amountInput'))$('amountInput').value=n?n.toLocaleString('es-ES',{minimumFractionDigits:2,maximumFractionDigits:2}):''}
function updateReports(){if($('incomeTotal'))$('incomeTotal').textContent=money(totals.income);if($('expenseTotal'))$('expenseTotal').textContent=money(totals.expense);if($('balanceTotal'))$('balanceTotal').textContent=money(totals.income-totals.expense)}
function renderMovements(){const list=$('movementList');if(!list)return;if(!movements.length){list.innerHTML='<p class="empty-list">Todavía no hay movimientos registrados.</p>';return}list.innerHTML=movements.slice().reverse().map(m=>`<article class="movement ${m.type}"><div class="movement-top"><strong>${m.type==='income'?'Ingreso':'Gasto'}</strong><b>${money(m.amount)}</b></div><div><span>Fecha</span><span>${new Date(m.date+'T00:00:00').toLocaleDateString('es-ES')}</span></div><div><span>Categoría</span><span>${m.category||'Sin categoría'}</span></div><div><span>Descripción</span><span>${m.description||'Sin descripción'}</span></div></article>`).join('')}
function resetForm(){digits='';if($('amountInput'))$('amountInput').value='';if($('dateInput'))$('dateInput').value=today();if($('categoryInput'))$('categoryInput').value='';if($('descriptionInput'))$('descriptionInput').value=''}
function openForm(type){movementType=type;if($('formTitle'))$('formTitle').textContent=type==='income'?'Ingreso':'Gastos';resetForm();show('movementForm')}
function toast(message){const el=$('toast');if(!el)return;el.textContent=message;el.classList.add('show');setTimeout(()=>el.classList.remove('show'),1600)}

$('registerButton')?.addEventListener('click',()=>show('register'));
$('reportsButton')?.addEventListener('click',()=>{updateReports();show('reports')});
$('backButton')?.addEventListener('click',()=>show('home'));
$('reportsBack')?.addEventListener('click',()=>show('home'));
$('incomeButton')?.addEventListener('click',()=>openForm('income'));
$('expenseButton')?.addEventListener('click',()=>openForm('expense'));
$('formBack')?.addEventListener('click',()=>show('register'));
$('movementsButton')?.addEventListener('click',()=>{renderMovements();show('movements')});
$('movementsBack')?.addEventListener('click',()=>show('reports'));
$('amountInput')?.addEventListener('input',e=>{digits=e.target.value.replace(/[^0-9]/g,'').slice(0,10);renderAmount()});

document.querySelectorAll('[data-key]').forEach(b=>b.addEventListener('click',()=>{const k=b.dataset.key;if(k==='clear')digits='';else if(k==='backspace')digits=digits.slice(0,-1);else if(digits.length<10)digits+=k;renderAmount()}));

$('saveButton')?.addEventListener('click',()=>{const amount=Number(digits||0)/100,category=$('categoryInput')?.value,date=$('dateInput')?.value,description=$('descriptionInput')?.value.trim()||'';if(amount<=0)return toast('Introduce un importe');if(!date)return toast('Selecciona una fecha');if(!category)return toast('Selecciona una categoría');totals[movementType]+=amount;movements.push({type:movementType,amount,date,category,description});localStorage.setItem('financial_totals_v1',JSON.stringify(totals));localStorage.setItem('financial_movements_v1',JSON.stringify(movements));toast('Movimiento guardado');setTimeout(()=>{resetForm();renderMovements();show('movements')},500)});

show('home');
if(window.Telegram?.WebApp){Telegram.WebApp.ready();Telegram.WebApp.expand()}
