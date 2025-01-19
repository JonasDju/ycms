# https://stackoverflow.com/a/34993964
from django.contrib.staticfiles.management.commands.runserver import Command as StaticfilesRunserverCommand
from django.core.cache import cache
import subprocess
import os


class Command(StaticfilesRunserverCommand):

    # Override the default runserver command to insert pra install check / gurobi license check
    def handle(self, *args, **options):

        print("Running PRA algorithm checks...")
        #cache = PRAState()

        try:
            with open(os.devnull, "wb") as devnull:
                result = subprocess.run(
                    ["tools/check_pra_algorithm.sh"],
                    stdout=devnull
                )

            if result.returncode == 0:
                # All tests passed: PRA algorithm is installed and gurobi is licensed
                print("✔ PRA algorithm installed and license check passed.")
                cache.set('pra_algorithm_installed', True, timeout=None)
                cache.set('gurobi_license', "valid", timeout=None)
            elif result.returncode == 1:
                # PRA algorithm not installed
                print("❌ PRA algorithm not installed, you will not be able to automatically assign patients.")
                cache.set('pra_algorithm_installed', False, timeout=None)
                cache.set('gurobi_license', "invalid", timeout=None)
            elif result.returncode == 2:
                # PRA algorithm installed, but gurobi license file is missing
                print("❌ PRA algorithm installed, but gurobi license file is missing. You will not be able to automatically assign patients.")
                cache.set('pra_algorithm_installed', True, timeout=None)
                cache.set('gurobi_license', "missing", timeout=None)
            elif result.returncode == 3:
                # PRA algorithm installed and gurobi license in place, but invalid
                print("❌ PRA algorithm installed, but gurobi license file is invalid. You will not be able to automatically assign patients.")
                cache.set('pra_algorithm_installed', True, timeout=None)
                cache.set('gurobi_license', "invalid", timeout=None)


        except subprocess.CalledProcessError as e:
            print(f"Error running pra / gurobi check: {e}")

        # Continue with the default runserver logic
        super().handle(*args, **options)
