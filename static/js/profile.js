document.addEventListener("DOMContentLoaded", () => {
    const nameInput = document.getElementById("name");
    const emailInput = document.getElementById("email");
    const phoneInput = document.getElementById("phone");
    const profilePhotoInput = document.getElementById("profilePhoto");
    const saveButton = document.getElementById("saveProfile");

    const savedName = document.getElementById("savedName");
    const savedEmail = document.getElementById("savedEmail");
    const savedPhone = document.getElementById("savedPhone");
    const savedPhoto = document.getElementById("savedPhoto");


    // Kullanıcı bilgilerini backend'den getir ve sayfada göster
    async function fetchProfile() {
        try {
            const response = await fetch("http://127.0.0.1:5000/profile", {
                method: "GET",
                headers: {
                    Authorization: `Bearer ${localStorage.getItem("accessToken")}` // JWT Token
                }
            });

            if (response.ok) {
                const userData = await response.json();
                savedName.textContent = userData.name || "[Adınız]";
                savedEmail.textContent = userData.email || "[Email]";
                savedPhone.textContent = userData.phone || "[Telefon]";

                if (userData.photo) {
                    savedPhoto.src = userData.photo;
                    savedPhoto.style.display = "block";
                } else {
                    savedPhoto.style.display = "none";
                }
            } else {
                console.error("Profil bilgileri alınamadı:", response.statusText);
            }
        } catch (error) {
            console.error("Profil bilgileri alınırken bir hata oluştu:", error);
        }
    }

    // Kullanıcı bilgilerini backend'e kaydet
    saveButton.addEventListener("click", async () => {
        const userData = {
            name: nameInput.value,
            email: emailInput.value,
            phone: phoneInput.value,
        };

        if (profilePhotoInput.files[0]) {
            const reader = new FileReader();
            reader.onload = async function (e) {
                userData.photo = e.target.result;

                await saveProfile(userData); // Profil verilerini backend'e gönder
            };
            reader.readAsDataURL(profilePhotoInput.files[0]);
        } else {
            await saveProfile(userData);
        }
    });

    async function saveProfile(userData) {
        try {
            const response = await fetch("http://127.0.0.1:5000/profile/update", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${localStorage.getItem("accessToken")}`
                },
                body: JSON.stringify(userData)
            });

            if (response.ok) {
                alert("Profil başarıyla güncellendi!");
                fetchProfile(); // Güncellenmiş bilgileri göster
            } else {
                console.error("Profil kaydedilemedi:", response.statusText);
            }
        } catch (error) {
            console.error("Profil kaydedilirken bir hata oluştu:", error);
        }
    }

    // Alınan ürünleri backend'den getir ve göster
    async function fetchPurchasedProducts() {
        try {
            const response = await fetch("http://127.0.0.1:5000/purchased-products", {
                method: "GET",
                headers: {
                    Authorization: `Bearer ${localStorage.getItem("accessToken")}` // JWT Token
                }
            });

            const purchasedProductsContainer = document.getElementById("purchasedProductsContainer");
            if (response.ok) {
                const purchasedProducts = await response.json();

                if (purchasedProducts.length === 0) {
                    purchasedProductsContainer.innerHTML = "<p>Henüz alınan ürün yok.</p>";
                } else {
                    purchasedProductsContainer.innerHTML = "";
                    purchasedProducts.forEach((product) => {
                        const productDiv = document.createElement("div");
                        productDiv.classList.add("purchased-product");

                        const productImage = product.photo || "default-image.jpg";

                        productDiv.innerHTML = `
                            <div class="product-image">
                                <img src="${productImage}" alt="${product.name}">
                            </div>
                            <div class="product-info">
                                <h3>${product.name}</h3>
                                <p>Kategori: ${product.category}</p>
                                <p>Fiyat: ${product.price}₺</p>
                                ${
                                    product.discountPrice
                                        ? `<p>İndirimli Fiyat: ${product.discountPrice}₺</p>`
                                        : ""
                                }
                            </div>
                        `;

                        purchasedProductsContainer.appendChild(productDiv);
                    });
                }
            } else {
                console.error("Satın alınan ürünler alınamadı:", response.statusText);
            }
        } catch (error) {
            console.error("Satın alınan ürünler alınırken bir hata oluştu:", error);
        }
    }

    // Sayfa yüklendiğinde kullanıcı bilgilerini ve satın alınan ürünleri göster
    fetchProfile();
    fetchPurchasedProducts();
});
