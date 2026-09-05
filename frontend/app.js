// LikhLo AI - Frontend Client Architecture
// "Bhaiya, Likh Lo!" - Built by Akansha Singh

const STATE = {
  merchantName: localStorage.getItem('likhlo_merchant') || 'Gupta Kirana Store',
  merchantUpi: localStorage.getItem('likhlo_upi') || 'gupta@okhdfcbank',
  openaiKey: localStorage.getItem('likhlo_openai_key') || '',
  activeFilter: 'ALL',
  isRecording: false,
  mediaRecorder: null,
  audioChunks: [],
  selectedReminderTx: null,
  activeReminderTone: 'polite',
  transactions: JSON.parse(localStorage.getItem('likhlo_txs')) || [
    {
      id: 'tx_1',
      transaction_type: 'CREDIT',
      amount: 280,
      customer: { name: 'Sharma ji' },
      items: [{ name: 'Atta / Wheat Flour', quantity: '5kg' }, { name: 'Milk', quantity: '2 pkt' }],
      payment_status: 'PENDING',
      due_date: 'Monday',
      notes: 'Logged via LikhLo AI engine',
      raw_transcript: 'Sharma ji ko 5kg atta aur 2 packet doodh udhaar diya, 280 rupaye baki hai, somvaar ko denge',
      created_at: new Date(Date.now() - 3600000).toISOString()
    },
    {
      id: 'tx_2',
      transaction_type: 'CASH_SALE',
      amount: 500,
      customer: { name: 'Ramesh' },
      items: [{ name: 'Cooking Oil', quantity: '2 litre' }],
      payment_status: 'COMPLETED',
      notes: 'Direct cash sale',
      raw_transcript: 'Ramesh ne 500 rupaye cash diya 2 packet tel ke liye',
      created_at: new Date(Date.now() - 7200000).toISOString()
    },
    {
      id: 'tx_3',
      transaction_type: 'PAYMENT_RECEIVED',
      amount: 1200,
      customer: { name: 'Gupta ji' },
      items: [],
      payment_status: 'COMPLETED',
      notes: 'Hisab clear / Vasooli',
      raw_transcript: 'Gupta ji ne purana 1200 rupaye jama karaya, hisab clear',
      created_at: new Date(Date.now() - 14400000).toISOString()
    }
  ]
};

// DOM References
const micBtn = document.getElementById('micBtn');
const recordingStatus = document.getElementById('recordingStatus');
const canvas = document.getElementById('waveformCanvas');
const ctx = canvas.getContext('2d');
const manualInput = document.getElementById('manualTextInput');
const processTextBtn = document.getElementById('processTextBtn');
const ledgerFeed = document.getElementById('ledgerFeed');
const exportCsvBtn = document.getElementById('exportCsvBtn');

// Metrics DOM
const cashInDisplay = document.getElementById('cashInTotal');
const pendingUdhaarDisplay = document.getElementById('pendingUdhaarTotal');
const cashOutDisplay = document.getElementById('cashOutTotal');
const netBalanceDisplay = document.getElementById('netBalanceTotal');
const cashInCountDisplay = document.getElementById('cashInCount');
const debtorsCountDisplay = document.getElementById('debtorsCount');
const expensesCountDisplay = document.getElementById('expensesCount');

// Filter Counts DOM
const countAll = document.getElementById('countAll');
const countCredit = document.getElementById('countCredit');
const countCash = document.getElementById('countCash');
const countRepay = document.getElementById('countRepay');
const countExpense = document.getElementById('countExpense');

// Modal Elements
const reminderModal = document.getElementById('reminderModal');
const closeModalBtn = document.getElementById('closeModalBtn');
const modalCustomerAvatar = document.getElementById('modalCustomerAvatar');
const modalCustomerName = document.getElementById('modalCustomerName');
const modalDueAmount = document.getElementById('modalDueAmount');
const modalMessageText = document.getElementById('modalMessageText');
const modalUpiDisplay = document.getElementById('modalUpiDisplay');
const copyMessageBtn = document.getElementById('copyMessageBtn');
const sendWhatsAppBtn = document.getElementById('sendWhatsAppBtn');

