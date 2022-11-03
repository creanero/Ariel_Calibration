import pandas as pd
import matplotlib.pyplot as plt
import os

# reads files structured in the format we're using for ariel files
def read_ariel(prompt):
    # loop until the user enters a correct filename
    while True:
        # asks the user to enter a file as prompted
        full_prompt = "Please enter the path to the " + prompt + " file:\t"
        filename = input(full_prompt)

        try:
            # reads the data into a pandas dataframe
            data= pd.read_csv(filename,
                              delim_whitespace=True, # files are delimted by whitespace (5 spaces)
                              header=None, # files have no headers
                              names=('Wavelength', 'Current', 'Control')) # files contain wavelength and current.
            break # end the loop if it worked correctly.

        # if the file isn't found
        except FileNotFoundError:
            print("File "+filename+" not found.")
            print("Please try again")

        #if the data can't be parsed into the 3-column structure we expect
        except pd.errors.ParserError:
            print("Unable to extract data from "+filename)
            print("Data in this file probably has the wrong structure")
            print("Please try again")

    return (data) # returns a pandas dataframe containing three columns

def read_dark():
    # describes the data to the user
    dark_name="Dark Current"

    # prompts the user for the file and reads it in
    dark_data=read_ariel(dark_name)

    # gets the average of the current values
    dark_average=dark_data['Current'].mean()


    print("Average Dark Current: "+f'{dark_average:.4g}'+" Amps")
    return (dark_average)

def remove_dark(raw_data,dark=0.0):
    # copies the raw data
    data=raw_data.copy()

    #subtracts the dark current from it
    data["Current"]=data["Current"].sub(dark)
    return data

def extract_dark(prompt,dark):
    # asks how many files to input
    count = ask_count("How many "+prompt+" files do you wish to input?")

    data_all = pd.DataFrame()
    data_list = pd.DataFrame()
    for i in range(count):

        # prompts the user for the file and reads it in
        raw_data_i=read_ariel(to_ordinal(1+i)+" "+prompt)

        # performs dark removal on the data
        data_i=remove_dark(raw_data_i,dark)

        # Drops the control column that's present in some input files but should be removed
        try:
            data_i.drop(columns=['Control'], inplace=True)
        except KeyError:
            # if this is already gone, then good, leave it alone
            pass

        # combines this data into a long dataframe with all Current values in one column for averaging
        data_all=pd.concat([data_all,data_i])

        # combines this data into a wide dataframe with separate current values for each input file
        if 0 == i: # to initialise before any data is added
            data_list = data_i # initialise the list with the data from file #0
        else: # from file #1 onwards
            # merge the new data with the existing data
            data_list=pd.merge(data_list,data_i, on="Wavelength", how='outer',suffixes=('','_'+str(i)))
        # rename the Current column to Current_i, so it's identifiable and iterable
        data_list.rename(columns={'Current':'Current_'+str(i)}, inplace = True)

    data_aggregate=data_all.groupby('Wavelength', as_index=False)['Current'].mean()
    data_aggregate=pd.merge(data_aggregate,data_list, on="Wavelength", how='outer')

    return data_aggregate

def to_ordinal(in_integer):
    if abs(in_integer) in (11,12,13):
        out_ordinal = str(in_integer)+'th'
    elif 1 == abs(in_integer)%10:
        out_ordinal = str(in_integer)+'st'
    elif 2 == abs(in_integer)%10:
        out_ordinal = str(in_integer)+'nd'
    elif 3 == abs(in_integer)%10:
        out_ordinal = str(in_integer)+'rd'
    else:
        out_ordinal = str(in_integer)+'th'
    return out_ordinal
def ask_count(prompt='Please Enter an integer:', negative_allowed=False, zero_allowed=False):
    count = 0
    while True:
        text_input=input(prompt+'\t')
        try:
            count = int(text_input)
            if count > 0:
                break
            elif count == 0 and zero_allowed:
                break
            elif count == 0:
                print("Zero value input not allowed!")
                print("Please try again")
            elif count < 0 and negative_allowed:
                break
            elif count < 0:
                print("Negative value ("+text_input+") not allowed!")
                print("Please try again")

        except ValueError:
            print("WARNING: input value ("+text_input+") is not an integer!")
            print("Please try again.")

    return count

def ask_dict(options={'Key':'Value'},prompt="Select from the following options:\t"):
    while True:
        print(prompt)
        for k in options.keys():
            print('For '+str(k)+' enter '+str(options[k]))

        selection=input("Please make your selection now:\t")
        if selection in options.values():
            break
        else:
            print("The value you have entered "+selection+" is not available.")
    return selection

