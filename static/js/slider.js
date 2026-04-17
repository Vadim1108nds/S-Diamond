document.addEventListener("DOMContentLoaded", function () {

    const slider = document.getElementById("productSlider");
    const leftBtn = document.querySelector(".arrow.left");
    const rightBtn = document.querySelector(".arrow.right");

    const cards = slider.querySelectorAll(".product-card");
    const gap = 40;
    let index = 0;
    const visible = 4;

    function updateSlider() {
        const cardWidth = cards[0].offsetWidth + gap;
        slider.style.transform = `translateX(-${index * cardWidth}px)`;

        leftBtn.disabled = index === 0;
        rightBtn.disabled = index >= cards.length - visible;
    }

    rightBtn.addEventListener("click", () => {
        if (index < cards.length - visible) {
            index++;
            updateSlider();
        }
    });

    leftBtn.addEventListener("click", () => {
        if (index > 0) {
            index--;
            updateSlider();
        }
    });

    updateSlider();
});
if (cards.length <= 4) {
    leftBtn.style.display = 'none';
    rightBtn.style.display = 'none';
}