// Settings Elements
const settingsBtn = document.getElementById('settingsBtn');
const settingsModal = document.getElementById('settingsModal');
const closeSettingsBtn = document.getElementById('closeSettingsBtn');
const saveSettingsBtn = document.getElementById('saveSettingsBtn');
const resetDataBtn = document.getElementById('resetDataBtn');
const settingStoreName = document.getElementById('settingStoreName');
const settingUpiId = document.getElementById('settingUpiId');
const settingOpenAiKey = document.getElementById('settingOpenAiKey');
const merchantNameDisplay = document.getElementById('merchantNameDisplay');

// Init
async function init() {
  merchantNameDisplay.textContent = STATE.merchantName;
  settingStoreName.value = STATE.merchantName;
  settingUpiId.value = STATE.merchantUpi;
  settingOpenAiKey.value = STATE.openaiKey;

  // Try fetching fresh data from backend API
  await fetchTransactionsFromApi();

  renderLedger();
  updateMetrics();
  setupEventListeners();
  drawIdleWaveform();
}

async function fetchTransactionsFromApi() {
  try {
    const res = await fetch('/api/transactions?limit=200');
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data) && data.length > 0) {
        STATE.transactions = data;
        localStorage.setItem('likhlo_txs', JSON.stringify(STATE.transactions));
      }
    }
  } catch (err) {
    // Backend offline; proceed with LocalStorage
  }
}

// Waveform Animation
let animationFrameId = null;
function drawIdleWaveform() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.strokeStyle = 'rgba(59, 130, 246, 0.3)';
  ctx.lineWidth = 2;
  ctx.beginPath();
  const centerY = canvas.height / 2;
  ctx.moveTo(0, centerY);
  for (let x = 0; x < canvas.width; x += 10) {
    const y = centerY + Math.sin(x * 0.05) * 3;
    ctx.lineTo(x, y);
  }
  ctx.stroke();
}

function drawActiveWaveform() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.strokeStyle = '#EF4444';
  ctx.lineWidth = 3;
  ctx.beginPath();
  const centerY = canvas.height / 2;
  ctx.moveTo(0, centerY);
  const time = Date.now() * 0.01;
  for (let x = 0; x < canvas.width; x += 6) {
    const randomAmp = Math.sin(x * 0.08 + time) * 18 * Math.sin(x * 0.02);
    ctx.lineTo(x, centerY + randomAmp);
  }
  ctx.stroke();
  if (STATE.isRecording) {
    animationFrameId = requestAnimationFrame(drawActiveWaveform);
  }
}

