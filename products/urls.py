from django.urls import path
from . import views


urlpatterns = [

    # =====================================================
    # HOME
    # =====================================================

    path("", views.home, name="home"),

    # =====================================================
    # LOADING
    # =====================================================

    path(
        "loading/",
        views.loading,
        name="loading"
    ),

    # =====================================================
    # CATEGORY
    # =====================================================

    path(
        "men/",
        views.men,
        name="men"
    ),

    path(
        "women/",
        views.women,
        name="women"
    ),

    path(
        "kids/",
        views.kids,
        name="kids"
    ),

    path(
        "offers/",
        views.offers,
        name="offers"
    ),

    # =====================================================
    # PRODUCT
    # =====================================================

    path(
        "product/<int:id>/",
        views.product_detail,
        name="product_detail"
    ),

    # =====================================================
    # CART
    # =====================================================

    path(
        "cart/",
        views.cart,
        name="cart"
    ),

    path(
        "add-to-cart/<int:id>/",
        views.add_to_cart,
        name="add_to_cart"
    ),

    path(
        "remove-from-cart/<int:cart_id>/",
        views.remove_from_cart,
        name="remove_from_cart"
    ),

    path(
        "update-cart-quantity/",
        views.update_cart_quantity,
        name="update_cart_quantity"
    ),

    # =====================================================
    # CHECKOUT
    # =====================================================

    path(
        "checkout/",
        views.checkout,
        name="checkout"
    ),

    path(
        "place-order/",
        views.place_order,
        name="place_order"
    ),

    # =====================================================
    # PAYMENT
    # =====================================================

    path(
        "payment/success/",
        views.payment_success,
        name="payment_success"
    ),

    # =====================================================
    # ORDERS
    # =====================================================

    path(
        "orders/",
        views.orders,
        name="orders"
    ),

    path(
        "my-orders/",
        views.my_orders,
        name="my_orders"
    ),

    path(
        "order-success/<int:order_id>/",
        views.order_success,
        name="order_success"
    ),

    path(
        "delete-order/<int:order_id>/",
        views.delete_order,
        name="delete_order"
    ),

    # =====================================================
    # WISHLIST
    # =====================================================

    path(
        "wishlist/",
        views.wishlist,
        name="wishlist"
    ),

    path(
        "add-to-wishlist/<int:id>/",
        views.add_to_wishlist,
        name="add_to_wishlist"
    ),

    path(
        "remove-from-wishlist/<int:wishlist_id>/",
        views.remove_from_wishlist,
        name="remove_from_wishlist"
    ),

    # =====================================================
    # PROFILE
    # =====================================================

    path(
        "profile/",
        views.profile,
        name="profile"
    ),

    path(
        "profile/edit/",
        views.edit_profile,
        name="edit_profile"
    ),

    path(
        "profile/change-password/",
        views.change_password,
        name="change_password"
    ),

    # =====================================================
    # ADDRESS
    # =====================================================

    path(
        "address/",
        views.address,
        name="address"
    ),

    path(
        "address/edit/<int:id>/",
        views.edit_address,
        name="edit_address"
    ),

    path(
        "address/delete/<int:id>/",
        views.delete_address,
        name="delete_address"
    ),

    # =====================================================
    # SETTINGS
    # =====================================================

    path(
        "settings/",
        views.settings_page,
        name="settings"
    ),

    path(
        "settings/notifications/",
        views.notifications,
        name="notifications"
    ),

    path(
        "settings/order-updates/",
        views.order_updates,
        name="order_updates"
    ),

    path(
        "settings/offers/",
        views.offers,
        name="settings_offers"
    ),

    path(
        "settings/preferences/",
        views.preferences,
        name="preferences"
    ),

    path(
        "settings/theme/",
        views.theme,
        name="theme"
    ),

    path(
        "settings/language/",
        views.language,
        name="language"
    ),

    path(
        "settings/privacy-security/",
        views.privacy_security,
        name="privacy_security"
    ),

    path(
        "settings/security/",
        views.security,
        name="security"
    ),

    path(
        "settings/delete-account/",
        views.delete_account,
        name="delete_account"
    ),

    # =====================================================
    # HELP & CONTACT
    # =====================================================

    path(
        "help-support/",
        views.help_support,
        name="help_support"
    ),

path(
    "settings/notifications/",
    views.notifications,
    name="notifications"
),

path("settings/address/", views.address, name="my_address"),
    path("settings/", views.settings_page, name="settings"),




    path(
        "contact/",
        views.contact,
        name="contact"
    ),

    path(
        "about/",
        views.about,
        name="about"
    ),

    # =====================================================
    # REGISTER
    # =====================================================

    path(
        "register/",
        views.register,
        name="register"
    ),
]