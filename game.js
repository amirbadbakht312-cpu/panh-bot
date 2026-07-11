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
    physics: {
        default: 'arcade',
        arcade: {
            gravity: { y: 0 },
            debug: false
        }
    },
    scale: {
        mode: Phaser.Scale.FIT,
        autoCenter: Phaser.Scale.CENTER_BOTH,
        width: 800,
        height: 600
    }
};

// ============================================
// وضعیت بازی
// ============================================

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

let penguin = null;
let fish = null;
let bobber = null;
let exclamation = null;
let caughtFish = null;
let statusText = null;
let fishText = null;
let energyText = null;
let fishBtn = null;
let feedBtn = null;

// ============================================
// تابع Preload
// ============================================

function preload() {
    // بارگذاری Assets
    this.load.image('sky', 'https://labs.phaser.io/assets/skies/space3.png');
    this.load.image('penguin', 'https://labs.phaser.io/assets/sprites/phaser-ship.png');
    
    // ساخت گرافیک ساده
    this.textures.generate('penguin_sprite', { data: generatePenguin() });
    this.textures.generate('fish_sprite', { data: generateFish() });
    this.textures.generate('bobber_sprite', { data: generateBobber() });
}

// ============================================
// توابع ساخت گرافیک
// ============================================

function generatePenguin() {
    const canvas = document.createElement('canvas');
    canvas.width = 64;
    canvas.height = 64;
    const ctx = canvas.getContext('2d');
    
    // بدن
    ctx.fillStyle = '#1a1a2e';
    ctx.beginPath();
    ctx.ellipse(32, 35, 22, 28, 0, 0, Math.PI * 2);
    ctx.fill();
    
    // شکم سفید
    ctx.fillStyle = '#f0f0f0';
    ctx.beginPath();
    ctx.ellipse(32, 40, 16, 22, 0, 0, Math.PI * 2);
    ctx.fill();
    
    // سر
    ctx.fillStyle = '#1a1a2e';
    ctx.beginPath();
    ctx.arc(32, 20, 16, 0, Math.PI * 2);
    ctx.fill();
    
    // صورت سفید
    ctx.fillStyle = '#f0f0f0';
    ctx.beginPath();
    ctx.arc(32, 18, 13, 0, Math.PI * 2);
    ctx.fill();
    
    // چشم‌ها
    ctx.fillStyle = 'white';
    ctx.beginPath();
    ctx.arc(26, 16, 5, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(38, 16, 5, 0, Math.PI * 2);
    ctx.fill();
    
    ctx.fillStyle = 'black';
    ctx.beginPath();
    ctx.arc(28, 17, 3, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(40, 17, 3, 0, Math.PI * 2);
    ctx.fill();
    
    // منقار
    ctx.fillStyle = '#e67e22';
    ctx.beginPath();
    ctx.moveTo(32, 22);
    ctx.lineTo(24, 28);
    ctx.lineTo(40, 28);
    ctx.closePath();
    ctx.fill();
    
    // پاها
    ctx.fillStyle = '#e67e22';
    ctx.fillRect(24, 56, 10, 6);
    ctx.fillRect(36, 56, 10, 6);
    
    return canvas;
}

function generateFish() {
    const canvas = document.createElement('canvas');
    canvas.width = 48;
    canvas.height = 32;
    const ctx = canvas.getContext('2d');
    
    const colors = ['#f1c40f', '#e74c3c', '#3498db', '#2ecc71', '#e67e22'];
    const color = colors[Math.floor(Math.random() * colors.length)];
    
    // بدن
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.ellipse(24, 16, 18, 12, 0, 0, Math.PI * 2);
    ctx.fill();
    
    // دم
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.moveTo(6, 16);
    ctx.lineTo(0, 6);
    ctx.lineTo(0, 26);
    ctx.closePath();
    ctx.fill();
    
    // چشم
    ctx.fillStyle = 'white';
    ctx.beginPath();
    ctx.arc(32, 13, 5, 0, Math.PI * 2);
    ctx.fill();
    
    ctx.fillStyle = 'black';
    ctx.beginPath();
    ctx.arc(34, 13, 3, 0, Math.PI * 2);
    ctx.fill();
    
    // باله
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.ellipse(22, 6, 8, 4, 0, 0, Math.PI * 2);
    ctx.fill();
    
    return canvas;
}

function generateBobber() {
    const canvas = document.createElement('canvas');
    canvas.width = 24;
    canvas.height = 24;
    const ctx = canvas.getContext('2d');
    
    // چوب‌پران
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
// تابع Create
// ============================================

function create() {
    const scene = this;
    const width = this.scale.width;
    const height = this.scale.height;
    
    // ===== پس‌زمینه =====
    // آسمان
    const sky = this.add.graphics();
    sky.fillStyle(0x87CEEB, 1);
    sky.fillRect(0, 0, width, 280);
    sky.fillStyle(0x5bc0eb, 1);
    sky.fillRect(0, 280, width, 120);
    sky.fillStyle(0x2980b9, 1);
    sky.fillRect(0, 400, width, 200);
    
    // خورشید
    this.add.circle(720, 60, 45, 0xf1c40f);
    this.add.circle(720, 60, 55, 0xf1c40f, 0.3);
    this.add.circle(720, 60, 65, 0xf1c40f, 0.1);
    
    // ابرها
    const cloud1 = this.add.graphics();
    cloud1.fillStyle(0xffffff, 0.6);
    cloud1.fillCircle(100, 50, 30);
    cloud1.fillCircle(130, 40, 35);
    cloud1.fillCircle(160, 50, 30);
    cloud1.fillCircle(145, 55, 25);
    
    const cloud2 = this.add.graphics();
    cloud2.fillStyle(0xffffff, 0.5);
    cloud2.fillCircle(380, 35, 25);
    cloud2.fillCircle(410, 25, 30);
    cloud2.fillCircle(440, 35, 25);
    
    const cloud3 = this.add.graphics();
    cloud3.fillStyle(0xffffff, 0.4);
    cloud3.fillCircle(580, 65, 20);
    cloud3.fillCircle(610, 55, 25);
    cloud3.fillCircle(640, 65, 20);
    
    // کوه‌ها
    const mountain = this.add.graphics();
    mountain.fillStyle(0x3d4a5c, 1);
    mountain.fillTriangle(0, 280, 180, 200, 360, 280);
    mountain.fillTriangle(250, 280, 430, 190, 610, 280);
    mountain.fillTriangle(500, 280, 680, 210, 800, 280);
    
    // برف روی کوه
    mountain.fillStyle(0xc8d8e0, 1);
    mountain.fillTriangle(140, 235, 180, 200, 220, 235);
    mountain.fillTriangle(390, 225, 430, 190, 470, 225);
    mountain.fillTriangle(640, 240, 680, 210, 720, 240);
    
    // درخت‌ها
    for (let i = 0; i < 5; i++) {
        const tx = 30 + i * 180 + Math.random() * 40;
        const ty = 250 + Math.random() * 20;
        const tree = this.add.graphics();
        tree.fillStyle(0x8B6914, 1);
        tree.fillRect(tx, ty, 6, 20);
        tree.fillStyle(0x27ae60, 1);
        tree.fillCircle(tx + 3, ty - 5, 18);
        tree.fillCircle(tx - 5, ty + 5, 15);
        tree.fillCircle(tx + 11, ty + 5, 15);
    }
    
    // ساحل
    this.add.rectangle(width/2, 275, width, 25, 0xc8b88a);
    
    // چمن
    for (let i = 0; i < width; i += 12) {
        const h = 3 + Math.random() * 6;
        this.add.rectangle(i, 262, 2, h, 0x27ae60);
    }
    
    // رودخانه
    this.add.rectangle(width/2, 385, width, 180, 0x2980b9);
    this.add.rectangle(width/2, 385, width, 160, 0x3498db);
    
    // موج‌ها
    for (let i = 0; i < 20; i++) {
        const x = i * 45;
        const wave = this.add.text(x + 10, 330 + Math.sin(i) * 8, '~', {
            fontSize: '24px',
            color: 'rgba(255,255,255,0.2)'
        });
        this.tweens.add({
            targets: wave,
            y: 330 + Math.sin(i + 1) * 8,
            duration: 1000 + i * 100,
            yoyo: true,
            repeat: -1
        });
    }
    
    // ===== پنگوئن =====
    penguin = this.add.sprite(130, 320, 'penguin_sprite');
    penguin.setScale(1.2);
    
    // ===== چوب ماهی‌گیری =====
    // چوب
    const rod = this.add.graphics();
    rod.lineStyle(4, 0x8B6914);
    rod.beginPath();
    rod.moveTo(170, 290);
    rod.lineTo(220, 260);
    rod.strokePath();
    
    // نخ
    this.line = this.add.graphics();
    this.line.lineStyle(2, 0xcccccc, 0.5);
    this.line.beginPath();
    this.line.moveTo(220, 270);
    this.line.lineTo(220, 300);
    this.line.strokePath();
    this.line.setVisible(false);
    
    // ===== چوب‌پران =====
    bobber = this.add.sprite(220, 300, 'bobber_sprite');
    bobber.setVisible(false);
    bobber.setScale(0.8);
    
    // ===== علامت تعجب =====
    exclamation = this.add.text(0, 0, '❗', {
        fontSize: '50px',
        color: '#e74c3c'
    });
    exclamation.setVisible(false);
    exclamation.setDepth(100);
    
    // ===== ماهی =====
    fish = this.add.sprite(0, 0, 'fish_sprite');
    fish.setVisible(false);
    fish.setScale(0.8);
    fish.setDepth(50);
    
    // ===== ماهی صید شده =====
    caughtFish = this.add.sprite(width/2, 60, 'fish_sprite');
    caughtFish.setVisible(false);
    caughtFish.setScale(2);
    caughtFish.setDepth(200);
    
    // ===== متن‌ها =====
    statusText = this.add.text(width/2, 420, '🎣 برای شروع ماهی‌گیری، دکمه رو بزن!', {
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
    
    energyText = this.add.text(width - 150, 460, '⚡ 10/10', {
        fontSize: '24px',
        color: '#f1c40f',
        fontFamily: 'Tahoma'
    });
    
    // ===== نوار انرژی =====
    const energyBarBg = this.add.graphics();
    energyBarBg.fillStyle(0x333333, 1);
    energyBarBg.fillRoundedRect(30, 500, 160, 16, 8);
    
    this.energyBar = this.add.graphics();
    this.updateEnergyBar();
    
    // ===== دکمه‌ها =====
    // دکمه ماهی‌گیری
    const fishBtnBg = this.add.graphics();
    fishBtnBg.fillStyle(0x2980b9, 1);
    fishBtnBg.fillRoundedRect(width/2 - 120, 460, 240, 45, 12);
    fishBtnBg.fillStyle(0x3498db, 1);
    fishBtnBg.fillRoundedRect(width/2 - 118, 462, 236, 41, 10);
    
    fishBtn = this.add.text(width/2, 483, '🎣 چوب بینداز!', {
        fontSize: '18px',
        color: '#ffffff',
        fontFamily: 'Tahoma',
        fontWeight: 'bold'
    }).setOrigin(0.5);
    
    fishBtn.setInteractive({ useHandCursor: true });
    fishBtn.on('pointerdown', startFishing);
    fishBtn.on('pointerover', () => { fishBtn.setScale(1.05); });
    fishBtn.on('pointerout', () => { fishBtn.setScale(1); });
    
    // دکمه غذا دادن
    const feedBtnBg = this.add.graphics();
    feedBtnBg.fillStyle(0xf1c40f, 1);
    feedBtnBg.fillRoundedRect(width/2 - 120, 515, 240, 45, 12);
    feedBtnBg.fillStyle(0xf39c12, 1);
    feedBtnBg.fillRoundedRect(width/2 - 118, 517, 236, 41, 10);
    
    feedBtn = this.add.text(width/2, 538, '🐧 غذا دادن', {
        fontSize: '18px',
        color: '#1a1a2e',
        fontFamily: 'Tahoma',
        fontWeight: 'bold'
    }).setOrigin(0.5);
    
    feedBtn.setInteractive({ useHandCursor: true });
    feedBtn.on('pointerdown', feedPenguin);
    feedBtn.on('pointerover', () => { feedBtn.setScale(1.05); });
    feedBtn.on('pointerout', () => { feedBtn.setScale(1); });
    
    // ===== کلیک روی صحنه =====
    this.input.on('pointerdown', function(pointer) {
        if (isWaiting && fishVisible) {
            const dist = Phaser.Math.Distance.Between(
                pointer.x, pointer.y,
                fish.x, fish.y
            );
            if (dist < 50) {
                catchFish();
            } else {
                statusText.setText('👆 نزدیک‌تر به ماهی کلیک کن!');
                statusText.setColor('#f39c12');
            }
        }
    });
    
    // ===== راهنما =====
    this.add.text(width/2, 590, '🎮 کلیک: ماهی‌گیری | کلیک روی دکمه‌ها | ESC: خروج', {
        fontSize: '14px',
        color: '#666666',
        fontFamily: 'Tahoma',
        align: 'center'
    }).setOrigin(0.5);
    
    // ===== ورودی کیبورد =====
    this.input.keyboard.on('keydown-SPACE', startFishing);
    this.input.keyboard.on('keydown-F', feedPenguin);
}

// ============================================
// تابع Update
// ============================================

function update() {
    // به‌روزرسانی چوب‌پران
    if (bobber.visible && isFishing) {
        // انیمیشن چوب‌پران
    }
}

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
    
    // نمایش چوب‌پران
    bobber.setVisible(true);
    bobber.x = 400 + Math.random() * 300;
    bobber.y = 350 + Math.random() * 60;
    
    // پنگوئن حرکت میکنه
    const scene = game.scene.scenes[0];
    scene.tweens.add({
        targets: penguin,
        x: 140,
        duration: 300,
        ease: 'Power2'
    });
    
    // زمان انتظار
    const waitTime = 3000 + Math.random() * 5000;
    fishTimer = setTimeout(showFish, waitTime);
}

function showFish() {
    isFishing = false;
    isWaiting = true;
    fishVisible = true;
    
    // نمایش ماهی
    fish.x = 200 + Math.random() * 400;
    fish.y = 350 + Math.random() * 60;
    fish.setVisible(true);
    
    // علامت تعجب
    exclamation.setVisible(true);
    exclamation.x = penguin.x + 30;
    exclamation.y = penguin.y - 60;
    
    // انیمیشن علامت تعجب
    const scene = game.scene.scenes[0];
    scene.tweens.add({
        targets: exclamation,
        y: penguin.y - 80,
        duration: 300,
        yoyo: true,
        repeat: 2
    });
    
    statusText.setText('🐟 ماهی پیدا شد! کلیک کن! (۳ ثانیه)');
    statusText.setColor('#2ecc71');
    
    // تایمر فرار
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
    
    // نمایش ماهی صید شده
    caughtFish.setVisible(true);
    const scene = game.scene.scenes[0];
    scene.tweens.add({
        targets: caughtFish,
        scaleX: 2.5,
        scaleY: 2.5,
        duration: 300,
        yoyo: true,
        repeat: 1
    });
    
    fishCount++;
    updateUI();
    
    statusText.setText('🎉 ماهی گرفتی! +۱ 🐟');
    statusText.setColor('#2ecc71');
    
    isFishing = false;
    
    // پنگوئن خوشحال
    scene.tweens.add({
        targets: penguin,
        y: penguin.y - 20,
        duration: 200,
        yoyo: true,
        repeat: 1
    });
    
    // بعد از ۱ ثانیه مخفی کن
    setTimeout(() => {
        caughtFish.setVisible(false);
        caughtFish.setScale(2);
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
    
    // پنگوئن خوشحال
    const scene = game.scene.scenes[0];
    scene.tweens.add({
        targets: penguin,
        y: penguin.y - 30,
        duration: 200,
        yoyo: true,
        repeat: 2
    });
}

function updateUI() {
    fishText.setText(`🐟 ${fishCount}`);
    energyText.setText(`⚡ ${energy}/${maxEnergy}`);
    updateEnergyBar();
}

function updateEnergyBar() {
    const scene = game.scene.scenes[0];
    scene.energyBar.clear();
    const fill = energy / maxEnergy;
    const color = fill > 0.5 ? 0x2ecc71 : fill > 0.25 ? 0xf1c40f : 0xe74c3c;
    scene.energyBar.fillStyle(color, 1);
    scene.energyBar.fillRoundedRect(30, 500, Math.floor(160 * fill), 16, 8);
}