// Event Listeners
function setupEventListeners() {
  micBtn.addEventListener('click', toggleRecording);
  processTextBtn.addEventListener('click', () => {
    const text = manualInput.value.trim();
    if (text) {
      processSpokenText(text);
      manualInput.value = '';
    }
  });
  manualInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      processTextBtn.click();
    }
  });

  // Export CSV
  exportCsvBtn.addEventListener('click', () => {
    window.location.href = '/api/export/csv';
  });

  // Preset test scenario chips
  document.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', (e) => {
      const scenarioText = e.target.textContent.replace(/^"|"$/g, '');
      processSpokenText(scenarioText);
    });
  });

  // Filter tabs
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      const target = e.target.closest('.tab-btn');
      target.classList.add('active');
      STATE.activeFilter = target.getAttribute('data-filter');
      renderLedger();
    });
  });

  // Modals
  closeModalBtn.addEventListener('click', () => reminderModal.classList.remove('active'));
  closeSettingsBtn.addEventListener('click', () => settingsModal.classList.remove('active'));
  settingsBtn.addEventListener('click', () => settingsModal.classList.add('active'));

  // Tone selector
  document.querySelectorAll('.tone-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('.tone-btn').forEach(b => b.classList.remove('active'));
      e.target.classList.add('active');
      STATE.activeReminderTone = e.target.getAttribute('data-tone');
      updateReminderModal();
    });
  });

  copyMessageBtn.addEventListener('click', () => {
    navigator.clipboard.writeText(modalMessageText.value);
    copyMessageBtn.textContent = 'Copied!';
    setTimeout(() => copyMessageBtn.textContent = 'Copy Message', 2000);
  });

  saveSettingsBtn.addEventListener('click', () => {
    STATE.merchantName = settingStoreName.value.trim() || 'Gupta Kirana Store';
    STATE.merchantUpi = settingUpiId.value.trim() || 'gupta@okhdfcbank';
    STATE.openaiKey = settingOpenAiKey.value.trim();
    localStorage.setItem('likhlo_merchant', STATE.merchantName);
    localStorage.setItem('likhlo_upi', STATE.merchantUpi);
    localStorage.setItem('likhlo_openai_key', STATE.openaiKey);
    merchantNameDisplay.textContent = STATE.merchantName;
    settingsModal.classList.remove('active');
    updateMetrics();
  });

  resetDataBtn.addEventListener('click', () => {
    if (confirm('Reset to initial sample transactions?')) {
      localStorage.removeItem('likhlo_txs');
      location.reload();
    }
  });
}

// Voice Recording
async function toggleRecording() {
  if (!STATE.isRecording) {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      STATE.mediaRecorder = new MediaRecorder(stream);
      STATE.audioChunks = [];
      STATE.mediaRecorder.ondataavailable = (e) => STATE.audioChunks.push(e.data);
      STATE.mediaRecorder.onstop = handleAudioUpload;
      STATE.mediaRecorder.start();
      STATE.isRecording = true;
      micBtn.classList.add('active-recording');
      recordingStatus.textContent = 'Listening... Speak your note in Hindi or Hinglish (Tap mic again to log)';
      recordingStatus.classList.add('recording');
      drawActiveWaveform();
    } catch (err) {
      console.warn('Microphone access unavailable or denied. Running simulated voice note.');
      simulateLiveVoice();
    }
  } else {
    STATE.isRecording = false;
    micBtn.classList.remove('active-recording');
    recordingStatus.textContent = 'Processing speech with LikhLo AI engine...';
    recordingStatus.classList.remove('recording');
    if (animationFrameId) cancelAnimationFrame(animationFrameId);
    drawIdleWaveform();

    if (STATE.mediaRecorder && STATE.mediaRecorder.state !== 'inactive') {
      STATE.mediaRecorder.stop();
      STATE.mediaRecorder.stream.getTracks().forEach(t => t.stop());
    }
  }
}

function simulateLiveVoice() {
  STATE.isRecording = true;
  micBtn.classList.add('active-recording');
  recordingStatus.textContent = 'Listening (Simulated Mic)...';
  recordingStatus.classList.add('recording');
  drawActiveWaveform();

  setTimeout(() => {
    STATE.isRecording = false;
    micBtn.classList.remove('active-recording');
    recordingStatus.textContent = 'Processing speech with LikhLo AI engine...';
    recordingStatus.classList.remove('recording');
    if (animationFrameId) cancelAnimationFrame(animationFrameId);
    drawIdleWaveform();
    processSpokenText('Sharma ji ko 5kg atta udhaar diya, 280 baki hai, somvaar denge');
  }, 2200);
}

async function handleAudioUpload() {
  const audioBlob = new Blob(STATE.audioChunks, { type: 'audio/wav' });
  const formData = new FormData();
  formData.append('file', audioBlob, 'record.wav');

  try {
    const res = await fetch('/api/voice/parse-audio', { method: 'POST', body: formData });
    if (res.ok) {
      const tx = await res.json();
      addTransaction(tx);
      recordingStatus.textContent = `Likh liya: ${tx.customer?.name || tx.transaction_type} (₹${tx.amount})`;
      return;
    }
  } catch (err) {
    console.log('Backend not reachable, falling back to client parser.');
  }

  processSpokenText('Sharma ji ko 5kg atta udhaar diya 280 baki hai somvaar denge');
}

