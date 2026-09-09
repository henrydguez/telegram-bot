const screens={home:document.getElementById('home'),register:document.getElementById('register'),amount:document.getElementById('amount'),reports:document.getElementById('reports')};
let movementType='income';
let digits='';
let totals=JSON.parse(localStorage.getItem('financial_totals_v1')||'{"income":0,"expense":0}');
let movements=JSON.parse(localStorage.getItem('financial_movements_v1')||'[]');

function show(name){Object.values(screens).forEach(s=>s.classList.add('hidden'));screens[name].classList.remove('hidden');window.scrollTo(0,0)}
function formatAmount(){const value=Number(digits||0)/100;document.getElementById('amountValue').textContent=value.toLocaleString('es-ES',{minimumFractionDigits:2,maximumFractionDigits:2})}
function money(n){return `€${n.toLocaleString('es-ES',{minimumFractionDigits:2,maximumFractionDigits:2})}`}
function updateReports(){document.getElementById('incomeTotal').textContent=money(totals.income);document.getElementById('expenseTotal').textContent=money(totals.expense);document.getElementById('balanceTotal').textContent=money(totals.income-totals.expense)}
function renderMovements(){const list=document.getElementById('movementList');if(!list)return;const income=movements.filter(m=>m.type==='income').slice().reverse();list.innerHTML=income.length?'<h3>Ingresos registrados</h3>'+income.map(m=>`<div class="movement"><span>Ingreso</span><strong>${money(m.amount)}</strong></div>`).join(''):'<p class="empty-list">Todavía no hay ingresos registrados.</p>'}
function toast(message){const el=document.getElementById('toast');el.textContent=message;el.classList.add('show');setTimeout(()=>el.classList.remove('show'),1600)}

document.getElementById('registerButton').onclick=()=>show('register');
document.getElementById('reportsButton').onclick=()=>{updateReports();show('reports')};
document.getElementById('backButton').onclick=()=>show('home');
document.getElementById('reportsBack').onclick=()=>show('home');
document.getElementById('incomeButton').onclick=()=>openAmount('income');
document.getElementById('expenseButton').onclick=()=>openAmount('expense');
document.getElementById('amountBack').onclick=()=>show('register');

function openAmount(type){movementType=type;digits='';document.getElementById('amountType').textContent=type==='income'?'Ingreso':'Gasto';document.getElementById('saveButton').textContent=type==='income'?'Guardar ingreso':'Guardar gasto';formatAmount();renderMovements();show('amount')}

document.querySelectorAll('[data-key]').forEach(button=>button.addEventListener('click',()=>{const key=button.dataset.key;if(key==='clear')digits='';else if(key==='backspace')digits=digits.slice(0,-1);else if(digits.length<10)digits+=key;formatAmount()}));

document.getElementById('saveButton').onclick=()=>{const amount=Number(digits||0)/100;if(amount<=0){toast('Introduce un importe');return}totals[movementType]+=amount;movements.push({type:movementType,amount,date:new Date().toISOString()});localStorage.setItem('financial_totals_v1',JSON.stringify(totals));localStorage.setItem('financial_movements_v1',JSON.stringify(movements));toast(movementType==='income'?'Ingreso guardado':'Gasto guardado');digits='';setTimeout(()=>{renderMovements();formatAmount()},500)};

if(window.Telegram?.WebApp){Telegram.WebApp.ready();Telegram.WebApp.expand()}
