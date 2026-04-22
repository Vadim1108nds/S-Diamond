document.addEventListener("DOMContentLoaded", function() {
    // Оновлення кількості товару або видалення
    const cartItems = document.querySelectorAll('.cart-item');
    
    async function updateCart(cartId, action) {
        try {
            const response = await fetch('/update_cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    cart_id: cartId,
                    action: action
                })
            });
            
            if (!response.ok) {
                throw new Error('Помилка оновлення');
            }
            
            const data = await response.json();
            
            // Оновлюємо лічильник у навігації
            document.getElementById('cartCount').innerText = data.cart_count;
            
            // Перезавантажуємо сторінку, щоб оновити вміст кошика
            // (можна зробити більш плавно, але для простоти поки так)
            window.location.reload();
        } catch (error) {
            console.error('Помилка:', error);
            alert('Не вдалося оновити кошик. Спробуйте ще раз.');
        }
    }
    
    // Додаємо обробники на всі кнопки
    document.querySelectorAll('.qty-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const cartItem = btn.closest('.cart-item');
            const cartId = cartItem.dataset.cartId;
            const action = btn.dataset.action; // 'increase' або 'decrease'
            updateCart(cartId, action);
        });
    });
    
    document.querySelectorAll('.remove-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const cartItem = btn.closest('.cart-item');
            const cartId = cartItem.dataset.cartId;
            updateCart(cartId, 'remove');
        });
    });
});