// Processing Spoken Text
async function processSpokenText(text) {
  recordingStatus.textContent = 'Analyzing voice note...';

  try {
    const res = await fetch('/api/voice/parse-text', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ transcript: text, auto_save: true })
    });
    if (res.ok) {
      const tx = await res.json();
      addTransaction(tx);
      recordingStatus.textContent = `Likh liya: ${tx.customer?.name || tx.transaction_type} (₹${tx.amount})`;
      return;
    }
  } catch (err) {
    // Fallback to client-side rule engine
  }

  const parsed = clientHeuristicParse(text);
  addTransaction(parsed);
  recordingStatus.textContent = `Likh liya: ${parsed.customer?.name || parsed.transaction_type} (₹${parsed.amount})`;
}

// Client Fallback Rule Engine
function clientHeuristicParse(text) {
  const tLower = text.toLowerCase();
  let amount = 100;
  const numMatch = tLower.match(/(\d+)\s*(?:rupaye|rs|rupees|₹|baki|diya)/) || tLower.match(/\b(\d{2,6})\b/);
  if (numMatch) amount = parseFloat(numMatch[1]);

  let type = 'CREDIT';
  let status = 'PENDING';
  if (tLower.includes('jama') || tLower.includes('clear') || tLower.includes('vasooli') || tLower.includes('paid back')) {
    type = 'PAYMENT_RECEIVED';
    status = 'COMPLETED';
  } else if (tLower.includes('kharcha') || tLower.includes('mandi') || tLower.includes('wholesale') || tLower.includes('debit')) {
    type = 'DEBIT';
    status = 'COMPLETED';
  } else if (tLower.includes('cash') || tLower.includes('nakad')) {
    type = 'CASH_SALE';
    status = 'COMPLETED';
  }

  let customer = 'Customer';
  const nameMatch = text.match(/(Sharma|Verma|Gupta|Ramesh|Suresh|Amit|Rahul|Priya|Sunita|Singh|Khan)\s*(?:ji|bhai|bhaiya)?/i);
  if (nameMatch) {
    customer = nameMatch[0].trim();
  }

  let dueDate = null;
  if (tLower.includes('somvaar') || tLower.includes('monday')) dueDate = 'Monday';
  else if (tLower.includes('kal') || tLower.includes('tomorrow')) dueDate = 'Tomorrow';
  else if (tLower.includes('next week') || tLower.includes('agle hafte')) dueDate = 'Next Week';

  const items = [];
  if (tLower.includes('atta')) items.push({ name: 'Atta / Wheat Flour', quantity: '5kg' });
  if (tLower.includes('doodh') || tLower.includes('milk')) items.push({ name: 'Milk', quantity: '2 pkt' });
  if (tLower.includes('tel') || tLower.includes('oil')) items.push({ name: 'Cooking Oil', quantity: '2 litre' });
  if (tLower.includes('chawal') || tLower.includes('dal')) items.push({ name: 'Dal / Chawal', quantity: 'Wholesale' });

  return {
    id: 'tx_' + Date.now(),
    transaction_type: type,
    amount: amount,
    customer: type !== 'DEBIT' ? { name: customer } : null,
    items: items,
    payment_status: status,
    due_date: dueDate,
    notes: 'Logged via LikhLo AI engine',
    raw_transcript: text,
    created_at: new Date().toISOString()
  };
}

function addTransaction(tx) {
  if (!tx.id) tx.id = 'tx_' + Date.now();
  STATE.transactions.unshift(tx);
  localStorage.setItem('likhlo_txs', JSON.stringify(STATE.transactions));
  renderLedger();
  updateMetrics();
}

