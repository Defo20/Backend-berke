document.addEventListener("DOMContentLoaded", () => {
    // Login Formu için DOM Elemanları
    const loginForm = document.getElementById("loginForm");

    // Profil Güncelleme Elemanları
    const nameInput = document.getElementById("name");
    const emailInput = document.getElementById("email");
    const phoneInput = document.getElementById("phone");
    const profilePhotoInput = document.getElementById("profilePhoto");
    const saveButton = document.getElementById("saveProfile");

    const savedName = document.getElementById("savedName");
    const savedEmail = document.getElementById("savedEmail");
    const savedPhone = document.getElementById("savedPhone");
    const savedPhoto = document.getElementById("savedPhoto");

    // Giriş Yap Fonksiyonu
    async function login(email, password) {
        try {
            const response = await fetch("http://127.0.0.1:5000/profile/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ email, password }),
            });
    
            if (response.ok) {
                const data = await response.json();
                localStorage.setItem("accessToken", data.access_token); // Token'ı kaydet
                console.log("Login başarılı, token kaydedildi:", data.access_token);
            } else {
                console.error("Login başarısız:", response.statusText);
            }
        } catch (error) {
            console.error("Login sırasında hata oluştu:", error);
        }
    }
    

    // Profil Bilgilerini Çekme Fonksiyonu
    async function fetchProfile() {
        try {
            const response = await fetch("http://127.0.0.1:5000/profile", {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${localStorage.getItem("accessToken")}`, // JWT Token
                },
            });
    
            if (!response.ok) {
                throw new Error("Profil bilgileri alınamadı.");
            }
    
            const userData = await response.json();
            console.log("Profil Bilgileri:", userData);
            return userData;
        } catch (error) {
            console.error("Hata:", error);
        }
    }
    
    // Profil Güncelleme Fonksiyonu
    async function saveProfile(userData) {
        try {
            const response = await fetch("http://127.0.0.1:5000/profile/update", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
                },
                body: JSON.stringify(userData),
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

    // Satın Alınan Ürünleri Çekme Fonksiyonu
    async function fetchPurchasedProducts() {
        try {
            const response = await fetch("http://127.0.0.1:5000/profile/purchased-products", {
                method: "GET",
                headers: {
                    Authorization: `Bearer ${localStorage.getItem("accessToken")}`, // JWT Token
                },
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

    // Login Form Submit Olayı
    loginForm.addEventListener("submit", (e) => {
        e.preventDefault(); // Sayfanın yeniden yüklenmesini engelle
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;
        login(email, password); // Login fonksiyonunu çağır
    });

    // Profil Kaydet Butonu
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

    // Sayfa Yüklendiğinde Profil ve Alınan Ürünleri Göster
    fetchProfile();
    fetchPurchasedProducts();
});
