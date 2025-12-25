import time
import requests
import statistics

BSKY_API = "https://public.api.bsky.app"

def analyze_handle(handle: str):
    profile_resp = requests.get(
        f"{BSKY_API}/xrpc/app.bsky.actor.getProfile",
        params={"actor": handle},
        timeout=10
    )

    if profile_resp.status_code != 200:
        raise ValueError(f"Profile lookup failed for {handle}")

    profile = profile_resp.json()

    # Defensive extraction
    followers = profile.get("followersCount", 0) or 1
    following = profile.get("followsCount", 0)
    posts_count = profile.get("postsCount", 0)

    feed_resp = requests.get(
        f"{BSKY_API}/xrpc/app.bsky.feed.getAuthorFeed",
        params={"actor": handle, "limit": 100},
        timeout=10
    )

    posts = []
    if feed_resp.status_code == 200:
        feed = feed_resp.json()
        posts = [f["post"] for f in feed.get("feed", [])]

    likes = [p.get("likeCount", 0) for p in posts]
    reposts = [p.get("repostCount", 0) for p in posts]
    replies = [p.get("replyCount", 0) for p in posts]

    total_engagement = sum(likes) + sum(reposts) + sum(replies)

    return {
        "handle": handle,
        "followers": followers,
        "following": following,
        "posts_sampled": len(posts),
        "posts_total": posts_count,
        "avg_likes": round(statistics.mean(likes), 2) if likes else 0,
        "avg_reposts": round(statistics.mean(reposts), 2) if reposts else 0,
        "avg_replies": round(statistics.mean(replies), 2) if replies else 0,
        "engagement_rate": round(total_engagement / followers, 4),
        "generated_at": int(time.time() * 1000)
    }
