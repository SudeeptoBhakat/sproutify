// Razorpay SDK
<script src="https://checkout.razorpay.com/v1/checkout.js"></script>

document.addEventListener('DOMContentLoaded', async () => {
    const authToken = localStorage.getItem("authToken");
    if (!authToken) {
        alert("Please login to view your cart.");
        return window.location.href = "/login/";
    }

    try {
        const res = await fetch("/api/cart/", {
            headers: {
                "Authorization": `Token ${authToken}`,
                "Content-Type": "application/json"
            }
        });

        if (!res.ok) throw new Error("Failed to fetch cart data");
        const data = await res.json();

        const cartContainer = document.querySelector(".cart-items");
        const summaryContainer = document.querySelector(".order-summary");
        const addressBlock = document.querySelector(".address-block");

        if (!cartContainer || !summaryContainer || !addressBlock) {
            console.error("Missing required containers in HTML.");
            return;
        }

        if (!data.items || data.items.length === 0) {
            cartContainer.innerHTML = `<p>Your cart is empty. Start adding some beautiful plants! 🌿</p>`;
            summaryContainer.innerHTML = "";
            addressBlock.innerHTML = "";
            return;
        }

        // 🛒 Render Cart Items
        cartContainer.innerHTML = data.items.map(item => `
      <div class="cart-item">
        <img src="${item.image}" alt="${item.product_name}" class="product-img" />
        <div class="item-details">
          <h2>${item.product_name}</h2>
          <p>Size: ${item.pot_size || 'Standard'} | ₹${item.price_at_time}</p>
          <p>Estimated Delivery: <strong>${data.delivery_start} - ${data.delivery_end}</strong></p>
          <div class="qty-control">
            <button onclick="updateQuantity(${item.id}, 'decrease')">−</button>
            <span class="qty">${item.quantity}</span>
            <button onclick="updateQuantity(${item.id}, 'increase')">+</button>
          </div>
          <button class="remove" onclick="removeItem(${item.id})">🗑 Remove</button>
        </div>
        <div class="item-price">₹${item.total_price}</div>
      </div>
    `).join("");

        // 🧾 Render Summary
        summaryContainer.innerHTML = `
      <h3>Order Summary</h3>
      <div class="summary-row"><span>Subtotal</span><span>₹${data.total}</span></div>
      <div class="summary-row"><span>Shipping</span><span>Free</span></div>
      <div class="summary-row"><span>Discount</span><span>₹${data.discount}</span></div>
      <hr>
      <div class="summary-row total"><strong>Total</strong><strong id="finalTotal">₹${data.final_total}</strong></div>
      <button class="checkout-btn">Proceed to Checkout</button>
      <div class="secure-msg">🔒 Secure payment gateway</div>
    `;

        // 🚚 Render Shipping Address
        const user = data.user;
        addressBlock.innerHTML = `
      <h3>Shipping To:</h3>
      <p>
        ${user.first_name} ${user.last_name}<br>
        ${user.street}, ${user.address_line1}, ${user.district}, ${user.state}<br>
        Pincode: ${user.pin_code}
      </p>
      <a href="#" class="edit-address">Edit</a>
    `;

        // 💳 Attach Razorpay Checkout
        const checkoutBtn = document.querySelector(".checkout-btn");
        if (checkoutBtn) {
            checkoutBtn.addEventListener("click", async () => {
                const total = parseFloat(document.getElementById("finalTotal").innerText.replace("₹", "").trim());

                // Optional: You can get this from user profile or pre-filled form
                const shippingInfo = {
                    full_name: user?.first_name + " " + user?.last_name,
                    phone: user?.phone || "9999999999",  // fallback if not present
                    state: user?.state || "",
                    district: user?.district || "",
                    address_line1: user?.address_line1 || "",
                    street: user?.street || "",
                    pin: user?.pin_code || "",
                    notes: ""
                };

                try {
                    const paymentRes = await fetch("/api/create-razorpay-order/", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "Authorization": `Token ${authToken}`
                        },
                        body: JSON.stringify({
                            amount: total,
                            ...shippingInfo
                        })
                    });

                    const paymentData = await paymentRes.json();
                    if (!paymentData.order_id) {
                        return alert("Payment initiation failed.");
                    }

                    const razorpay = new Razorpay({
                        key: paymentData.razorpay_key,
                        amount: paymentData.amount,
                        currency: "INR",
                        name: "Sproutify",
                        description: "Nursery Plants Purchase",
                        order_id: paymentData.order_id,
                        handler: async function (response) {
                            const verifyRes = await fetch("/api/verify-payment/", {
                                method: "POST",
                                headers: {
                                    "Content-Type": "application/json",
                                    "Authorization": `Token ${authToken}`
                                },
                                body: JSON.stringify({
                                    ...response,
                                    order_db_id: paymentData.order_db_id
                                })
                            });

                            const verifyData = await verifyRes.json();
                            if (verifyRes.ok) {
                                alert("✅ Payment Successful!");
                                window.location.href = "/order-success/";
                            } else {
                                alert("❌ Payment verification failed: " + (verifyData.error || "Unknown error"));
                            }
                        },
                        prefill: {
                            name: shippingInfo.full_name,
                            contact: shippingInfo.phone
                        },
                        theme: {
                            color: "#27ae60"
                        }
                    });

                    razorpay.open();

                } catch (error) {
                    console.error("Razorpay Init Error:", error);
                    alert("Something went wrong. Try again later.");
                }
            });
        } else {
            console.warn("Checkout button not found.");
        }

    } catch (err) {
        console.error("Cart load error:", err);
        alert("Something went wrong while loading the cart.");
        // Optionally:
        // localStorage.removeItem("authToken");
        // window.location.href = "/login/";
    }
});