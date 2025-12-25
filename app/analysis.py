import time
import requests
import statistics

BSKY_API = "https://public.api.bsky.app"

def analyze_handle(handle: str):
    profile = requests.get(
        f"{BSKY_API}/xrpc/app.bsky.actor.getProfile",
        params={"actor": handle}
    ).json()

    feed = requests.get(
        f"{BSKY_API}/xrpc/app.bsky.feed.getAuthorFeed",
        params={"actor": handle, "limit": 100}
    ).json()

    posts = [f["post"] for f in feed.get("feed", [])]

    likes = [p["likeCount"] for p in posts]
    reposts = [p["repostCount"] for p in posts]
    replies = [p["replyCount"] for p in posts]

    followers = profile["followersCount"] or 1

    return {
        "handle": handle,
        "followers": followers,
        "following": profile["followsCount"],
        "posts_sampled": len(posts),
        "avg_likes": round(statistics.mean(likes), 2) if likes else 0,
        "avg_reposts": round(statistics.mean(reposts), 2) if reposts else 0,
        "avg_replies": round(statistics.mean(replies), 2) if replies else 0,
        "engagement_rate": round(
            (sum(likes) + sum(reposts) + sum(replies)) / followers, 4
        ),
        "generated_at": int(time.time() * 1000)
    }
