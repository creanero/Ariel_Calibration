import sys
import os
import pandas as pd

# parse arguments
def parse_args(args):
    in_dir_name=os.getcwd()
    out_file_name="test.csv"
    if len(args)!=3:
        print("WARNING: Interactive mode not yet defined.  Please use the format\n\t" + \
              "python merge_ariel.py IN_DIR OUT_FILE")
        # in_dir_name, out_file_name = ask_for_in(args)
    # if len(args)>1:
    #     in_dir_name = args[1]
    if 3==len(args):
        in_dir_name = args[1]
        out_file_name = args[2]
    return (in_dir_name, out_file_name)

def ask_for_in(args):
    pass
# read in the data
def read_data(in_dir_name):
    data_dir = {}

    print("Reading from directory "+in_dir_name)

    dir_list = os.listdir(in_dir_name)
    
    i=0
    for file in dir_list:
        data = read_ariel_file(in_dir_name+'/'+file)
        # Drops the control column that's present in some input files but should be removed
        try:
            data.drop(columns=['Control'], inplace=True)
        except KeyError:
            # if this is already gone, then good, leave it alone
            pass
        
        data_dir[file]=data

    return data_dir

def read_ariel_file(filename):
    print("Reading from file "+filename)

    data = pd.DataFrame()
    try:
        # reads the data into a pandas dataframe
        data = pd.read_csv(filename,
                           delim_whitespace=True,  # files are delimted by whitespace (5 spaces)
                           header=None,  # files have no headers
                           names=('Wavelength', 'Current', 'Control'))  # files contain wavelength and current.
    # if the file isn't found
    except FileNotFoundError:
        print("File " + filename + " not found.")

    # if the data can't be parsed into the 3-column structure we expect
    except pd.errors.ParserError:
        print("Unable to extract data from " + filename)
        print("Data in this file probably has the wrong structure")

    return data
# Calculates the transmission and merges the data (filtered/unfiltered)
def merge_data(data_dir):
    data_list = pd.DataFrame()
    i=0

    for filename, data in data_dir.items():
        # combines this data into a wide dataframe with separate current values for each input file
        if 0 == i: # to initialise before any data is added
            data_list = data # initialise the list with the data from file #0
        else: # from file #1 onwards
            # merge the new data with the existing data
            data_list=pd.merge(data_list,data, on="Wavelength", how='outer',suffixes=('','_'+str(i)))
        # rename the Current column to Current_i, so it's identifiable and iterable
        data_list.rename(columns={'Current':filename}, inplace = True)
        i=i+1

    return data_list

# saves the calculated and aggregated data
def save_data(data_list,filename):
    print("Saving to "+filename)
    try:
        data_list.to_csv(filename, index=False)
    except OSError:
        print('Unable to save')
    pass

def main():
    args = sys.argv[0:]

    # parse arguments
    in_dir_name, out_file_name = parse_args(args)

    #read in the data
    data_dir = read_data(in_dir_name)

    # merges the data
    data_list = merge_data(data_dir)

    # saves the calculated and aggregated data
    save_data(data_list,out_file_name)



if __name__ == '__main__':
    main()
