import gurobipy as gp
from gurobipy import GRB

def check_gurobi_license():
    try:
        # Create a simple environment
        env = gp.Env(empty=True)
        env.setParam("OutputFlag", 0)  # Suppress output
        env.start()  # Start the environment to check license

        # If no exception occurs, the license is valid
        print("Gurobi license is valid.")
        return True
    except gp.GurobiError as e:
        if e.errno == GRB.ERROR_NO_LICENSE:
            print("No valid Gurobi license found.")
        else:
            print(f"An error occurred: {e}")
        return False

if __name__ == "__main__":
    is_licensed = check_gurobi_license()
    print(f"Licensed: {is_licensed}")

    if is_licensed:
        exit(0)
    else:
        exit(1)
