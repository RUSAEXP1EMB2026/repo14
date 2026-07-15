from modules import nature_remo


def main():
    appliances = nature_remo.get_appliances()
    for appliance in appliances:
        nickname = appliance.get("nickname")
        appliance_id = appliance.get("id")
        appliance_type = appliance.get("type")
        print(f"{nickname} | {appliance_type} | {appliance_id}")


if __name__ == "__main__":
    main()
