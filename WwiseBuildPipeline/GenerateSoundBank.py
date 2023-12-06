import sys
import waapi

has_error = False


def get_all_banks():
    query = {
        "from": {
            "ofType": ["SoundBank"]
        },
        "options": {
            "return": ["name"]
        }
    }
    query_result = client.call("ak.wwise.core.object.get", query)
    return query_result["return"] if query_result else None


def on_generation_done(*args, **kwargs):
    for log in kwargs["logs"]:
        if log["severity"] == "Error":
            print(log["message"])
            global has_error
            has_error = True


if __name__ == "__main__":
    with waapi.connect() as client:
        subscription_id = client.subscribe(
            "ak.wwise.core.soundbank.generationDone", on_generation_done
        )

        all_banks = get_all_banks()
        if all_banks:
            for bank_info in all_banks:
                bank_name = bank_info["name"]
                print(f"Bank Name: {bank_name}")

            args = {
                "soundbanks": all_banks,
                "rebuildSoundBanks": True,
                "writeToDisk": True
            }
            result = client.call("ak.wwise.core.soundbank.generate", args)
            if has_error:
                sys.exit(1)
