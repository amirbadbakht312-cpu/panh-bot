// ============================================
// Abyss AI - بازی ماهی‌گیری با Phaser 3
// ============================================

const config = {
    type: Phaser.AUTO,
    width: 800,
    height: 600,
    backgroundColor: '#0a0e1a',
    parent: 'game-container',
    scene: {
        preload: preload,
        create: create,
        update: update
    },
    scale: {
        mode: Phaser.Scale.FIT,
        autoCenter: Phaser.Scale.CENTER_BOTH
    }
};

let game = new Phaser.Game(config);

let fishCount = 0;
let energy = 10;
let maxEnergy = 10;
let isFishing = false;
let isWaiting = false;
let fishVisible = false;
let fishCaught = false;
let fishTimer = null;
let clickTimer = null;

let penguin, fish, bobber, exclamation, caughtFish;
let statusText, fishText, energyText;

// ============================================
// Preload
// ============================================

function preload() {
    // ساخت گرافیک
    this.textures.generate('penguin', { data: drawPenguin() });
    this.textures.generate('fish', { data: drawFish() });
    this.textures.generate('bobber', { data: drawBobber() });
}

// ============================================
// رسم پنگوئن
// ============================================

function drawPenguin() {
    const canvas = document.createElement('canvas');
    canvas.width = 64;
    canvas.height = 70;
    const ctx = canvas.getContext('2d');
    
    // بدن
    ctx.fillStyle = '#1a1a2e';
    ctx.beginPath();
    ctx.ellipse(32, 38, 22, 30, 0, 0, Math.PI * 2);
    ctx.fill();
    
    // شکم
    ctx.fillStyle = '#f0f0f0';
    ctx.beginPath();
    ctx.ellipse(32, 42, 16, 24, 0, 0, Math.PI * 2);
    ctx.fill();
    
    // سر
    ctx.fillStyle = '#1a1a2e';
    ctx.beginPath();
    ctx.arc(32, 18, 18, 0, Math.PI * 2);
    ctx.fill();
    
    // صورت
    ctx.fillStyle = '#f0f0f0';
    ctx.beginPath();
    ctx.arc(32, 16, 14, 0, Math.PI * 2);
    ctx.fill();
    
    // چشم‌ها
    ctx.fillStyle = 'white';
    ctx.beginPath();
    ctx.arc(26, 14, 6, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(38, 14, 6, 0, Math.PI * 2);
    ctx.fill();
    
    ctx.fillStyle = 'black';
    ctx.beginPath();
    ctx.arc(28, 15, 3, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(40, 15, 3, 0, Math.PI * 2);
    ctx.fill();
    
    // منقار
    ctx.fillStyle = '#e67e22';
    ctx.beginPath();
    ctx.moveTo(32, 20);
    ctx.lineTo(24, 26);
    ctx.lineTo(40, 26);
    ctx.closePath();
    ctx.fill();
    
    // پاها
    ctx.fillStyle = '#e67e22';
    ctx.fillRect(24, 62, 10, 6);
    ctx.fillRect(36, 62, 10, 6);
    
    return canvas;
}

// ============================================
// رسم ماهی
// ============================================

function drawFish() {
    const canvas = document.createElement('canvas');
    canvas.width = 48;
    canvas.height = 32;
    const ctx = canvas.getContext('2d');
    
    const colors = ['#f1c40f', '#e74c3c', '#3498db', '#2ecc71', '#e67e22'];
    const color = colors[Math.floor(Math.random() * colors.length)];
    
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.ellipse(24, 16, 18, 12, 0, 0, Math.PI * 2);
    ctx.fill();
    
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.moveTo(6, 16);
    ctx.lineTo(0, 6);
    ctx.lineTo(0, 26);
    ctx.closePath();
    ctx.fill();
    
    ctx.fillStyle = 'white';
    ctx.beginPath();
    ctx.arc(32, 13, 5, 0, Math.PI * 2);
    ctx.fill();
    
    ctx.fillStyle = 'black';
    ctx.beginPath();
    ctx.arc(34, 13, 3, 0, Math.PI * 2);
    ctx.fill();
    
    return canvas;
}

// ============================================
// رسم چوب‌پران
// ============================================

function drawBobber() {
    const canvas = document.createElement('canvas');
    canvas.width = 24;
    canvas.height = 24;
    const ctx = canvas.getContext('2d');
    
    ctx.fillStyle = '#e74c3c';
    ctx.beginPath();
    ctx.arc(12, 12, 10, 0, Math.PI * 2);
    ctx.fill();
    
    ctx.fillStyle = 'white';
    ctx.beginPath();
    ctx.arc(12, 8, 6, 0, Math.PI * 2);
    ctx.fill();
    
    ctx.fillStyle = '#e74c3c';
    ctx.beginPath();
    ctx.arc(12, 16, 5, 0, Math.PI * 2);
    ctx.fill();
    
    return canvas;
}

// ============================================
// Create - ساخت صحنه
// ============================================

function create() {
    const scene = this;
    const w = this.scale.width;
    const h = this.scale.height;
    
    // ===== پس‌زمینه =====
    // آسمان
    const sky = this.add.graphics();
    sky.fillStyle(0x87CEEB, 1);
    sky.fillRect(0, 0, w, 280);
    sky.fillStyle(0x5bc0eb, 1);
    sky.fillRect(0, 280, w, 120);
    sky.fillStyle(0x2980b9, 1);
    sky.fillRect(0, 400, w, 200);
    
    // خورشید
    this.add.circle(720, 60, 45, 0xf1c40f);
    this.add.circle(720, 60, 55, 0xf1c40f, 0.3);
    
    // کوه‌ها
    const mt = this.add.graphics();
    mt.fillStyle(0x3d4a5c, 1);
    mt.fillTriangle(0, 280, 180, 200, 360, 280);
    mt.fillTriangle(250, 280, 430, 190, 610, 280);
    mt.fillTriangle(500, 280, 680, 210, 800, 280);
    
    mt.fillStyle(0xc8d8e0, 1);
    mt.fillTriangle(140, 235, 180, 200, 220, 235);
    mt.fillTriangle(390, 225, 430, 190, 470, 225);
    mt.fillTriangle(640, 240, 680, 210, 720, 240);
    
    // ساحل
    this.add.rectangle(w/2, 275, w, 25, 0xc8b88a);
    
    // رودخانه
    this.add.rectangle(w/2, 385, w, 180, 0x2980b9);
    this.add.rectangle(w/2, 385, w, 160, 0x3498db);
    
    // ===== پنگوئن =====
    penguin = this.add.sprite(130, 320, 'penguin');
    penguin.setScale(1.2);
    
    // ===== چوب =====
    const rod = this.add.graphics();
    rod.lineStyle(4, 0x8B6914);
    rod.beginPath();
    rod.moveTo(170, 290);
    rod.lineTo(220, 260);
    rod.strokePath();
    
    // ===== چوب‌پران =====
    bobber = this.add.sprite(220, 300, 'bobber');
    bobber.setVisible(false);
    bobber.setScale(0.8);
    
    // ===== علامت تعجب =====
    exclamation = this.add.text(0, 0, '❗', {
        fontSize: '50px',
        color: '#e74c3c'
    });
    exclamation.setVisible(false);
    
    // ===== ماهی =====
    fish = this.add.sprite(0, 0, 'fish');
    fish.setVisible(false);
    fish.setScale(0.8);
    
    // ===== ماهی صید شده =====
    caughtFish = this.add.sprite(w/2, 60, 'fish');
    caughtFish.setVisible(false);
    caughtFish.setScale(2);
    
    // ===== متن‌ها =====
    statusText = this.add.text(w/2, 420, '🎣 برای شروع ماهی‌گیری، دکمه رو بزن!', {
        fontSize: '18px',
        color: '#ffffff',
        fontFamily: 'Tahoma',
        align: 'center'
    }).setOrigin(0.5);
    
    fishText = this.add.text(30, 460, '🐟 0', {
        fontSize: '24px',
        color: '#2ecc71',
        fontFamily: 'Tahoma'
    });
    
    energyText = this.add.text(w - 150, 460, '⚡ 10/10', {
        fontSize: '24px',
        color: '#f1c40f',
        fontFamily: 'Tahoma'
    });
    
    // ===== نوار انرژی =====
    const barBg = this.add.graphics();
    barBg.fillStyle(0x333333, 1);
    barBg.fillRoundedRect(30, 500, 160, 16, 8);
    this.energyBar = this.add.graphics();
    this.updateEnergyBar();
    
    // ===== دکمه ماهی‌گیری =====
    const fishBtn = this.add.text(w/2, 483, '🎣 چوب بینداز!', {
        fontSize: '20px',
        color: '#ffffff',
        fontFamily: 'Tahoma',
        fontWeight: 'bold'
    }).setOrigin(0.5);
    
    fishBtn.setInteractive({ useHandCursor: true });
    fishBtn.on('pointerdown', startFishing);
    
    // پس‌زمینه دکمه
    const btnBg = this.add.graphics();
    btnBg.fillStyle(0x2980b9, 1);
    btnBg.fillRoundedRect(w/2 - 120, 460, 240, 45, 12);
    btnBg.setDepth(-1);
    
    // ===== دکمه غذا دادن =====
    const feedBtn = this.add.text(w/2, 538, '🐧 غذا دادن', {
        fontSize: '20px',
        color: '#1a1a2e',
        fontFamily: 'Tahoma',
        fontWeight: 'bold'
    }).setOrigin(0.5);
    
    feedBtn.setInteractive({ useHandCursor: true });
    feedBtn.on('pointerdown', feedPenguin);
    
    const feedBg = this.add.graphics();
    feedBg.fillStyle(0xf1c40f, 1);
    feedBg.fillRoundedRect(w/2 - 120, 515, 240, 45, 12);
    feedBg.setDepth(-1);
    
    // ===== کلیک روی صحنه =====
    this.input.on('pointerdown', function(pointer) {
        if (isWaiting && fishVisible) {
            const dist = Phaser.Math.Distance.Between(
                pointer.x, pointer.y, fish.x, fish.y
            );
            if (dist < 50) {
                catchFish();
            }
        }
    });
    
    // ===== راهنما =====
    this.add.text(w/2, 590, '🎮 کلیک روی دکمه‌ها | ESC: خروج', {
        fontSize: '14px',
        color: '#666666',
        fontFamily: 'Tahoma'
    }).setOrigin(0.5);
}

// ============================================
// Update
// ============================================

function update() {}

// ============================================
// توابع بازی
// ============================================

function startFishing() {
    if (isFishing || isWaiting) {
        statusText.setText('⏳ صبر کن!');
        statusText.setColor('#f39c12');
        return;
    }
    if (energy < 1) {
        statusText.setText('❌ انرژی کافی نیست!');
        statusText.setColor('#e74c3c');
        return;
    }
    
    energy--;
    updateUI();
    isFishing = true;
    statusText.setText('🎣 چوب به آب افتاد...');
    statusText.setColor('#3498db');
    
    bobber.setVisible(true);
    bobber.x = 300 + Math.random() * 300;
    bobber.y = 350 + Math.random() * 50;
    
    const waitTime = 3000 + Math.random() * 5000;
    fishTimer = setTimeout(showFish, waitTime);
}

function showFish() {
    isFishing = false;
    isWaiting = true;
    fishVisible = true;
    
    fish.x = 200 + Math.random() * 400;
    fish.y = 350 + Math.random() * 50;
    fish.setVisible(true);
    
    exclamation.setVisible(true);
    exclamation.x = penguin.x + 30;
    exclamation.y = penguin.y - 60;
    
    statusText.setText('🐟 ماهی پیدا شد! کلیک کن! (۳ ثانیه)');
    statusText.setColor('#2ecc71');
    
    clickTimer = setTimeout(fishEscaped, 3000);
}

function catchFish() {
    if (!isWaiting || !fishVisible) return;
    
    clearTimeout(clickTimer);
    isWaiting = false;
    fishVisible = false;
    fishCaught = true;
    
    fish.setVisible(false);
    exclamation.setVisible(false);
    bobber.setVisible(false);
    
    caughtFish.setVisible(true);
    caughtFish.x = 400;
    caughtFish.y = 80;
    
    fishCount++;
    updateUI();
    statusText.setText('🎉 ماهی گرفتی! +۱ 🐟');
    statusText.setColor('#2ecc71');
    isFishing = false;
    
    setTimeout(() => {
        caughtFish.setVisible(false);
    }, 1000);
}

function fishEscaped() {
    if (fishCaught) return;
    isWaiting = false;
    fishVisible = false;
    fish.setVisible(false);
    exclamation.setVisible(false);
    bobber.setVisible(false);
    statusText.setText('😔 ماهی فرار کرد! دوباره امتحان کن.');
    statusText.setColor('#e67e22');
    isFishing = false;
}

function feedPenguin() {
    if (fishCount < 10) {
        statusText.setText(`❌ به ۱۰ ماهی نیاز داری! (داری ${fishCount})`);
        statusText.setColor('#e74c3c');
        return;
    }
    if (energy >= maxEnergy) {
        statusText.setText('✅ انرژی کامل است!');
        statusText.setColor('#2ecc71');
        return;
    }
    fishCount -= 10;
    energy = Math.min(energy + 5, maxEnergy);
    updateUI();
    statusText.setText('🐧 پنگوئن خوشحال شد! +۵ انرژی ❤️');
    statusText.setColor('#2ecc71');
}

function updateUI() {
    fishText.setText(`🐟 ${fishCount}`);
    energyText.setText(`⚡ ${energy}/${maxEnergy}`);
    const scene = game.scene.scenes[0];
    if (scene) scene.updateEnergyBar();
}

function updateEnergyBar() {
    const scene = game.scene.scenes[0];
    if (!scene) return;
    scene.energyBar.clear();
    const fill = energy / maxEnergy;
    const color = fill > 0.5 ? 0x2ecc71 : fill > 0.25 ? 0xf1c40f : 0xe74c3c;
    scene.energyBar.fillStyle(color, 1);
    scene.energyBar.fillRoundedRect(30, 500, Math.floor(160 * fill), 16, 8);
}
