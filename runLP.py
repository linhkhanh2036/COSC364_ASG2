
import sys
import time
import subprocess

def parseLPfile(file):
    args = [
        'C:/Program Files/IBM/ILOG/CPLEX_Studio_Community129/cplex/bin/x64_win64/cplex', 
        '-c', 'read C://Users/Jerry/Desktop/cosc364-as2/' + file,
        'optimize',
        'display solution variable -'
    ]
    
    start = time.time()
    procs = subprocess.Popen(args, stdout=subprocess.PIPE)
    output, err = procs.communicate()
    end = time.time()
    elapsed = end - start
    output = output.decode("utf-8").split()
    return elapsed, output
    
def main(file):
    run_time, output = parseLPfile(file)
    transit_loads = {}
    num_non_zero_links = 0
    highest_capacities = {'max':[0,[]]}
    max_cappacity = 0.0

    for i in output[output.index("r"):]:
        if i[0] == 'x':
            trans_node = int(i[2])
            index = output.index(i)
            if trans_node in transit_loads:
                transit_loads[trans_node] += float(output[index + 1])
            else:
                transit_loads[trans_node] = float(output[index + 1])
                
        if (i[0] == 'c' or i[0] == 'd') and len(i) == 3:
            index = output.index(i)
            cappacity = float(output[index + 1])
            if cappacity > 0:
                num_non_zero_links += 1
            if cappacity == max_cappacity:
                highest_capacities['max'][1].append(i)            
            if cappacity > max_cappacity:
                max_cappacity = cappacity
                highest_capacities['max'][0] = max_cappacity
                highest_capacities['max'][1]= [i]

    print('''
    Execution time: {0:.3f}
    Load on transit nodes: {1}
    Heighest cappacity links: {2}
    Number of links with non-zero capacities: {3}
    '''.format(run_time, transit_loads, highest_capacities, num_non_zero_links))
    
main(sys.argv[1])