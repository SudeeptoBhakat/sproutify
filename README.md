# Sproutify  

**Sproutify** is a modern, plant‑focused e‑commerce platform that lets users discover, browse, and purchase a curated selection of indoor, outdoor, succulent, bonsai, and fruit plants. It provides a full shopping experience—from product catalog and search to cart, checkout (Razorpay), order tracking, and invoicing—while delivering a clean, responsive UI built with vanilla HTML, CSS and JavaScript.

> **Live demo:** The repository is currently in development mode. Follow the setup instructions below to run the app locally.

---  

## Table of Contents  

1. [Features](#features)  
2. [Tech Stack](#tech-stack)  
3. [Architecture Overview](#architecture-overview)  
4. [API Endpoints](#api-endpoints)  
5. [Installation & Running Locally](#installation--running-locally)  
6. [Contributing](#contributing)  
7. [License](#license)  

---  

## Features  

| ✅ | Feature | Details |
|---|---|---|
| 💚 | **User Registration & Login** | Custom user model with email/phone authentication; JWT & token‑based API auth【14†L44-L58】【17†L34-L50】 |
| 🌱 | **Product Catalog** | Plants are stored as `Product` objects with rich meta‑data (category, pot size, sunlight, water frequency, etc.)【18†L94-L106】【18†L110-L116】 |
| 🔍 | **Search & Filtering** | Fast “search‑as‑you‑type” endpoint (`/api/product-search/`) that returns up to 10 matching products【46†L34-L36】 |
| 🛒 | **Shopping Cart** | Add, update, and delete items; live cart UI with quantity controls, price‑calc & discount logic【33†L33-L44】【40†L41-L56】 |
| 💳 | **Razorpay Checkout** | Secure payment flow – creates Razorpay order, opens Razorpay widget, verifies signature and marks order as paid【41†L122-L129】【41†L130-L144】 |
| 📦 | **Order Management** | Order creation, status tracking (pending → processing → shipped → delivered), invoice generation, and order‑tracking UI【34†L63-L84】【34†L85-L120】 |
| 🗂️ | **Admin Dashboard** | Django admin provides full CRUD for products, users and orders【14†L37-L49】 |
| 📱 | **Responsive Design** | Mobile‑first layout with CSS grid/flex; fade‑in scroll animation and pre‑loader for smooth UX【9†L11-L22】【47†L27-L68】 |
| 📞 | **WhatsApp Quick‑Contact** | Floating WhatsApp button for instant support【9†L32-L43】 |
| ⚡ | **Performance Optimisations** | Lazy product loading, pre‑loader animation, client‑side caching of auth token, and static assets served via Django’s `staticfiles` framework【9†L71-L84】【31†L1-L22】 |

---  

## Tech Stack  

| Layer | Technology | Why it’s used |
|-------|-------------|----------------|
| **Backend** | **Django 5.1** – full‑stack web framework【14†L6-L9】 | Handles routing, ORM, admin panel, and templating |
| | **Django REST Framework** – for API endpoints【14†L44-L48】 | Provides browsable API, serializers, viewsets |
| | **Simple JWT** – JWT authentication【14†L51-L55】 | Stateless token auth for SPA‑style front‑end |
| | **Django Rest Framework TokenAuth** – fallback token auth【14†L55-L58】 |
| | **SQLite** – development database【14†L94-L98】 | Zero‑config local DB |
| | **Razorpay Python SDK** – payment gateway integration【14†L154-L156】 | Secure, Indian‑centric checkout |
| **Frontend** | **HTML5 + CSS3** – templating with Django `templates` folder (e.g., `index.html`, `product_detail.html`)【52†L28-L30】【36†L10-L14】 | Semantic markup & styling |
| | **Vanilla JavaScript** – UI logic for carousel, cart, checkout, pre‑loader (files `static/js/*.js`)【38†L4-L12】【40†L6-L15】 | No heavy front‑end framework required |
| | **Razorpay JS SDK** – embedded payment widget【41†L122-L129】 | Smooth checkout flow |
| | **Google Fonts** – custom typography (Poppins, Aboreto)【9†L3-L5】 | Consistent branding |
| **DevOps** | **Git** – source control (GitHub) | Collaboration & versioning |
| | **Docker (optional)** – can be added for containerised deployment | Production‑ready scaling |
| **Other** | **Static assets** – images stored in `media/products/` (e.g., plant photos)【42†L35-L45】 | High‑quality product visuals |

---  

## Architecture Overview  

```
sproutify/
│
├─ manage.py                     # Django CLI entry point
│
├─ sproutify/                    # Core project settings
│   ├─ __init__.py
│   ├─ settings.py               # DB, INSTALLED_APPS, Razorpay keys
│   ├─ urls.py                   # Includes users & orders URLs
│   ├─ wsgi.py / asgi.py
│
├─ users/                        # User‑related logic
│   ├─ models.py                # CustomUser + Product + Review
│   ├─ serializers.py
│   ├─ views.py                  # Register, login, profile, product list/search
│   └─ urls.py
│
├─ orders/                       # Cart, Order, Payment, Invoice
│   ├─ models.py                # Cart, Order, OrderItem, Payment, Tracking
│   ├─ serializers.py
│   ├─ views.py                 # Cart API, Razorpay order creation, verification
│   └─ urls.py
│
├─ templates/                    # HTML templates (index, product_detail, basket, orders, profile, …)
│   ├─ partials/                 # login_popup, register_popup, navbar, preloader, whatsapp, footer
│   └─ *.html
│
└─ static/                       # CSS & JS
    ├─ css/
    │   ├─ styles.css            # Global styles, fade‑in, preloader, WhatsApp button
    │   └─ product_overview.css  # Product‑grid & responsive utilities
    └─ js/
        ├─ main.js               # Carousel logic
        └─ checkout.js           # Cart rendering & Razorpay integration
```

*The UI is built entirely with Django template inheritance, making the front‑end lightweight and SEO‑friendly.*  

---  

## API Endpoints  

| Method | Path | Description |
|--------|------|-------------|
| **Auth** | `POST /api/login/` | Returns JWT token and user data【25†L23-L24】 |
| | `POST /api/validate-token/` | Confirms token validity【25†L31-L33】 |
| **Products** | `GET /api/products/` | Public product list (no auth)【46†L31-L33】 |
| | `POST /api/products/create/` | Admin‑only create product【46†L34-L36】 |
| | `GET /api/product-search/?q=…` | Search products (max 10)【46†L34-L36】 |
| **Cart** | `GET /api/cart/` | Retrieve current user’s cart items【33†L33-L44】 |
| | `POST /api/cart/add/` | Add a product to the cart (authenticated)【22†L30-L38】 |
| | `PUT /api/cart/update/<id>/` | Increase / decrease quantity【23†L105-L111】 |
| | `DELETE /api/cart/delete/<id>/` | Remove item from cart【23†L118-L124】 |
| **Checkout** | `POST /api/create-razorpay-order/` | Creates a Razorpay order & DB order record【41†L172-L190】 |
| | `POST /api/verify-payment/` | Verifies Razorpay signature, marks payment & order paid【41†L236-L254】 |
| **Orders** | `GET /api/orders/` | List all orders for the logged‑in user【45†L31-L33】 |
| | `GET /api/user-orders-items/` | Detailed order items for the current user【45†L34-L35】 |
| **Payments** | `GET /api/payment-methods/` | Available payment methods (Razorpay, etc.)【45†L13-L15】 |
| | `GET /api/payments/` | View payment records (admin) |
| **Tracking** | `GET /api/tracking/` | Retrieve tracking number & status【45†L37-L38】 |
| **Invoices** | `GET /api/invoice/` | Download generated PDF invoice【45†L39-L40】 |

All endpoints return JSON responses and are protected by `IsAuthenticated` permission where appropriate.

---  

## Installation & Running Locally  

1. **Clone the repository**  

   ```bash
   git clone https://github.com/SudeeptoBhakat/sproutify.git
   cd sproutify
   ```

2. **Create and activate a virtual environment**  

   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**  

   The repo does not ship a `requirements.txt`, but the project uses the following packages. Install them with pip:

   ```bash
   pip install Django==5.1.7 \
               djangorestframework \
               djangorestframework-simplejwt \
               djangorestframework-authtoken \
               razorpay
   ```

4. **Configure environment variables**  

   Edit `sproutify/sproutify/settings.py` and replace the placeholder Razorpay keys with your own test credentials (or keep the test keys that are already in the file)【14†L154-L156】.  
   Optionally add a `.env` file and load it via `python-decouple` if you prefer.

5. **Run migrations & create a superuser**

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Collect static files (optional for production)**  

   ```bash
   python manage.py collectstatic
   ```

7. **Start the development server**

   ```bash
   python manage.py runserver
   ```

8. **Visit the app**  

   Open `http://127.0.0.1:8000/` in your browser.  
   - Register a new user via the **Register** popup.  
   - Browse the plant catalog, add items to the cart, and test the checkout flow using Razorpay’s test mode.  
   - Check the **Orders** page to see created orders, invoices, and tracking numbers.

> **Note:** The site is currently in development mode; no public URL is available yet.

---  

## Contributing  

Contributions are welcome! To submit a change:

1. Fork the repository.  
2. Create a feature branch (`git checkout -b feature/awesome‑feature`).  
3. Make your changes, write tests if applicable.  
4. Run `python manage.py test` to ensure everything passes.  
5. Open a Pull Request describing the changes.

Please follow the existing code style (PEP 8) and keep the front‑end consistent with the current design language (CSS variables, fade‑in sections, and mobile‑first breakpoints).

---  

### Acknowledgements  

- **Razorpay** for the easy‑to‑integrate payment SDK.  
- **Django** and **Django REST Framework** for providing a robust full‑stack foundation.  
- Plant images contributed from the `media/products/` folder (e.g., Guava, Pots)【42†L35-L45】.  

---  

*Happy planting! 🌿*  
