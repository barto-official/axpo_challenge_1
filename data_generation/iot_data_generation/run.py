import asyncio
from generator import Generator
from mqtt_handler import setup_mqtt, aggregate_data

if __name__ == "__main__":
    generator = Generator()
    loop = asyncio.get_event_loop()

    async def main():
        """
        Main asynchronous function to start data generation and aggregation.
        """
        # Run data generation and aggregation concurrently
        await asyncio.gather(
            generator.generate(),
            aggregate_data()
        )

    # Set up MQTT client
    mqtt_client = setup_mqtt()

    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        mqtt_client.loop_stop()
        print("Event loop closed and MQTT loop stopped")
