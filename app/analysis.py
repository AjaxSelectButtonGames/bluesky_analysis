import time
import requests
import statistics

from .db import get_cached_did, cache_did

BSKY_API = "https://public.api.bsky.app"


def normalize_handle(handle: str) -> str:
    handle = handle.strip().lower()
    if handle.startswith("@"):
        handle = handle[1:]
    return handle


def resolve_handle_to_did(handle: str) -> str:
    handle = normalize_handle(handle)

    # 1️⃣ Check cache first
    cached = get_cached_did(handle)
    if cached:
        return cached

    # 2️⃣ Resolve via Bluesky
    resp = requests.get(
        f"{BSKY_API}/xrpc/app.bsky.actor.resolveHandle",
        params={"handle": handle},
        timeout=10
    )

    if resp.status_code != 200:
        raise ValueError(f"Unable to resolve handle: {handle}")

    data = resp.json()
    did = data.get("did")

    if not did:
        raise ValueError(f"No DID found for handle: {handle}")

    # 3️⃣ Cache result
    cache_did(handle, did)

    return did


def analyze_handle(handle: str):
    handle = normalize_handle(handle)
    did = resolve_handle_to_did(handle)

    # Profile
    profile_resp = requests.get(
        f"{BSKY_API}/xrpc/app.bsky.actor.getProfile",
        params={"actor": did},
        timeout=10
    )

    if profile_resp.status_code != 200:
        raise ValueError(f"Profile lookup failed for {handle}")

    profile = profile_resp.json()

    followers = profile.get("followersCount", 0) or 1
    following = profile.get("followsCount", 0)
    posts_total = profile.get("postsCount", 0)

    # Feed
    feed_resp = requests.get(
        f"{BSKY_API}/xrpc/app.bsky.feed.getAuthorFeed",
        params={"actor": did, "limit": 100},
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
        "did": did,
        "followers": followers,
        "following": following,
        "posts_sampled": len(posts),
        "posts_total": posts_total,
        "avg_likes": round(statistics.mean(likes), 2) if likes else 0,
        "avg_reposts": round(statistics.mean(reposts), 2) if reposts else 0,
        "avg_replies": round(statistics.mean(replies), 2) if replies else 0,
        "engagement_rate": round(total_engagement / followers, 4),
        "generated_at": int(time.time() * 1000)
    }
