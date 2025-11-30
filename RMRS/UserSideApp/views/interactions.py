"""User interactions view (reviews and favorites) for UserSideApp."""

from django.contrib import messages
from django.shortcuts import redirect

from ..auth_utils import get_current_user, user_login_required
from ..forms import FavoriteForm, ReviewForm
from ..models import Favorite, Review
from .utils import _render


@user_login_required
def interactions(request):
    """Manage user reviews and favorites."""
    user = get_current_user(request)
    edit_review_id = request.GET.get("edit_review")
    editing_review = None
    if edit_review_id:
        editing_review = (
            Review.objects.filter(user=user, pk=edit_review_id)
            .select_related("restaurant", "meal")
            .first()
        )
        if not editing_review:
            messages.error(request, "找不到要編輯的評論。")
    review_form = ReviewForm(user=user, instance=editing_review)
    favorite_form = FavoriteForm(user=user)
    user_reviews = (
        Review.objects.filter(user=user)
        .select_related("restaurant", "meal", "meal__restaurant")
        .order_by("-created_at")
    )
    favorites = (
        Favorite.objects.filter(user=user)
        .select_related("meal", "meal__restaurant")
        .order_by("-created_at")
    )
    if request.method == "POST":
        action = request.POST.get("form_type")
        if action == "review":
            review_instance = None
            review_id = request.POST.get("review_id")
            if review_id:
                review_instance = Review.objects.filter(user=user, pk=review_id).first()
                if not review_instance:
                    messages.error(request, "無法編輯指定的評論。")
            review_form = ReviewForm(user=user, data=request.POST, instance=review_instance)
            if review_form.is_valid():
                meal = review_form.cleaned_data["meal"]
                duplicate_qs = Review.objects.filter(user=user, meal=meal)
                if review_instance:
                    duplicate_qs = duplicate_qs.exclude(pk=review_instance.pk)
                if duplicate_qs.exists():
                    review_form.add_error(
                        "meal",
                        "你已評論過此餐點，可直接編輯原評論。",
                    )
                else:
                    review_form.save()
                    if review_instance:
                        messages.success(request, "評論已更新。")
                    else:
                        messages.success(request, "感謝您的評論！")
                    return redirect("usersideapp:interactions")
            editing_review = review_instance or editing_review
            messages.error(request, "評論送出失敗，請檢查欄位。")
        elif action == "favorite_add":
            favorite_form = FavoriteForm(user=user, data=request.POST)
            if favorite_form.is_valid():
                favorite_form.save()
                messages.success(request, "已加入收藏餐點。")
                return redirect("usersideapp:interactions")
            messages.error(request, "收藏失敗，請重新選擇餐點。")
        elif action == "favorite_remove":
            favorite_id = request.POST.get("favorite_id")
            deleted, _ = Favorite.objects.filter(user=user, pk=favorite_id).delete()
            if deleted:
                messages.success(request, "已移除收藏餐點。")
            else:
                messages.error(request, "找不到要移除的收藏。")
            return redirect("usersideapp:interactions")
    return _render(
        request,
        "usersideapp/interactions.html",
        "interactions",
        {
            "review_form": review_form,
            "favorite_form": favorite_form,
            "user_reviews": user_reviews,
            "favorites": favorites,
            "editing_review": editing_review,
        },
    )
