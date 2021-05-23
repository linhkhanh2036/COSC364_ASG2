import time
import subprocess
from operator import itemgetter

def demand_volume_constraint(X, Y, Z):
    '''xikj + xi(k+1)j = hij'''
    DV_lst = []
    for i in range(1, X+1):
        for j in range(1, Z+1):
            lst = []
            for k in range(1, Y+1):
                xikj = 'x'+str(i)+str(k)+str(j)
                lst.append(xikj)
            lst.append(str(i+j))
            DV_lst.append(lst)
    result = ''
    for n in DV_lst:
        result += ' + '.join(n[:-1]) + ' = ' + n[-1] + '\n'
    return result

def source_to_transit_capacity_constraint(X, Y, Z):
    ''' capacity constraint from source to transit
        xikj - cij <= 0'''
    capp1_lst = []
    for i in range(1, X+1):
        for k in range(1, Y+1):
            lst = []
            for j in range(1, Z+1):
                xikj = 'x'+str(i)+str(k)+str(j)
                lst.append(xikj)
            lst.append('c'+str(i)+str(k))
            capp1_lst.append(lst)
    result = ''
    for n in capp1_lst:
        result += ' + '.join(n[:-1]) + ' - ' + n[-1] + ' <= 0' '\n'
    return result

def transit_to_destination_constraint(X, Y, Z):
    ''' capacity constraint from transit to destination
        xikj - dij <= 0'''
    capp2_lst = []
    for k in range(1, Y+1):
        for j in range(1, Z+1):
            lst = []
            for i in range(1, X+1):
                xikj = 'x'+str(i)+str(k)+str(j)
                lst.append(xikj)
            lst.append('d'+str(k)+str(j))
            capp2_lst.append(lst)
    result = ''
    for n in capp2_lst:
        result += ' + '.join(n[:-1]) + ' - ' + n[-1] + ' <= 0' '\n'
    return result

def transit_nodes_constraint(X, Y, Z, N):
    '''transit load constraint of the nodes that need to be minimized'''
    transit_nodes = []
    transit = []
    for k in range(1, Y + 1):
        t_node = []
        for j in range(1, Z + 1):
            for i in range(1, X + 1):
                t_node.append('x'+str(i)+str(k)+str(j))
        transit_nodes = ' + '.join(t_node) + ' - r <= 0'.format(k, j)     
        transit.append(transit_nodes)
    result = '\n'.join(transit)
    return result

def binary_variables_constriant(X, Y, Z, N):
    '''binary variables constraint uikj = nk '''
    binary_variables = []
    binary = []
    for i in range(1, X + 1):
        for j in range(1, Z + 1):
            variable = []
            for k in range(1, Y + 1):
                variable.append('u'+str(i)+str(k)+str(j))
            binary_variables = ' + '.join(variable) + ' = {0}'.format(N)
            binary.append(binary_variables)
    result = '\n'.join(binary)
    return result

def demand_flow_constraint(X, Y, Z, N):
    '''demand flow constraint nk * xikj = hij * uikj'''
    demand_flow = []
    flow = []
    for i in range(1, X + 1):
        for j in range(1, Z + 1):
            for k in range(1, Y + 1):
                demand_flow = str(N) + ' x'+str(i)+str(k)+str(j) + ' - ' + str(i + j) + ' u'+str(i)+str(k)+str(j) + ' = 0'
                flow.append(demand_flow)
    result = '\n'.join(flow)
    return result

def bounds_constraint(X, Y, Z):
    '''Non-negativity constraints'''
    result = '0 <= r \n'
    for i in range(1, X+1):
        for j in range(1, Z+1):
            for k in range(1, Y+1):
                result += '0 <= x' + str(i)+str(k)+str(j) + '\n'
    return result

def binary_constraint(X, Y, Z):
    '''return binary constraints'''
    constraints = ''
    for i in range(1, X + 1):
        for k in range(1, Y + 1):
            for j in range(1, Z + 1):
                constraints += 'u' + str(i)+str(k)+str(j) + '\n'
    return constraints


