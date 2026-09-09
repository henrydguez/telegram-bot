const screens={home:$('home'),register:$('register'),movementForm:$('movementForm'),movements:$('movements'),reports:$('reports')};
let movementType='income',digits='';
let totals=JSON.parse(localStorage.getItem('financial_totals_v1')||'{"income":0,"expense":0}');
let movements=JSON.parse(localStorage.getItem('financial_movements_v1')||'[]');
function $(id){return document.getElementById(id)}
function show(name){Object.values(screens).forEach(s=>s.classList.add('hidden'));screens[name].classList.remove('hidden');window.scrollTo(0,0)}
function money(n){return `€${Number(n).toLocaleString('es-ES',{minimumFractionDigits:2,maximumFractionDigits:2})}`}
function today(){return new Date().toISOString().slice(0,10)}
function renderAmount(){const n=Number(digits||0)/100;$('amountInput').value=n?n.toLocaleString('es-ES',{minimumFractionDigits:2,maximumFractionDigits:2}):''}
function updateReports(){$('incomeTotal').textContent=money(totals.income);$('expenseTotal').textContent=money(totals.expense);$('balanceTotal').textContent=money(totals.income-totals.expense)}
function renderMovements(){const list=$('movementList');if(!movements.length){list.innerHTML='<p class="empty-list">Todavía no hay movimientos registrados.</p>';return}list.innerHTML=movements.slice().reverse().map(m=>`<article class="movement ${m.type}"><div class="movement-top"><strong>${m.type==='income'?'Ingreso':'Gasto'}</strong><b>${money(m.amount)}</b></div><div><span>Fecha</span><span>${new Date(m.date+'T00:00:00').toLocaleDateString('es-ES')}</span></div><div><span>Categoría</span><span>${m.category||'Sin categoría'}</span></div><div><span>Descripción</span><span>${m.description||'Sin descripción'}</span></div></article>`).join('')}
function resetForm(){digits='';$('amountInput').value='';$('dateInput').value=today();$('categoryInput').value='';$('descriptionInput').value=''}
function openForm(type){movementType=type;$('formTitle').textContent=type==='income'?'Ingreso':'Gastos';resetForm();show('movementForm')}
function toast(message){const el=$('toast');el.textContent=message;el.classList.add('show');setTimeout(()=>el.classList.remove('show'),1600)}
$('registerButton').onclick=()=>show('register');$('reportsButton').onclick=()=>{updateReports();show('reports')};$('backButton').onclick=()=>show('home');$('reportsBack').onclick=()=>show('home');$('incomeButton').onclick=()=>openForm('income');$('expenseButton').onclick=()=>openForm('expense');$('formBack').onclick=()=>show('register');$('movementsButton').onclick=()=>{renderMovements();show('movements')};$('movementsBack').onclick=()=>show('reports');
$('amountInput').addEventListener('input',e=>{digits=e.target.value.replace(/[^0-9]/g,'').slice(0,10);renderAmount()});
document.querySelectorAll('[data-key]').forEach(b=>b.addEventListener('click',()=>{const k=b.dataset.key;if(k==='clear')digits='';else if(k==='backspace')digits=digits.slice(0,-1);else if(digits.length<10)digits+=k;renderAmount()}));
$('saveButton').onclick=()=>{const amount=Number(digits||0)/100,category=$('categoryInput').value,date=$('dateInput').value,description=$('descriptionInput').value.trim();if(amount<=0)return toast('Introduce un importe');if(!date)return toast('Selecciona una fecha');if(!category)return toast('Selecciona una categoría');totals[movementType]+=amount;movements.push({type:movementType,amount,date,category,description});localStorage.setItem('financial_totals_v1',JSON.stringify(totals));localStorage.setItem('financial_movements_v1',JSON.stringify(movements));toast('Movimiento guardado');setTimeout(()=>{resetForm();renderMovements();show('movements')},500)};
if(window.Telegram?.WebApp){Telegram.WebApp.ready();Telegram.WebApp.expand()}