def merge_and_calculate(unfiltered, filtered):
    # gets the number of filtered columns
    filtered_count=sum(1 for col in filtered.columns if "Current_" in col)

    # renames the columns
    for col in unfiltered.columns:
        if "Current" in col:
            unfiltered.rename(columns={col:col+'_unfiltered'}, inplace = True)

    for col in filtered.columns:
        if "Current" in col:
            filtered.rename(columns={col:col+'_filtered'}, inplace = True)

    # merges the dataframes with an outer joi. Any data where there is no corresponding value in other columns is
    # assigned NaN value which is not plotted
    merge_df=pd.merge(unfiltered,filtered, on="Wavelength", how='outer',suffixes=('_unfiltered','_filtered'))
    # gets the overall values
    merge_df['Transmission']=merge_df['Current_filtered']/merge_df['Current_unfiltered']


    for i in range(filtered_count):
        # gets the values for each filtered data
        merge_df['Transmission_'+str(i)] = merge_df['Current_'+str(i)+'_filtered'] / merge_df['Current_unfiltered']

    return(merge_df)

def plot_data(merge_df):

    if 'y' == ask_yn("plot the data on a graph"):
        while True:
            plot_type=ask_dict({'Transmission':'t','Raw Data':'r'}, "Select whether to plot Transmission or Raw Data")
            plot_num=ask_dict({'Only Mean':'m','Only Separate':'s', 'Both at once':'b'},
                               "Select whether to plot the mean of all filtered values, the individual filtered values"+
                               " or both the mean and the individual values.")

            if plot_type=='t':
                plt.ylabel('Transmission')
                plt.title('Plot of Transmission against Wavelength')
                if plot_num in ('m', 'b'):
                    plt.plot(merge_df['Wavelength'], merge_df['Transmission'], 'k.')#



            if plot_type=='r':
                plt.ylabel('Current (Amps)')
                plt.title('Plot of Current against Wavelength')
                if plot_num in ('m', 'b'):
                    plt.plot(merge_df['Wavelength'], merge_df['Current_filtered'], 'k.')
                    plt.plot(merge_df['Wavelength'], merge_df['Current_unfiltered'], 'r.')



            # if plot_num in ('m','b'):
            #     plt.plot(merge_df[x], merge_df[y], 'k.')
            # if plot_num in ('i','b'):
            #     plt.plot(merge_df[x], merge_df[y], 'k.')
            plt.xlabel('Wavelength (nm)')
            plt.show()
            if 'n' == ask_yn("plot another graph"):
                break



def ask_yn(prompt):
    while True:
        ans_yn=input('Do you wish to '+prompt+'? (y/n): \t')
        if ans_yn.lower() in ('y','yes', 'yeah', 'yep', 'yus', 'yarp'):
            ans_yn = 'y'
            break
        elif ans_yn.lower() in ('n','no', 'nah', 'nope', 'narp'):
            ans_yn = 'n'
            break
        else:
            print("Invalid response: "+ans_yn)

    return ans_yn

def get_save_path():
    while True: # repeat until it works
        filename = input("Please enter the file path to save to:\t")
        dirname = os.path.dirname(filename)
        if os.path.exists(filename): # if the file already exists
            print("WARNING: "+filename+" exists already!") # warn the user
            if 'y'==ask_yn("Overwrite "+filename): # check if they want to overwrite
                break # if they do, break the while loop and return the path
            else: # if they don't want to overwrite
                print("Select a new file") # tell them to try again, don't break the loop

        elif ''==dirname: # if the path is a relative path
            break # break the loop and return the filename

        elif os.path.exists(dirname): # if the directory exists (but not the file)
            break # break the loop and return the filename

        else: # if neither the file nor the directory exists and the path isn't relative
            try: # try to make the directory
                os.mkdir(dirname) # make the directory
                break # break the main loop and return the filename
            except OSError: # if it doesn't work
                print("ERROR: unable to create directory "+dirname)
                print("Please try again.") # warn the user, and allow them to try again

    return (filename)

def save_data(merge_df):
    save_yn=ask_yn("save the calculated data")
    if 'y'==save_yn:
        while True:
            filename=get_save_path()
            try:
                merge_df.to_csv(filename, index=False)
                break
            except OSError:
                print('Unable to save')

def read_data():
    # reads in the dark current values and return the average
    dark=read_dark()

    # reads in unfiltered data per frequency
    unfiltered=extract_dark("Unfiltered",dark)

    # reads in filtered data per frequency
    filtered=extract_dark("Filtered",dark)

    return(unfiltered,filtered)



def main():
    #read in the data
    unfiltered, filtered = read_data()

    # Calculates the transmission and merges the data (filtered/unfiltered)
    merge_df=merge_and_calculate(unfiltered, filtered)

    # Plots the data on a graph
    plot_data(merge_df)

    # saves the calculated and aggregated data
    save_data(merge_df)



if __name__ == '__main__':
    main()

