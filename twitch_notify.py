import requests
import os
import json

TWITCH_USERNAME  = "nohitjerome"
CHANNEL_NAME     = "NOHITJEROME"
DISCORD_WEBHOOK  = os.environ["DISCORD_WEBHOOK"]
TWITCH_CLIENT_ID = os.environ["TWITCH_CLIENT_ID"]
TWITCH_SECRET    = os.environ["TWITCH_SECRET"]
STATE_FILE       = "state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"was_live": False}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def get_token():
    r = requests.post(
        "https://id.twitch.tv/oauth2/token",
        params={
            "client_id":     TWITCH_CLIENT_ID,
            "client_secret": TWITCH_SECRET,
            "grant_type":    "client_credentials"
        },
        timeout=10
    )
    r.raise_for_status()
    return r.json()["access_token"]

def get_stream(token):
    r = requests.get(
        "https://api.twitch.tv/helix/streams",
        params={"user_login": TWITCH_USERNAME},
        headers={
            "Client-ID":     TWITCH_CLIENT_ID,
            "Authorization": f"Bearer {token}"
        },
        timeout=10
    )
    r.raise_for_status()
    data = r.json()["data"]
    return data[0] if data else None

def post_to_discord(message):
    requests.post(DISCORD_WEBHOOK, json={"content": message}, timeout=10).raise_for_status()

def main():
    state    = load_state()
    token    = get_token()
    stream   = get_stream(token)
    is_live  = stream is not None
    was_live = state.get("was_live", False)

    print(f"Live: {is_live} | Was live: {was_live}")

    # Only notify on offline → online transition
    if is_live and not was_live:
        title = stream.get("title", "")
        game  = stream.get("game_name", "Unknown")
        print("Just went live — posting to Discord!")
        post_to_discord(
            f"🔴 **{CHANNEL_NAME}** is live on Twitch!\n"
            f"**{title}**\n"
            f"Playing: {game}\n"
            f"https://twitch.tv/{TWITCH_USERNAME}"
        )
    elif is_live and was_live:
        print("Still live — no notification.")
    else:
        print("Not live.")

    state["was_live"] = is_live
    save_state(state)

if __name__ == "__main__":
    main()
