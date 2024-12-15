document.addEventListener("DOMContentLoaded", () => {
    // Ürün detaylarını backend'den alma
    const productId = localStorage.getItem("selectedProductId"); // Ürün ID'sini localStorage'dan al
    if (productId) {
        fetch(`http://127.0.0.1:5000/product/${productId}`)
            .then((response) => response.json())
            .then((data) => {
                document.getElementById("product-image").src = data.photo || "default-image.jpg";
                document.getElementById("product-name").textContent = data.name || "Ürün Adı";
                document.getElementById("product-price").textContent = `Fiyat: ${data.price}₺`;

                const discountPriceElement = document.getElementById("product-discount-price");
                if (data.discountPrice) {
                    discountPriceElement.textContent = `İndirimli Fiyat: ${data.discountPrice}₺`;
                    discountPriceElement.style.display = "block";
                } else {
                    discountPriceElement.style.display = "none";
                }

                document.getElementById("product-description").textContent =
                    data.description || "Ürün açıklaması burada görünecek.";
            })
            .catch((error) => {
                console.error("Ürün detayları alınamadı:", error);
            });
    }
});

// Sepet verilerini backend'den çekme
let basket = [];
fetch("http://127.0.0.1:5000/basket?user_id=1") // Kullanıcı ID'sine göre sepet verilerini çek
    .then((response) => response.json())
    .then((data) => {
        basket = data;
        updateBasketUI();
    })
    .catch((error) => {
        console.error("Sepet verileri alınamadı:", error);
    });

// Sepete ürün ekle
document.getElementById("add-to-basket").addEventListener("click", () => {
    const productId = localStorage.getItem("selectedProductId"); // Ürün ID'sini al
    if (productId) {
        fetch("http://127.0.0.1:5000/basket", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_id: 1, // Örnek kullanıcı ID'si
                product_id: parseInt(productId, 10),
                quantity: 1, // Varsayılan olarak 1 adet
            }),
        })
            .then((response) => response.json())
            .then((data) => {
                alert(data.message); // "Ürün sepete eklendi!" mesajını göster
                basket.push({
                    product_id: parseInt(productId, 10),
                    name: data.name,
                    price: data.price,
                    quantity: 1,
                });
                updateBasketUI();
            })
            .catch((error) => {
                console.error("Sepete ekleme hatası:", error);
            });
    }
});

// Sepeti güncelle
function updateBasketUI() {
    const basketList = document.getElementById("basket-list");
    const totalPriceElement = document.getElementById("total-price");

    basketList.innerHTML = "";
    let totalPrice = 0;

    basket.forEach((product, index) => {
        const listItem = document.createElement("li");
        listItem.innerHTML = `
            <span>${product.name} - ${product.price}₺</span>
            <button class="remove-item" data-index="${index}">Kaldır</button>
        `;
        basketList.appendChild(listItem);

        totalPrice += parseFloat(product.price);
    });

    totalPriceElement.textContent = `Toplam Tutar: ${totalPrice.toFixed(2)}₺`;

    // Sepetten ürün kaldır
    document.querySelectorAll(".remove-item").forEach((button) => {
        button.addEventListener("click", (e) => {
            const index = e.target.getAttribute("data-index");
            const product = basket[index];

            // Backend'den sepetten çıkarma işlemi
            fetch(`http://127.0.0.1:5000/basket/${product.product_id}`, {
                method: "DELETE",
            })
                .then(() => {
                    basket.splice(index, 1);
                    updateBasketUI();
                })
                .catch((error) => {
                    console.error("Sepetten çıkarma hatası:", error);
                });
        });
    });
}

// Ödeme popup'ını yönet
const paymentModal = document.getElementById("paymentModal");
const checkoutButton = document.getElementById("checkout");
const closeModal = document.querySelector(".close");

// Ödeme popup'ını aç
checkoutButton.addEventListener("click", () => {
    if (basket.length === 0) {
        alert("Sepetiniz boş. Lütfen ürün ekleyin!");
        return;
    }
    paymentModal.style.display = "block";
});

// Ödeme popup'ını kapat
closeModal.addEventListener("click", () => {
    paymentModal.style.display = "none";
});

// Ödeme işlemini tamamla
document.getElementById("paymentForm").addEventListener("submit", (e) => {
    e.preventDefault();

    const name = document.getElementById("name").value;
    const phone = document.getElementById("phone").value;
    const address = document.getElementById("address").value;

    if (name && phone && address) {
        fetch("http://127.0.0.1:5000/checkout", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name,
                phone,
                address,
                basket: basket.map((item) => ({
                    product_id: item.product_id,
                    quantity: 1,
                })),
            }),
        })
            .then((response) => response.json())
            .then((data) => {
                alert(data.message); // "Sipariş başarıyla oluşturuldu!" mesajını göster
                basket = [];
                updateBasketUI(); // Sepeti sıfırla
                paymentModal.style.display = "none";
            })
            .catch((error) => {
                console.error("Ödeme işlemi hatası:", error);
            });
    } else {
        alert("Lütfen tüm bilgileri doldurun.");
    }
});