// Metrics Calculation
function updateMetrics() {
  let cashIn = 0;
  let cashInCount = 0;
  let pendingUdhaar = 0;
  let debtorsCount = 0;
  let cashOut = 0;
  let cashOutCount = 0;

  let countCred = 0;
  let countCs = 0;
  let countRep = 0;
  let countDeb = 0;

  STATE.transactions.forEach(tx => {
    if (tx.transaction_type === 'CASH_SALE') {
      cashIn += tx.amount;
      cashInCount++;
      countCs++;
    } else if (tx.transaction_type === 'PAYMENT_RECEIVED') {
      cashIn += tx.amount;
      cashInCount++;
      countRep++;
    } else if (tx.transaction_type === 'CREDIT') {
      countCred++;
      if (tx.payment_status === 'PENDING') {
        pendingUdhaar += tx.amount;
        debtorsCount++;
      }
    } else if (tx.transaction_type === 'DEBIT') {
      cashOut += tx.amount;
      cashOutCount++;
      countDeb++;
    }
  });

  cashInDisplay.textContent = `₹${cashIn.toLocaleString('en-IN')}`;
  cashInCountDisplay.textContent = `${cashInCount} receipts recorded`;

  pendingUdhaarDisplay.textContent = `₹${pendingUdhaar.toLocaleString('en-IN')}`;
  debtorsCountDisplay.textContent = `${debtorsCount} pending udhaar`;

  cashOutDisplay.textContent = `₹${cashOut.toLocaleString('en-IN')}`;
  expensesCountDisplay.textContent = `${cashOutCount} payouts`;

  const net = cashIn - cashOut;
  netBalanceDisplay.textContent = `₹${net.toLocaleString('en-IN')}`;

  countAll.textContent = STATE.transactions.length;
  countCredit.textContent = countCred;
  countCash.textContent = countCs;
  countRepay.textContent = countRep;
  countExpense.textContent = countDeb;
}

// Render Ledger Cards
function renderLedger() {
  ledgerFeed.innerHTML = '';

  const filtered = STATE.transactions.filter(tx => {
    if (STATE.activeFilter === 'ALL') return true;
    return tx.transaction_type === STATE.activeFilter;
  });

  if (filtered.length === 0) {
    ledgerFeed.innerHTML = '<div class="empty-state">No transactions in this filter. Tap the mic to log one!</div>';
    return;
  }

  filtered.forEach(tx => {
    const card = document.createElement('div');
    card.className = 'tx-card';

    const typeIcons = {
      CREDIT: '⏳',
      CASH_SALE: '💰',
      PAYMENT_RECEIVED: '✅',
      DEBIT: '📦'
    };

    const typeTitles = {
      CREDIT: tx.customer ? `${tx.customer.name} (Udhaar)` : 'Credit Given',
      CASH_SALE: tx.customer ? `${tx.customer.name} (Cash Sale)` : 'Cash Sale',
      PAYMENT_RECEIVED: tx.customer ? `${tx.customer.name} (Repayment)` : 'Repayment Received',
      DEBIT: 'Expense / Stock Purchase'
    };

    const itemsBadges = (tx.items || []).map(it => `<span class="item-tag">${it.quantity || ''} ${it.name}</span>`).join(' ');
    const dueBadge = tx.due_date ? `<span class="due-tag">📅 Due: ${tx.due_date}</span>` : '';

    const actionsHtml = [];
    if (tx.transaction_type === 'CREDIT' && tx.payment_status === 'PENDING') {
      actionsHtml.push(`<button class="btn-whatsapp-sm" onclick="openReminderModal('${tx.id}')">💬 WhatsApp</button>`);
      actionsHtml.push(`<button class="btn-settle-sm" onclick="settleTransaction('${tx.id}')">✓ Mark Paid</button>`);
    } else if (tx.payment_status === 'COMPLETED') {
      actionsHtml.push(`<span style="font-size: 11px; color: var(--color-green); font-weight: 700;">Settled</span>`);
    }

    card.innerHTML = `
      <div class="tx-card-left">
        <div class="tx-type-badge ${tx.transaction_type}">
          ${typeIcons[tx.transaction_type] || '📝'}
        </div>
        <div class="tx-info">
          <h3>${typeTitles[tx.transaction_type]}</h3>
          <div class="tx-meta">
            ${itemsBadges}
            ${dueBadge}
            <span>${new Date(tx.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
          </div>
        </div>
      </div>
      <div class="tx-card-right">
        <div class="tx-amount ${tx.transaction_type}">
          ${tx.transaction_type === 'DEBIT' ? '-' : '+'}₹${tx.amount.toLocaleString('en-IN')}
        </div>
        <div class="tx-actions">
          ${actionsHtml.join('')}
        </div>
      </div>
    `;

    ledgerFeed.appendChild(card);
  });
}

