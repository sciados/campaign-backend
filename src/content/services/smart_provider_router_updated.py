# UPDATED select_text_provider and select_image_provider methods
# Replace these in smart_provider_router.py

def select_text_provider(
    self,
    user_tier: str,
    task_complexity: str,
    content_type: str,
    credits_remaining: int,
    user_preference: Optional[str] = None
) -> Dict[str, Any]:
    """
    Select optimal text AI provider with quality warnings and upgrade suggestions

    Args:
        user_tier: User's subscription tier
        task_complexity: Complexity of the task
        content_type: Type of content being generated
        credits_remaining: User's remaining credits
        user_preference: User's provider preference (agency tier only)

    Returns:
        Dict with provider name, estimated cost, quality level, warnings, and suggestions
    """

    try:
        tier_enum = UserTier(user_tier.lower())
        complexity_enum = TaskComplexity(task_complexity.lower())
    except ValueError as e:
        logger.warning(f"Invalid tier or complexity: {e}, using defaults")
        tier_enum = UserTier.FREE
        complexity_enum = TaskComplexity.STANDARD

    # Agency users can override provider selection
    if tier_enum == UserTier.AGENCY and user_preference:
        if user_preference in self.PROVIDER_COSTS:
            provider = user_preference
        else:
            provider = self.TEXT_PROVIDER_MATRIX[tier_enum][complexity_enum]
    else:
        provider = self.TEXT_PROVIDER_MATRIX[tier_enum][complexity_enum]

    # Track original provider for comparison
    original_provider = provider
    original_quality = self.PROVIDER_COSTS[provider]["quality"]

    # Check if credits running low, downgrade provider if needed
    low_credit_warning = None
    if credits_remaining < 50 and tier_enum != UserTier.FREE:
        provider = self._get_fallback_text_provider(provider)
        new_quality = self.PROVIDER_COSTS[provider]["quality"]
        logger.warning(f"⚠️ Low credits ({credits_remaining}), downgrading to {provider}")

        low_credit_warning = {
            "type": "low_credits",
            "message": f"You have {credits_remaining} credits remaining. A lower quality provider ({provider}, quality {new_quality}/5) will be used instead of {original_provider} (quality {original_quality}/5) to preserve your credits.",
            "credits_remaining": credits_remaining,
            "original_provider": original_provider,
            "downgraded_provider": provider,
            "quality_difference": original_quality - new_quality,
            "action": "buy_credits",
            "action_text": "Buy More Credits"
        }

    provider_info = self.PROVIDER_COSTS[provider]

    # Check if user could benefit from tier upgrade
    upgrade_suggestion = None
    if tier_enum != UserTier.AGENCY and not low_credit_warning:
        next_tier = self._get_next_tier(tier_enum)
        if next_tier:
            next_tier_provider = self.TEXT_PROVIDER_MATRIX[next_tier][complexity_enum]
            next_tier_quality = self.PROVIDER_COSTS[next_tier_provider]["quality"]

            if next_tier_quality > provider_info["quality"]:
                upgrade_suggestion = {
                    "type": "upgrade_available",
                    "message": f"Upgrade to {next_tier.value.title()} tier for better quality content using {next_tier_provider} (quality {next_tier_quality}/5 vs current {provider_info['quality']}/5)",
                    "current_tier": tier_enum.value,
                    "recommended_tier": next_tier.value,
                    "current_provider": provider,
                    "upgrade_provider": next_tier_provider,
                    "quality_improvement": next_tier_quality - provider_info["quality"],
                    "action": "upgrade_tier",
                    "action_text": f"Upgrade to {next_tier.value.title()}"
                }

    result = {
        "provider": provider,
        "quality": provider_info["quality"],
        "input_cost_per_1m": provider_info["input"],
        "output_cost_per_1m": provider_info["output"],
        "tier": user_tier,
        "complexity": task_complexity
    }

    # Add warnings/suggestions if present
    if low_credit_warning:
        result["warning"] = low_credit_warning
    if upgrade_suggestion:
        result["suggestion"] = upgrade_suggestion

    return result


