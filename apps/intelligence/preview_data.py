"""Example inputs + result payloads shown when an org is in preview
mode (not yet subscribed).

These render in each playground panel as a realistic demo: the input
fields are pre-filled and the result panels show what real output
looks like. Click the Submit button and the
``@intelligence_subscription_required`` decorator swaps the result
panel for the ``_subscribe_required.html`` paywall fragment.

Kept in its own module rather than inlined in ``views.py`` so the
view stays focused on request handling. Data shapes match the
``apps/api/serializers.py`` response schemas exactly — each example
goes through the same result partial that a real API response would.
"""

from __future__ import annotations


# Inputs pre-filled into form fields so the playground reads like a
# realistic walkthrough rather than an empty shell.
PREVIEW_INPUTS = {
    "score_packaging": {
        "title": "How I Built a $1M SaaS in 6 Months",
    },
    "score_video_hook": {
        "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    },
    "benchmark_channel": {
        "url": "https://youtube.com/@EconomicsExplained",
    },
    "benchmark_video": {
        "url": "https://www.youtube.com/watch?v=Nw1jHB4SMio",
    },
    "research_content_gaps": {
        # The combobox uses this as the pre-selected niche.
        "niche_slug": "ai_money_making",
        "niche_name": "ai money making",
    },
}


# Realistic API response payloads — each one passes through the
# corresponding ``_*_result.html`` partial as if it were a real call.
PREVIEW_RESULTS = {
    "score_packaging": {
        "score": 0.72,
        "percentile": 73,
        "raw_score": 0.7521,
        "mode": "title",
        "niche_slug": "entrepreneurship_business_growth",
        "niche_label": "entrepreneurship & business growth",
        "niche_confidence": 0.81,
    },
    "score_video_hook": {
        "score_id": "preview",
        "primary_archetype": "bold_claim",
        "secondary_archetype": "pattern_interrupt",
        "scores": {
            "clarity": 8,
            "specificity": 4,
            "tension": 6,
            "visual_energy": 7,
            "pace": 7,
        },
        "overall_score": 68,
        "transcript": "Ricky Gervais sollte unser aller Vorbild sein. I give a f*ck what you think.",
        "visual_summary": (
            "The host is speaking in a studio setting with dynamic text overlays "
            "appearing on screen in sync with his words, including the name "
            "'RICKY GERVAIS' and the phrase 'I GIVE A F*CK WHAT YOU THINK'."
        ),
        "strengths": [
            "The bold claim at second 0-2 immediately establishes a strong, opinionated stance.",
            "Dynamic text overlays from second 0-5 effectively reinforce the spoken message for viewers watching on mute.",
            "The transition to the English profanity at second 3 acts as a pattern interrupt that grabs attention.",
        ],
        "weaknesses": [
            "The claim that he should be a 'role model' is vague and lacks specific context or evidence at second 1.",
            "There is no clear curiosity gap or stake established; the viewer doesn't know why they should care about this specific opinion.",
            "The visual of the host is static, relying entirely on text overlays for energy.",
        ],
        "suggestions": [
            "Add a specific reason for the claim at second 2, such as 'because he never apologizes for his jokes'.",
            "Include a 1-second clip of a famous Ricky Gervais moment at second 4 to visually ground the bold claim.",
            "Add a specific question at second 5 to force viewer engagement, like 'Do you agree?'",
        ],
        "delta_vs_niche_top": -7,
        "key_differences_vs_top": [
            "Top hooks in this niche introduce specific stakes or a concrete 'why' within the first 4 seconds.",
            "High-performing clips often use a visual demonstration or a specific example rather than just a talking head with text.",
        ],
    },
    "benchmark_channel": {
        "channel": {
            "channel_id": "UCZ4AMrDcNrfy3X6nsU8-rPg",
            "title": "Economics Explained",
            "subscriber_count": 2_860_000,
            "video_count": 431,
            "engagement": {
                "view_to_sub_ratio": 0.1229,
                "like_to_view_ratio": 0.0298,
                "comment_to_view_ratio": 0.003,
            },
            "engagement_percentiles": {
                "view_to_sub_ratio": 50,
                "like_to_view_ratio": 50,
                "comment_to_view_ratio": 42,
                "overall": 47,
            },
            "sample_window_days": 60,
            "title_patterns": {
                "mean_length_chars": 40,
                "mean_length_words": 7,
                "share_with_question_mark": 0.30,
                "share_with_number": 0.10,
                "median_uppercase_ratio": 0.201,
                "share_with_emoji": 0.0,
            },
        },
        "niche": {
            "slug": "geopolitical_news_commentary",
            "name": "geopolitical news commentary",
            "match_score": 0.7561,
            "match_strength": "strong",
            "engagement": {
                "view_to_sub_ratio": {"p50": 0.122},
                "like_to_view_ratio": {"p50": 0.0295},
                "comment_to_view_ratio": {"p50": 0.0035},
            },
            "title_patterns": {
                "mean_length_chars": 66.52,
                "mean_length_words": 10.47,
                "share_with_question_mark": 0.0277,
                "share_with_number": 0.1318,
                "median_uppercase_ratio": 0.2059,
                "share_with_emoji": 0.0764,
                "common_niche_phrases": [
                    {"phrase": "trump s", "frequency": 0.0802, "used_by_channel": False},
                    {"phrase": "u s", "frequency": 0.0592, "used_by_channel": False},
                    {"phrase": "iran war", "frequency": 0.0458, "used_by_channel": True},
                    {"phrase": "white house", "frequency": 0.0325, "used_by_channel": False},
                    {"phrase": "of hormuz", "frequency": 0.0363, "used_by_channel": False},
                    {"phrase": "strait of", "frequency": 0.0344, "used_by_channel": False},
                ],
            },
            "exemplar_channels": [
                {"title": "60 Minutes", "subscriber_count": 0},
                {"title": "Middle East Eye", "subscriber_count": 3_730_000},
                {"title": "CBC News", "subscriber_count": 4_650_000},
                {"title": "Shawn Ryan Show", "subscriber_count": 0},
            ],
        },
    },
    "benchmark_video": {
        "video": {
            "video_id": "Nw1jHB4SMio",
            "title": "ÖRR am Tiefpunkt: Julia Ruhs gecancelt",
            "channel_title": "{ungeskriptet} by Ben",
            "published_at": "2025-09-20T07:59:00+00:00",
            "view_count": 598_823,
            "like_count": 18_044,
            "comment_count": 4_668,
            "engagement": {
                "view_to_sub_ratio": 0.631,
                "like_to_view_ratio": 0.0301,
                "comment_to_view_ratio": 0.0078,
            },
            "engagement_percentiles": {
                "view_to_sub_ratio": 96,
                "like_to_view_ratio": 59,
                "comment_to_view_ratio": 63,
                "overall": 73,
            },
            "title_patterns": {
                "length_chars": 38,
                "has_question": False,
                "has_number": False,
                "has_emoji": False,
                "fits_niche_patterns": False,
            },
        },
        "niche": {
            "slug": "uk_political_commentary",
            "name": "uk political commentary",
            "match_score": 0.7213,
            "match_strength": "moderate",
            "engagement": {
                "view_to_sub_ratio": {"p50": 0.0602},
                "like_to_view_ratio": {"p50": 0.0222},
                "comment_to_view_ratio": {"p50": 0.0050},
            },
            "title_patterns": {
                "mean_length_chars": 73.27,
                "mean_length_words": 11.76,
                "share_with_question_mark": 0.0425,
                "share_with_number": 0.1604,
                "median_uppercase_ratio": 0.1465,
                "share_with_emoji": 0.0472,
                "common_niche_phrases": [
                    {"phrase": "king charles", "frequency": 0.1038, "used_by_channel": False},
                    {"phrase": "prince harry", "frequency": 0.0519, "used_by_channel": False},
                    {"phrase": "keir starmer", "frequency": 0.0519, "used_by_channel": False},
                    {"phrase": "nigel farage", "frequency": 0.0283, "used_by_channel": False},
                ],
            },
        },
    },
    "research_content_gaps": {
        "niche": {"slug": "ai_money_making", "name": "ai money making"},
        "gaps": [
            {
                "canonical_title": "94% Use AI Side Hustles 2026! #shorts #viral",
                "opportunity_score": 65,
                "gap_type": "stale",
                "components": {"demand": 0.24, "supply": 0.04, "recency": 0.10},
                "explanation": (
                    "The assumption that generic 'AI Side Hustles' consistently "
                    "generate '$5K/month' relies on broad, high-level claims that "
                    "lack granular execution details for current market conditions. "
                    "A fresh take is warranted to shift the focus from speculative "
                    "monthly income projections to specific, repeatable workflows."
                ),
                "suggested_angles": [
                    "3 AI Side Hustles That Actually Scaled in Q3 2026",
                    "Midjourney vs. Flux: Which AI Art Workflow Pays Better?",
                    "Stop Selling AI Logos: 3 Services Clients Pay More For",
                ],
                "evidence": {
                    "newest_quality_video_age_days": 36,
                    "trends_appearance_count": 4,
                    "autocomplete_rank": None,
                    "residual_outlier_count": 1,
                    "top_competitors": [
                        {"title": "These AI Side Hustles Make $5K/Month in 2026",
                         "channel_title": "FINANCER NEEDS", "subscriber_count": 46,
                         "view_count": 378, "age_days": 43},
                        {"title": "5 AI Side Hustles That Pay Real Money in 2026",
                         "channel_title": "OLY", "subscriber_count": None,
                         "view_count": 170, "age_days": 36},
                    ],
                    "related_queries": [],
                },
            },
            {
                "canonical_title": "How to make $100 with ChatGPT",
                "opportunity_score": 42,
                "gap_type": "underserved",
                "components": {"demand": 0.29, "supply": 0.18, "recency": 0.35},
                "explanation": (
                    "Top videos rely on generic 'copy-paste' strategies and lack "
                    "verified daily-revenue audits — there's room for a creator "
                    "who shows real, repeatable workflows with screenshots and "
                    "actual payouts."
                ),
                "suggested_angles": [
                    "I Tried 5 ChatGPT Hustles: Only 1 Made Real Money",
                    "30-Day ChatGPT Side-Income Audit (Spreadsheet Inside)",
                    "Real Results: Scaling AI Income From $0 to $3K/Month",
                ],
                "evidence": {
                    "newest_quality_video_age_days": 95,
                    "trends_appearance_count": 5,
                    "autocomplete_rank": 2,
                    "residual_outlier_count": 0,
                    "top_competitors": [
                        {"title": "The SIMPLEST Way to Make Money Online with AI",
                         "channel_title": "Sean Dollwet", "subscriber_count": 449_000,
                         "view_count": 228_858, "age_days": 112},
                        {"title": "Copy & Paste THIS Strategy to Make $13k/Month",
                         "channel_title": "Iman Gadzhi", "subscriber_count": 5_850_000,
                         "view_count": 183_178, "age_days": 166},
                    ],
                    "related_queries": [],
                },
            },
        ],
    },
    "list_niches": {
        "niches": [
            {"slug": "ai_money_making", "name": "ai money making", "gap_count": 44},
            {"slug": "ai_business_automation", "name": "ai business automation", "gap_count": 89},
            {"slug": "beginner_guitar_lessons", "name": "beginner guitar lessons", "gap_count": 70},
            {"slug": "cryptocurrency_education_guides", "name": "cryptocurrency education guides", "gap_count": 82},
            {"slug": "diy_woodworking_projects", "name": "diy woodworking projects", "gap_count": 81},
            {"slug": "geopolitical_news_commentary", "name": "geopolitical news commentary", "gap_count": 81},
            {"slug": "homemade_bread_baking", "name": "homemade bread baking", "gap_count": 79},
            {"slug": "manhwa_recap_summaries", "name": "manhwa recap summaries", "gap_count": 75},
            {"slug": "python_programming_tutorials", "name": "python programming tutorials", "gap_count": 76},
            {"slug": "real_estate_investing", "name": "real estate investing", "gap_count": 108},
        ],
    },
}
