"""Restaurant search view for UserSideApp."""

import folium
from folium.plugins import Fullscreen, LocateControl
from django.db.models import Q
from django.utils.html import escape

from MerchantSideApp.models import Meal, Restaurant

from ..auth_utils import get_current_user, user_login_required
from ..forms import RestaurantSearchForm
from .utils import _render, DEFAULT_MAP_CENTER, MAX_MAP_RESULTS, MAX_MEAL_RESULTS


@user_login_required
def search_restaurants(request):
    """Search restaurants and display on map."""
    form = RestaurantSearchForm(request.GET or None)
    cleaned_filters = {}
    if form.is_bound and form.is_valid():
        cleaned_filters = form.cleaned_data

    restaurants_qs = Restaurant.objects.filter(is_active=True)
    meals_qs = (
        Meal.objects.filter(is_available=True, restaurant__is_active=True)
        .select_related("restaurant")
    )
    keyword = cleaned_filters.get("keyword")
    if keyword:
        restaurants_qs = restaurants_qs.filter(
            Q(name__icontains=keyword)
            | Q(address__icontains=keyword)
            | Q(cuisine_type__icontains=keyword)
            | Q(meals__name__icontains=keyword)
            | Q(meals__description__icontains=keyword)
        ).distinct()
        meals_qs = meals_qs.filter(
            Q(name__icontains=keyword)
            | Q(description__icontains=keyword)
            | Q(restaurant__name__icontains=keyword)
        )
    city = cleaned_filters.get("city")
    if city:
        restaurants_qs = restaurants_qs.filter(city__icontains=city)
        meals_qs = meals_qs.filter(restaurant__city__icontains=city)
    district = cleaned_filters.get("district")
    if district:
        restaurants_qs = restaurants_qs.filter(district__icontains=district)
        meals_qs = meals_qs.filter(restaurant__district__icontains=district)
    cuisine_type = cleaned_filters.get("cuisine_type")
    if cuisine_type:
        restaurants_qs = restaurants_qs.filter(cuisine_type__icontains=cuisine_type)
        meals_qs = meals_qs.filter(restaurant__cuisine_type__icontains=cuisine_type)
    category = cleaned_filters.get("category")
    if category:
        restaurants_qs = restaurants_qs.filter(meals__category__iexact=category).distinct()
        meals_qs = meals_qs.filter(category__iexact=category)
    price_range = cleaned_filters.get("price_range")
    if price_range:
        restaurants_qs = restaurants_qs.filter(price_range=price_range)
        meals_qs = meals_qs.filter(restaurant__price_range=price_range)

    restaurants_qs = restaurants_qs.order_by("-rating", "name")
    total_results = restaurants_qs.count()
    restaurants = list(restaurants_qs[:MAX_MAP_RESULTS])
    limited = total_results > len(restaurants)

    meals_qs = meals_qs.order_by("name")
    meal_total_results = meals_qs.count()
    meals = list(meals_qs[:MAX_MEAL_RESULTS])
    meal_limited = meal_total_results > len(meals)

    user_location = None
    latitude = cleaned_filters.get("latitude")
    longitude = cleaned_filters.get("longitude")
    if latitude is not None and longitude is not None:
        user_location = (latitude, longitude)

    markers = []
    for restaurant in restaurants:
        if restaurant.latitude is None or restaurant.longitude is None:
            continue
        markers.append(
            {
                "name": restaurant.name,
                "lat": float(restaurant.latitude),
                "lon": float(restaurant.longitude),
                "address": restaurant.address or "",
                "cuisine": restaurant.cuisine_type or "",
                "price": restaurant.get_price_range_display(),
                "rating": restaurant.rating,
            }
        )

    center_lat, center_lon = DEFAULT_MAP_CENTER
    zoom_start = 13 if markers else 7
    if user_location:
        center_lat, center_lon = user_location
        zoom_start = 15
    elif markers:
        center_lat = sum(marker["lat"] for marker in markers) / len(markers)
        center_lon = sum(marker["lon"] for marker in markers) / len(markers)
    restaurant_map = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_start,
        control_scale=True,
        tiles="OpenStreetMap",
        width="100%",
        height="600px",
    )

    Fullscreen(position="topright", title="進入全螢幕", title_cancel="退出全螢幕").add_to(restaurant_map)
    LocateControl(
        auto_start=False,
        keepCurrentZoomLevel=True,
        flyTo=True,
        strings={"title": "移動到目前位置", "popup": "目前位置"},
    ).add_to(restaurant_map)

    bounds_points: list[list[float]] = []
    if user_location:
        folium.CircleMarker(
            location=user_location,
            radius=8,
            color="#2563eb",
            fill=True,
            fill_color="#2563eb",
            fill_opacity=0.9,
            tooltip="目前位置",
        ).add_to(restaurant_map)
        bounds_points.append([user_location[0], user_location[1]])

    if markers:
        bounds_points.extend([[marker["lat"], marker["lon"]] for marker in markers])
    if len(bounds_points) >= 2:
        restaurant_map.fit_bounds(bounds_points, padding=(20, 20))
    elif len(bounds_points) == 1:
        restaurant_map.location = bounds_points[0]
        restaurant_map.zoom_start = 15

    for marker in markers:
        popup_lines = [f"<strong>{escape(marker['name'])}</strong>"]
        if marker["address"]:
            popup_lines.append(escape(marker["address"]))
        detail_parts = []
        if marker["cuisine"]:
            detail_parts.append(escape(marker["cuisine"]))
        if marker["price"]:
            detail_parts.append(escape(marker["price"]))
        if marker["rating"] is not None:
            detail_parts.append(f"評分：{marker['rating']}")
        if detail_parts:
            popup_lines.append(" ・ ".join(detail_parts))
        popup_html = "<br/>".join(popup_lines)
        folium.Marker(
            [marker["lat"], marker["lon"]],
            tooltip=marker["name"],
            popup=folium.Popup(popup_html, max_width=280),
        ).add_to(restaurant_map)

    folium_map_html = restaurant_map._repr_html_()
    map_hint = None
    if not markers and not user_location:
        map_hint = "目前結果缺少座標資訊，顯示預設地圖。"
    elif not markers and user_location:
        map_hint = "已使用您的定位，但目前尚無提供座標的餐廳資料。"

    return _render(
        request,
        "usersideapp/search.html",
        "search",
        {
            "form": form,
            "restaurants": restaurants,
            "result_count": total_results,
            "limit_reached": limited,
            "meals": meals,
            "meal_result_count": meal_total_results,
            "meal_limit_reached": meal_limited,
            "folium_map": folium_map_html,
            "map_has_markers": bool(markers),
            "has_user_location": bool(user_location),
            "map_hint": map_hint,
        },
    )
