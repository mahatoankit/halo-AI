from django.core.management.base import BaseCommand
from services.iot_simulator import sensor_simulator


class Command(BaseCommand):
    help = "Run IoT sensor simulation to test Firebase integration"

    def add_arguments(self, parser):
        parser.add_argument(
            "--mode",
            choices=["test", "continuous"],
            default="test",
            help="Run mode: test (single run) or continuous (keep running)",
        )
        parser.add_argument(
            "--interval",
            type=int,
            default=30,
            help="Interval in seconds for continuous mode (default: 30)",
        )

    def handle(self, *args, **options):
        mode = options["mode"]
        interval = options["interval"]

        if mode == "test":
            self.stdout.write(self.style.SUCCESS("Running single IoT sensor test..."))
            sensor_simulator.run_single_test()
            self.stdout.write(self.style.SUCCESS("IoT sensor test completed!"))

        elif mode == "continuous":
            self.stdout.write(
                self.style.SUCCESS(
                    f"Starting continuous IoT simulation (every {interval}s)..."
                )
            )
            self.stdout.write(self.style.WARNING("Press Ctrl+C to stop the simulation"))
            try:
                sensor_simulator.start_continuous_simulation(interval)
            except KeyboardInterrupt:
                self.stdout.write(self.style.SUCCESS("\nIoT simulation stopped."))
