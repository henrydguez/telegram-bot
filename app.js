function $(id){return document.getElementById(id)}

const screens={home:$('home'),register:$('register'),movementForm:$('movementForm'),movements:$('movements'),reports:$('reports')};
const screenList=Object.values(screens).filter(Boolean);
let totals=JSON.parse(localStorage.getItem('financial_totals_v1')||'{"income":0,"expense":0}');
let movements=JSON.parse(localStorage.getItem('financial_movements_v1')||'[]');
let digits={income:'',expense:''};
let activeType='income';
const categories={income:['Salario','Trabajo','Ventas','Inversiones','Bizum','Transferencia','Otros'],expense:['Alimentación','Transporte','Vivienda','Ocio','Compras','Salud','Bizum','Transferencia','Otros']};
const personCategories=['Bizum','Transferencia'];

function show(name){screenList.forEach(s=>s.classList.add('hidden'));if(screens[name])screens[name].classList.remove('hidden');window.scrollTo(0,0)}
function money(n){return `€${Number(n).toLocaleString('es-ES',{minimumFractionDigits:2,maximumFractionDigits:2})}`}
function today(){return new Date().toISOString().slice(0,10)}
function renderAmount(){const input=$('activeAmount');if(!input)return;const n=Number(digits[activeType]||0)/100;input.value=n?n.toLocaleString('es-ES',{minimumFractionDigits:2,maximumFractionDigits:2}):''}
function updateReports(){if($('incomeTotal'))$('incomeTotal').textContent=money(totals.income);if($('expenseTotal'))$('expenseTotal').textContent=money(totals.expense);if($('balanceTotal'))$('balanceTotal').textContent=money(totals.income-totals.expense)}
function renderMovements(){const list=$('movementList');if(!list)return;if(!movements.length){list.innerHTML='<p class="empty-list">Todavía no hay movimientos registrados.</p>';return}list.innerHTML=movements.slice().reverse().map(m=>`<article class="movement ${m.type}"><div class="movement-top"><strong>${m.type==='income'?'Ingreso':'Gasto'}</strong><b>${money(m.amount)}</b></div><div><span>Fecha</span><span>${new Date(m.date+'T00:00:00').toLocaleDateString('es-ES')}</span></div><div><span>Categoría</span><span>${m.category||'Sin categoría'}</span></div>${m.person?`<div><span>Persona</span><span>${m.person}</span></div>`:''}<div><span>Descripción</span><span>${m.description||'Sin descripción'}</span></div></article>`).join('')}
function resetActive(){digits[activeType]='';$('activeAmount').value='';$('activeDate').value=today();$('activeCategory').value='';$('activeDescription').value='';$('activePerson').value='';updatePersonField()}
function toast(message){const el=$('toast');if(!el)return;el.textContent=message;el.classList.add('show');setTimeout(()=>el.classList.remove('show'),1600)}
function saveMovement(){const amount=Number(digits[activeType]||0)/100,category=$('activeCategory').value,date=$('activeDate').value,description=$('activeDescription').value.trim(),person=$('activePerson').value.trim();if(amount<=0)return toast(`Introduce un importe de ${activeType==='income'?'ingreso':'gasto'}`);if(!date)return toast('Selecciona una fecha');if(!category)return toast('Selecciona una categoría');if(personCategories.includes(category)&&!person)return toast('Indica la persona de este movimiento');totals[activeType]+=amount;movements.push({type:activeType,amount,date,category,description,...(personCategories.includes(category)&&person?{person}: {})});localStorage.setItem('financial_totals_v1',JSON.stringify(totals));localStorage.setItem('financial_movements_v1',JSON.stringify(movements));resetActive();toast(activeType==='income'?'Ingreso guardado':'Gasto guardado');updateReports();renderMovements()}
function updatePersonField(){const field=$('personField'),input=$('activePerson'),category=$('activeCategory')?.value,showPerson=personCategories.includes(category);if(!field||!input)return;field.classList.toggle('hidden',!showPerson);input.required=showPerson}
function renderCategories(){const select=$('activeCategory');if(!select)return;select.innerHTML='<option value="">Selecciona una categoría</option>'+categories[activeType].map(c=>`<option>${c}</option>`).join('');updatePersonField()}
function switchType(type){activeType=type;const income=$('incomeTab'),expense=$('expenseTab');income.classList.toggle('active',type==='income');expense.classList.toggle('active',type==='expense');income.setAttribute('aria-selected',type==='income');expense.setAttribute('aria-selected',type==='expense');$('saveActive').textContent=type==='income'?'Guardar ingreso':'Guardar gasto';renderCategories();renderAmount();$('activeDate').value=today();$('activeCategory').value='';$('activeDescription').value='';$('activePerson').value='';updatePersonField()}
function applyTheme(mode){const dark=mode==='dark',html=document.documentElement;html.classList.toggle('theme-light',!dark);html.classList.toggle('theme-dark',dark);document.body.classList.toggle('theme-light',!dark);document.body.classList.toggle('theme-dark',dark);const button=$('themeToggle'),icon=$('themeIcon');if(button&&icon){icon.textContent=dark?'☀':'☾';button.setAttribute('aria-label',dark?'Cambiar a modo día':'Cambiar a modo noche');button.title=dark?'Modo día':'Modo noche'}localStorage.setItem('theme_mode_v1',dark?'dark':'light')}

$('registerButton')?.addEventListener('click',()=>show('register'));
$('reportsButton')?.addEventListener('click',()=>{updateReports();show('reports')});
$('backButton')?.addEventListener('click',()=>show('home'));
$('reportsBack')?.addEventListener('click',()=>show('home'));
$('formBack')?.addEventListener('click',()=>show('register'));
$('movementsButton')?.addEventListener('click',()=>{renderMovements();show('movements')});
$('movementsBack')?.addEventListener('click',()=>show('reports'));
$('saveActive')?.addEventListener('click',saveMovement);
$('incomeTab')?.addEventListener('click',()=>switchType('income'));
$('expenseTab')?.addEventListener('click',()=>switchType('expense'));
$('themeToggle')?.addEventListener('click',()=>applyTheme(document.documentElement.classList.contains('theme-dark')?'light':'dark'));
$('activeCategory')?.addEventListener('change',updatePersonField);

const input=$('activeAmount');
input?.addEventListener('focus',()=>input.select());
input?.addEventListener('input',e=>{digits[activeType]=e.target.value.replace(/[^0-9]/g,'').slice(0,10);renderAmount()});
$('activeDate').value=today();
$('sharedKeypad')?.querySelectorAll('[data-key]').forEach(b=>b.addEventListener('click',()=>{const k=b.dataset.key;if(k==='clear')digits[activeType]='';else if(k==='backspace')digits[activeType]=digits[activeType].slice(0,-1);else if(digits[activeType].length<10)digits[activeType]+=k;renderAmount()}));

const savedTheme=localStorage.getItem('theme_mode_v1');
const initialTheme=savedTheme==='dark'||savedTheme==='light'?savedTheme:'light';
applyTheme(initialTheme);
renderCategories();
show('home');
if(window.Telegram?.WebApp){Telegram.WebApp.ready();Telegram.WebApp.expand()}
