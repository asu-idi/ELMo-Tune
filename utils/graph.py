import matplotlib.pyplot as plt

def plot(values, title, file):
    '''
    Plots a single line graph based on a list of values.

    This function plots a simple line graph where the X-axis represents the index of each value in the list, and the Y-axis represents the value itself.

    Parameters:
    values (list): A list of numerical values to be plotted.
    title (str): The title of the plot.
    file (str): The file path where the plot image will be saved.

    Returns:
    - None. The plot is saved to the specified file path.

    '''
    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(range(len(values)), values, label=title, linestyle='-')

    plt.title(title)
    plt.legend()
    plt.grid(True)

    plt.ylim(0, 400000)

    # Save the plot to a file
    plt.savefig(file)


def plot_2axis(keys, values, title, file):
    '''
    Plots a line graph with specified keys and values.

    This function is designed to plot a line graph where the X-axis is determined by the 'keys' parameter and the Y-axis by the 'values' parameter.

    Parameters:
    keys (list): A list of keys or indices for the X-axis.
    values (list): A list of numerical values for the Y-axis.
    title (str): The title of the plot.
    file (str): The file path where the plot image will be saved.

    Returns:
    - None. The plot is saved to the specified file path.
    '''
    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(keys, values, label=title, linestyle='-')

    plt.title(title)
    plt.legend()
    plt.grid(True)

    plt.ylim(0, 400000)

    # Save the plot to a file
    plt.savefig(file)


def plot_multiple(data, title, file):
    '''
    Plots multiple line graphs from a list of data sets.

    This function is used to plot multiple line graphs on the same plot. Each item in the 'data' list represents a different line on the graph.

    Parameters:
    data (list of tuples): Each tuple contains two elements - a list of keys for the X-axis and a list of values for the Y-axis.
    title (str): The title of the plot.
    file (str): The file path where the plot image will be saved.

    Each line is labeled as 'Iteration-i' where i is the index of the data set in the 'data' list.

    Returns:
    - None. The plot is saved to the specified file path.

    '''

    # Plotting setup
    plt.figure(figsize=(12, 6))
    for i, iteration in enumerate(data):
        keys, values = iteration[1]["ops_per_second_graph"]
        plt.plot(keys, values, label=f"Iteration-{i}", linestyle='-')

    plt.title(title)
    plt.legend()
    plt.grid(True)

    plt.ylim(0, 400000)

    # Save the plot to a file
    plt.savefig(file)

def plot_multiple_manual(data, file):
    # Plotting
    plt.figure(figsize=(16.5, 8))
    # labels = ["Default file", "Iteration 3", "Iteration 3", "Iteration 7"]
    labels = ["Default file", "Iteration 2", "Iteration 4", "Iteration 6"]
    colors = ['red', 'orange', 'royalblue', 'green'] 
    for i, ops in enumerate(data):
        plt.plot(ops, label=f"{labels[i]}", linestyle='-',color=colors[i])
    plt.xlabel("Time (seconds)")  
    plt.ylabel("Throughput (kops/s)")  
    plt.legend()


    plt.ylim(0, 400)
    plt.tight_layout()

    # Save the plot to a file
    plt.savefig(file)


# pattern = r"\((\d+),(\d+)\) ops and \((\d+\.\d+),(\d+\.\d+)\) ops/second in \((\d+\.\d+),(\d+\.\d+)\) seconds"

# folder_path = "/data/gpt_project/gpt-assisted-rocksdb-config/saved_output/fillrandom/output_nvme_v2/c4_m4"
# file_names = ['0.ini', '2.ini', '4.ini', '6.ini']
# pattern = r'"ops_per_second_graph": \[\[([\d.,\s]+)\],\s+\[([\d.,\s]+)\]\]'

# data = []

# for file_name in file_names:
#     file_path = os.path.join(folder_path, file_name)
#     with open(file_path, 'r') as f:
#         file_contents = f.read()
#         matches = re.findall(pattern, file_contents)
#         ops = [float(x)/1000 for x in matches[0][1].split(', ')]
#         data.append(ops)

# plot_multiple_manual(data, "Ops_per_Second_combined.png")

