const digitPatterns = {
    '0': '0111111', '1': '0000110', '2': '1011011', '3': '1001111', '4': '1100110',
    '5': '1101101', '6': '1111101', '7': '0000111', '8': '1111111', '9': '1101111',
    '-': '1000000', ' ': '0000000',
};

let startTime, timerInterval;
let currentTarget = 0;
let isRunning = false;

function updateSevenSegment(elementId, value) {
    const container = document.getElementById(elementId);
    if (!container) return;
    const pattern = digitPatterns[value] || digitPatterns['-'];

    const segMap = ['a', 'b', 'c', 'd', 'e', 'f', 'g'];
    for (let i = 0; i < 7; i++) {
        const segClass = segMap[i];
        const segElement = container.querySelector(`.${segClass}`);
        if (!segElement) continue;

        if (pattern.split('').reverse()[i] === '1') {
            segElement.classList.add('on');
        } else {
            segElement.classList.remove('on');
        }
    }
}

function displayTime(seconds, prefix) {
    const timeStr = seconds.toFixed(2).padStart(5, '0');
    const tens = timeStr[0];
    const ones = timeStr[1];
    const tenths = timeStr[3];
    const hundredths = timeStr[4];

    updateSevenSegment(`${prefix}-tens`, tens === '0' ? ' ' : tens);
    updateSevenSegment(`${prefix}-ones`, ones);
    updateSevenSegment(`${prefix}-tenths`, tenths);
    updateSevenSegment(`${prefix}-hundredths`, hundredths);
    document.getElementById(`${prefix}-dot`).classList.add('on');
}

// ランキング表示を更新する関数
async function updateRankingDisplay() {
    const res = await fetch('/api/ranking');
    const ranking = await res.json();
    renderRanking(ranking);
}

function renderRanking(ranking) {
    const list = document.getElementById('rankingList');
    if (!ranking || ranking.length === 0) {
        list.innerHTML = '<li>まだ記録がありません</li>';
        return;
    }
    list.innerHTML = '';
    ranking.forEach((r, i) => {
        let medal = i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : '🏅';
        list.innerHTML += `<li><span>${medal} ${r.name}</span> <span class="score-value">${r.score} 点 <span style="font-size: 0.8rem; color: #888;">(誤差 ${r.diff}秒)</span></span></li>`;
    });
}

async function initTarget() {
    document.getElementById('resultDisplay').innerHTML = "";
    document.getElementById('shutter').classList.remove('closed');
    displayTime(0.00, 'counter');
    
    document.getElementById('startBtn').style.display = 'inline-block';
    document.getElementById('startBtn').disabled = false;
    document.getElementById('stopBtn').style.display = 'inline-block';
    document.getElementById('stopBtn').disabled = true;
    document.getElementById('resetBtn').style.display = 'none';

    const response = await fetch('/api/start');
    const data = await response.json();
    currentTarget = data.target_seconds;
    displayTime(currentTarget, 'target');
    
    // 画面ロード時にランキングを取得して表示
    updateRankingDisplay();
}

window.onload = initTarget;

function startGame() {
    document.getElementById('startBtn').disabled = true;
    document.getElementById('stopBtn').disabled = false;
    // プレイ中は名前入力欄をロックする
    document.getElementById('playerName').disabled = true;

    startTime = Date.now();
    isRunning = true;

    timerInterval = setInterval(() => {
        let elapsed = (Date.now() - startTime) / 1000;
        displayTime(elapsed, 'counter');

        if (elapsed >= 3 && !document.getElementById('shutter').classList.contains('closed')) {
            document.getElementById('shutter').classList.add('closed');
        }
    }, 50);
}

async function stopGame() {
    if (!isRunning) return;
    isRunning = false;
    clearInterval(timerInterval);

    let actualSeconds = (Date.now() - startTime) / 1000;
    let playerName = document.getElementById('playerName').value;

    document.getElementById('shutter').classList.remove('closed');
    displayTime(actualSeconds, 'counter');

    document.getElementById('startBtn').style.display = 'none';
    document.getElementById('stopBtn').style.display = 'none';
    document.getElementById('resetBtn').style.display = 'inline-block';
    document.getElementById('playerName').disabled = false; // 入力ロック解除

    const response = await fetch('/api/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            target_seconds: currentTarget, 
            actual_seconds: actualSeconds,
            player_name: playerName 
        })
    });
    const result = await response.json();

    let diffText = result.diff > 0 ? `+${result.diff}` : `${result.diff}`;
    // 結果にスコアを追加表示
    document.getElementById('resultDisplay').innerHTML = `
        <div style="margin-bottom: 5px;">あなたの記録</div>
        <div class="result-time">${actualSeconds.toFixed(2)} 秒</div>
        <div style="color: #795548; margin-bottom: 5px;">誤差: ${diffText} 秒</div>
        <div style="color: #ff5252; font-size: 1.6rem; font-weight: bold; margin-bottom: 10px;">スコア: ${result.score} 点</div>
        <div class="result-message">${result.message}</div>
    `;

    // ランキングを再描画
    renderRanking(result.ranking);
}