// Settle & Reminder Actions
window.settleTransaction = async function(txId) {
  try {
    await fetch(`/api/transactions/${txId}/settle`, { method: 'PATCH' });
  } catch (err) {
    // Proceed locally
  }

  const tx = STATE.transactions.find(t => t.id === txId);
  if (tx) {
    tx.payment_status = 'COMPLETED';
    localStorage.setItem('likhlo_txs', JSON.stringify(STATE.transactions));
    renderLedger();
    updateMetrics();
  }
};

window.openReminderModal = function(txId) {
  const tx = STATE.transactions.find(t => t.id === txId);
  if (!tx) return;
  STATE.selectedReminderTx = tx;
  modalCustomerAvatar.textContent = (tx.customer?.name || 'C')[0].toUpperCase();
  modalCustomerName.textContent = tx.customer?.name || 'Customer';
  modalDueAmount.textContent = `₹${tx.amount.toLocaleString('en-IN')} Pending`;
  updateReminderModal();
  reminderModal.classList.add('active');
};

function updateReminderModal() {
  if (!STATE.selectedReminderTx) return;
  const tx = STATE.selectedReminderTx;
  const customerName = tx.customer?.name || 'Customer';
  const amount = tx.amount;
  const itemsText = (tx.items || []).map(i => i.name).join(', ');
  const itemNote = itemsText ? ` (${itemsText})` : '';

  const upiLink = `upi://pay?pa=${encodeURIComponent(STATE.merchantUpi)}&pn=${encodeURIComponent(STATE.merchantName)}&am=${amount.toFixed(2)}&cu=INR&tn=LikhLo+Khata+Settlement`;
  modalUpiDisplay.textContent = `upi://pay?pa=${STATE.merchantUpi}&am=${amount}`;

  let message = '';
  if (STATE.activeReminderTone === 'polite') {
    message = `Namaste ${customerName} ji! 🙏\n\nA gentle reminder from ${STATE.merchantName}. Your balance of Rs ${amount.toFixed(0)}${itemNote} is pending in our khata.\n\nYou can easily clear it via UPI:\n${upiLink}\n\nThank you for your trust! Have a great day.`;
  } else if (STATE.activeReminderTone === 'formal') {
    message = `Hello ${customerName},\n\nThis is an automated ledger statement from ${STATE.merchantName}.\nPending Amount: Rs ${amount.toFixed(0)}${itemNote}\n\nPlease settle via UPI:\n${upiLink}\n\nThank you.`;
  } else {
    message = `Hi ${customerName}! Hope you are doing well.\n\nJust updating our weekly khata at ${STATE.merchantName}. Rs ${amount.toFixed(0)}${itemNote} is remaining.\nPay anytime via UPI: ${upiLink}\n\nDhanyawad!`;
  }

  modalMessageText.value = message;
  const encoded = encodeURIComponent(message);
  sendWhatsAppBtn.href = `https://wa.me/?text=${encoded}`;
}

document.addEventListener('DOMContentLoaded', init);
