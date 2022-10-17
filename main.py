def read_dark():
    pass

def read_unfiltered(dark):
    pass

def read_filtered(dark):
    pass

def calculate_transmission(unfiltered,filtered):
    pass

def plot_data(transmission):
    pass

def save_data(transmission):
    pass


def main():
    # reads in the dark current values and return the average
    dark=read_dark()

    # reads in unfiltered data per frequency
    unfiltered=read_unfiltered(dark)

    # reads in filtered data per frequency
    filtered=read_filtered(dark)

    # Calculates the transmission (filtered/unfiltered)
    transmission=calculate_transmission(unfiltered,filtered)

    # Plots the data on a graph
    plot_data(transmission)

    # saves the transmission data
    save_data(transmission)



if __name__ == '__main__':
    main()

#