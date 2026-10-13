/* ==========================================
        LOGIN CHECK
========================================== */

if(localStorage.getItem("isLoggedIn") !== "true"){

    alert("Please login first!");

    localStorage.setItem("redirectAfterLogin","cart.html");

    window.location.href="login.html";

}

/* ==========================================
        LOAD CART
========================================== */

function loadCart(){

    let cart = JSON.parse(localStorage.getItem("electrohub_cart")) || [];

    let container = document.getElementById("cartContainer");

    let totalItems = document.getElementById("totalItems");

    let subtotal = document.getElementById("subtotal");

    let grandTotal = document.getElementById("grandTotal");

    container.innerHTML="";

    if(cart.length===0){

        container.innerHTML=`

        <div class="empty-cart">

        <i class="bi bi-cart-x"></i>

        <h2>Your Cart is Empty</h2>

        <p>

        Add your favourite gadgets and they will appear here.

        </p>

        <a href="product.html" class="shop-btn">

        Continue Shopping

        </a>

        </div>

        `;

        totalItems.innerHTML="0";

        subtotal.innerHTML="₹0";

        grandTotal.innerHTML="₹0";

        return;

    }

    let items=0;

    let total=0;

    cart.forEach((product,index)=>{

        items += product.quantity;

        total += product.price * product.quantity;

        container.innerHTML +=`

<div class="cart-card">

<div class="row align-items-center">

<div class="col-md-3">

<img src="${product.image}"

class="product-image">

</div>

<div class="col-md-5">

<h4 class="product-name">

${product.name}

</h4>

<p class="product-price">

₹${product.price.toLocaleString()}

</p>

<p class="item-total">

Total :

₹${(product.price*product.quantity).toLocaleString()}

</p>

</div>

<div class="col-md-4">

<div class="quantity-box">

<button
class="minus-btn"
onclick="decreaseQty(${index})">

<i class="bi bi-dash"></i>

</button>

<span class="quantity-value">

${product.quantity}

</span>

<button
class="plus-btn"
onclick="increaseQty(${index})">

<i class="bi bi-plus"></i>

</button>

</div>

<button
class="remove-btn"
onclick="removeItem(${index})">

<i class="bi bi-trash"></i>

Remove

</button>

</div>

</div>

</div>

`;

    });

    totalItems.innerHTML=items;

    subtotal.innerHTML="₹"+total.toLocaleString();

    grandTotal.innerHTML="₹"+total.toLocaleString();

}

/* ==========================================
        INCREASE QUANTITY
========================================== */
function increaseQty(index){

    let cart = JSON.parse(localStorage.getItem("electrohub_cart")) || [];

    cart[index].quantity = Number(cart[index].quantity) + 1;

    localStorage.setItem("electrohub_cart", JSON.stringify(cart));

    loadCart();

}

/* ==========================================
        DECREASE QUANTITY
========================================== */
function decreaseQty(index){

    let cart = JSON.parse(localStorage.getItem("electrohub_cart")) || [];

    if(cart[index].quantity > 1){

        cart[index].quantity = Number(cart[index].quantity) - 1;

    }else{

        cart.splice(index,1);

    }

    localStorage.setItem("electrohub_cart", JSON.stringify(cart));

    loadCart();

}

/* ==========================================
        REMOVE PRODUCT
========================================== */

function removeItem(index){

    let cart = JSON.parse(localStorage.getItem("electrohub_cart")) || [];

    let confirmDelete = confirm("Remove this product from cart?");

    if(confirmDelete){

        cart.splice(index,1);

        localStorage.setItem("electrohub_cart",JSON.stringify(electrohub_cart));

        loadCart();

    }

}

/* ==========================================
        CLEAR CART
========================================== */

function clearCart(){

    let confirmClear = confirm("Clear your entire cart?");

    if(confirmClear){

        localStorage.removeItem("electrohub_cart");

        loadCart();

    }

}

/* ==========================================
        CHECKOUT
========================================== */

function checkoutCart(){

    let cart = JSON.parse(localStorage.getItem("electrohub_cart")) || [];

    if(cart.length===0){

        alert("Your cart is empty!");

        return;

    }

    window.location.href="checkout.html";

}

/* ==========================================
        PAGE LOAD
========================================== */

window.onload=function(){

    loadCart();

}