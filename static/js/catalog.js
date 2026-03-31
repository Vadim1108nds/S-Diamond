// ===== ACCORDION =====
document.querySelectorAll(".filter-title").forEach(title => {
    title.addEventListener("click", () => {
        const content = title.nextElementSibling
        content.style.display =
            content.style.display === "block" ? "none" : "block"
    })
})


// ===== PRICE =====
const min = document.getElementById("rangeMin")
const max = document.getElementById("rangeMax")

const minText = document.getElementById("minPrice")
const maxText = document.getElementById("maxPrice")

min.oninput = () => {
    if (+min.value > +max.value) min.value = max.value
    minText.innerText = min.value
}

max.oninput = () => {
    if (+max.value < +min.value) max.value = min.value
    maxText.innerText = max.value
}


// ===== APPLY FILTER =====
document.querySelector(".apply").onclick = () => {

    const type = document.querySelector("input[name='type']:checked")?.value
    const material = document.querySelector("input[name='material']:checked")?.value
    const stone = document.querySelector("input[name='stone']:checked")?.value

    const minPrice = min.value
    const maxPrice = max.value

    let params = []

    if(type) params.push("type=" + type)
    if(material) params.push("material=" + material)
    if(stone) params.push("stone=" + stone)

    params.push("min=" + minPrice)
    params.push("max=" + maxPrice)

    window.location = "/catalog?" + params.join("&")
}


// ===== RESET FILTER =====
document.querySelector(".reset").onclick = () => {
    window.location = "/catalog"
}


// ===== ВІДНОВЛЕННЯ ФІЛЬТРІВ З URL =====
const params = new URLSearchParams(window.location.search)

// type
if(params.get("type")){
    const el = document.querySelector(`input[name="type"][value="${params.get("type")}"]`)
    if(el) el.checked = true
}

// material
if(params.get("material")){
    const el = document.querySelector(`input[name="material"][value="${params.get("material")}"]`)
    if(el) el.checked = true
}

// stone
if(params.get("stone")){
    const el = document.querySelector(`input[name="stone"][value="${params.get("stone")}"]`)
    if(el) el.checked = true
}

// price
if(params.get("min")){
    min.value = params.get("min")
    minText.innerText = params.get("min")
}

if(params.get("max")){
    max.value = params.get("max")
    maxText.innerText = params.get("max")
}
document.querySelectorAll(".buy-btn").forEach(btn => {
    btn.addEventListener("click", async () => {

        const card = btn.closest(".product-card")
        const productId = card.dataset.id

        try {
            const res = await fetch("/add_to_cart", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    product_id: productId
                })
            })

            if (res.status === 401) {
                alert("Увійдіть в акаунт")
                window.location = "/login"
                return
            }

            const data = await res.json()

            // 🔥 оновлюємо число
            document.getElementById("cartCount").innerText = data.count

        } catch (err) {
            console.log(err)
        }
    })
})