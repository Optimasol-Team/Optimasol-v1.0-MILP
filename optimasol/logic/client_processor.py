from data_preparation import load_client_context
from decision_engine import write_decision
from optimizer.milp_solver import optimise


#The main function : 

def process_client(client_dir : str, conf_path) -> None:
    data = load_client_context(client_dir,conf_path) 


    decision_list = optimise(data) 


    write_decision(client_dir,decision_list) 


if __name__ == "__main__" :
    process_client("C:\\Users\\elbou\\Optimasol\\optimasol\\clients\\PV0001","C:\\Users\\elbou\\Optimasol\\optimasol\\config\\optimize_config.txt")