def LPformat(X, Y, Z, N):
    '''print LP file as a format below'''
    demand_volume = demand_volume_constraint(X, Y, Z)
    source_to_transit_capacity = source_to_transit_capacity_constraint(X, Y, Z)
    transit_to_destination = transit_to_destination_constraint(X, Y, Z)
    transit_nodes = transit_nodes_constraint(X, Y, Z, N)
    binary_variables = binary_variables_constriant(X, Y, Z, N)
    demand_flow = demand_flow_constraint(X, Y, Z, N)
    bounds = bounds_constraint(X, Y, Z)
    binaries = binary_constraint(X, Y, Z)

    object_function = \
        f'Minimize \n' + \
        f'\tr \n' + \
        f'Subject to\n' + \
        f'demand volume:\n{demand_volume}' + \
        f'source to transit capacities:\n{source_to_transit_capacity}' + \
        f'transit to destination capacities:\n{transit_to_destination}' + \
        f'transit nodes:\n{transit_nodes}\n' + \
        f'binary variables:\n{binary_variables}\n' + \
        f'demand flow:\n{demand_flow}\n' + \
        f'Bounds\n{bounds}' + \
        f'Binaries\n{binaries}' + \
        f'End'
    return object_function

def parseLPfile(lp_filename):
    '''run CPLEX and parse LP file'''
    cplex_command = "/home/bachlinux/opt/ibm/ILOG/CPLEX_Studio_Community129/cplex/bin/x86-64_linux/cplex" #GET CORRECT
    args = [
        "-c",
        "read /home/bachlinux/cosc364-as2/" + lp_filename,
        "optimize",
        'display solution variables -'
    ]
    time1 = time.time()
    process = subprocess.Popen([cplex_command] + args, stdout=subprocess.PIPE)
    out, err = process.communicate()
    time2 = time.time()
    exe_time = time2 - time1
    result = out.decode("utf-8")
    result = result.split('Incumbent solution')[1]
    result = result.splitlines()
    result = [line.split() for line in result]
    return exe_time, result[2:-2]

def print_output(run_time, transit_loads, highest_capacities, highest_cappacity, num_non_zero_links):
    '''print output of CPLEX + LP file'''
    print('\nExecution time: {:3f}s'.format(run_time))
    print('Number of links with non-zero capacities: ' + str(num_non_zero_links))
    print('Load on transit nodes:')
    for key, value in sorted(transit_loads.items()):
        print('\ttransit node: {}, load: {}'.format(key, value))
    print('Highest capacities:')
    for i in highest_capacities:
        print('\t{}: {}'.format(i, highest_cappacity))
    
def run_CPLEX(LP_file):
    '''extract info from CPLEX + LP file'''
    run_time, output = parseLPfile(LP_file)
    transit_loads = {}
    num_non_zero_links = 0
    capacity_lst = []
    highest_capacity_lst = []
    for node, var in output:
        if node[0] == 'x':
            trans_node = int(node[2])
            if trans_node in transit_loads:
                transit_loads[trans_node] += float(var)
            
            else:
                transit_loads[trans_node] = float(var)
                
        if node[0] == 'c' or node[0] == 'd':
            capacity_lst.append((node, float(var)))
            highest_capacity = max(float(var) for _, var in capacity_lst)
            highest_capacities = [a for a, b in capacity_lst if b == highest_capacity]
            capacity = float(var)
            
            if capacity > 0:
                num_non_zero_links += 1
    print_output(run_time, transit_loads, highest_capacities, highest_capacity, num_non_zero_links)
def main():
    X = input('input X: ')
    Y = input('input Y: ')
    Z = input('input Z: ')
    N = 2 # balance flow between two transit nodes
    format = LPformat(int(X), int(Y), int(Z), N)
    filename = '{0}{1}{2}.lp'.format(X, Y, Z)
    file = open(filename, 'w')
    file.write(format)
    file.close()
    
    run_CPLEX(filename) # uncomment to run CPLEX with generated LP file

main()
