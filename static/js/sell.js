document.addEventListener("DOMContentLoaded", () => {
    // DOM Elemanlarını Seç
    const productNameInput = document.getElementById("productName");
    const brandInput = document.getElementById("brand");
    const defectTypeInput = document.getElementById("defectType");
    const priceInput = document.getElementById("price");
    const discountInput = document.getElementById("discount");
    const categoryInput = document.getElementById("category");
    const productPhotoInput = document.getElementById("productPhoto");
    const submitButton = document.getElementById("submitProduct");
    const productDisplay = document.getElementById("productDisplay");

    // Ürünleri backend'den al ve göster
    async function fetchProducts() {
        try {
            const response = await fetch("http://127.0.0.1:5000/products/add", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
            });

            if (!response.ok) throw new Error("Ürünler alınamadı!");

            products = await response.json();
            displayProducts(); // Alınan ürünleri ekrana yazdır
        } catch (error) {
            console.error("Ürünler yüklenirken bir hata oluştu:", error);
            productDisplay.innerHTML = "<p>Ürünler yüklenemedi. Lütfen tekrar deneyin.</p>";
        }
    }

    // Ürünleri Göster
    function displayProducts() {
        productDisplay.innerHTML = ""; // Mevcut Listeyi Temizle
        products.forEach((product) => {
            const li = document.createElement("li");
            li.className = "product-item";

            const img = document.createElement("img");
            img.src = product.photo || "default-image.jpg"; // Fotoğraf Yoksa Varsayılan Görsel
            img.alt = product.name;
            img.style.width = "100px";
            img.style.height = "100px";
            img.style.objectFit = "cover";
            img.style.marginRight = "10px";

            const info = document.createElement("span");
            info.textContent = `Ürün: ${product.name}, Kategori: ${product.category}, Fiyat: ${product.price}₺, İndirimli Fiyat: ${product.discounted_price}₺`;

            const deleteButton = document.createElement("button");
            deleteButton.textContent = "Sil";
            deleteButton.className = "delete-button";
            deleteButton.addEventListener("click", () => {
                deleteProduct(product.id); // Ürün ID'sini silmek için gönder
            });

            li.appendChild(img);
            li.appendChild(info);
            li.appendChild(deleteButton);
            productDisplay.appendChild(li);
        });
    }

    // Ürünü Backend'e Kaydet
    submitButton.addEventListener("click", async () => {
        const product = {
            name: productNameInput.value,
            brand: brandInput.value,
            defect: defectTypeInput.value,
            price: parseFloat(priceInput.value),
            discount: parseFloat(discountInput.value) || 0,
            discounted_price:
                parseFloat(priceInput.value) -
                (parseFloat(priceInput.value) * (parseFloat(discountInput.value) || 0)) / 100,
            category: categoryInput.value,
            photo: "",
        };

        if (productPhotoInput.files[0]) {
            const reader = new FileReader();
            reader.onload = async function (e) {
                product.photo = e.target.result;
                await saveProduct(product); // Ürünü backend'e kaydet
            };
            reader.readAsDataURL(productPhotoInput.files[0]);
        } else {
            await saveProduct(product);
        }
    });

    // Ürünü Backend'e Gönderme
    async function saveProduct(product) {
        try {
            const response = await fetch("http://127.0.0.1:5000/products/buy", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(product),
            });

            if (!response.ok) throw new Error("Ürün kaydedilemedi!");

            const newProduct = await response.json();
            products.push(newProduct); // Backend'den dönen ürünü listeye ekle
            displayProducts();
            clearForm();
        } catch (error) {
            console.error("Ürün kaydedilirken bir hata oluştu:", error);
        }
    }

    // Ürünü Backend'den Sil
    async function deleteProduct(productId) {
        try {
            const response = await fetch(`http://127.0.0.1:5000/products/${productId}`, {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json",
                },
            });

            if (!response.ok) throw new Error("Ürün silinemedi!");

            products = products.filter((product) => product.id !== productId);
            displayProducts(); // Listeyi Güncelle
        } catch (error) {
            console.error("Ürün silinirken bir hata oluştu:", error);
        }
    }

    // Formu Temizleme İşlevi
    function clearForm() {
        productNameInput.value = "";
        brandInput.value = "";
        defectTypeInput.value = "";
        priceInput.value = "";
        discountInput.value = "";
        categoryInput.value = "Şapka"; // Varsayılan Kategori
        productPhotoInput.value = null;
    }

    // Sayfa Yüklendiğinde Backend'den Ürünleri Al ve Göster
    fetchProducts();
});
