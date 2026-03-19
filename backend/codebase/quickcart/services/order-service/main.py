from controllers.orderController import create_order


def simulate_request() -> None:
    user = {"id": "u-101", "address": None}
    create_order(user)


if __name__ == "__main__":
    try:
        simulate_request()
        print("Request simulated successfully")
    except Exception as e:
        print(f"Request failed: {e}")
