from hp import HoneyPot

if __name__ == "__main__":
    server: HoneyPot = HoneyPot(
        name="My-HoneyPot",
        host="public",
        ports=[8822, 8823, 8824],
    )
    server.add_interactive_shell(on_ports=[8825], mode='ssh')
    server.run()