def select_image_provider(
    self,
    user_tier: str,
    image_type: str,
    credits_remaining: int,
    user_preference: Optional[str] = None
) -> Dict[str, Any]:
    """
    Select optimal image AI provider with quality warnings and upgrade suggestions

    Args:
        user_tier: User's subscription tier
        image_type: Type of image (social_media, marketing, hero)
        credits_remaining: User's remaining credits
        user_preference: User's provider preference (agency tier only)

    Returns:
        Dict with provider name, cost, quality level, warnings, and suggestions
    """

    try:
        tier_enum = UserTier(user_tier.lower())
    except ValueError:
        tier_enum = UserTier.FREE

    # Agency users can override
    if tier_enum == UserTier.AGENCY and user_preference:
        if user_preference in self.PROVIDER_COSTS:
            provider = user_preference
        else:
            tier_providers = self.IMAGE_PROVIDER_MATRIX[tier_enum]
            provider = tier_providers.get(image_type, tier_providers.get("all", "flux-schnell"))
    else:
        tier_providers = self.IMAGE_PROVIDER_MATRIX[tier_enum]
        provider = tier_providers.get(image_type, tier_providers.get("all", "flux-schnell"))

    # Track original provider for comparison
    original_provider = provider
    original_quality = self.PROVIDER_COSTS[provider]["quality"]

    # Low credits fallback
    low_credit_warning = None
    if credits_remaining < 10 and original_provider != "flux-schnell":
        provider = "flux-schnell"
        new_quality = self.PROVIDER_COSTS[provider]["quality"]
        logger.warning(f"⚠️ Low credits ({credits_remaining}), downgrading to {provider}")

        low_credit_warning = {
            "type": "low_credits",
            "message": f"You have {credits_remaining} credits remaining. A lower cost provider ({provider}, quality {new_quality}/5) will be used instead of {original_provider} (quality {original_quality}/5) to preserve your credits.",
            "credits_remaining": credits_remaining,
            "original_provider": original_provider,
            "downgraded_provider": provider,
            "quality_difference": original_quality - new_quality,
            "action": "buy_credits",
            "action_text": "Buy More Credits"
        }

    provider_info = self.PROVIDER_COSTS[provider]

    # Check if user could benefit from tier upgrade for better image quality
    upgrade_suggestion = None
    if tier_enum != UserTier.AGENCY and not low_credit_warning:
        next_tier = self._get_next_tier(tier_enum)
        if next_tier:
            next_tier_providers = self.IMAGE_PROVIDER_MATRIX[next_tier]
            next_tier_provider = next_tier_providers.get(image_type, next_tier_providers.get("all", "flux-schnell"))
            next_tier_quality = self.PROVIDER_COSTS[next_tier_provider]["quality"]

            if next_tier_quality > provider_info["quality"]:
                upgrade_suggestion = {
                    "type": "upgrade_available",
                    "message": f"Upgrade to {next_tier.value.title()} tier for better quality images using {next_tier_provider} (quality {next_tier_quality}/5 vs current {provider_info['quality']}/5)",
                    "current_tier": tier_enum.value,
                    "recommended_tier": next_tier.value,
                    "current_provider": provider,
                    "upgrade_provider": next_tier_provider,
                    "quality_improvement": next_tier_quality - provider_info["quality"],
                    "action": "upgrade_tier",
                    "action_text": f"Upgrade to {next_tier.value.title()}"
                }

    result = {
        "provider": provider,
        "quality": provider_info["quality"],
        "cost_per_image": provider_info["cost"],
        "tier": user_tier,
        "image_type": image_type
    }

    # Add warnings/suggestions if present
    if low_credit_warning:
        result["warning"] = low_credit_warning
    if upgrade_suggestion:
        result["suggestion"] = upgrade_suggestion

    return result
