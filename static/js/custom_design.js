import { setCustomization, capturePreview } from './custom_design_3d.js';

document.addEventListener('DOMContentLoaded', function() {
    // DOM елементи
    const typeBtns = document.querySelectorAll('#typeOptions .option-btn');
    const materialBtns = document.querySelectorAll('#materialOptions .option-btn');
    const stoneBtns = document.querySelectorAll('#stoneOptions .option-btn');
    const sizeSlider = document.getElementById('ringSize');
    const sizeValue = document.getElementById('sizeValue');
    const sizeGroup = document.getElementById('sizeGroup');
    const totalPriceSpan = document.getElementById('totalPrice');
    const deliveryTimeSpan = document.getElementById('deliveryTime');
    const addToCartBtn = document.getElementById('addToCartCustom');

    // Поточні вибори
    let currentType = 'ring';
    let currentMaterial = 'gold';
    let currentStone = 'diamond';
    let currentSize = 17;

    // Базова ціна та надбавки
    const basePrice = 5000;
    const materialPrice = { gold: 3000, silver: 0, platinum: 5000 };
    const stonePrice = { amethyst: 1500, diamond: 4000, sapphire: 3000, none: 0 };
    const deliveryDays = { amethyst: 14, diamond: 16, sapphire: 15, none: 12 };

    // Оновлення ціни та терміну
    function updatePriceAndDelivery() {
        let total = basePrice + materialPrice[currentMaterial] + stonePrice[currentStone];
        totalPriceSpan.innerText = total;
        let delivery = deliveryDays[currentStone] || 14;
        deliveryTimeSpan.innerText = delivery + ' днів';
    }

    // Показати/сховати розмір (тільки для кільця)
    function toggleSizeGroup() {
        sizeGroup.style.display = currentType === 'ring' ? 'block' : 'none';
    }

    // Активний стан кнопок
    function setActive(buttons, value, dataAttr) {
        buttons.forEach(btn => {
            if (btn.getAttribute(dataAttr) === value) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }

    // Оновлення всього (ціна, 3D, розмір)
    function updateAll() {
        updatePriceAndDelivery();
        // Викликаємо 3D-оновлення – замість статичної картинки
        setCustomization(currentType, currentMaterial, currentStone);
        toggleSizeGroup();
    }

    // Обробники подій для типів
    typeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            currentType = btn.getAttribute('data-type');
            setActive(typeBtns, currentType, 'data-type');
            updateAll();
        });
    });

    // Обробники для матеріалів
    materialBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            currentMaterial = btn.getAttribute('data-material');
            setActive(materialBtns, currentMaterial, 'data-material');
            updateAll();
        });
    });

    // Обробники для каменів
    stoneBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            currentStone = btn.getAttribute('data-stone');
            setActive(stoneBtns, currentStone, 'data-stone');
            updateAll();
        });
    });

    // Слайдер розміру
    if (sizeSlider) {
        sizeSlider.addEventListener('input', (e) => {
            currentSize = e.target.value;
            sizeValue.innerText = currentSize;
        });
    }

    // Кнопка "Додати в кошик"
    addToCartBtn.addEventListener('click', async () => {
        const totalPrice = parseInt(totalPriceSpan.innerText);
        const leadDays = parseInt(deliveryTimeSpan.innerText) || 14;
        const previewImage = capturePreview();

        const payload = {
            type: currentType,
            metal: currentMaterial,
            stone: currentStone,
            image: previewImage,
            size: currentType === 'ring' ? currentSize : null,
            price: totalPrice,
            lead_days: leadDays,
            description: `Індивідуальне ${currentType === 'ring' ? 'кільце' : currentType === 'earrings' ? 'сережки' : 'браслет'} з ${currentMaterial}, камінь: ${currentStone}${currentType === 'ring' ? `, розмір ${currentSize}` : ''}`,
        };

        try {
            const response = await fetch('/add_custom_to_cart', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (response.status === 401) {
                alert('⚠️ Увійдіть в акаунт, щоб додати товар до кошика.');
                window.location.href = '/login';
                return;
            }

            if (!response.ok) throw new Error('Помилка сервера');

            const data = await response.json();
            if (data.success) {
                const cartCountSpan = document.getElementById('cartCount');
                if (cartCountSpan) cartCountSpan.innerText = data.count;
                alert(' Товар додано до кошика!');
                window.location.href = '/cart';
            } else {
                alert('Помилка додавання товару.');
            }
        } catch (err) {
            console.error('Помилка:', err);
            alert(' Не вдалося додати товар. Спробуйте пізніше.');
        }
    });

    // Ініціалізація
    updateAll();
});