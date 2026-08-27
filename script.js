/* =========================================
   BAYZID MARKETPLACE
   Main JavaScript
   ========================================= */

"use strict";

/* =========================================
   CART
   ========================================= */

let cart = JSON.parse(localStorage.getItem("bayzidCart")) || [];


// Update cart count
function updateCartCount() {
    const cartCount = document.getElementById("cartCount");

    if (!cartCount) return;

    cartCount.textContent = cart.length;
}


// Add product to cart
function addToCart(productName, price) {

    const product = {
        id: Date.now(),
        name: productName,
        price: Number(price),
        quantity: 1
    };

    cart.push(product);

    localStorage.setItem(
        "bayzidCart",
        JSON.stringify(cart)
    );

    updateCartCount();

    showNotification(
        `${productName} added to cart!`
    );
}


/* =========================================
   REMOVE FROM CART
   ========================================= */

function removeFromCart(productId) {

    cart = cart.filter(
        product => product.id !== productId
    );

    localStorage.setItem(
        "bayzidCart",
        JSON.stringify(cart)
    );

    updateCartCount();

    if (typeof renderCart === "function") {
        renderCart();
    }
}


/* =========================================
   CLEAR CART
   ========================================= */

function clearCart() {

    cart = [];

    localStorage.setItem(
        "bayzidCart",
        JSON.stringify(cart)
    );

    updateCartCount();

    if (typeof renderCart === "function") {
        renderCart();
    }

    showNotification("Cart cleared.");
}


/* =========================================
   SEARCH PRODUCTS
   ========================================= */

function searchProducts() {

    const input =
        document.getElementById("searchInput");

    if (!input) return;

    const searchTerm =
        input.value.trim();

    if (!searchTerm) {
        showNotification(
            "Please enter a product name."
        );
        return;
    }

    // Later this will connect with
    // Django product API.
    window.location.href =
        `products.html?search=${encodeURIComponent(searchTerm)}`;
}


/* =========================================
   SEARCH WITH ENTER KEY
   ========================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        updateCartCount();

        const searchInput =
            document.getElementById("searchInput");

        if (searchInput) {

            searchInput.addEventListener(
                "keydown",
                function (event) {

                    if (event.key === "Enter") {
                        searchProducts();
                    }

                }
            );
        }

    }
);


/* =========================================
   NEWSLETTER
   ========================================= */

function subscribeNewsletter(event) {

    event.preventDefault();

    const emailInput =
        document.getElementById("newsletterEmail");

    if (!emailInput) return;

    const email =
        emailInput.value.trim();

    if (!email) {
        showNotification(
            "Please enter your email."
        );
        return;
    }

    // Demo only.
    // Later connect this with Django backend.

    showNotification(
        "Thank you! You are subscribed."
    );

    emailInput.value = "";
}


/* =========================================
   NOTIFICATION
   ========================================= */

function showNotification(message) {

    const oldNotification =
        document.querySelector(
            ".bayzid-notification"
        );

    if (oldNotification) {
        oldNotification.remove();
    }


    const notification =
        document.createElement("div");

    notification.className =
        "bayzid-notification";

    notification.textContent =
        message;


    notification.style.position = "fixed";
    notification.style.bottom = "25px";
    notification.style.right = "25px";
    notification.style.zIndex = "9999";
    notification.style.padding = "13px 18px";
    notification.style.background = "#1e3a8a";
    notification.style.color = "#ffffff";
    notification.style.borderRadius = "8px";
    notification.style.fontSize = "14px";
    notification.style.fontWeight = "600";
    notification.style.boxShadow =
        "0 8px 25px rgba(0,0,0,0.15)";


    document.body.appendChild(
        notification
    );


    setTimeout(function () {

        notification.remove();

    }, 2500);
}


/* =========================================
   PRODUCT FILTER
   ========================================= */

function filterProducts(category) {

    const products =
        document.querySelectorAll(
            ".product-card"
        );

    products.forEach(function (product) {

        const productCategory =
            product.dataset.category;

        if (
            category === "all" ||
            productCategory === category
        ) {

            product.style.display = "";

        } else {

            product.style.display = "none";

        }

    });
}


/* =========================================
   SORT PRODUCTS
   ========================================= */

function sortProducts(sortType) {

    const grid =
        document.getElementById(
            "productGrid"
        );

    if (!grid) return;

    const products =
        Array.from(
            grid.querySelectorAll(
                ".product-card"
            )
        );


    products.sort(function (a, b) {

        const priceA =
            parseFloat(
                a.dataset.price || 0
            );

        const priceB =
            parseFloat(
                b.dataset.price || 0
            );


        if (sortType === "low") {
            return priceA - priceB;
        }

        if (sortType === "high") {
            return priceB - priceA;
        }

        return 0;

    });


    products.forEach(function (product) {

        grid.appendChild(product);

    });
}


/* =========================================
   MOBILE MENU
   ========================================= */

function toggleMobileMenu() {

    const navigation =
        document.querySelector(
            ".navigation"
        );

    if (!navigation) return;

    navigation.classList.toggle(
        "mobile-menu-open"
    );
}


/* =========================================
   LOGIN DEMO
   ========================================= */

function loginUser(event) {

    event.preventDefault();

    const email =
        document.getElementById(
            "loginEmail"
        )?.value.trim();

    const password =
        document.getElementById(
            "loginPassword"
        )?.value;


    if (!email || !password) {

        showNotification(
            "Please enter email and password."
        );

        return;
    }


    /*
       DEMO LOGIN

       Real authentication will be
       handled by Django later.
    */

    localStorage.setItem(
        "bayzidUser",
        JSON.stringify({
            email: email
        })
    );


    showNotification(
        "Login successful!"
    );


    setTimeout(function () {

        window.location.href =
            "index.html";

    }, 1000);
}


/* =========================================
   LOGOUT
   ========================================= */

function logoutUser() {

    localStorage.removeItem(
        "bayzidUser"
    );

    showNotification(
        "You have been logged out."
    );

    setTimeout(function () {

        window.location.href =
            "index.html";

    }, 800);
}


/* =========================================
   CHECK USER LOGIN
   ========================================= */

function getCurrentUser() {

    const user =
        localStorage.getItem(
            "bayzidUser"
        );

    if (!user) {
        return null;
    }

    try {

        return JSON.parse(user);

    } catch (error) {

        return null;

    }
}


/* =========================================
   PRICE FORMAT
   ========================================= */

function formatPrice(price) {

    return new Intl.NumberFormat(
        "en-BD",
        {
            style: "currency",
            currency: "BDT",
            maximumFractionDigits: 0
        }
    ).format(price);
}


/* =========================================
   PAGE INITIALIZATION
   ========================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        updateCartCount();

        console.log(
            "Bayzid Marketplace loaded successfully."
        );

    }
);
